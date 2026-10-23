"""Automated test suite for Rehearsal reference MCP test server.

Verifies:
1. All six reference tools (three flawed, three corrected) register correctly.
2. Each tool provides a name, description, and valid input schema.
3. Flawed and corrected tools execute deterministically.
4. Corrected tool responses satisfy voice conciseness and speech readability criteria.
5. Argument validation and conversational error handling operate safely.
6. MCP server transports (Streamable HTTP and SSE) instantiate properly.
"""

import json
import pytest
from starlette.applications import Starlette
from mcp.server.mcpserver.exceptions import ToolError
from rehearsal.server import (
    create_reference_server,
    get_streamable_http_app,
)
from rehearsal.server.server import get_sse_app

EXPECTED_FLAWED_TOOLS = [
    "fetch_meteorological_telemetry_v2",
    "execute_home_iot_command_rpc",
    "query_itinerary_and_schedule_matrix",
]

EXPECTED_CORRECTED_TOOLS = [
    "get_weather_summary",
    "control_home_device",
    "find_flight_summary",
]

ALL_EXPECTED_TOOLS = EXPECTED_FLAWED_TOOLS + EXPECTED_CORRECTED_TOOLS


@pytest.fixture
def server():
    """Create a fresh reference MCP server for each test."""
    return create_reference_server()


@pytest.mark.asyncio
async def test_server_registers_all_six_tools(server):
    """Verify that all six tools are registered with distinct, non-empty names."""
    tools = await server.list_tools()
    tool_names = [t.name for t in tools]

    assert len(tools) == 6, f"Expected 6 tools, found {len(tools)}: {tool_names}"
    for expected in ALL_EXPECTED_TOOLS:
        assert expected in tool_names, f"Expected tool '{expected}' not found in registered tools"


@pytest.mark.asyncio
async def test_tool_metadata_and_input_schemas(server):
    """Verify that each tool has an informative description and inspect schema nesting."""
    tools = await server.list_tools()
    tool_map = {t.name: t for t in tools}

    for name, tool in tool_map.items():
        assert tool.description and len(tool.description.strip()) > 10, (
            f"Tool '{name}' lacks an adequate description."
        )
        assert tool.input_schema is not None
        assert tool.input_schema.get("type") == "object"

    # Schema ergonomics comparison: Flawed tools exhibit nested definitions
    flawed_weather_schema = tool_map["fetch_meteorological_telemetry_v2"].input_schema
    assert "$defs" in flawed_weather_schema or "spec" in flawed_weather_schema.get("properties", {}), (
        "Flawed weather tool should have a complex/nested input structure."
    )

    # Corrected tools exhibit flat, simple primitive properties
    corrected_weather_schema = tool_map["get_weather_summary"].input_schema
    assert "location" in corrected_weather_schema.get("properties", {}), (
        "Corrected weather tool should accept a flat 'location' parameter."
    )
    assert "$defs" not in corrected_weather_schema, (
        "Corrected weather tool should not require nested object definitions."
    )

    corrected_home_schema = tool_map["control_home_device"].input_schema
    assert "room" in corrected_home_schema.get("properties", {})
    assert "action" in corrected_home_schema.get("properties", {})


@pytest.mark.asyncio
async def test_flawed_tools_deterministic_output(server):
    """Verify that flawed tools return deterministic, voice-hostile outputs."""
    # 1. Weather: returns raw JSON with sensor telemetry
    call_wx = await server.call_tool(
        "fetch_meteorological_telemetry_v2",
        {"spec": {"coordinates": {"latitude": 47.6062, "longitude": -122.3321}}},
    )
    assert not call_wx.is_error
    raw_text = call_wx.content[0].text
    parsed_json = json.loads(raw_text)
    assert "atmospheric_telemetry" in parsed_json
    assert "thermodynamic_temp_kelvin" in parsed_json["atmospheric_telemetry"]
    assert "raw_checksum_crc32" in parsed_json

    # 2. Smart Home: returns a markdown table with hex codes
    call_iot = await server.call_tool(
        "execute_home_iot_command_rpc",
        {"device_guid_hex": "0x4A9F-B3C1", "register_state_mask": 1},
    )
    assert not call_iot.is_error
    assert "| Node GUID |" in call_iot.content[0].text
    assert "0x4A9F-B3C1" in call_iot.content[0].text

    # 3. Travel: returns a markdown table with flight matrix
    call_travel = await server.call_tool(
        "query_itinerary_and_schedule_matrix",
        {"spec": {"origin_iata": "JFK", "dest_iata": "LHR", "dates": {"depart_iso": "2026-11-01"}}},
    )
    assert not call_travel.is_error
    assert "| Flight # |" in call_travel.content[0].text
    assert "BA0178" in call_travel.content[0].text


