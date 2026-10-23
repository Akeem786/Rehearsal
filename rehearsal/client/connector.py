"""MCP client connector implementation for Rehearsal.

Connects to local MCP servers via official Python MCP SDK client interfaces.
Supports in-process MCPServer instances, Streamable HTTP URLs, and SSE endpoints.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union
from mcp.client import Client
from mcp.server import MCPServer
from mcp_types._types import CallToolResult, Tool

logger = logging.getLogger("rehearsal.client")


class MCPConnectorError(Exception):
    """Base exception for Rehearsal MCP client connector errors."""
    pass


class ToolNotFoundError(MCPConnectorError):
    """Raised when an invoked tool does not exist on the connected server."""
    pass


class ToolExecutionError(MCPConnectorError):
    """Raised when an MCP tool invocation fails on the server."""
    def __init__(self, tool_name: str, message: str) -> None:
        super().__init__(f"Tool '{tool_name}' failed: {message}")
        self.tool_name = tool_name
        self.message = message


class MCPClientConnector:
    """Asynchronous client connector wrapping the official MCP Python SDK Client.

    Can connect to:
    - An in-process `MCPServer` instance (fast, reliable, fully offline).
    - A Streamable HTTP / SSE endpoint URL string (e.g. 'http://127.0.0.1:8001/mcp').
    """

    def __init__(
        self,
        server: Optional[Union[MCPServer, str]] = None,
        raise_on_tool_error: bool = False,
    ) -> None:
        """Initialize connector.

        Args:
            server: Target MCPServer instance or server URL string.
                    If None, defaults to Rehearsal's reference server factory.
            raise_on_tool_error: If True, tool errors raise ToolExecutionError.
        """
        if server is None:
            from rehearsal.server.server import create_reference_server
            self._target: Union[MCPServer, str] = create_reference_server()
        else:
            self._target = server

        self.raise_on_tool_error = raise_on_tool_error
        self._client: Optional[Client] = None
        self._is_connected = False

    @property
    def is_connected(self) -> bool:
        """Whether the client session is currently active."""
        return self._is_connected

    async def connect(self) -> None:
        """Establish connection and initialize MCP client session."""
        if self._is_connected:
            return

        try:
            self._client = Client(self._target)
            await self._client.__aenter__()
            self._is_connected = True
            logger.info("Connected to MCP server target: %s", self._target)
        except Exception as exc:
            self._is_connected = False
            self._client = None
            raise MCPConnectorError(f"Failed to connect to MCP target '{self._target}': {exc}") from exc

    async def close(self) -> None:
        """Close client session and release network/task resources safely."""
        if not self._is_connected or self._client is None:
            self._is_connected = False
            self._client = None
            return

        try:
            await self._client.__aexit__(None, None, None)
        except Exception as exc:
            logger.warning("Error during MCP client session shutdown: %s", exc)
        finally:
            self._is_connected = False
            self._client = None
            logger.info("MCP client session closed.")

    async def __aenter__(self) -> MCPClientConnector:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def _ensure_connected(self) -> Client:
        """Verify client connection before making requests."""
        if not self._is_connected or self._client is None:
            raise MCPConnectorError("Client is not connected. Call 'await connect()' or use 'async with connector'.")
        return self._client

    async def list_tools(self) -> List[Tool]:
        """Query and return all registered tools and their schemas from the server."""
        client = self._ensure_connected()
        try:
            result = await client.list_tools()
            return list(result.tools)
        except Exception as exc:
            raise MCPConnectorError(f"Failed to list tools from MCP server: {exc}") from exc

    async def get_tool(self, name: str) -> Optional[Tool]:
        """Retrieve schema metadata for a specific tool by name."""
        tools = await self.list_tools()
        for t in tools:
            if t.name == name:
                return t
        return None

    async def call_tool(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> CallToolResult:
        """Invoke a tool by name with arguments.

        Args:
            name: Tool identifier.
            arguments: Dictionary of arguments conforming to tool schema.

        Returns:
            CallToolResult object.

        Raises:
            ToolNotFoundError: If the tool does not exist on the server.
            ToolExecutionError: If raise_on_tool_error is True and execution fails.
        """
        client = self._ensure_connected()
        args = arguments or {}

        try:
            result: CallToolResult = await client.call_tool(name, args)
        except Exception as exc:
            err_msg = str(exc)
            if "Unknown tool" in err_msg or "not found" in err_msg.lower():
                raise ToolNotFoundError(f"Tool '{name}' was not found on server: {err_msg}") from exc
            raise MCPConnectorError(f"Transport failure while calling tool '{name}': {exc}") from exc

        # Check for error payload in result
        if result.is_error:
            error_text = ""
            if result.content and len(result.content) > 0:
                first = result.content[0]
                error_text = getattr(first, "text", str(first))

            if "Unknown tool" in error_text:
                raise ToolNotFoundError(f"Server reported unknown tool: '{name}'")

            if self.raise_on_tool_error:
                raise ToolExecutionError(name, error_text)

        return result

    @staticmethod
    def extract_text(result: CallToolResult) -> str:
        """Helper to extract text content from CallToolResult."""
        if not result or not result.content:
            return ""
        texts = [getattr(c, "text", str(c)) for c in result.content if hasattr(c, "text")]
        return "\n".join(texts)
