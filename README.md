# Rehearsal: Voice-Readiness Testing & Evaluation for MCP Tools

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.12+](https://img.shields.io/badge/Python-3.12%2B-brightgreen.svg)]()
[![MCP SDK](https://img.shields.io/badge/MCP-Python%20SDK-purple.svg)]()

> **Notice & Disclaimer**: Rehearsal is an independent, open-source testing platform. It is **not** affiliated with, endorsed by, or an official implementation of Amazon Alexa, Alexa+, or Amazon.com, Inc.

---

## 🎙️ Overview

**Rehearsal** is an open-source evaluation and linting platform designed for developers building **Model Context Protocol (MCP)** tools for voice-first AI assistants (smart speakers, voice agents, hands-free automotive interfaces, and multimodal displays).

In graphical and chat-based AI environments, tools can return large JSON blobs, nested dictionaries, markdown tables, and lengthy URLs. However, when an agent speaks responses aloud via Text-to-Speech (TTS), these patterns degrade the user experience:
- **TTS Hostility**: Reading out raw Markdown, URLs, or JSON arrays causes conversational friction and ear fatigue.
- **Unutterable Parameters**: Complex, deeply-nested parameter schemas cannot be naturally requested by a user speaking a single sentence.
- **Ambiguous Tool Descriptions**: In voice environments, users phrase requests concisely; vague tool descriptions cause selection errors or hallucinated calls.
- **Latency Overruns**: Voice interactions demand sub-second responsiveness before user perceived failure.

Rehearsal provides static linting, deterministic evaluation test suites, and dynamic MCP execution to test and score your MCP tools for voice readiness.

---

## 🏗️ Architecture

```
                                  +---------------------------------------+
                                  |         Rehearsal Dashboard           |
                                  |   (React + TypeScript + Vite + CSS)   |
                                  +-------------------+-------------------+
                                                      | REST / SSE
                                                      v
+-----------------------------------------------------------------------------------------+
|                                    Rehearsal Core Engine                                |
|                                   (FastAPI + Python 3.12)                               |
|                                                                                         |
|  +------------------------+  +--------------------------+  +-------------------------+  |
|  |  Voice-Readiness       |  |  Voice Test Suite        |  |  MCP Client Manager     |  |
|  |  Linter                |  |  Runner                  |  |  (Official Python SDK)  |  |
|  |  - Schema complexity   |  |  - Utterance matches     |  |  - Stdio / Streamable   |  |
|  |  - Parameter ergonomics|  |  - Slot extraction tests |  |    HTTP transport       |  |
|  |  - TTS output score    |  |  - Latency profiling     |  |                         |  |
|  +------------------------+  +--------------------------+  +-------------------------+  |
|                                                                                         |
|                                  +--------------------+                                 |
|                                  | Deterministic Test |                                 |
|                                  | Fixtures (Local)   |                                 |
|                                  +--------------------+                                 |
+---------------------------------------------+-------------------------------------------+
                                              | MCP Protocol (Streamable HTTP / Stdio)
                                              v
                      +-----------------------------------------------+
                      |             MCP Reference Test Server         |
                      |                                               |
                      |  [Flawed Anti-Patterns]  [Corrected Patterns] |
                      |   - Weather verbose json   - Weather concise  |
                      |   - Smart home raw dump    - Smart home brief |
                      |   - Flight booking table   - Flight summary   |
                      +-----------------------------------------------+
```

---

## 🖥️ The Six Workbench Screens

Rehearsal provides a unified Developer IDE / Testing Workbench interface organized into six dedicated screens:

1. **Overview (`OverviewPage`)**:
   Central workbench console featuring live benchmark telemetry (`60 ➔ 100 (+40 pts)`), a responsive 3-column comparison grid across Weather, Smart Home, and Travel domains, an interactive domain inspector, the heuristic standards strip (`RULE-001` through `RULE-003`), and a supporting dock summarizing reference tools and SQLite run telemetry.
2. **Tool Explorer (`ToolExplorerPage`)**:
   Master-detail MCP catalog browser with real-time search, group filters (`All`, `Flawed`, `Voice-First`), and domain filters. Includes the Heuristic Ergonomics strip, Table View vs. Raw JSON schema toggling, and one-click schema copying.
3. **Voice Linter (`VoiceLinterPage`)**:
   Static schema analysis console evaluating 5 heuristic voice rules (`RULE-001` Schema Depth, `RULE-002` Argument Count, `RULE-003` TTS Hostility, `RULE-004` Parameter Ergonomics, `RULE-005` Description Clarity). Displays overall score grade, severity counters, line-level evidence, and voice remediation guidance.
4. **Compare (`ComparePage`)**:
   Side-by-side benchmark workspace displaying the aggregate +40.0 pt voice-ergonomics score lift, a segmented 0–100 progress scale, paired domain scorecards, schema nesting depth comparisons (Depth 3 vs. Flat Depth 1), and architectural transformation notes.
5. **Evaluation Runner (`EvaluationRunnerPage`)**:
   Test execution workbench testing natural spoken utterances against 18 deterministic fixtures. Features domain filtering, a Live MCP Execution toggle with visual indicator badges, tool selection accuracy, exact argument match rate, slot extraction F1, speech duration estimation, and in-browser Audio TTS playback.
6. **Run History (`RunHistoryPage`)**:
   Verifiable SQLite audit trail (`rehearsal_history.sqlite3`) logging every evaluation execution. Provides run filtering, Copy Run ID, an inspection modal with full report telemetry, and one-click JSON export for CI/CD integration.

---

## 📚 Demo Runbook & Guides

- **[Demo Presentation Script](docs/DEMO_SCRIPT.md)**: A timed 3-minute spoken presentation script for hackathon judging and technical reviews.
- **[Demo Runbook](docs/DEMO_RUNBOOK.md)**: A complete 3–5 minute live presentation walkthrough with step-by-step instructions, expected outputs, and troubleshooting.
- **[Pre-Demo Checklist](docs/DEMO_CHECKLIST.md)**: Operational checklist covering service launch, health checks, TTS verification, and presentation hygiene.
- **[Screenshot Checklist](docs/SCREENSHOT_CHECKLIST.md)**: Manual capture guidelines, privacy hygiene, and required screenshot specifications.
- **[Screenshot Assets](docs/screenshots/README.md)**: Specifications and storage directory for dashboard screenshots.

---

## 🚀 Milestones

- [x] **Milestone 1**: Environment setup, dependency manifest, and baseline MCP SDK verification.
- [x] **Milestone 2**: Reference MCP Test Server with flawed and corrected tool implementations.
- [x] **Milestone 3**: Voice-readiness linter engine with explainable findings.
- [x] **Milestone 4**: MCP client connector & deterministic test-suite runner with scoring.
- [x] **Milestone 5**: FastAPI orchestration service exposing evaluation endpoints.
- [x] **Milestone 6**: React + TypeScript frontend dashboard for interactive voice-readiness evaluation.
- [x] **Milestone 7**: End-to-end integration testing, sample reports, and documentation.

---

## 📋 System Requirements & Setup

- **Python**: 3.12+ (verified with Python 3.12.4 on Windows x64)
- **Node.js**: v20+ (verified with v22.18.0)
- **npm**: 10+ (verified with npm 10.9.3)
- **Git**: 2.40+ (verified with Git 2.49.0)

### Windows PowerShell Setup
```powershell
# 1. Clone repository & enter workspace
git clone <repository-url>
cd rehearsal

# 2. Verify Python virtual environment
.venv\Scripts\python.exe --version

# 3. Verify installed Python dependencies
.venv\Scripts\python.exe -m pip list
```

---

## ⚡ Quickstart & Local Execution

### 1. Launch Backend API (Terminal 1)
```powershell
.venv\Scripts\python.exe -m uvicorn rehearsal.api.app:app --host 127.0.0.1 --port 8000 --reload
```
- **Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

### 2. Launch Frontend UI (Terminal 2)
```powershell
cd ui
npm run dev
```
- **Dashboard URL**: `http://127.0.0.1:5173/`

### 3. Verify Test Suites & Production Build
```powershell
# Run backend pytest suite (51 passing unit & integration tests)
.venv\Scripts\python.exe -m pytest tests -v

# Run frontend TypeScript check & production bundle
cd ui
npm run build
```

---

## 🌐 API Endpoint Summary

| Method | Endpoint | Description | Sample Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Health pulse, UTC timestamp, MCP SDK version, and open-source disclaimer | `200 OK` |
| `GET` | `/api/tools` | Discovers registered reference MCP tools with input schemas and classifications | `200 OK` |
| `POST` | `/api/lint` | Lints tools against 5 voice rules for target groups (`all`, `flawed`, `corrected`) | `200 OK` |
| `POST` | `/api/compare` | Compares flawed vs. corrected tools with paired scorecards and voice diffs | `200 OK` |
| `POST` | `/api/evaluate` | Deterministic natural-language test suite runner with live MCP tool execution | `200 OK` |
| `GET` | `/api/runs` | Queries recent persisted evaluation runs with pagination (`limit`, `offset`) | `200 OK` |
| `GET` | `/api/runs/{run_id}` | Retrieves full evaluation report JSON for a specific run ID (or `404 Not Found`) | `200 OK` / `404` |
| `GET` | `/docs` | Interactive Swagger UI documentation | `200 OK` |

---

## ⚖️ Metric Integrity & Limitations

1. **Independent Heuristic Scoring**:
   - Rehearsal's voice-readiness scores are heuristic estimates based on conversational interface design principles (schema depth $\le 2$, argument budgets, TTS-safe markdown/plain text outputs, and natural language descriptions).
   - These scores are **not** official Amazon, Alexa, or Alexa+ metrics and do not guarantee production acceptance or real-world end-user satisfaction.
   - Rehearsal is an independent open-source evaluation platform and is **not** an official Amazon product, integration, or endorsement.
2. **Deterministic Baseline Evaluator**:
   - The 18 evaluation cases are deterministic fixtures with pre-compiled natural-language utterances.
   - It runs completely offline without paid external LLMs or third-party API dependencies. Predictions are generated strictly from user utterances without inspecting ground-truth answers.
   - **Fixture results do not establish real-world assistant accuracy**, as production voice assistants encounter open-ended acoustic noise, diverse accents, and dynamic conversational contexts.
3. **Speech Duration Estimates**:
   - Duration estimates are calculated at a standard reading pace of 150 Words Per Minute (WPM) to illustrate ear-fatigue and conversational brevity differences.

---

## 🎙️ 3-Minute Hackathon Demo Script

> For the comprehensive presenter walkthrough, expected outputs, and troubleshooting, see the [Demo Runbook](docs/DEMO_RUNBOOK.md).

1. **0:00 - 0:45 | Overview & The Problem**:
   - Open `http://127.0.0.1:5173/`. Point out the active health indicator and MCP Python SDK 2.3.0 connection.
   - Highlight the core thesis: *Most MCP tools are built for visual chatbots—returning multi-kilobyte JSON blobs and deeply-nested schemas. When spoken aloud by a voice assistant, they cause acute ear fatigue and conversational failure.*
2. **0:45 - 1:30 | Flawed vs. Corrected Benchmark (`Compare` tab)**:
   - Walk through the side-by-side comparison across Weather, Smart Home, and Travel.
   - Highlight the **60.0 vs. 100.0** voice-readiness gap:
     - **Weather**: Flawed tool requires nested geodetic coordinates ($defs/NestedCoord) and returns raw telemetry; corrected tool takes a simple spoken city name and speaks a 25-word forecast.
     - **Smart Home**: Flawed tool expects 16-bit register masks and hex GUIDs (`0x4A9F`); corrected tool accepts natural room names and verbs.
3. **1:30 - 2:15 | Voice Linter Engine (`Voice Linter` tab)**:
   - Select `flawed` group and click **Run Voice Linter**.
   - Show how the linter pinpoints `RULE-001` (Excessive Schema Depth), `RULE-003` (TTS Hostility), and `RULE-004` (Parameter Ergonomics) with precise line-level evidence and actionable fixes.
4. **2:15 - 2:50 | Natural Utterance Runner (`Evaluation Runner` tab)**:
   - Select `All Domains` and ensure `Execute MCP Tools Live` is checked. Click **Execute Evaluation**.
   - Review live metrics: **100% Tool Selection Accuracy**, argument matching rate, and a contrast in speech duration between verbose and concise tool outputs.
   - Click the speech synthesis button to listen to the browser's spoken response.
5. **2:50 - 3:00 | Persistence & Run History (`Run History` tab)**:
   - Show the newly recorded evaluation run persisted in SQLite. Open the inspect modal and click **Export JSON** to show the verifiable evaluation artifact.

---

## 📸 Screenshots

- Visual capture checklist and privacy guidelines: [`docs/SCREENSHOT_CHECKLIST.md`](docs/SCREENSHOT_CHECKLIST.md)
- Screenshot storage directory: [`docs/screenshots/`](docs/screenshots/README.md)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Rehearsal Contributors.

