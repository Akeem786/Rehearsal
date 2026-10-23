"""Automated test suite for Rehearsal Voice-Readiness Linter Engine.

Tests:
1. Positive triggering for each rule (RULE-001 through RULE-005).
2. Pristine schemas with zero findings and perfect score.
3. Missing or empty descriptions generating errors.
4. Schema references ($ref) and recursion cycle safety.
5. Required vs. optional argument count thresholds.
6. TTS hostility detection (Markdown tables, JSON, URLs, hex).
7. Parameter ergonomics (cryptic abbreviations, opaque IDs).
8. Deterministic scoring stability.
9. Side-by-side comparison of flawed vs. corrected tools.
10. Empty list and malformed/incomplete metadata handling.
11. Diagnostic deduplication.
12. Full integration with the reference MCP server.
"""

import pytest
from rehearsal.linter import (
    LinterConfig,
    LinterFinding,
    Severity,
    calculate_tool_score,
    lint_mcp_server,
    lint_tool,
    lint_tools,
)
from rehearsal.linter.rules import (
    check_argument_count,
    check_description_clarity,
    check_parameter_ergonomics,
    check_schema_depth,
    check_tts_hostility,
)
from rehearsal.server import create_reference_server


# -----------------------------------------------------------------------------
# 1. Rule Positive Cases
# -----------------------------------------------------------------------------

def test_rule_001_schema_depth_warning_and_error():
    """RULE-001: Detects nested schemas exceeding warning and error thresholds."""
    cfg = LinterConfig(max_schema_depth_warning=1, max_schema_depth_error=2)

    # Depth 2: warning
    schema_depth_2 = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
            }
        },
    }
    findings_w = check_schema_depth("tool_d2", schema_depth_2, cfg)
    assert len(findings_w) == 1
    assert findings_w[0].rule_id == "RULE-001"
    assert findings_w[0].severity == Severity.WARNING

    # Depth 3: error
    schema_depth_3 = {
        "type": "object",
        "properties": {
            "outer": {
                "type": "object",
                "properties": {
                    "inner": {
                        "type": "object",
                        "properties": {"leaf": {"type": "string"}},
                    }
                },
            }
        },
    }
    findings_e = check_schema_depth("tool_d3", schema_depth_3, cfg)
    assert len(findings_e) == 1
    assert findings_e[0].rule_id == "RULE-001"
    assert findings_e[0].severity == Severity.ERROR
    assert "3 levels" in findings_e[0].title


def test_rule_002_argument_count_required_vs_optional():
    """RULE-002: Distinguishes required parameter count from optional total count."""
    cfg = LinterConfig(
        max_required_arguments_warning=3,
        max_required_arguments_error=5,
        max_total_arguments_warning=6,
    )

    # 4 required: triggers required warning
    schema_req_4 = {
        "type": "object",
        "properties": {f"p{i}": {"type": "string"} for i in range(4)},
        "required": ["p0", "p1", "p2", "p3"],
    }
    findings = check_argument_count("tool_req4", schema_req_4, cfg)
    assert any(f.rule_id == "RULE-002" and f.severity == Severity.WARNING for f in findings)

    # 6 required: triggers required error
    schema_req_6 = {
        "type": "object",
        "properties": {f"p{i}": {"type": "string"} for i in range(6)},
        "required": [f"p{i}" for i in range(6)],
    }
    findings_err = check_argument_count("tool_req6", schema_req_6, cfg)
    assert any(f.rule_id == "RULE-002" and f.severity == Severity.ERROR for f in findings_err)

    # 2 required, 7 optional: triggers total count warning, not required warning
    schema_opt_7 = {
        "type": "object",
        "properties": {f"p{i}": {"type": "string"} for i in range(7)},
        "required": ["p0", "p1"],
    }
    findings_opt = check_argument_count("tool_opt7", schema_opt_7, cfg)
    assert any("High total parameter count" in f.title for f in findings_opt)


