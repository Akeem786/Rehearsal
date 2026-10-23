"""Automated tests for Rehearsal FastAPI Orchestration Backend.

Verifies:
1. GET /api/health status, version, and disclaimer.
2. GET /api/tools discovery, schema inspection, and sample grouping.
3. POST /api/lint for all, flawed, and corrected tool groups.
4. POST /api/evaluate for all domains and single domain filters.
5. Error handling for invalid domain requests (HTTP 400).
6. POST /api/compare side-by-side scorecard and improvement metrics.
7. SQLite persistence: saving runs, pagination (limit/offset), and retrieval.
8. Unknown run ID error handling (HTTP 404).
9. Swagger docs availability at /docs and /openapi.json.
10. Database isolation using pytest tmp_path.
"""

import httpx
import pytest
from rehearsal.api.app import create_app


@pytest.fixture
def app_and_client(tmp_path):
    """Create a test FastAPI instance isolated with a temporary SQLite database."""
    test_db = tmp_path / "test_rehearsal.sqlite3"
    test_app = create_app(db_path=str(test_db))
    transport = httpx.ASGITransport(app=test_app)
    return test_app, transport


@pytest.mark.asyncio
async def test_health_check_endpoint(app_and_client):
    """GET /api/health returns 200 with service status, version, and disclaimer."""
    _, transport = app_and_client
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["service"] == "rehearsal-api"
        assert "timestamp" in data
        assert "mcp_sdk_version" in data
        assert "disclaimer" in data


@pytest.mark.asyncio
async def test_list_tools_endpoint(app_and_client):
    """GET /api/tools returns all six reference MCP tools with transparent grouping."""
    _, transport = app_and_client
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/api/tools")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_tools"] == 6

        tool_map = {t["name"]: t for t in data["tools"]}
        assert "fetch_meteorological_telemetry_v2" in tool_map
        assert "get_weather_summary" in tool_map
        assert "execute_home_iot_command_rpc" in tool_map
        assert "control_home_device" in tool_map
        assert "query_itinerary_and_schedule_matrix" in tool_map
        assert "find_flight_summary" in tool_map

        # Check grouping
        assert tool_map["fetch_meteorological_telemetry_v2"]["group"] == "flawed"
        assert tool_map["get_weather_summary"]["group"] == "corrected"
        assert tool_map["fetch_meteorological_telemetry_v2"]["domain"] == "weather"
        assert tool_map["control_home_device"]["domain"] == "smart_home"


@pytest.mark.asyncio
async def test_lint_endpoint_all_flawed_and_corrected(app_and_client):
    """POST /api/lint runs voice linter for all, flawed, and corrected tool groups."""
    _, transport = app_and_client
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Lint all tools
        resp_all = await client.post("/api/lint", json={"target_group": "all"})
        assert resp_all.status_code == 200
        data_all = resp_all.json()
        assert data_all["total_tools_analyzed"] == 6
        assert data_all["overall_score"] > 0
        assert len(data_all["findings"]) > 0

        # 2. Lint flawed tools only
        resp_flawed = await client.post("/api/lint", json={"target_group": "flawed"})
        assert resp_flawed.status_code == 200
        data_flawed = resp_flawed.json()
        assert data_flawed["total_tools_analyzed"] == 3
        assert data_flawed["overall_score"] < 100
        assert data_flawed["error_count"] > 0

        # 3. Lint corrected tools only
        resp_corrected = await client.post("/api/lint", json={"target_group": "corrected"})
        assert resp_corrected.status_code == 200
        data_corrected = resp_corrected.json()
        assert data_corrected["total_tools_analyzed"] == 3
        assert data_corrected["overall_score"] == 100
        assert data_corrected["error_count"] == 0
        assert data_corrected["warning_count"] == 0


@pytest.mark.asyncio
async def test_evaluate_endpoint_all_and_filtered(app_and_client):
    """POST /api/evaluate executes the test suite and persists the run."""
    _, transport = app_and_client
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Evaluate all domains (18 cases)
        resp = await client.post("/api/evaluate", json={"domain": None, "live_execution": False})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_cases"] == 18
        assert data["tool_selection_accuracy"] == 1.0
        assert data["exact_argument_match_rate"] == 1.0
        assert data["run_id"].startswith("run_")
        assert len(data["case_results"]) == 18

        # 2. Evaluate single domain (weather: 6 cases)
        resp_wx = await client.post("/api/evaluate", json={"domain": "weather", "live_execution": False})
        assert resp_wx.status_code == 200
        data_wx = resp_wx.json()
        assert data_wx["total_cases"] == 6
        assert data_wx["domain"] == "weather"


