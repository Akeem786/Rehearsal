# Rehearsal: Implementation Plan & Architectural Specification

**Version:** 0.1.0  
**Status:** Approved for Implementation (Step 1 Complete)  
**Authors:** Senior Python Engineer / Hackathon Lead  

---

## 1. Executive Summary & Goals

**Rehearsal** is an automated voice-readiness evaluation platform for Model Context Protocol (MCP) servers and tools. It equips tool authors and assistant builders with automated testing, static analysis, and interactive side-by-side benchmarking to guarantee that tools are suited for voice-first AI agents.

### Core Objectives
1. **Zero External API Dependency for Core MVP**: Run deterministic, reproducible evaluations locally using fixtures and rule engines without requiring paid LLM tokens or external API keys.
2. **Explainable Voice Linting**: Provide concrete, actionable diagnostics (e.g., "Parameter `filter_criteria_nested_obj` exceeds voice ergonomics depth limit; recommend flattening to `category: str`").
3. **Reference Benchmark Suite**: Provide a reference server demonstrating canonical voice mistakes (anti-patterns) alongside their voice-optimized counterparts.
4. **Interactive Comparison UI**: Side-by-side visual comparison showing how voice-readiness scores improve when tools adopt voice-first conventions.

---

## 2. Voice-Readiness Evaluation Rubric

Rehearsal evaluates MCP tools across 5 fundamental dimensions:

| Dimension | Anti-Pattern (Flawed) | Voice-Optimized Pattern (Corrected) | Evaluation Metric |
| :--- | :--- | :--- | :--- |
| **1. Tool Description & Discovery** | Technical jargon, ambiguous triggers (e.g., "Fetches data entity 401") | Natural spoken intent phrasing (e.g., "Gets current weather and forecast for any city") | Trigger phrase semantic overlap, clarity index |
| **2. Schema & Argument Ergonomics** | Nested objects, required enums with 50+ obscure codes, unguided formats | Flat primitives, sensible voice defaults, flexible string matching | Nesting depth ($\le 1$), required param count ($\le 3$) |
| **3. Output Conciseness (TTS-Ready)** | Raw JSON dumps, Markdown tables, links (`[click here](http...)`), >200 words | Natural spoken summary ($<40$ words), phonetic numbers, no unparsed Markdown syntax | Syllable count, speech duration estimate, markdown artifact count |
| **4. Conversational Error Handling** | Stack trace or silent failure (`null`, code 500) | Conversational recovery suggestion (e.g., "I couldn't find Seattle, did you mean Seattle, Washington?") | Error speech quality, recovery prompt presence |
| **5. Turn Latency & Responsiveness** | Multi-step unindexed remote fetches ($>3000$ms) | Fast responses, streamed progress hints ($<800$ms) | Server execution turnaround time (ms) |

---

## 3. System Architecture & Components

```
+----------------------------------------------------------------------------------------+
|                                  rehearsal-ui (Frontend)                               |
|                     React 18+ / TypeScript / Vite / Vanilla CSS Design                 |
|  - Tool Inspection Deck           - Live Utterance Tester        - Score Comparison    |
+-------------------------------------------+--------------------------------------------+
                                            | REST API / Server-Sent Events (SSE)
                                            v
+----------------------------------------------------------------------------------------+
|                                rehearsal-core (FastAPI)                                |
|                                                                                        |
|  +---------------------------+  +----------------------------+  +-------------------+  |
|  |    Linter Engine          |  |   Evaluation Suite Runner  |  |   Report Engine   |  |
|  |  - Schema Complexity Rule |  |  - Utterance Fixtures      |  |  - Scorecard JSON |  |
|  |  - TTS Hostility Rule     |  |  - Slot Extraction Matcher |  |  - Markdown Diff  |  |
|  |  - Param Ergonomics Rule  |  |  - Intent Disambiguation   |  |  - SQLite Store   |  |
|  +---------------------------+  +----------------------------+  +-------------------+  |
|                                               |                                        |
|  +--------------------------------------------+-------------------------------------+  |
|  |                         MCP Client Adapter (mcp SDK)                             |  |
|  |              Supports Stdio and Streamable HTTP / SSE Transports                 |  |
+-----------------------------------------------+----------------------------------------+
                                                | MCP Protocol
                                                v
+----------------------------------------------------------------------------------------+
|                                rehearsal-server (MCP Testbed)                          |
|                                                                                        |
|    Flawed Tools (Anti-Patterns)            vs.    Voice-Optimized Tools (Corrected)    |
|    - `get_detailed_weather_data`                  - `get_current_weather`              |
|    - `smart_home_raw_device_dump`                 - `control_device`                   |
|    - `flight_booking_matrix_query`                - `find_flight_summary`              |
+----------------------------------------------------------------------------------------+
```

