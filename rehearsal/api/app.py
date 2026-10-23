"""FastAPI application factory and route definitions for Rehearsal."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.metadata
import uuid
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from rehearsal.api.schemas import (
    CompareResponse,
    EvaluateRequest,
    EvaluateResponse,
    HealthResponse,
    LintRequest,
    LintResponse,
    MCPToolSchema,
    RunListResponse,
    RunSummary,
    ToolComparisonItem,
    ToolsListResponse,
)
from rehearsal.api.storage import EvaluationStorage
from rehearsal.client.connector import MCPClientConnector
from rehearsal.linter.engine import lint_tools
from rehearsal.runner.engine import load_fixtures, run_evaluation
from rehearsal.server.server import create_reference_server

# Known reference tool mapping for metadata grouping
FLAWED_TOOL_NAMES = {
    "fetch_meteorological_telemetry_v2": "weather",
    "execute_home_iot_command_rpc": "smart_home",
    "query_itinerary_and_schedule_matrix": "travel",
}
CORRECTED_TOOL_NAMES = {
    "get_weather_summary": "weather",
    "control_home_device": "smart_home",
    "find_flight_summary": "travel",
}


def create_app(
    db_path: Optional[str] = None,
    cors_origins: Optional[List[str]] = None,
) -> FastAPI:
    """FastAPI application factory."""
    application = FastAPI(
        title="Rehearsal API",
        version="0.1.0",
        description=(
            "Orchestration backend for Rehearsal: evaluating MCP tools for voice-readiness, "
            "linting schemas, and benchmarking spoken interaction ergonomics."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Storage initialization
    storage = EvaluationStorage(db_path=db_path)

    # CORS configuration
    origins = cors_origins or [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Reference server singleton for tool inspection
    reference_server = create_reference_server()

    # -------------------------------------------------------------------------
    # Route: Health Check
    # -------------------------------------------------------------------------
    @application.get(
        "/api/health",
        response_model=HealthResponse,
        summary="Service Health Check",
        tags=["System"],
    )
    def health_check() -> HealthResponse:
        """Return API service status, timestamp, and installed MCP SDK version."""
        try:
            mcp_ver = importlib.metadata.version("mcp")
        except Exception:
            mcp_ver = "unknown"

        return HealthResponse(
            status="healthy",
            version="0.1.0",
            service="rehearsal-api",
            timestamp=datetime.now(timezone.utc).isoformat(),
            mcp_sdk_version=mcp_ver,
        )

    # -------------------------------------------------------------------------
    # Route: Tool Discovery
    # -------------------------------------------------------------------------
    @application.get(
        "/api/tools",
        response_model=ToolsListResponse,
        summary="List Reference MCP Tools",
        tags=["Tools"],
    )
    async def list_tools() -> ToolsListResponse:
        """Return all registered reference MCP tools with schemas and sample grouping."""
        tools = await reference_server.list_tools()
        schemas: List[MCPToolSchema] = []

        for t in tools:
            name = t.name
            if name in FLAWED_TOOL_NAMES:
                group = "flawed"
                domain = FLAWED_TOOL_NAMES[name]
            elif name in CORRECTED_TOOL_NAMES:
                group = "corrected"
                domain = CORRECTED_TOOL_NAMES[name]
            else:
                group = "flawed"
                domain = "weather"

            schemas.append(
                MCPToolSchema(
                    name=name,
                    description=t.description or "",
                    input_schema=t.input_schema or {},
                    group=group,
                    domain=domain,
                )
            )

        return ToolsListResponse(total_tools=len(schemas), tools=schemas)

    # -------------------------------------------------------------------------
    # Route: Voice-Readiness Linter
    # -------------------------------------------------------------------------
    @application.post(
        "/api/lint",
        response_model=LintResponse,
        summary="Run Voice-Readiness Linter",
        tags=["Linter"],
    )
    async def run_linter(req: LintRequest) -> LintResponse:
        """Inspect registered MCP tools using Rehearsal's voice-readiness heuristics."""
        all_tools = await reference_server.list_tools()

        # Filter by requested target group
        if req.target_group == "flawed":
            target_tools = [t for t in all_tools if t.name in FLAWED_TOOL_NAMES]
        elif req.target_group == "corrected":
            target_tools = [t for t in all_tools if t.name in CORRECTED_TOOL_NAMES]
        else:
            target_tools = list(all_tools)

        report = lint_tools(target_tools)
        tool_scores = {name: tr.score for name, tr in report.tool_reports.items()}

        return LintResponse(
            target_group=req.target_group,
            overall_score=report.overall_score,
            total_tools_analyzed=report.total_tools_analyzed,
            error_count=report.error_count,
            warning_count=report.warning_count,
            info_count=report.info_count,
            tool_scores=tool_scores,
            findings=report.findings,
            findings_by_severity=report.findings_by_severity,
            rule_counts=report.rule_counts,
            scoring_methodology=report.scoring_methodology,
        )

    # -------------------------------------------------------------------------
    # Route: Deterministic Evaluation Runner
    # -------------------------------------------------------------------------
    @application.post(
        "/api/evaluate",
        response_model=EvaluateResponse,
        summary="Execute Evaluation Suite",
        tags=["Evaluation"],
    )
    async def evaluate_suite(req: EvaluateRequest) -> EvaluateResponse:
        """Run natural-language voice utterance evaluation cases and persist results."""
        # Validate domain if provided
        valid_domains = {"weather", "smart_home", "travel"}
        if req.domain is not None and req.domain not in valid_domains:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid domain '{req.domain}'. Valid choices: {sorted(valid_domains)}",
            )

        cases = load_fixtures(domain=req.domain)
        if not cases:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No evaluation fixtures found for domain '{req.domain}'.",
            )

        run_id = f"run_{uuid.uuid4().hex[:12]}"

        if req.live_execution:
            async with MCPClientConnector(server=reference_server) as client:
                report = await run_evaluation(cases, connector=client)
        else:
            report = await run_evaluation(cases)

        # Save to SQLite repository
        storage.save_run(run_id=run_id, domain=req.domain, report=report)

        return EvaluateResponse(
            run_id=run_id,
            domain=req.domain,
            total_cases=report.total_cases,
            correct_tool_selections=report.correct_tool_selections,
            tool_selection_accuracy=report.tool_selection_accuracy,
            exact_argument_matches=report.exact_argument_matches,
            exact_argument_match_rate=report.exact_argument_match_rate,
            slot_metrics=report.slot_metrics,
            missing_argument_count=report.missing_argument_count,
            unexpected_argument_count=report.unexpected_argument_count,
            total_abstentions=report.total_abstentions,
            correct_abstentions=report.correct_abstentions,
            average_estimated_speech_duration_seconds=report.average_estimated_speech_duration_seconds,
            per_domain_results=report.per_domain_results,
            case_results=report.case_results,
        )

    # -------------------------------------------------------------------------
    # Route: Side-by-Side Comparison
    # -------------------------------------------------------------------------
    @application.post(
        "/api/compare",
        response_model=CompareResponse,
        summary="Compare Flawed vs Corrected Tools",
        tags=["Evaluation"],
    )
    async def compare_tools() -> CompareResponse:
        """Generate side-by-side comparative voice-readiness scorecard."""
        all_tools = await reference_server.list_tools()
        flawed_tools = [t for t in all_tools if t.name in FLAWED_TOOL_NAMES]
        corrected_tools = [t for t in all_tools if t.name in CORRECTED_TOOL_NAMES]

        flawed_report = lint_tools(flawed_tools)
        corrected_report = lint_tools(corrected_tools)

        flawed_avg = flawed_report.overall_score
        corrected_avg = corrected_report.overall_score
        improvement = round(float(corrected_avg - flawed_avg), 1)

        def _get_score(rep: Any, tool_name: str, fallback: int) -> int:
            tr = rep.tool_reports.get(tool_name)
            return getattr(tr, "score", fallback) if tr is not None else fallback

        def _get_findings_count(rep: Any, tool_name: str) -> int:
            return len(rep.findings_by_tool.get(tool_name, []))

        comparisons: List[ToolComparisonItem] = [
            ToolComparisonItem(
                domain="weather",
                flawed_tool_name="fetch_meteorological_telemetry_v2",
                corrected_tool_name="get_weather_summary",
                flawed_score=_get_score(flawed_report, "fetch_meteorological_telemetry_v2", 65),
                corrected_score=_get_score(corrected_report, "get_weather_summary", 100),
                flawed_findings_count=_get_findings_count(flawed_report, "fetch_meteorological_telemetry_v2"),
                corrected_findings_count=_get_findings_count(corrected_report, "get_weather_summary"),
                flawed_nesting_depth=3,
                corrected_nesting_depth=1,
                voice_differences=[
                    "Flawed uses nested geodetic coordinates ($defs/NestedCoord); corrected uses flat city string.",
                    "Flawed returns 900-char raw JSON with crc32; corrected returns a 25-word spoken sentence.",
                    "Flawed description contains sensor telemetry jargon without voice intent triggers.",
                ],
            ),
            ToolComparisonItem(
                domain="smart_home",
                flawed_tool_name="execute_home_iot_command_rpc",
                corrected_tool_name="control_home_device",
                flawed_score=_get_score(flawed_report, "execute_home_iot_command_rpc", 70),
                corrected_score=_get_score(corrected_report, "control_home_device", 100),
                flawed_findings_count=_get_findings_count(flawed_report, "execute_home_iot_command_rpc"),
                corrected_findings_count=_get_findings_count(corrected_report, "control_home_device"),
                flawed_nesting_depth=1,
                corrected_nesting_depth=1,
                voice_differences=[
                    "Flawed requires hardware device GUID hex ('0x4A9F'); corrected accepts spoken room ('living room').",
                    "Flawed returns a Markdown table with hex ACKs; corrected returns a crisp 6-word confirmation.",
                    "Flawed description uses low-level RPC terminology instead of smart home control verbs.",
                ],
            ),
            ToolComparisonItem(
                domain="travel",
                flawed_tool_name="query_itinerary_and_schedule_matrix",
                corrected_tool_name="find_flight_summary",
                flawed_score=_get_score(flawed_report, "query_itinerary_and_schedule_matrix", 45),
                corrected_score=_get_score(corrected_report, "find_flight_summary", 100),
                flawed_findings_count=_get_findings_count(flawed_report, "query_itinerary_and_schedule_matrix"),
                corrected_findings_count=_get_findings_count(corrected_report, "find_flight_summary"),
                flawed_nesting_depth=3,
                corrected_nesting_depth=1,
                voice_differences=[
                    "Flawed requires strict 3-letter IATA codes and nested dates; corrected accepts natural city names.",
                    "Flawed returns a 200-word GDS markdown table with URLs; corrected gives top 2 spoken choices with prices.",
                    "Flawed lacks conversational closing turn; corrected closes with conversational CTA.",
                ],
            ),
        ]

        return CompareResponse(
            flawed_average_score=float(flawed_avg),
            corrected_average_score=float(corrected_avg),
            score_improvement=improvement,
            comparisons=comparisons,
        )

    # -------------------------------------------------------------------------
    # Route: Evaluation Run History
    # -------------------------------------------------------------------------
    @application.get(
        "/api/runs",
        response_model=RunListResponse,
        summary="List Saved Evaluation Runs",
        tags=["History"],
    )
    def list_runs(
        limit: int = Query(default=20, ge=1, le=100, description="Max runs to return"),
        offset: int = Query(default=0, ge=0, description="Pagination offset"),
    ) -> RunListResponse:
        """Return recent evaluation runs ordered newest first."""
        total = storage.count_runs()
        runs = storage.list_runs(limit=limit, offset=offset)
        return RunListResponse(total_runs=total, limit=limit, offset=offset, runs=runs)

    @application.get(
        "/api/runs/{run_id}",
        summary="Get Evaluation Run Details",
        tags=["History"],
    )
    def get_run_details(run_id: str) -> Dict[str, Any]:
        """Retrieve full evaluation report for a saved run ID."""
        run_data = storage.get_run(run_id)
        if not run_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation run '{run_id}' not found.",
            )
        return run_data

    return application


# Default module-level ASGI instance for Uvicorn
app = create_app()
