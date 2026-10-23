"""Voice-readiness linter engine for inspecting MCP tools."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence
from rehearsal.linter.models import (
    LinterConfig,
    LinterFinding,
    LinterReport,
    Severity,
    ToolLintReport,
)
from rehearsal.linter.rules import (
    check_argument_count,
    check_description_clarity,
    check_parameter_ergonomics,
    check_schema_depth,
    check_tts_hostility,
)


def calculate_tool_score(findings: List[LinterFinding]) -> int:
    """Calculate an explainable voice-readiness score from 0 to 100 for a tool.

    Formula:
      Baseline = 100 points
      Deductions:
        - ERROR:   -25 points each
        - WARNING: -10 points each
        - INFO:    -2 points each
      Result is clamped to range [0, 100].
    """
    errors = sum(1 for f in findings if f.severity == Severity.ERROR)
    warnings = sum(1 for f in findings if f.severity == Severity.WARNING)
    infos = sum(1 for f in findings if f.severity == Severity.INFO)

    deductions = (errors * 25) + (warnings * 10) + (infos * 2)
    return max(0, min(100, 100 - deductions))


def _normalize_tool(tool: Any) -> Dict[str, Any]:
    """Safely extract name, description, and input_schema from an MCP Tool object or dict."""
    if isinstance(tool, dict):
        name = str(tool.get("name") or "unnamed_tool")
        description = str(tool.get("description") or "")
        input_schema = tool.get("input_schema") or tool.get("inputSchema") or {}
    else:
        name = str(getattr(tool, "name", "unnamed_tool"))
        description = str(getattr(tool, "description", "") or "")
        input_schema = getattr(tool, "input_schema", None) or getattr(tool, "inputSchema", None) or {}

    if not isinstance(input_schema, dict):
        input_schema = {}

    return {
        "name": name,
        "description": description,
        "input_schema": input_schema,
    }


def lint_tool(
    tool: Any,
    config: Optional[LinterConfig] = None,
    sample_output: Optional[str] = None,
) -> ToolLintReport:
    """Lint an individual MCP tool and return its structured diagnostics and score."""
    cfg = config or LinterConfig()
    norm = _normalize_tool(tool)
    tool_name = norm["name"]
    description = norm["description"]
    input_schema = norm["input_schema"]

    findings: List[LinterFinding] = []

    # Execute all 5 voice-readiness rules
    findings.extend(check_schema_depth(tool_name, input_schema, cfg))
    findings.extend(check_argument_count(tool_name, input_schema, cfg))
    findings.extend(check_tts_hostility(tool_name, description, input_schema, sample_output, cfg))
    findings.extend(check_parameter_ergonomics(tool_name, input_schema, cfg))
    findings.extend(check_description_clarity(tool_name, description, cfg))

    # Deduplicate findings by (rule_id, severity, title)
    unique_findings: List[LinterFinding] = []
    seen_keys = set()
    for f in findings:
        key = (f.rule_id, f.severity.value, f.title)
        if key not in seen_keys:
            seen_keys.add(key)
            unique_findings.append(f)

    # Calculate counts and score
    errors = sum(1 for f in unique_findings if f.severity == Severity.ERROR)
    warnings = sum(1 for f in unique_findings if f.severity == Severity.WARNING)
    infos = sum(1 for f in unique_findings if f.severity == Severity.INFO)
    score = calculate_tool_score(unique_findings)

    return ToolLintReport(
        tool_name=tool_name,
        score=score,
        error_count=errors,
        warning_count=warnings,
        info_count=infos,
        findings=unique_findings,
    )


def lint_tools(
    tools: Sequence[Any],
    config: Optional[LinterConfig] = None,
    sample_outputs: Optional[Dict[str, str]] = None,
) -> LinterReport:
    """Analyze a sequence of MCP tools and compile an aggregated voice-readiness report.

    Args:
        tools: Sequence of MCP Tool instances or dicts.
        config: Optional custom LinterConfig thresholds.
        sample_outputs: Optional mapping of tool_name -> static output string.

    Returns:
        LinterReport containing aggregated findings, score, and per-tool breakdowns.
    """
    cfg = config or LinterConfig()
    samples = sample_outputs or {}

    if not tools:
        return LinterReport(
            total_tools_analyzed=0,
            overall_score=100,
            error_count=0,
            warning_count=0,
            info_count=0,
        )

    tool_reports: Dict[str, ToolLintReport] = {}
    all_findings: List[LinterFinding] = []
    findings_by_severity: Dict[str, List[LinterFinding]] = {
        Severity.ERROR.value: [],
        Severity.WARNING.value: [],
        Severity.INFO.value: [],
    }
    findings_by_tool: Dict[str, List[LinterFinding]] = {}
    rule_counts: Dict[str, int] = {}

    for tool in tools:
        norm = _normalize_tool(tool)
        t_name = norm["name"]
        sample_out = samples.get(t_name)
        report = lint_tool(tool, cfg, sample_output=sample_out)

        tool_reports[t_name] = report
        findings_by_tool[t_name] = report.findings

        for finding in report.findings:
            all_findings.append(finding)
            findings_by_severity[finding.severity.value].append(finding)
            rule_counts[finding.rule_id] = rule_counts.get(finding.rule_id, 0) + 1

    total_tools = len(tools)
    total_score = sum(r.score for r in tool_reports.values())
    overall_score = round(total_score / total_tools) if total_tools > 0 else 100

    total_errors = sum(r.error_count for r in tool_reports.values())
    total_warnings = sum(r.warning_count for r in tool_reports.values())
    total_infos = sum(r.info_count for r in tool_reports.values())

    return LinterReport(
        total_tools_analyzed=total_tools,
        overall_score=overall_score,
        error_count=total_errors,
        warning_count=total_warnings,
        info_count=total_infos,
        findings=all_findings,
        findings_by_severity=findings_by_severity,
        findings_by_tool=findings_by_tool,
        rule_counts=rule_counts,
        tool_reports=tool_reports,
    )


async def lint_mcp_server(
    server: Any,
    config: Optional[LinterConfig] = None,
    sample_outputs: Optional[Dict[str, str]] = None,
) -> LinterReport:
    """Convenience helper to introspect and lint an MCPServer directly."""
    tools = await server.list_tools()
    return lint_tools(tools, config=config, sample_outputs=sample_outputs)