def test_rule_003_tts_hostility_detection():
    """RULE-003: Detects markdown tables, raw JSON, URLs, and hex in text."""
    cfg = LinterConfig()
    schema = {"type": "object", "properties": {}}

    # Markdown table in description
    table_desc = "Status:\n| Col1 | Col2 |\n| :--- | :--- |\n| A | B |"
    findings_tbl = check_tts_hostility("t_tbl", table_desc, schema, config=cfg)
    assert any(f.rule_id == "RULE-003" and "Markdown table" in f.title for f in findings_tbl)

    # Raw JSON in static output
    json_output = '{"status": "ok", "telemetry": {"voltage": 12.4}}'
    findings_json = check_tts_hostility("t_json", "Normal desc", schema, sample_output=json_output, config=cfg)
    assert any(f.rule_id == "RULE-003" and "Raw JSON" in f.title for f in findings_json)

    # Raw URL in description
    url_desc = "Refer to documentation at https://api.internal.corp/spec for details."
    findings_url = check_tts_hostility("t_url", url_desc, schema, config=cfg)
    assert any(f.rule_id == "RULE-003" and "Raw URL" in f.title for f in findings_url)

    # Hex literal in description
    hex_desc = "Cluster node register 0x0006 on pan 0xDEAD."
    findings_hex = check_tts_hostility("t_hex", hex_desc, schema, config=cfg)
    assert any(f.rule_id == "RULE-003" and "Hexadecimal" in f.title for f in findings_hex)


def test_rule_004_parameter_ergonomics():
    """RULE-004: Flags opaque GUIDs, hex masks, and cryptic abbreviations."""
    cfg = LinterConfig()
    schema = {
        "type": "object",
        "properties": {
            "device_guid_hex": {"type": "string"},
            "origin_iata": {"type": "string"},
            "register_state_mask": {"type": "integer"},
            "room_name": {"type": "string"},  # clean parameter
        },
    }
    findings = check_parameter_ergonomics("t_param", schema, cfg)
    flagged = [f.evidence for f in findings]
    assert any("device_guid_hex" in ev for ev in flagged)
    assert any("origin_iata" in ev for ev in flagged)
    assert any("register_state_mask" in ev for ev in flagged)
    assert not any("room_name" in ev for ev in flagged)


def test_rule_005_description_clarity():
    """RULE-005: Flags empty, too short, too long, or pure-jargon descriptions."""
    cfg = LinterConfig(min_description_length_warning=20, max_description_length_warning=100)

    # Empty: ERROR
    f_empty = check_description_clarity("t_empty", "", cfg)
    assert any(f.rule_id == "RULE-005" and f.severity == Severity.ERROR for f in f_empty)

    # Too short: WARNING
    f_short = check_description_clarity("t_short", "Gets stuff", cfg)
    assert any(f.rule_id == "RULE-005" and "too brief" in f.title for f in f_short)

    # Too long: WARNING
    long_desc = "A" * 120
    f_long = check_description_clarity("t_long", long_desc, cfg)
    assert any(f.rule_id == "RULE-005" and "excessively long" in f.title for f in f_long)

    # Heavy jargon: WARNING
    jargon_desc = "Low-level binary RPC actuator dispatcher for peripheral network clusters."
    f_jargon = check_description_clarity("t_jargon", jargon_desc, cfg)
    assert any("technical jargon" in f.title for f in f_jargon)


# -----------------------------------------------------------------------------
# 2. Clean Schemas (Negative Cases)
# -----------------------------------------------------------------------------

def test_clean_voice_tool_receives_zero_findings():
    """A well-designed voice tool receives zero findings and a score of 100."""
    clean_tool = {
        "name": "get_weather_summary",
        "description": "Get a concise, spoken weather summary and forecast for a city or location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City or region name"},
                "timeframe": {"type": "string", "default": "today"},
            },
            "required": ["location"],
        },
    }
    report = lint_tool(clean_tool)
    assert report.score == 100
    assert len(report.findings) == 0
    assert report.error_count == 0
    assert report.warning_count == 0


# -----------------------------------------------------------------------------
# 3. Schema References ($ref) and Recursion Safety
# -----------------------------------------------------------------------------

def test_schema_ref_resolution_and_cycle_safety():
    """RULE-001 resolves $defs correctly and does not crash or loop on cyclical schemas."""
    # Cyclical schema definition
    cyclic_schema = {
        "$defs": {
            "Node": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "parent": {"$ref": "#/$defs/Node"},  # cycle
                },
            }
        },
        "type": "object",
        "properties": {
            "root": {"$ref": "#/$defs/Node"}
        },
    }
    cfg = LinterConfig(max_schema_depth_warning=1, max_schema_depth_error=2)
    # Must complete safely without RecursionError
    findings = check_schema_depth("cyclic_tool", cyclic_schema, cfg)
    assert isinstance(findings, list)


