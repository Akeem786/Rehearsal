"""Corrected reference MCP tools demonstrating voice-first best practices.

These tools are designed specifically for voice assistants:
- Clear, natural language tool names and descriptions for high-precision discovery.
- Flat schemas with intuitive, utterance-friendly argument names and sensible defaults.
- Concise, speech-ready responses (TTS-friendly: no raw JSON, no markdown tables, no URLs).
- Conversational turn management and clear error recovery prompts.
All implementations are deterministic and execute locally without external dependencies.
"""

from __future__ import annotations

from mcp.server import MCPServer


# -----------------------------------------------------------------------------
# Pair A: Weather (Corrected)
# Voice-first pattern: Spoken summary, flat location parameter, speech-ready output
# -----------------------------------------------------------------------------

def get_weather_summary(location: str, timeframe: str = "today") -> str:
    """Get a concise, spoken weather summary and forecast for a city or location. Use this when the user asks about current weather, rain, or temperatures."""
    loc = location.strip() if location else ""
    if not loc:
        return "I need a city or location to look up the weather. Which city would you like to check?"

    timeframe_clean = timeframe.strip().lower() if timeframe else "today"

    # Deterministic simulated voice responses for key locations
    loc_lower = loc.lower()
    if "seattle" in loc_lower:
        return (
            f"In Seattle {timeframe_clean}, it is 58 degrees and mostly cloudy with a light breeze. "
            "There is a 20 percent chance of rain later this evening."
        )
    elif "new york" in loc_lower or "nyc" in loc_lower:
        return (
            f"In New York {timeframe_clean}, it is currently 64 degrees and sunny with clear skies. "
            "Expect a pleasant day with temperatures reaching the upper sixties."
        )
    elif "london" in loc_lower:
        return (
            f"In London {timeframe_clean}, it is 54 degrees and overcast with scattered drizzle. "
            "You might want to take an umbrella if you are heading out."
        )
    else:
        # Generalized fallback voice summary
        return (
            f"In {loc.title()} {timeframe_clean}, it is currently 62 degrees and partly cloudy "
            "with mild winds and no rain expected."
        )


# -----------------------------------------------------------------------------
# Pair B: Smart Home (Corrected)
# Voice-first pattern: Natural room & device names, concise conversational confirmation
# -----------------------------------------------------------------------------

def control_home_device(
    room: str,
    device: str = "lights",
    action: str = "turn on",
) -> str:
    """Control smart home devices like lights, thermostats, and switches using natural voice names and simple actions."""
    clean_room = room.strip().lower() if room else ""
    if not clean_room:
        return "Which room would you like to control?"

    clean_device = device.strip().lower() if device else "lights"
    clean_action = action.strip().lower() if action else "turn on"

    # Normalize common spoken actions
    if clean_action in ("turn on", "on", "enable", "switch on"):
        verb = "Turned on"
    elif clean_action in ("turn off", "off", "disable", "switch off"):
        verb = "Turned off"
    elif clean_action in ("dim", "lower"):
        verb = "Dimmed"
    elif clean_action in ("brighten", "raise"):
        verb = "Brightened"
    else:
        verb = f"Set {clean_action} for"

    return f"{verb} the {clean_room} {clean_device}."


# -----------------------------------------------------------------------------
# Pair C: Travel / Flights (Corrected)
# Voice-first pattern: Flexible city names, top 2 spoken choices, clear voice CTA
# -----------------------------------------------------------------------------

def find_flight_summary(
    origin: str,
    destination: str,
    date: str = "this Friday",
) -> str:
    """Search and summarize the best flight options between two cities for a given date. Ideal for answering spoken travel questions."""
    orig = origin.strip().title() if origin else ""
    dest = destination.strip().title() if destination else ""

    if not orig or not dest:
        return "Please specify both departure and arrival cities to check flights."

    clean_date = date.strip() if date else "this Friday"

    # Deterministic spoken summary highlighting the top two options
    return (
        f"I found two nonstop flights from {orig} to {dest} {clean_date}: "
        "British Airways departing at 8:15 AM for $450, and "
        "Virgin Atlantic departing at 6:30 PM for $482. "
        "Would you like me to reserve a seat on either flight?"
    )


# -----------------------------------------------------------------------------
# Registration Helper
# -----------------------------------------------------------------------------

def register_corrected_tools(server: MCPServer) -> None:
    """Register all voice-optimized reference tools onto the given MCPServer."""
    server.tool(name="get_weather_summary")(get_weather_summary)
    server.tool(name="control_home_device")(control_home_device)
    server.tool(name="find_flight_summary")(find_flight_summary)