@pytest.mark.asyncio
async def test_corrected_tools_deterministic_output(server):
    """Verify that corrected tools return speech-ready, conversational responses."""
    # 1. Weather: concise spoken sentence
    call_wx = await server.call_tool("get_weather_summary", {"location": "Seattle"})
    assert not call_wx.is_error
    wx_text = call_wx.content[0].text
    assert "In Seattle today, it is 58 degrees" in wx_text
    assert "mostly cloudy" in wx_text

    # 2. Smart Home: crisp spoken confirmation
    call_iot = await server.call_tool(
        "control_home_device",
        {"room": "living room", "device": "lights", "action": "turn on"},
    )
    assert not call_iot.is_error
    assert call_iot.content[0].text == "Turned on the living room lights."

    # 3. Travel: conversational summary with two top flights and closing CTA
    call_flight = await server.call_tool(
        "find_flight_summary",
        {"origin": "New York", "destination": "London", "date": "this Friday"},
    )
    assert not call_flight.is_error
    flight_text = call_flight.content[0].text
    assert "I found two nonstop flights from New York to London this Friday:" in flight_text
    assert "British Airways" in flight_text
    assert "Would you like me to reserve a seat on either flight?" in flight_text


@pytest.mark.asyncio
async def test_corrected_outputs_voice_conciseness_and_readability(server):
    """Verify that corrected tools satisfy speech ergonomics (low word count, no raw markdown/tables)."""
    # Weather conciseness
    wx_res = await server.call_tool("get_weather_summary", {"location": "New York"})
    wx_text = wx_res.content[0].text
    words_wx = wx_text.split()
    assert len(words_wx) <= 40, f"Weather response too long for voice: {len(words_wx)} words"
    assert "{" not in wx_text and "|" not in wx_text and "http" not in wx_text

    # Smart Home conciseness
    iot_res = await server.call_tool("control_home_device", {"room": "kitchen", "device": "fan", "action": "turn off"})
    iot_text = iot_res.content[0].text
    assert len(iot_text.split()) <= 15
    assert iot_text == "Turned off the kitchen fan."
    assert "|" not in iot_text and "0x" not in iot_text

    # Flight conciseness
    flight_res = await server.call_tool("find_flight_summary", {"origin": "Boston", "destination": "Chicago"})
    flight_text = flight_res.content[0].text
    words_flight = flight_text.split()
    assert len(words_flight) <= 50, f"Flight response too long for voice: {len(words_flight)} words"
    assert "|" not in flight_text and "[" not in flight_text and "http" not in flight_text


@pytest.mark.asyncio
async def test_tool_argument_validation_and_conversational_recovery(server):
    """Verify schema validation catches missing arguments and functions handle empty inputs gracefully."""
    # Missing required argument on flawed weather raises ToolError
    with pytest.raises(ToolError):
        await server.call_tool("fetch_meteorological_telemetry_v2", {})

    # Missing required argument on flawed travel raises ToolError
    with pytest.raises(ToolError):
        await server.call_tool("query_itinerary_and_schedule_matrix", {})

    # Corrected weather: empty location returns conversational recovery prompt
    empty_loc_res = await server.call_tool("get_weather_summary", {"location": ""})
    assert not empty_loc_res.is_error
    assert "Which city would you like to check?" in empty_loc_res.content[0].text

    # Corrected smart home: empty room returns conversational clarification
    empty_room_res = await server.call_tool("control_home_device", {"room": ""})
    assert not empty_room_res.is_error
    assert "Which room would you like to control?" in empty_room_res.content[0].text

    # Corrected flights: empty destination returns conversational clarification
    empty_dest_res = await server.call_tool("find_flight_summary", {"origin": "New York", "destination": ""})
    assert not empty_dest_res.is_error
    assert "Please specify both departure and arrival cities" in empty_dest_res.content[0].text


def test_transport_app_instantiation():
    """Verify that Streamable HTTP and SSE Starlette applications instantiate cleanly."""
    http_app = get_streamable_http_app()
    assert isinstance(http_app, Starlette)

    sse_app = get_sse_app()
    assert isinstance(sse_app, Starlette)
