"""Rehearsal reference MCP server implementation.

Exposes six reference tools (three flawed anti-patterns and three corrected voice patterns)
via the official MCP Python SDK (MCPServer). Supports Streamable HTTP, SSE, and Stdio transports.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional
from starlette.applications import Starlette
from mcp.server import MCPServer

from rehearsal.server.flawed_tools import register_flawed_tools
from rehearsal.server.corrected_tools import register_corrected_tools


def create_reference_server(
    name: str = "rehearsal-reference-server",
    version: str = "0.1.0",
) -> MCPServer:
    """Create and configure the reference MCP server with all flawed and corrected tools."""
    server = MCPServer(
        name=name,
        version=version,
        instructions=(
            "Rehearsal reference MCP server providing both voice anti-pattern tools and "
            "voice-optimized tool counterparts for comparative evaluation."
        ),
    )

    # Register all 3 flawed reference tools
    register_flawed_tools(server)

    # Register all 3 corrected reference tools
    register_corrected_tools(server)

    return server


# Default singleton instance for ASGI server runners
reference_server = create_reference_server()


def get_streamable_http_app(server: Optional[MCPServer] = None) -> Starlette:
    """Return a Starlette ASGI application configured for Streamable HTTP transport."""
    target_server = server or reference_server
    return target_server.streamable_http_app()


def get_sse_app(server: Optional[MCPServer] = None) -> Starlette:
    """Return a Starlette ASGI application configured for SSE transport."""
    target_server = server or reference_server
    return target_server.sse_app()


# ASGI application instance for uvicorn (e.g. `uvicorn rehearsal.server.server:app --port 8001`)
app = get_streamable_http_app()


def run_server(
    transport: str = "streamable-http",
    host: str = "127.0.0.1",
    port: int = 8001,
) -> None:
    """Start the reference MCP server on the specified transport."""
    import uvicorn
    import anyio

    if transport == "streamable-http":
        print(f"Starting Rehearsal reference MCP server [Streamable HTTP] on http://{host}:{port}/mcp ...")
        http_app = get_streamable_http_app()
        uvicorn.run(http_app, host=host, port=port, log_level="info")
    elif transport == "sse":
        print(f"Starting Rehearsal reference MCP server [SSE] on http://{host}:{port}/sse ...")
        sse_app = get_sse_app()
        uvicorn.run(sse_app, host=host, port=port, log_level="info")
    elif transport == "stdio":
        print("Starting Rehearsal reference MCP server [Stdio] ...", file=sys.stderr)
        anyio.run(reference_server.run_stdio_async)
    else:
        raise ValueError(f"Unsupported transport: {transport}. Choose 'streamable-http', 'sse', or 'stdio'.")


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Run the Rehearsal reference MCP test server with flawed and corrected tools."
    )
    parser.add_argument(
        "--transport",
        choices=["streamable-http", "sse", "stdio"],
        default="streamable-http",
        help="MCP transport to run (default: streamable-http)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind for HTTP transports (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to bind for HTTP transports (default: 8001)",
    )
    args = parser.parse_args()
    run_server(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