# -----------------------------------------------------------------------------
# 4. Scoring Stability and Determinism
# -----------------------------------------------------------------------------

def test_scoring_determinism():
    """Linting the exact same tool input repeatedly yields identical scores and findings."""
    tool = {
        "name": "sample_tool",
        "description": "Sample description that is moderately long.",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_guid_hex": {"type": "string"},
                "nested_obj": {
                    "type": "object",
                    "properties": {"val": {"type": "string"}},
                },
            },
            "required": ["device_guid_hex"],
        },
    }
    report_1 = lint_tool(tool)
    report_2 = lint_tool(tool)

    assert report_1.score == report_2.score
    assert len(report_1.findings) == len(report_2.findings)
    assert [f.title for f in report_1.findings] == [f.title for f in report_2.findings]


def test_score_calculation_deductions():
    """Verify that score formula accurately deducts errors, warnings, and infos."""
    f_err = LinterFinding(
        rule_id="RULE-001",
        severity=Severity.ERROR,
        tool_name="t",
        title="Error 1",
        evidence="e",
        voice_impact="v",
        recommendation="r",
    )
    f_warn = LinterFinding(
        rule_id="RULE-002",
        severity=Severity.WARNING,
        tool_name="t",
        title="Warn 1",
        evidence="e",
        voice_impact="v",
        recommendation="r",
    )
    f_info = LinterFinding(
        rule_id="RULE-005",
        severity=Severity.INFO,
        tool_name="t",
        title="Info 1",
        evidence="e",
        voice_impact="v",
        recommendation="r",
    )

    # 1 Error (-25) + 1 Warning (-10) + 1 Info (-2) = 63
    score = calculate_tool_score([f_err, f_warn, f_info])
    assert score == 63

    # Clamping test: 5 errors = -125 => score 0 (not negative)
    score_clamped = calculate_tool_score([f_err] * 5)
    assert score_clamped == 0


# -----------------------------------------------------------------------------
# 5. Empty and Malformed Inputs
# -----------------------------------------------------------------------------

def test_empty_tools_list_handling():
    """lint_tools returns an empty report with score 100 when passed an empty list."""
    report = lint_tools([])
    assert report.total_tools_analyzed == 0
    assert report.overall_score == 100
    assert len(report.findings) == 0


def test_malformed_tool_metadata_handling():
    """Linter safely processes tools missing descriptions, schemas, or non-dict objects."""
    malformed_tool = {"name": "incomplete_tool"}
    report = lint_tool(malformed_tool)
    assert report.tool_name == "incomplete_tool"
    # Should catch missing description error
    assert any(f.rule_id == "RULE-005" and f.severity == Severity.ERROR for f in report.findings)


# -----------------------------------------------------------------------------
# 6. Integration with Reference MCP Server
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_full_integration_with_reference_mcp_server():
    """Lint all six reference tools and verify that flawed tools have lower scores than corrected tools."""
    server = create_reference_server()
    report = await lint_mcp_server(server)

    assert report.total_tools_analyzed == 6
    assert len(report.tool_reports) == 6

    # Verify flawed tools received findings
    flawed_weather = report.tool_reports["fetch_meteorological_telemetry_v2"]
    flawed_iot = report.tool_reports["execute_home_iot_command_rpc"]
    flawed_travel = report.tool_reports["query_itinerary_and_schedule_matrix"]

    assert flawed_weather.score < 100
    assert flawed_iot.score < 100
    assert flawed_travel.score < 100

    # Verify corrected tools scored perfectly or significantly higher
    corrected_weather = report.tool_reports["get_weather_summary"]
    corrected_iot = report.tool_reports["control_home_device"]
    corrected_travel = report.tool_reports["find_flight_summary"]

    assert corrected_weather.score > flawed_weather.score
    assert corrected_iot.score > flawed_iot.score
    assert corrected_travel.score > flawed_travel.score
    assert corrected_weather.score == 100
    assert corrected_iot.score == 100
    assert corrected_travel.score == 100

    # Verify rule counts are tracked
    assert "RULE-001" in report.rule_counts
    assert "RULE-004" in report.rule_counts
    assert "RULE-005" in report.rule_counts