---

## 4. Proposed Repository Structure

```
rehearsal/
├── .gitignore                      # Python, Node, SQLite, secrets exclusion
├── README.md                       # Project introduction, architecture, disclaimers
├── PROJECT_PLAN.md                 # Technical specification and implementation phases
├── pyproject.toml                  # Python package metadata and dependencies
├── requirements.txt                # Pinned backend dependencies
├── Makefile / run.py               # Development automation scripts
│
├── rehearsal/                      # Core Python package
│   ├── __init__.py
│   ├── config.py                   # Environment settings & constants
│   ├── models/                     # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── evaluation.py           # Evaluation models (Intent, Slot, TestResult)
│   │   ├── linter.py               # Rule finding and diagnostic models
│   │   └── mcp_types.py            # Normalized MCP tool schemas
│   ├── linter/                     # Voice-readiness static analysis
│   │   ├── __init__.py
│   │   ├── engine.py               # Rule orchestration engine
│   │   ├── rules/
│   │   │   ├── __init__.py
│   │   │   ├── schema_depth.py     # Checks parameter nesting depth
│   │   │   ├── tts_hostility.py    # Detects Markdown tables, URLs, raw JSON
│   │   │   ├── param_ergonomics.py # Evaluates argument names for speech
│   │   │   └── description.py      # Checks trigger phrases and clarity
│   │   └── explainers.py           # Generates human-friendly fix recommendations
│   ├── runner/                     # Test suite execution engine
│   │   ├── __init__.py
│   │   ├── engine.py               # Executes query batches against MCP tools
│   │   ├── metrics.py              # Precision, recall, brevity score calculator
│   │   └── fixtures/               # Deterministic local test datasets
│   │       ├── weather_queries.json
│   │       ├── smarthome_queries.json
│   │       └── flight_queries.json
│   ├── client/                     # MCP client integration
│   │   ├── __init__.py
│   │   ├── connector.py            # Connects via Stdio or Streamable HTTP/SSE
│   │   └── inspector.py            # Discovers tools and inspects schemas
│   ├── server/                     # Reference MCP test server
│   │   ├── __init__.py
│   │   ├── server.py               # Server entry point (FastMCP / MCP SDK)
│   │   ├── flawed_tools.py         # Anti-pattern reference implementations
│   │   └── corrected_tools.py      # Voice-optimized reference implementations
│   └── api/                        # FastAPI application
│       ├── __init__.py
│       ├── main.py                 # FastAPI application factory
│       ├── routes/
│       │   ├── tools.py            # Inspect and list connected tools
│       │   ├── lint.py             # Run linter on selected tools
│       │   ├── evaluate.py         # Execute evaluation suite
│       │   └── compare.py          # Flawed vs. corrected comparison endpoint
│       └── storage.py              # Optional local SQLite test history storage
│
├── tests/                          # Automated Pytest suite
│   ├── conftest.py
│   ├── test_linter.py              # Unit tests for linter rules
│   ├── test_mcp_client.py          # Integration tests for MCP connector
│   ├── test_reference_server.py    # Tests validating reference tools
│   ├── test_runner.py              # Tests for deterministic test-suite runner
│   └── test_api.py                 # FastAPI endpoint tests
│
└── ui/                             # React + TypeScript + Vite Dashboard (Phase 5)
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── App.tsx
        ├── main.tsx
        ├── components/
        │   ├── ToolCard.tsx
        │   ├── LinterReport.tsx
        │   ├── ComparisonView.tsx
        │   └── TestRunScorecard.tsx
        └── styles/
            └── index.css           # Premium Vanilla CSS design system
```

