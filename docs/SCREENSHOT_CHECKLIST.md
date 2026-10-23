# Rehearsal — Manual Screenshot Checklist & Capture Guide

This document provides a clean, standardized checklist for manually capturing high-resolution screenshots of the **Rehearsal MCP Voice Testing Workbench** for hackathon submissions, technical reviews, and repository documentation.

---

## 🔒 Privacy & Hygiene Checklist (Before Capturing)

To ensure presentation materials remain professional and secure:
1. **No Local Secrets or Credentials**: Ensure no API keys, tokens, or environment secrets are visible.
2. **Clean URL & Window Chrome**:
   - Use standard `http://127.0.0.1:5173/` or `http://localhost:5173/`.
   - Close non-essential browser tabs, bookmarks bars, and personal browser extensions.
3. **Mute Desktop Notifications**: Disable Windows notifications / Focus Assist during capture to avoid popups.
4. **Resolution & Scaling**:
   - Recommended resolution: **1920x1080 (1080p)** or **2560x1440 (1440p)**.
   - Browser Zoom: Set strictly to **100%**.
   - Operating System DPI Scaling: 100% recommended to maintain crisp typography.
5. **Lossless Format**: Save all assets as lossless **PNG** files into `docs/screenshots/`.

---

## 📸 Required Screenshot Manifest

| # | Target Filename | Screen | State to Capture | Key Elements to Verify |
| :-: | :--- | :--- | :--- | :--- |
| **01** | `01_overview_workbench.png` | **Overview** | Default workbench view with Weather or Smart Home domain selected in the active inspector. | • Breadcrumbs `rehearsal / overview`<br>• Backend status `127.0.0.1:8000 (HEALTHY)`<br>• Benchmark pill `60 ➔ 100 (+40 pts)`<br>• 3-column workbench grid with segmented score scales<br>• Active Inspector Telemetry pane expanded<br>• Standards strip with RULE-001/002/003 chips<br>• Supporting dock showing reference tools and SQLite telemetry |
| **02** | `02_tool_explorer_schema.png` | **Tool Explorer** | Master-detail view with `fetch_meteorological_telemetry_v2` selected and Table View active. | • Search input and group filter buttons (`All`, `Flawed`, `Voice-First`)<br>• Catalog list with status dots and parameter badges<br>• Inspector header with domain badge and copy schema button<br>• Heuristic Ergonomics strip (Depth 3, Raw JSON)<br>• Schema specification table showing property types and descriptions |
| **03** | `03_voice_linter_findings.png` | **Voice Linter** | Linter executed on `Flawed Only` group displaying active diagnostic findings. | • Control bar with target group pills and `Run Linter` button<br>• Scorecard showing aggregate score (60/100, Grade D)<br>• Severity counters: 2 Errors, 7 Warnings<br>• Diagnostic Findings Console table displaying `RULE-001`, `RULE-003`, `RULE-004`<br>• Line-level evidence blocks and remediation guidance |
| **04** | `04_comparison_benchmark.png` | **Compare** | Full comparative benchmark view displaying side-by-side domain scorecards. | • Aggregate delta counter: Flawed 60.0 ➔ Corrected 100.0 (+40.0 pts)<br>• Segmented score lift track clearly showing baseline vs. lift<br>• Side-by-side columns for Weather, Smart Home, and Travel<br>• Nesting depth comparisons (Depth 3 vs. Flat Depth 1)<br>• Architectural transformations list |
| **05** | `05_evaluation_results.png` | **Evaluation Runner** | Evaluation suite executed on `All (18)` with `Live MCP Execution` enabled. | • Top controls with `All (18)` selected and Live MCP checked<br>• Results summary strip: `100% Tool Match`, `100% Exact Arg Match`, `Slot F1: 1.000`, `Est. Speech: 3.3s`<br>• `Live MCP Connected` green badge<br>• Utterance test case table showing spoken phrases, mapped tools, extracted slots, live response strings, and `Listen` TTS buttons |
| **06** | `06_run_history_inspection.png` | **Run History** | Run History screen with the **Run Telemetry Inspector Modal** open for the latest run. | • Background table showing persisted SQLite runs with timestamps and accuracy metrics<br>• Modal header with Run ID<br>• Metric cards: Domain, Cases Tested, Tool Accuracy, Arg Match<br>• Verifiable Report JSON code block with `Copy` and `Export JSON` buttons |

---

## 🛠️ Step-by-Step Capture Procedure

1. **Launch Services**:
   ```powershell
   # Terminal 1: Backend
   cd "C:\Users\akeem\Rehearsal Hackthone"
   .venv\Scripts\python.exe -m uvicorn rehearsal.api.app:app --host 127.0.0.1 --port 8000

   # Terminal 2: Frontend
   cd "C:\Users\akeem\Rehearsal Hackthone\ui"
   npm run dev -- --host 127.0.0.1 --port 5173
   ```
2. **Open Browser**: Navigate to `http://127.0.0.1:5173/`.
3. **Capture 01 (Overview)**: Ensure the backend is healthy. Click the Smart Home IoT card to reveal the active inspector pane. Capture full browser viewport.
4. **Capture 02 (Tool Explorer)**: Switch to Tool Explorer. Select `fetch_meteorological_telemetry_v2`. Capture the master-detail split.
5. **Capture 03 (Voice Linter)**: Switch to Voice Linter. Select `Flawed Only (3)`. Click `Run Linter`. Capture the findings console.
6. **Capture 04 (Compare)**: Switch to Compare. Capture the aggregate delta header, segmented meter, and domain cards.
7. **Capture 05 (Evaluation Runner)**: Switch to Evaluation Runner. Ensure `Live MCP Execution` is checked. Click `Run Test Suite`. When complete, capture the results table.
8. **Capture 06 (Run History)**: Switch to Run History. Click `Inspect` on the top run. Capture the screen with the inspection modal active.
9. **Store Assets**: Save images as `01_overview_workbench.png`, `02_tool_explorer_schema.png`, etc., in `docs/screenshots/`.
