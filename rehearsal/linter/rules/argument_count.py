"""RULE-002: Argument Count.

Flags tools with too many required or total arguments that overload
single-turn spoken requests and force cumbersome multi-turn slot dialogues.
"""

from __future__ import annotations

from typing import Any, Dict, List
from rehearsal.linter.models import LinterConfig, LinterFinding, Severity
from rehearsal.linter.explainers import explain_argument_count, example_argument_simplification


def check_argument_count(
    tool_name: str,
    input_schema: Dict[str, Any],
    config: LinterConfig,
) -> List[LinterFinding]:
    """Evaluate required and optional parameter counts for voice friendliness."""
    findings: List[LinterFinding] = []
    if not input_schema or not isinstance(input_schema, dict):
        return findings

    properties = input_schema.get("properties", {})
    if not isinstance(properties, dict):
        return findings

    required_fields = input_schema.get("required", [])
    if not isinstance(required_fields, list):
        required_fields = []

    total_count = len(properties)
    required_count = len(required_fields)

    # 1. Check required parameter budget
    if required_count > config.max_required_arguments_error:
        findings.append(
            LinterFinding(
                rule_id="RULE-002",
                severity=Severity.ERROR,
                tool_name=tool_name,
                title=f"Excessive required arguments ({required_count} required)",
                evidence=(
                    f"Required: {required_count} ({', '.join(required_fields[:5])}...), "
                    f"Total: {total_count}"
                ),
                voice_impact=explain_argument_count(
                    required=required_count,
                    total=total_count,
                    max_req=config.max_required_arguments_warning,
                ),
                recommendation="Provide sensible default values for secondary parameters or split the tool into focused intents.",
                suggested_fix_example=example_argument_simplification(),
                is_heuristic=True,
            )
        )
    elif required_count > config.max_required_arguments_warning:
        findings.append(
            LinterFinding(
                rule_id="RULE-002",
                severity=Severity.WARNING,
                tool_name=tool_name,
                title=f"High required argument count ({required_count} required)",
                evidence=f"Required parameters: {', '.join(required_fields)} (Total: {total_count})",
                voice_impact=explain_argument_count(
                    required=required_count,
                    total=total_count,
                    max_req=config.max_required_arguments_warning,
                ),
                recommendation="Assign default values so users can speak a single sentence without stating all parameters.",
                suggested_fix_example=example_argument_simplification(),
                is_heuristic=True,
            )
        )
    elif total_count > config.max_total_arguments_warning:
        findings.append(
            LinterFinding(
                rule_id="RULE-002",
                severity=Severity.WARNING,
                tool_name=tool_name,
                title=f"High total parameter count ({total_count} parameters)",
                evidence=f"Total parameters: {total_count} (Required: {required_count})",
                voice_impact=(
                    f"Tool defines {total_count} total parameters. While not all are required, broad parameter spaces "
                    "can confuse spoken intent matchers and LLM tool selection prompts."
                ),
                recommendation="Review if all parameters are essential for voice interactions; remove seldom-used flags.",
                suggested_fix_example=example_argument_simplification(),
                is_heuristic=True,
            )
        )

    return findings