---

## 5. Phased Implementation Checklist

### Phase 1: Environment & Dependency Foundation (Next Step)
- [ ] Initialize Python virtual environment (`.venv`).
- [ ] Install pinned core dependencies: `fastapi`, `uvicorn`, `pydantic`, `mcp`, `httpx`, `pytest`.
- [ ] Establish `pyproject.toml` and verify toolchain with a baseline sanity test.

### Phase 2: Reference MCP Test Server
- [ ] Implement `rehearsal/server/flawed_tools.py` with 3 deliberate anti-patterns:
  - Deeply nested weather query tool returning 120-line raw JSON.
  - Smart home tool requiring raw device GUIDs and returning Markdown status tables.
  - Flight booking tool with 14 required unutterable parameters.
- [ ] Implement `rehearsal/server/corrected_tools.py` with 3 voice-ready counterparts:
  - Concise weather tool returning a spoken speech summary (<30 words).
  - Smart home tool accepting friendly names ("living room lamp") and returning short affirmative speech.
  - Flight tool accepting natural dates and returning top 2 conversational options.
- [ ] Expose tools via MCP SDK server supporting both Stdio and Streamable HTTP.

### Phase 3: Voice-Readiness Linter Engine
- [ ] Implement static rule engine checking:
  - `RULE-001`: Maximum parameter nesting depth.
  - `RULE-002`: Required parameter count budget for voice.
  - `RULE-003`: TTS hostility in descriptions & outputs (Markdown tables, URLs, raw JSON).
  - `RULE-004`: Parameter phonetic readability and utterance compatibility.
- [ ] Implement structured diagnostic report with severity (`CRITICAL`, `WARNING`, `INFO`) and explicit remediation advice.

### Phase 4: Deterministic Test Suite & Runner
- [ ] Construct local deterministic test fixture files with natural spoken utterances.
- [ ] Implement query matcher simulating user voice requests.
- [ ] Calculate voice-readiness metrics:
  - Selection Accuracy (Intent match)
  - Argument Extraction rate
  - Estimated Spoken Duration (based on average 150 words per minute TTS rate)
  - Ear Fatigue Index (length, punctuation density, technical terms)

### Phase 5: FastAPI Backend Orchestration
- [ ] Build REST API connecting linter, runner, and MCP client.
- [ ] Expose `/api/lint`, `/api/tools`, `/api/evaluate`, and `/api/compare`.
- [ ] Provide optional SQLite history logger for tracking regression test runs.

### Phase 6: Interactive Web Dashboard
- [ ] Scaffold Vite + React + TypeScript in `ui/`.
- [ ] Implement polished, dark-mode design system using pure CSS.
- [ ] Build interactive side-by-side comparison view (Flawed vs Corrected).
- [ ] Live audio preview / simulated TTS readout ticker.

---

## 6. Risks, Assumptions & Verification Plan

1. **MCP Python SDK Transport Support**:
   - *Assumption*: The official Python `mcp` SDK supports both Stdio and Streamable HTTP / SSE.
   - *Verification*: Verify during Phase 1 by running the SDK's built-in server and client transports in automated unit tests.
2. **Deterministic Evaluation vs. LLM Flakiness**:
   - *Assumption*: A voice-readiness linter and test-runner must provide 100% reproducible results for automated CI/CD pipelines without external API costs.
   - *Mitigation*: Design the core evaluation engine with rule-based and fixture-driven evaluators first; add an optional LLM adapter interface later.
3. **Platform Compatibility (Windows)**:
   - *Assumption*: Windows PowerShell paths and process management must be handled cleanly.
   - *Mitigation*: Use `pathlib.Path`, cross-platform asyncio subprocesses, and standard forward slashes or raw string paths.
