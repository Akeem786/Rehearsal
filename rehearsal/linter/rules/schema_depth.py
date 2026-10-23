"""RULE-001: Schema Nesting Depth.

Detects deeply nested input schemas that create cognitive and slot-mapping
friction for natural-language voice invocation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple
from rehearsal.linter.models import LinterConfig, LinterFinding, Severity
from rehearsal.linter.explainers import explain_schema_depth, example_schema_flattening


def check_schema_depth(
    tool_name: str,
    input_schema: Dict[str, Any],
    config: LinterConfig,
) -> List[LinterFinding]:
    """Inspect input_schema for excessive object/array nesting depth."""
    findings: List[LinterFinding] = []
    if not input_schema or not isinstance(input_schema, dict):
        return findings

    defs = input_schema.get("$defs") or input_schema.get("definitions") or {}
    visited_refs: Set[str] = set()

    def resolve_ref(ref_str: str) -> Dict[str, Any]:
        """Resolve a local JSON schema $ref."""
        if not ref_str or not isinstance(ref_str, str):
            return {}
        ref_key = ref_str.split("/")[-1]
        return defs.get(ref_key, {})

    def calculate_depth(
        node: Any,
        current_path: str,
        current_depth: int,
    ) -> Tuple[int, str]:
        """Recursively calculate maximum schema nesting depth and path."""
        if not isinstance(node, dict) or current_depth > 12:
            return current_depth, current_path

        # Handle $ref
        if "$ref" in node:
            ref_target = node["$ref"]
            if ref_target in visited_refs:
                return current_depth, current_path  # Break recursion
            visited_refs.add(ref_target)
            resolved = resolve_ref(ref_target)
            result = calculate_depth(resolved, current_path, current_depth)
            visited_refs.discard(ref_target)
            return result

        max_sub_depth = current_depth
        deepest_sub_path = current_path

        # Check properties of objects
        properties = node.get("properties")
        if isinstance(properties, dict):
            for prop_name, prop_node in properties.items():
                next_path = f"{current_path}.{prop_name}" if current_path else prop_name
                sub_d, sub_p = calculate_depth(prop_node, next_path, current_depth + 1)
                if sub_d > max_sub_depth:
                    max_sub_depth = sub_d
                    deepest_sub_path = sub_p

        # Check array items
        items = node.get("items")
        if isinstance(items, dict):
            next_path = f"{current_path}[]"
            sub_d, sub_p = calculate_depth(items, next_path, current_depth + 1)
            if sub_d > max_sub_depth:
                max_sub_depth = sub_d
                deepest_sub_path = sub_p

        return max_sub_depth, deepest_sub_path

    # Root properties start at depth 1
    root_properties = input_schema.get("properties", {})
    if not isinstance(root_properties, dict) or not root_properties:
        return findings

    max_overall_depth = 1
    deepest_path = ""

    for prop_name, prop_node in root_properties.items():
        d, p = calculate_depth(prop_node, prop_name, 1)
        if d > max_overall_depth:
            max_overall_depth = d
            deepest_path = p

    # Threshold evaluation
    if max_overall_depth > config.max_schema_depth_error:
        findings.append(
            LinterFinding(
                rule_id="RULE-001",
                severity=Severity.ERROR,
                tool_name=tool_name,
                title=f"Excessive schema nesting depth ({max_overall_depth} levels)",
                evidence=f"Deepest parameter path: '{deepest_path}' (depth = {max_overall_depth})",
                voice_impact=explain_schema_depth(deepest_path, max_overall_depth, config.max_schema_depth_warning),
                recommendation="Flatten nested objects into top-level primitive arguments (string, number, boolean).",
                suggested_fix_example=example_schema_flattening(),
                is_heuristic=True,
            )
        )
    elif max_overall_depth > config.max_schema_depth_warning:
        findings.append(
            LinterFinding(
                rule_id="RULE-001",
                severity=Severity.WARNING,
                tool_name=tool_name,
                title=f"Nested schema structure detected (depth = {max_overall_depth})",
                evidence=f"Deepest parameter path: '{deepest_path}'",
                voice_impact=explain_schema_depth(deepest_path, max_overall_depth, config.max_schema_depth_warning),
                recommendation="Prefer flat schemas with primitive types for optimal voice assistant slot extraction.",
                suggested_fix_example=example_schema_flattening(),
                is_heuristic=True,
            )
        )

    return findings
