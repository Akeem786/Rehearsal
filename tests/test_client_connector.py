"""Automated tests for Rehearsal MCP Client Connector.

Verifies:
1. Client lifecycle management and clean resource release.
2. Listing tools and retrieving schemas from the reference server.
3. Successful tool calls returning expected CallToolResult.
4. Error handling for non-existent tools (ToolNotFoundError).
5. Error handling for malformed/missing arguments (ToolExecutionError).
6. Text extraction helper utility.
"""

import pytest
from rehearsal.client import (
    MCPClientConnector,
    MCPConnectorError,
    ToolExecutionError,
    ToolNotFoundError,
)
from rehearsal.server import create_reference_server


@pytest.mark.asyncio
async def test_client_lifecycle_and_connection_state():
    """Verify connect, is_connected flag, and clean close."""
    server = create_reference_server()
    connector = MCPClientConnector(server=server)

    assert not connector.is_connected
    await connector.connect()
    assert connector.is_connected

    await connector.close()
    assert not connector.is_connected


@pytest.mark.asyncio
async def test_client_async_context_manager():
    """Verify that async with context manager automatically connects and cleans up."""
    server = create_reference_server()
    async with MCPClientConnector(server=server) as client:
        assert client.is_connected
        tools = await client.list_tools()
        assert len(tools) == 6

    assert not client.is_connected


@pytest.mark.asyncio
async def test_client_list_tools_and_get_tool():
    """Verify tool discovery and retrieving individual tool metadata."""
    async with MCPClientConnector() as client:
        tools = await client.list_tools()
        names = [t.name for t in tools]
        assert "get_weather_summary" in names
        assert "fetch_meteorological_telemetry_v2" in names

        # Test get_tool
        weather_tool = await client.get_tool("get_weather_summary")
        assert weather_tool is not None
        assert weather_tool.name == "get_weather_summary"

        missing_tool = await client.get_tool("non_existent_tool")
        assert missing_tool is None


@pytest.mark.asyncio
async def test_client_call_valid_tools():
    """Verify calling valid tools returns successful results and extract_text works."""
    async with MCPClientConnector() as client:
        # Call corrected weather tool
        res_wx = await client.call_tool("get_weather_summary", {"location": "Seattle"})
        assert not res_wx.is_error
        text = client.extract_text(res_wx)
        assert "In Seattle today, it is 58 degrees" in text

        # Call corrected smart home tool
        res_iot = await client.call_tool(
            "control_home_device",
            {"room": "kitchen", "device": "fan", "action": "turn off"},
        )
        assert not res_iot.is_error
        assert client.extract_text(res_iot) == "Turned off the kitchen fan."


@pytest.mark.asyncio
async def test_client_unknown_tool_error_handling():
    """Verify that calling an unknown tool raises ToolNotFoundError or marks error."""
    # When raise_on_tool_error=True
    async with MCPClientConnector(raise_on_tool_error=True) as client:
        with pytest.raises(ToolNotFoundError):
            await client.call_tool("unregistered_bogus_tool", {})

    # When raise_on_tool_error=False
    async with MCPClientConnector(raise_on_tool_error=False) as client:
        try:
            res = await client.call_tool("unregistered_bogus_tool", {})
            assert res.is_error
        except ToolNotFoundError:
            pass  # Also valid behavior


@pytest.mark.asyncio
async def test_client_malformed_arguments_error_handling():
    """Verify that invoking a tool with invalid/missing arguments triggers ToolExecutionError."""
    # Flawed weather tool requires nested coordinates in spec
    async with MCPClientConnector(raise_on_tool_error=True) as client:
        with pytest.raises(ToolExecutionError) as exc_info:
            await client.call_tool("fetch_meteorological_telemetry_v2", {})
        assert "fetch_meteorological_telemetry_v2" in str(exc_info.value)


@pytest.mark.asyncio
async def test_client_not_connected_call_raises_error():
    """Verify calling methods before connect() raises MCPConnectorError."""
    client = MCPClientConnector()
    with pytest.raises(MCPConnectorError) as exc:
        await client.list_tools()
    assert "not connected" in str(exc.value).lower()
