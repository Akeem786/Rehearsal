"""RULE-005: Description Clarity.

Flags missing, excessively short, overly long, or purely technical descriptions
that lack natural-language trigger indicators for voice assistants.
"""

from __future__ import annotations

import re
from typing import List
from rehearsal.linter.models import LinterConfig, LinterFinding, Severity

# Common intent verbs expected in clear voice tool descriptions
VOICE_INTENT_VERBS = {
    "get", "find", "search", "check", "control", "turn", "set", "query",
    "lookup", "show", "read", "update", "create", "book", "reserve", "play"
}

JARGON_PATTERNS = re.compile(
    r"(low-level binary rpc|multi-spectral atmospheric sensor array|multi-tenant gds relational itinerary)",
    re.IGNORECASE,
)


def check_description_clarity(
    tool_name: str,
    description: str,
    config: LinterConfig,
) -> List[LinterFinding]:
    """Inspect tool description for voice discoverability and intent clarity."""
    findings: List[LinterFinding] = []
    desc = (description or "").strip()

    # 1. Missing or empty description (ERROR)
    if not desc:
        findings.append(
            LinterFinding(
                rule_id="RULE-005",
                severity=Severity.ERROR,
                tool_name=tool_name,
                title="Missing tool description",
                evidence="Description is empty or contains only whitespace.",
                voice_impact=(
                    "Voice-first assistants rely heavily on descriptions to decide which tool to call "
                    "when a user speaks an utterance. Without a description, tool selection fails or hallucinates."
                ),
                recommendation="Provide a clear 1-2 sentence description explaining what the tool does and when to call it.",
                suggested_fix_example=(
                    f"Description: 'Get a concise weather summary for any city or location. "
                    "Use when the user asks about current temperatures or rain.'"
                ),
                is_heuristic=True,
            )
        )
        return findings

    # 2. Excessively short description (WARNING)
    if len(desc) < config.min_description_length_warning or len(desc.split()) < 4:
        findings.append(
            LinterFinding(
                rule_id="RULE-005",
                severity=Severity.WARNING,
                tool_name=tool_name,
                title=f"Description is too brief ({len(desc)} characters)",
                evidence=f"Description: '{desc}'",
                voice_impact=(
                    "Terse descriptions fail to provide enough semantic context for speech intent matchers "
                    "to distinguish between similar voice requests."
                ),
                recommendation="Expand the description to specify user intent triggers and key argument purposes.",
                suggested_fix_example=(
                    "Include what the tool does and when to use it (e.g., 'Control smart home devices like lights...')"
                ),
                is_heuristic=True,
            )
        )

    # 3. Excessively long description (WARNING - ear fatigue / prompt bloat)
    if len(desc) > config.max_description_length_warning:
        findings.append(
            LinterFinding(
                rule_id="RULE-005",
                severity=Severity.WARNING,
                tool_name=tool_name,
                title=f"Description is excessively long ({len(desc)} characters)",
                evidence=f"Description character count: {len(desc)} (exceeds recommended {config.max_description_length_warning})",
                voice_impact=(
                    "Overly long tool descriptions bloat the assistant prompt context and may cause latency "
                    "or confuse semantic tool routing in voice assistants."
                ),
                recommendation="Keep descriptions concise (under 250 characters) and focused on user intent triggers.",
                suggested_fix_example="Trim technical implementation details; describe only the user-facing capability.",
                is_heuristic=True,
            )
        )

    # 4. Purely technical jargon lacking conversational intent triggers (WARNING)
    if JARGON_PATTERNS.search(desc):
        findings.append(
            LinterFinding(
                rule_id="RULE-005",
                severity=Severity.WARNING,
                tool_name=tool_name,
                title="Description uses heavy technical jargon without conversational triggers",
                evidence=f"Description contains internal implementation terminology: '{desc[:75]}...'",
                voice_impact=(
                    "Spoken queries use natural phrases ('what's the weather in Seattle?'). When a tool description "
                    "is written entirely in hardware/network jargon, intent routers fail to match user requests."
                ),
                recommendation="Rephrase using natural language phrasing that reflects how end-users speak requests.",
                suggested_fix_example=(
                    "Replace 'Low-level binary RPC actuator dispatcher...' with "
                    "'Control smart home devices like lights, thermostats, and switches using natural room names.'"
                ),
                is_heuristic=True,
            )
        )

    return findings
