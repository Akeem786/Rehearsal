"""Reusable explanation templates and remediation examples for voice-readiness diagnostics."""

from __future__ import annotations


def explain_schema_depth(path: str, depth: int, max_allowed: int) -> str:
    """Generate voice reasoning for deeply nested schemas."""
    return (
        f"Input nesting depth is {depth} (at path '{path}'), which exceeds the recommended "
        f"voice maximum of {max_allowed}. Voice assistants struggle to map unstructured spoken utterances "
        "into deeply nested objects without conversational slot-filling friction."
    )


def example_schema_flattening() -> str:
    """Before/after example for schema flattening."""
    return (
        "Before: `{\"spec\": {\"coordinates\": {\"latitude\": 47.6, \"longitude\": -122.3}}}`\n"
        "After:  `{\"location\": \"Seattle\"}` or `{\"latitude\": 47.6, \"longitude\": -122.3}`"
    )


def explain_argument_count(required: int, total: int, max_req: int) -> str:
    """Generate voice reasoning for high argument counts."""
    return (
        f"Tool requires {required} arguments ({total} total), exceeding the voice recommendation of {max_req}. "
        "In voice interactions, a user rarely specifies more than 2-3 parameters in a single utterance. "
        "Excessive required parameters force long multi-turn clarification dialogues."
    )


def example_argument_simplification() -> str:
    """Before/after example for argument simplification."""
    return (
        "Before: `def book_flight(origin_iata, dest_iata, depart_iso, return_iso, fare_tier, seat_class, meal_code)`\n"
        "After:  `def book_flight(origin: str, destination: str, date: str = 'today')`"
    )


def explain_tts_hostility(artifact_type: str, snippet: str) -> str:
    """Generate voice reasoning for TTS-hostile artifacts."""
    return (
        f"Detected {artifact_type} ('{snippet}'). Text-to-Speech (TTS) synthesizers read out raw table pipes, "
        "hex codes, and markdown punctuation verbatim, creating severe ear fatigue and unintelligible speech."
    )


def example_tts_remediation() -> str:
    """Before/after example for TTS-friendly responses."""
    return (
        "Before: `| Node ID | Status | ACK_HEX |\n| 0x4A9F | 200_OK | 0xDEADBEEF |`\n"
        "After:  `'Turned on the living room lights.'`"
    )


def explain_parameter_ergonomics(param_name: str, issue_kind: str) -> str:
    """Generate voice reasoning for problematic parameter names."""
    return (
        f"Parameter '{param_name}' contains {issue_kind}. In conversational voice interfaces, "
        "parameter names should correspond to natural spoken concepts that speech models can easily map from spoken slots."
    )


def example_parameter_remediation(param_name: str) -> str:
    """Before/after example for speech-friendly parameter names."""
    replacements = {
        "device_guid_hex": "device: str = 'lights', room: str = 'living room'",
        "register_state_mask": "action: str = 'turn on'",
        "origin_iata": "origin: str (e.g., 'New York' or 'JFK')",
        "dest_iata": "destination: str (e.g., 'London' or 'LHR')",
        "depart_iso": "date: str (e.g., 'this Friday')",
        "spec": "flat parameters directly at top level",
    }
    suggested = replacements.get(param_name, "natural conversational noun (e.g., 'city', 'room')")
    return f"Before: `{param_name}`\nAfter:  `{suggested}`"
