"""Pydantic schemas for Rehearsal FastAPI orchestration backend."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from rehearsal.linter.models import LinterFinding, Severity
from rehearsal.runner.models import CaseEvaluationResult, DomainEvaluationResult, SlotMetrics


# -----------------------------------------------------------------------------
# Health & Tool Schemas
# -----------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = "healthy"
    version: str = "0.1.0"
    service: str = "rehearsal-api"
    timestamp: str
    mcp_sdk_version: str
    disclaimer: str = (
        "Rehearsal is an independent open-source evaluation platform. "
        "It is not affiliated with, endorsed by, or an official implementation of Amazon Alexa or Alexa+."
    )


class MCPToolSchema(BaseModel):
    """Normalized metadata for a registered MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    group: Literal["flawed", "corrected"]
    domain: Literal["weather", "smart_home", "travel"]


class ToolsListResponse(BaseModel):
    """Response containing registered reference MCP tools."""
    total_tools: int
    tools: List[MCPToolSchema]


# -----------------------------------------------------------------------------
# Linter Schemas
# -----------------------------------------------------------------------------

class LintRequest(BaseModel):
    """Request payload for running the voice-readiness linter."""
    target_group: Literal["all", "flawed", "corrected"] = Field(
        default="all",
        description="Tool group to analyze: 'all', 'flawed', or 'corrected'",
    )


class LintResponse(BaseModel):
    """Voice-readiness linting diagnostics and scorecard."""
    target_group: str
    overall_score: int
    total_tools_analyzed: int
    error_count: int
    warning_count: int
    info_count: int
    tool_scores: Dict[str, int]
    findings: List[LinterFinding]
    findings_by_severity: Dict[str, List[LinterFinding]]
    rule_counts: Dict[str, int]
    scoring_methodology: str
    disclaimer: str = "Scores are calculated using Rehearsal's voice-first heuristics, not official platform restrictions."


# -----------------------------------------------------------------------------
# Evaluation Schemas
# -----------------------------------------------------------------------------

class EvaluateRequest(BaseModel):
    """Request payload for executing the deterministic evaluation suite."""
    domain: Optional[Literal["weather", "smart_home", "travel"]] = Field(
        default=None,
        description="Optional domain filter. If null, evaluates all domains.",
    )
    live_execution: bool = Field(
        default=True,
        description="Whether to execute predicted tools live on the reference server to capture outputs and speech duration.",
    )


class EvaluateResponse(BaseModel):
    """Response containing evaluation results and run summary."""
    run_id: str
    domain: Optional[str]
    total_cases: int
    correct_tool_selections: int
    tool_selection_accuracy: float
    exact_argument_matches: int
    exact_argument_match_rate: float
    slot_metrics: SlotMetrics
    missing_argument_count: int
    unexpected_argument_count: int
    total_abstentions: int
    correct_abstentions: int
    average_estimated_speech_duration_seconds: float
    per_domain_results: Dict[str, DomainEvaluationResult]
    case_results: List[CaseEvaluationResult]


# -----------------------------------------------------------------------------
# Comparison Schemas
# -----------------------------------------------------------------------------

class ToolComparisonItem(BaseModel):
    """Side-by-side comparison item for a single domain pair."""
    domain: str
    flawed_tool_name: str
    corrected_tool_name: str
    flawed_score: int
    corrected_score: int
    flawed_findings_count: int
    corrected_findings_count: int
    flawed_nesting_depth: int
    corrected_nesting_depth: int
    voice_differences: List[str]


class CompareResponse(BaseModel):
    """Side-by-side comparative analysis of flawed vs. corrected tools."""
    flawed_average_score: float
    corrected_average_score: float
    score_improvement: float
    comparisons: List[ToolComparisonItem]
    disclaimer: str = "Comparative scores reflect Rehearsal voice ergonomics rules, not official Amazon metrics."


# -----------------------------------------------------------------------------
# Run History Schemas
# -----------------------------------------------------------------------------

class RunSummary(BaseModel):
    """Summary of a saved evaluation run."""
    run_id: str
    created_at: str
    domain: Optional[str]
    total_cases: int
    tool_accuracy: float
    exact_match_rate: float
    f1_score: float
    average_duration_seconds: float


class RunListResponse(BaseModel):
    """Paginated list of saved evaluation runs."""
    total_runs: int
    limit: int
    offset: int
    runs: List[RunSummary]
