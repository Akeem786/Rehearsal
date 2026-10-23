"""RULE-003: TTS Hostility.

Detects artifacts that create severe speech synthesis (TTS) problems, such as
Markdown tables, raw JSON structures, raw URLs, and hexadecimal bitmasks.
Analyzes static tool descriptions and parameter metadata without executing code.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from rehearsal.linter.models import LinterConfig, LinterFinding, Severity
from rehearsal.linter.explainers import explain_tts_hostility, example_tts_remediation

# Regex patterns for speech synthesis hostility
MARKDOWN_TABLE_REGEX = re.compile(r"\|.+\|.+\|", re.MULTILINE)
URL_REGEX = re.compile(r"https?://[^\s<>\"')]+|\[[^\]]+\]\([^\)]+\)", re.IGNORECASE)
RAW_HEX_REGEX = re.compile(r"\b0x[0-9a-fA-F]{3,}\b")
RAW_JSON_BLOCK_REGEX = re.compile(r"\{[^{}]*\"[a-zA-Z0-9_-]+\"\s*:\s*[^{}]*\}", re.DOTALL)


def check_tts_hostility(
    tool_name: str,
    description: str,
    input_schema: Dict[str, Any],
    sample_output: Optional[str] = None,
    config: Optional[LinterConfig] = None,
) -> List[LinterFinding]:
    """Inspect tool metadata, descriptions, and optional static output for TTS hostility."""
    findings: List[LinterFinding] = []
    cfg = config or LinterConfig()

    targets_to_check = [("description", description or "")]

    # Also inspect parameter descriptions in schema
    properties = input_schema.get("properties", {}) if isinstance(input_schema, dict) else {}
    if isinstance(properties, dict):
        for prop_name, prop_data in properties.items():
            if isinstance(prop_data, dict) and "description" in prop_data:
                targets_to_check.append((f"parameter '{prop_name}' description", str(prop_data["description"])))

    # If static sample output is provided (from offline fixtures, not code execution), inspect it
    if sample_output and isinstance(sample_output, str):
        targets_to_check.append(("static sample output", sample_output))

    for target_label, text in targets_to_check:
        if not text:
            continue

        # 1. Markdown tables
        if MARKDOWN_TABLE_REGEX.search(text):
            findings.append(
                LinterFinding(
                    rule_id="RULE-003",
                    severity=Severity.ERROR,
                    tool_name=tool_name,
                    title=f"Markdown table detected in {target_label}",
                    evidence=f"Text contains Markdown table pipes: '{text[:80]}...'",
                    voice_impact=explain_tts_hostility("Markdown table formatting", "table columns and rows"),
                    recommendation="Convert tabular data into a short conversational narrative or bullet points suited for audio.",
                    suggested_fix_example=example_tts_remediation(),
                    is_heuristic=True,
                )
            )

        # 2. Raw JSON blocks
        if "```json" in text.lower() or RAW_JSON_BLOCK_REGEX.search(text):
            findings.append(
                LinterFinding(
                    rule_id="RULE-003",
                    severity=Severity.ERROR,
                    tool_name=tool_name,
                    title=f"Raw JSON payload detected in {target_label}",
                    evidence=f"Text contains serialized JSON dictionaries: '{text[:80]}...'",
                    voice_impact=explain_tts_hostility("raw JSON", "braces, quotes, and colons"),
                    recommendation="Extract the key takeaway into a natural spoken sentence instead of returning raw JSON.",
                    suggested_fix_example=example_tts_remediation(),
                    is_heuristic=True,
                )
            )

        # 3. Raw URLs
        url_match = URL_REGEX.search(text)
        if url_match:
            findings.append(
                LinterFinding(
                    rule_id="RULE-003",
                    severity=Severity.WARNING,
                    tool_name=tool_name,
                    title=f"Raw URL detected in {target_label}",
                    evidence=f"Found URL: '{url_match.group(0)[:60]}'",
                    voice_impact=(
                        "TTS synthesizers read out URLs letter by letter ('h-t-t-p-s-colon-slash-slash...'), "
                        "which is completely unusable in voice-only interfaces."
                    ),
                    recommendation="Send links via assistant companion cards or SMS; do not speak URLs aloud.",
                    suggested_fix_example="Replace link with: 'I sent the details to your companion app.'",
                    is_heuristic=True,
                )
            )

        # 4. Hexadecimal codes / Bitmasks
        hex_match = RAW_HEX_REGEX.search(text)
        if hex_match:
            findings.append(
                LinterFinding(
                    rule_id="RULE-003",
                    severity=Severity.WARNING,
                    tool_name=tool_name,
                    title=f"Hexadecimal/Bitmask value in {target_label}",
                    evidence=f"Found hex literal: '{hex_match.group(0)}'",
                    voice_impact=explain_tts_hostility("hexadecimal values", hex_match.group(0)),
                    recommendation="Translate low-level bitmasks into human-readable states ('on', 'off', 'standby').",
                    suggested_fix_example="Replace '0x0001' with 'enabled' or 'active'.",
                    is_heuristic=True,
                )
            )

    return findings
