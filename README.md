# 🎙️ Rehearsal — Hackathon Demo Runbook

![Banner](https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,100:1a0a2e&height=200&section=header&text=Rehearsal&fontSize=56&fontColor=fb923c&animation=twinkling&fontAlignY=35&desc=MCP%20Voice%20Testing%20Workbench&descAlignY=55&descColor=fed7aa)

<p align="center">
  <img src="https://img.shields.io/badge/Type-Hackathon%20Demo-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Protocol-MCP-6366F1?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12.4%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Tests-51%2F51%20Passing-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Fixtures-18%20Deterministic-informational?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
</p>

> A structured, end-to-end operational guide for demonstrating the **Rehearsal MCP Voice Testing Workbench** to technical judges and reviewers in **3 to 5 minutes**.

---

## 📑 Table of Contents

1. [Important Disclosures & Evaluation Scope](#️-1-important-disclosures--evaluation-scope)
2. [Architecture](#️-2-architecture)
3. [Prerequisites & Verification](#️-3-prerequisites--verification)
4. [Service Startup & Health Verification](#-4-service-startup--health-verification)
5. [3–5 Minute Live Walkthrough Script](#️-5-35-minute-live-walkthrough-script)
6. [Troubleshooting Guide](#-6-troubleshooting-guide)
7. [Summary Checklist for Demo Presenters](#-7-summary-checklist-for-demo-presenters)

---

## ⚠️ 1. Important Disclosures & Evaluation Scope

```
1. Independent Project
   Rehearsal is an independent open-source evaluation project. It is NOT
   affiliated with, endorsed by, or an official implementation of Amazon
   Alexa, Alexa+, or Amazon.com, Inc.

2. Heuristic Scores
   Linting and voice-readiness scores are rule-based heuristic calculations
   assessing input schema depth, required argument counts, and spoken TTS
   formatting risks. They are NOT official benchmarks or certifications.

3. Deterministic Evaluation Fixtures
   The 18 test cases evaluate intent matching and slot extraction using
   deterministic offline utterances. High scores on deterministic fixtures
   do NOT prove real-world accuracy across acoustic background noise,
   regional accents, or open-ended conversations.
```

---

## 🏗️ 2. Architecture

Rehearsal is a three-tier system: a React dashboard talks to a FastAPI core engine over REST / SSE, and the engine drives an MCP reference test server through the official Python SDK.

```text
                        +-----------------------------------------+
                        |           Rehearsal Dashboard           |
                        |    (React + TypeScript + Vite + CSS)    |
                        +-----------------------------------------+
                                             | REST / SSE
                                             v
+------------------------------------------------------------------------------------------+
|                                  Rehearsal Core Engine                                   |
|                                 (FastAPI + Python 3.12)                                  |
|                                                                                          |
| +--------------------------+  +--------------------------+  +--------------------------+ |
| | Voice-Readiness Linter   |  | Voice Test Suite Runner  |  | MCP Client Manager       | |
| | - Schema complexity      |  | - Utterance matches      |  | (Official Python SDK)    | |
| | - Parameter ergonomics   |  | - Slot extraction tests  |  | - Stdio / Streamable     | |
| | - TTS output score       |  | - Latency profiling      |  |   HTTP transport         | |
| |                          |  |                          |  |                          | |
| +--------------------------+  +--------------------------+  +--------------------------+ |
|                                                                                          |
|                                  +--------------------+                                  |
|                                  | Deterministic Test |                                  |
|                                  | Fixtures (Local)   |                                  |
|                                  +--------------------+                                  |
+------------------------------------------------------------------------------------------+
                                             | MCP Protocol (Streamable HTTP / Stdio)
                                             v
                    +-------------------------------------------------+
                    |            MCP Reference Test Server            |
                    |                                                 |
                    |  [Flawed Anti-Patterns]   [Corrected Patterns]  |
                    |   - Weather verbose json    - Weather concise   |
                    |   - Smart home raw dump     - Smart home brief  |
                    |   - Flight booking table    - Flight summary    |
                    +-------------------------------------------------+
```

| Layer | Technology | Responsibility |
|---|---|---|
| **Rehearsal Dashboard** | React, TypeScript, Vite, CSS | Workbench UI — Overview, Tool Explorer, Voice Linter, Compare, Evaluation Runner, Run History |
| **Rehearsal Core Engine** | FastAPI, Python 3.12 | Hosts the linter, test suite runner and MCP client manager; persists runs to SQLite |
| **Voice-Readiness Linter** | Python (rule-based) | Schema complexity, parameter ergonomics and TTS output scoring (`RULE-001` to `RULE-005`) |
| **Voice Test Suite Runner** | Python | Utterance matching, slot extraction tests and latency profiling against deterministic local fixtures |
| **MCP Client Manager** | Official Python MCP SDK | Connects over Stdio or Streamable HTTP transport |
| **MCP Reference Test Server** | MCP Protocol | Ships flawed anti-pattern tools and corrected voice-first tools for Weather, Smart Home and Flight booking |

---

## 🛠️ 3. Prerequisites & Verification

Ensure you have PowerShell open in the project root: `C:\Users\akeem\Rehearsal Hackthone`

```powershell
# 1. Verify Python virtual environment (Python 3.12.4+)
.venv\Scripts\python.exe --version

# 2. Verify Node.js and npm
node --version
npm --version

# 3. Verify backend test suite (51/51 tests passing)
.venv\Scripts\python.exe -m pytest tests -v

# 4. Verify frontend build
cd ui
npm run build
cd ..
```

---

## 🚀 4. Service Startup & Health Verification

Open **two dedicated Windows PowerShell terminal windows**:

### 🖥️ Terminal 1 — FastAPI Backend & Reference MCP Server
```powershell
cd "C:\Users\akeem\Rehearsal Hackthone"
.venv\Scripts\python.exe -m uvicorn rehearsal.api.app:app --host 127.0.0.1 --port 8000
```

**Pulse Check:** Navigate to `http://127.0.0.1:8000/api/health` in your browser or run:
```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

> ✅ **Expected Response:** `status: healthy`, `service: rehearsal-api`, `mcp_sdk_version: 2.3.0`

### 🎨 Terminal 2 — React + TypeScript Frontend Workbench
```powershell
cd "C:\Users\akeem\Rehearsal Hackthone\ui"
npm run dev -- --host 127.0.0.1 --port 5173
```

> 🌐 **Dashboard URL:** `http://127.0.0.1:5173/`

---

## ⏱️ 5. 3–5 Minute Live Walkthrough Script

| Step | Screen | Time |
|:---:|---|:---:|
| 1 | Overview & The Voice Problem | 0:00 – 0:50 |
| 2 | Tool Explorer — Schema Deep-Dive | 0:50 – 1:30 |
| 3 | Voice Linter — Diagnostic Console | 1:30 – 2:15 |
| 4 | Compare — Side-by-Side Ergonomic Gains | 2:15 – 2:50 |
| 5 | Evaluation Runner — Utterance Testing & TTS | 2:50 – 3:45 |
| 6 | Run History — Verifiable SQLite Audit Trail | 3:45 – 4:15 |

---

### 🎬 Step 1: Overview & The Voice Problem `(0:00 – 0:50)`

**Action:** Open `http://127.0.0.1:5173/` in your browser.

**Visuals to Point Out:**
- The top bar displays breadcrumbs `rehearsal / overview` and connection status `127.0.0.1:8000 (HEALTHY)`
- The compact workspace header shows the live benchmark pill: `60 ➔ 100 (+40 pts)`
- The **3-Column Responsive Workbench Grid** organizes the three benchmark domains: Weather Services, Smart Home IoT, and Flight & Travel Booking
- The **Segmented 0–100 Score Scales**: Show that the dark slate baseline bar (e.g. 65 for Weather, 45 for Travel) is visually distinct from the vibrant emerald ergonomic lift span (+35, +55)

**Narrative:**
> *"Most MCP tools are built for visual chatbot clients—they take deeply nested parameters and return 200-word raw JSON payloads. When hooked up to a voice assistant, this causes immediate conversational failure: ear fatigue, unutterable parameter names, and high turn-taking latency. Rehearsal tests and benchmarks MCP schemas specifically for voice readiness."*

**Interaction:** Click on the **Smart Home IoT** card. Notice how the **Active Inspector Telemetry** pane below smoothly expands to show the full tool identifiers (`execute_home_iot_command_rpc` vs `control_home_device`) and the concrete architectural diffs.

---

### 🔍 Step 2: Tool Explorer — Schema Deep-Dive `(0:50 – 1:30)`

**Action:** Click **Tool Explorer** in the left sidebar.

**Visuals to Point Out:**
- Master-detail split layout. The left list catalogs 6 registered tools (3 flawed, 3 voice-first) across 3 domains
- Filter toggles: Click **Flawed (3)** then **Voice-First (3)** to show transparent categorization
- Type `telemetry` in the search box to demonstrate real-time client-side search filtering
- Select `fetch_meteorological_telemetry_v2`: Point out the **Heuristic Ergonomics Strip** showing `Depth 3 ($defs nested)` and `Raw JSON / Markdown`
- Switch the schema inspector from **Table View** to **Raw JSON** and click **Copy Schema** to demonstrate clipboard integration

**Narrative:**
> *"Here developers can inspect registered tools. The flawed weather tool requires nested coordinate definitions and geodetic flags that no human speaker would ever dictate aloud. The voice-first tool flattens this into a single spoken location string."*

---

### 🧪 Step 3: Voice Linter — Diagnostic Console `(1:30 – 2:15)`

**Action:** Click **Voice Linter** in the left sidebar.

**The 5 Heuristic Rules:**

| Rule | Focus |
|---|---|
| `RULE-001` | Nesting Depth |
| `RULE-002` | Argument Count |
| `RULE-003` | TTS Hostility |
| `RULE-004` | Parameter Ergonomics |
| `RULE-005` | Description Clarity |

**Visuals to Point Out:**
- Select **Flawed Only (3)** and click **Run Linter**
- Review the score (**60/100, Grade D**) and the findings table showing exact rule IDs, evidence codes, voice impact, and remediation instructions
- Select **Voice-First Only (3)** and click **Run Linter**
- Show the empty state: `No Active Lint Findings — All scanned tool schemas comply with selected voice-readiness heuristic rules` (**100/100, Grade A+**)

**Narrative:**
> *"Our static linter flags schema traps before runtime. Notice how RULE-003 detects raw JSON and Markdown output formats that would cause text-to-speech engines to read out punctuation marks and brackets, frustrating the listener."*

---

### ⚖️ Step 4: Compare — Side-by-Side Ergonomic Gains `(2:15 – 2:50)`

**Action:** Click **Compare** in the left sidebar.

**Visuals to Point Out:**
- Aggregate comparison counter: Flawed baseline `60.0/100` ➔ Voice-First `100.0/100` with **+40.0 pts** net improvement
- The segmented progress track highlights the 60% baseline and the +40 pt lift without overlapping or clipping
- The 3 paired domain cards (Weather, Smart Home, Travel) showing side-by-side nesting depth reductions (Depth 3 down to Depth 1) and exact architectural transformations

**Narrative:**
> *"This screen quantifies the architectural shift. By replacing 16-bit register hex masks with natural device targets in Smart Home, we achieve a +30 point lift. In Travel, replacing a 200-word flight matrix with 2 spoken choices achieves a +55 point lift."*

---

### 🎤 Step 5: Evaluation Runner — Utterance Testing & TTS `(2:50 – 3:45)`

**Action:** Click **Evaluation Runner** in the left sidebar.

**Visuals to Point Out:**
- Initial state indicates `18 Fixtures Ready`
- Domain selector: `All (18)`, `Weather (6)`, `Smart Home (6)`, `Travel (6)`
- Ensure the **Live MCP Execution** checkbox is enabled
- Click **Run Test Suite**

**Expected Results:**

| Metric | Value |
|---|---|
| Tool Match Accuracy | `100%` |
| Exact Argument Match | `100%` |
| Slot Extraction F1 | `1.000` |
| Est. Speech Duration | `~3.3s` |
| Status Badge | 🟢 **Live MCP Connected** |

- Review the results table showing casual spoken utterances, mapped MCP tools, extracted slots, and live tool responses
- Click the **Listen** button on any case (e.g. `sh_01`) to demonstrate Web Speech API synthesis speaking the concise response aloud

**Narrative:**
> *"Rehearsal doesn't just lint schemas; it runs test utterances against live in-memory MCP clients. Here, casual user phrases like 'turn off the kitchen lights' are mapped to the tool and slots are extracted. We also estimate spoken duration at 150 words-per-minute to keep turn-taking brief."*

---

### 🗂️ Step 6: Run History — Verifiable SQLite Audit Trail `(3:45 – 4:15)`

**Action:** Click **Run History** in the left sidebar.

**Visuals to Point Out:**
- Show the newly recorded evaluation run persisted in `rehearsal_history.sqlite3`
- Click **Copy Run ID** to demonstrate clipboard integration
- Click **Inspect** on the latest run
- Inside the inspection modal, review the run telemetry summary and the raw evaluation report JSON
- Click **Export JSON** to show the generated downloadable audit file (`rehearsal-run-run_....json`)

**Narrative:**
> *"Every evaluation run is automatically persisted to an audit log in SQLite. Teams can export the full report JSON to integrate voice-readiness gating into CI/CD pipelines."*

---

## 🔧 6. Troubleshooting Guide

| Issue | Root Cause | Resolution |
|---|---|---|
| **"Workbench Connection Offline" on Overview** | FastAPI backend is not running on port 8000 | Start Terminal 1 with `.venv\Scripts\python.exe -m uvicorn rehearsal.api.app:app --host 127.0.0.1 --port 8000`. Click **Retry Connection**. |
| **Frontend displays blank page** | Node dependencies not built or port 5173 occupied | In `ui/`, run `npm run build` to verify compilation, then `npm run dev -- --host 127.0.0.1 --port 5173` |
| **Listen button produces no audio** | Browser speech synthesis blocked or muted | Ensure browser tab is not muted and OS audio output is enabled. Note that `window.speechSynthesis` requires user gesture activation. |
| **Clipboard copy fails** | Browser permissions denied | Ensure your browser allows clipboard access on `http://127.0.0.1:5173/` |
| **Port 8000 or 5173 already in use** | Stale processes from previous sessions | Check running tasks with `Get-Process -Name python, node` in PowerShell and terminate stale instances |

---

## 📌 7. Summary Checklist for Demo Presenters

- [ ] Backend running and healthy at `http://127.0.0.1:8000/api/health`
- [ ] Frontend running at `http://127.0.0.1:5173/`
- [ ] Browser window zoomed to 100% at 1080p or 1440p resolution
- [ ] Audio volume set to a comfortable level for TTS demonstration
- [ ] Independent open-source disclaimer clearly communicated to viewers

---

<p align="center">
  ⭐ If you found this project helpful, please <strong>star the repo</strong> and share it!
</p>

![Footer](https://capsule-render.vercel.app/api?type=waving&color=0:1a0a2e,100:0d1117&height=120&section=footer&fontColor=fb923c)