@pytest.mark.asyncio
async def test_evaluate_endpoint_invalid_domain_rejection(app_and_client):
    """POST /api/evaluate returns HTTP 400 or 422 when given an invalid domain."""
    _, transport = app_and_client
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/api/evaluate", json={"domain": "non_existent_domain"})
        assert resp.status_code in (400, 422)


@pytest.mark.asyncio
async def test_compare_endpoint(app_and_client):
    """POST /api/compare computes side-by-side flawed vs corrected scorecard."""
    _, transport = app_and_client
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/api/compare")
        assert resp.status_code == 200
        data = resp.json()
        assert data["flawed_average_score"] < data["corrected_average_score"]
        assert data["score_improvement"] > 0
        assert len(data["comparisons"]) == 3

        domains = [c["domain"] for c in data["comparisons"]]
        assert "weather" in domains
        assert "smart_home" in domains
        assert "travel" in domains

        for comp in data["comparisons"]:
            assert comp["corrected_score"] > comp["flawed_score"]
            assert len(comp["voice_differences"]) > 0


@pytest.mark.asyncio
async def test_runs_history_and_retrieval(app_and_client):
    """GET /api/runs and GET /api/runs/{run_id} verify persistence and retrieval."""
    _, transport = app_and_client
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Initially empty runs list
        resp_init = await client.get("/api/runs")
        assert resp_init.status_code == 200
        assert resp_init.json()["total_runs"] == 0

        # Execute an evaluation run
        eval_resp = await client.post("/api/evaluate", json={"domain": "smart_home", "live_execution": False})
        assert eval_resp.status_code == 200
        run_id = eval_resp.json()["run_id"]

        # List runs: should now contain 1 run
        list_resp = await client.get("/api/runs")
        assert list_resp.status_code == 200
        list_data = list_resp.json()
        assert list_data["total_runs"] == 1
        assert list_data["runs"][0]["run_id"] == run_id
        assert list_data["runs"][0]["domain"] == "smart_home"

        # Retrieve specific run details
        detail_resp = await client.get(f"/api/runs/{run_id}")
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()
        assert detail_data["run_id"] == run_id
        assert "report" in detail_data
        assert detail_data["report"]["total_cases"] == 6

        # Non-existent run returns 404
        missing_resp = await client.get("/api/runs/non_existent_run_999")
        assert missing_resp.status_code == 404


@pytest.mark.asyncio
async def test_swagger_and_openapi_docs(app_and_client):
    """Verify OpenAPI schema and Swagger UI documentation endpoints are functional."""
    _, transport = app_and_client
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        docs_resp = await client.get("/docs")
        assert docs_resp.status_code == 200

        schema_resp = await client.get("/openapi.json")
        assert schema_resp.status_code == 200
        schema = schema_resp.json()
        assert schema["info"]["title"] == "Rehearsal API"
        assert "/api/health" in schema["paths"]
        assert "/api/tools" in schema["paths"]
        assert "/api/lint" in schema["paths"]
        assert "/api/evaluate" in schema["paths"]
        assert "/api/compare" in schema["paths"]
        assert "/api/runs" in schema["paths"]


@pytest.mark.asyncio
async def test_evaluate_endpoint_with_live_execution(app_and_client):
    """POST /api/evaluate with live_execution=True executes reference MCP server and estimates speech duration."""
    _, transport = app_and_client
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/api/evaluate", json={"domain": "smart_home", "live_execution": True})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_cases"] == 6
        assert data["average_estimated_speech_duration_seconds"] > 0.0
        # Verify tool outputs exist on cases that called tools
        has_tool_output = any(c.get("tool_output") is not None for c in data["case_results"])
        assert has_tool_output is True


@pytest.mark.asyncio
async def test_runs_pagination_and_offset(app_and_client):
    """GET /api/runs respects limit and offset parameters."""
    _, transport = app_and_client
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        for _ in range(3):
            await client.post("/api/evaluate", json={"domain": "weather", "live_execution": False})

        # Test limit
        resp_limit = await client.get("/api/runs?limit=2&offset=0")
        assert resp_limit.status_code == 200
        data_limit = resp_limit.json()
        assert data_limit["total_runs"] == 3
        assert len(data_limit["runs"]) == 2

        # Test offset
        resp_offset = await client.get("/api/runs?limit=2&offset=2")
        assert resp_offset.status_code == 200
        data_offset = resp_offset.json()
        assert len(data_offset["runs"]) == 1

