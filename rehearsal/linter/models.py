"""Data models for Rehearsal voice-readiness linter diagnostics and reports."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Diagnostic severity levels for voice-readiness lint findings."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class LinterConfig(BaseModel):
    """Configuration thresholds for voice-readiness heuristic rules.

    Notice: These thresholds represent Rehearsal's voice ergonomics heuristics,
    not official Amazon Alexa+ validation requirements.
    """
    max_schema_depth_warning: int = Field(
        default=1,
        description="Schema nesting depth above this triggers a warning",
    )
    max_schema_depth_error: int = Field(
        default=2,
        description="Schema nesting depth above this triggers an error",
    )
    max_required_arguments_warning: int = Field(
        default=3,
        description="Required arguments count above this triggers a warning",
    )
    max_required_arguments_error: int = Field(
        default=5,
        description="Required arguments count above this triggers an error",
    )
    max_total_arguments_warning: int = Field(
        default=6,
        description="Total arguments count above this triggers a warning",
    )
    min_description_length_warning: int = Field(
        default=20,
        description="Tool description character count below this triggers a warning",
    )
    max_description_length_warning: int = Field(
        default=350,
        description="Tool description character count above this triggers an ear-fatigue warning",
    )


class LinterFinding(BaseModel):
    """A structured finding emitted by a voice-readiness rule."""
    rule_id: str = Field(..., description="Unique rule identifier, e.g., 'RULE-001'")
    severity: Severity = Field(..., description="Severity level: error, warning, info")
    tool_name: str = Field(..., description="Name of the inspected tool")
    title: str = Field(..., description="Short, human-readable summary of the issue")
    evidence: str = Field(..., description="Concrete evidence extracted from schema/metadata")
    voice_impact: str = Field(..., description="Explanation of why this impedes voice interaction")
    recommendation: str = Field(..., description="Actionable suggestion to fix the issue")
    suggested_fix_example: Optional[str] = Field(
        default=None,
        description="Optional before/after example illustrating the fix",
    )
    is_heuristic: bool = Field(
        default=True,
        description="Indicates that this finding is based on voice heuristics, not platform restrictions",
    )


class ToolLintReport(BaseModel):
    """Detailed lint report for an individual MCP tool."""
    tool_name: str
    score: int = Field(ge=0, le=100, description="Voice-readiness score from 0 to 100")
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    findings: List[LinterFinding] = Field(default_factory=list)


class LinterReport(BaseModel):
    """Aggregated voice-readiness evaluation report across all analyzed tools."""
    total_tools_analyzed: int = 0
    overall_score: int = Field(ge=0, le=100, description="Aggregate voice-readiness score from 0 to 100")
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    findings: List[LinterFinding] = Field(default_factory=list)
    findings_by_severity: Dict[str, List[LinterFinding]] = Field(default_factory=dict)
    findings_by_tool: Dict[str, List[LinterFinding]] = Field(default_factory=dict)
    rule_counts: Dict[str, int] = Field(default_factory=dict)
    tool_reports: Dict[str, ToolLintReport] = Field(default_factory=dict)
    scoring_methodology: str = Field(
        default=(
            "Baseline 100 points per tool. Deductions: Error -25 pts, Warning -10 pts, Info -2 pts. "
            "Tool score clamped to [0, 100]. Overall score is the mean across all tool scores."
        )
    )
