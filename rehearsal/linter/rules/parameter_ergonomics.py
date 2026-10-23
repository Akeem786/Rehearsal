"""RULE-004: Parameter Ergonomics.

Identifies parameter names that are unnatural or difficult to map from
spoken voice requests, such as opaque hardware GUIDs, cryptic abbreviations,
or machine register bitmasks.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set
from rehearsal.linter.models import LinterConfig, LinterFinding, Severity
from rehearsal.linter.explainers import explain_parameter_ergonomics, example_parameter_remediation

# Heuristic patterns for speech-unfriendly parameter names
OPAQUE_ID_PATTERNS = re.compile(
    r"(guid|uuid|hex|bitmask|mask|crc32|hash|mac_address|cluster_id|register)",
    re.IGNORECASE,
)
CRYPTIC_ABBREVIATIONS = {
    "lat": "latitude or city name",
    "lon": "longitude or city name",
    "iata": "city or airport name",
    "rpc": "action or command name",
    "pnr": "booking confirmation code",
    "gds": "travel inventory system",
    "flt": "flight number or flight",
    "dt": "date",
}


def check_parameter_ergonomics(
    tool_name: str,
    input_schema: Dict[str, Any],
    config: LinterConfig,
) -> List[LinterFinding]:
    """Inspect parameter names for spoken conversational ergonomics."""
    findings: List[LinterFinding] = []
    if not input_schema or not isinstance(input_schema, dict):
        return findings

    all_param_names: Set[str] = set()

    # Collect top-level property names
    properties = input_schema.get("properties", {})
    if isinstance(properties, dict):
        all_param_names.update(properties.keys())

    # Also collect property names from $defs / definitions
    defs = input_schema.get("$defs") or input_schema.get("definitions") or {}
    if isinstance(defs, dict):
        for def_schema in defs.values():
            if isinstance(def_schema, dict):
                def_props = def_schema.get("properties", {})
                if isinstance(def_props, dict):
                    all_param_names.update(def_props.keys())

    for param in sorted(all_param_names):
        # 1. Opaque IDs / Hex / Bitmasks
        if OPAQUE_ID_PATTERNS.search(param):
            findings.append(
                LinterFinding(
                    rule_id="RULE-004",
                    severity=Severity.WARNING,
                    tool_name=tool_name,
                    title=f"Unutterable/Opaque parameter name '{param}'",
                    evidence=f"Parameter name matches opaque identifier pattern: '{param}'",
                    voice_impact=explain_parameter_ergonomics(param, "opaque machine identifier or register pattern"),
                    recommendation="Use friendly natural language names that users naturally speak aloud (e.g. 'room', 'device_name').",
                    suggested_fix_example=example_parameter_remediation(param),
                    is_heuristic=True,
                )
            )
            continue

        # 2. Cryptic abbreviations
        param_lower = param.lower()
        for abbrev, suggested in CRYPTIC_ABBREVIATIONS.items():
            if abbrev == param_lower or param_lower.endswith(f"_{abbrev}") or param_lower.startswith(f"{abbrev}_"):
                findings.append(
                    LinterFinding(
                        rule_id="RULE-004",
                        severity=Severity.WARNING,
                        tool_name=tool_name,
                        title=f"Cryptic abbreviation in parameter '{param}'",
                        evidence=f"Parameter '{param}' contains abbreviation '{abbrev}'",
                        voice_impact=explain_parameter_ergonomics(param, f"cryptic abbreviation ('{abbrev}')"),
                        recommendation=f"Replace abbreviation with natural spoken term (e.g. '{suggested}').",
                        suggested_fix_example=example_parameter_remediation(param),
                        is_heuristic=True,
                    )
                )
                break

    return findings
