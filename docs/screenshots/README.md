# Rehearsal Dashboard — Screenshot Guide

This directory documents the visual assets for Rehearsal's presentation and public documentation.

> **Notice**: To maintain strict integrity for open-source evaluation, screenshots must be captured from a live running instance of the dashboard. Do not use synthetic mockups.

## Recommended Capture Specifications
- **Display Resolution**: 1920x1080 (1080p) or 2560x1440 (1440p)
- **Browser Zoom**: 100%
- **Theme**: Dark charcoal default theme (`#0a0d14`)
- **Format**: PNG (lossless)

---

## Required Screenshots

| File Name | View / Tab | State & Details to Highlight |
| :--- | :--- | :--- |
| `01_overview.png` | **Overview** | System health status (`HEALTHY`), MCP SDK version `2.3.0`, 6 reference tools count, average voice-readiness scores (Flawed 60.0 vs Corrected 100.0), and recent evaluation runs. |
| `02_tool_explorer.png` | **Tool Explorer** | All 6 reference tools displayed in responsive grid, domain filter active, at least one tool with expanded input schema JSON showing property types and descriptions. |
| `03_voice_linter.png` | **Voice Linter** | Linter executed for flawed group, showing overall score `60`, 2 errors, 7 warnings, with expanded findings showing `RULE-001`, `RULE-003`, `RULE-004`, evidence, and fix recommendations. |
| `04_comparison.png` | **Compare** | Side-by-side benchmark scorecard with Weather, Smart Home, and Travel pairs, +40.0 pt score improvement, and voice usability differences. |
| `05_evaluation_results.png` | **Evaluation Runner** | Evaluation executed with `Execute MCP Tools Live` enabled, showing 100% tool selection accuracy, exact match rate, slot metrics, average speech duration, and per-case results table with speech audio playback button. |
| `06_run_history.png` | **Run History** | Persisted evaluation runs table loaded from SQLite storage, with one run's detailed inspection modal open displaying the full evaluation report and Export JSON button. |

---

## Capture Procedure

1. **Start the backend server**:
   ```powershell
   .venv\Scripts\python.exe -m uvicorn rehearsal.api.app:app --host 127.0.0.1 --port 8000
   ```
2. **Start the frontend development server**:
   ```powershell
   cd ui
   npm run dev
   ```
3. **Open browser**: Navigate to `http://127.0.0.1:5173/`.
4. Capture each screen listed above and save the PNG images into this directory (`docs/screenshots/`).
