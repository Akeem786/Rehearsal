"""Sanity tests for Rehearsal development environment and dependency harness."""

import importlib.metadata
import sys
import pytest
from pydantic import BaseModel, Field
from fastapi import FastAPI
import httpx
import rehearsal


def test_python_runtime_version():
    """Verify that Python runtime is at least 3.12."""
    assert sys.version_info >= (3, 12), f"Expected Python >= 3.12, got {sys.version}"


def test_rehearsal_package_metadata():
    """Verify that Rehearsal root package is importable and has version metadata."""
    assert rehearsal.__version__ == "0.1.0"
    assert rehearsal.__author__ == "Rehearsal Hackathon Team"


@pytest.mark.asyncio
async def test_fastapi_and_pydantic_sanity():
    """Verify that FastAPI and Pydantic work together cleanly with async client."""
    class HealthPayload(BaseModel):
        status: str = Field(..., description="Service status")
        service: str = "rehearsal-test"

    app = FastAPI(title="Rehearsal Test App")

    @app.get("/health", response_model=HealthPayload)
    async def health_endpoint():
        return HealthPayload(status="healthy")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "rehearsal-test"


def test_mcp_sdk_version_and_imports():
    """Verify that the official MCP SDK is installed at expected version and core symbols import."""
    version = importlib.metadata.version("mcp")
    assert version.startswith("2."), f"Expected MCP SDK v2.x, found {version}"

    # Verify server & client modules
    import mcp.server
    import mcp.client
    from mcp.server import MCPServer
    from mcp.client import Client

    assert MCPServer is not None
    assert Client is not None


def test_mcp_transport_modules_present():
    """Verify availability of Streamable HTTP, SSE, and Stdio transports in MCP SDK."""
    # Server transports
    import mcp.server.streamable_http
    import mcp.server.sse
    import mcp.server.stdio

    # Client transports
    import mcp.client.streamable_http
    import mcp.client.sse
    import mcp.client.stdio

    assert mcp.server.streamable_http is not None
    assert mcp.client.streamable_http is not None


@pytest.mark.asyncio
async def test_mcp_server_in_memory_tool_registration_and_execution():
    """Verify that MCPServer can register, list, and invoke tools deterministically."""
    from mcp.server import MCPServer

    test_server = MCPServer(name="rehearsal-sanity-server")

    @test_server.tool(name="voice_echo", description="Echoes a spoken prompt back for testing")
    def voice_echo(utterance: str) -> str:
        return f"Heard: {utterance}"

    # Test tool listing
    tools = await test_server.list_tools()
    tool_names = [t.name for t in tools]
    assert "voice_echo" in tool_names

    # Test tool invocation
    call_result = await test_server.call_tool("voice_echo", {"utterance": "turn on lights"})
    assert not call_result.is_error
    assert len(call_result.content) > 0
    assert "Heard: turn on lights" in call_result.content[0].text
