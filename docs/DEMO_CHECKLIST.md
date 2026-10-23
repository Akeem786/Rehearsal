# Rehearsal — Pre-Demo & Technical Review Checklist

A rapid, step-by-step checklist to ensure a seamless, error-free presentation of the **Rehearsal MCP Voice Testing Workbench**.

---

## 📋 1. Service Launch & Health Verification

- [ ] **Start Backend Service (Terminal 1)**:
  ```powershell
  cd "C:\Users\akeem\Rehearsal Hackthone"
  .venv\Scripts\python.exe -m uvicorn rehearsal.api.app:app --host 127.0.0.1 --port 8000
  ```
- [ ] **Verify Backend Pulse**:
  Open `http://127.0.0.1:8000/api/health` in your browser. Confirm:
  - `status: "healthy"`
  - `service: "rehearsal-api"`
  - `mcp_sdk_version: "2.3.0"`
  - Independent open-source disclaimer present
- [ ] **Start Frontend Dev Server (Terminal 2)**:
  ```powershell
  cd "C:\Users\akeem\Rehearsal Hackthone\ui"
  npm run dev -- --host 127.0.0.1 --port 5173
  ```
- [ ] **Verify Frontend Dashboard**:
  Open `http://127.0.0.1:5173/` in your browser. Confirm:
  - Top bar breadcrumbs show `rehearsal / overview`
  - Backend status indicator displays `127.0.0.1:8000 (HEALTHY)`
  - Benchmark pill displays `60 ➔ 100 (+40 pts)`

---

## 🎧 2. Audio & Browser Permissions Check

- [ ] **Audio Volume & Web Speech API**:
  - Unmute your browser tab and set system audio to a comfortable volume.
  - Navigate to the **Evaluation Runner** tab (`http://127.0.0.1:5173/`).
  - Run the evaluation and click the **Listen** button on any case with output (e.g. `sh_01`) to verify spoken TTS playback.
- [ ] **Clipboard Access**:
  - Navigate to **Tool Explorer**, select any tool, and click **Copy Schema**. Verify the "Copied" feedback appears.
  - Navigate to **Run History** and click **Copy Run ID**. Verify clipboard write permission is granted.

---

## 🗂️ 3. Data & State Preparation

- [ ] **Pre-Seed Initial Evaluation Run**:
  - Run the evaluation suite once before presenting so that **Run History** already contains at least one audit record.
  - Confirm the run appears in `http://127.0.0.1:5173/` under the Run History tab.
- [ ] **Inspect SQLite Database**:
  - Confirm `rehearsal_history.sqlite3` exists in the project root and is excluded from Git via `.gitignore`.
- [ ] **Verify Test Suite Baseline**:
  - Run `.venv\Scripts\python.exe -m pytest tests -v` in PowerShell to confirm all 51 tests pass.

---

## 🖥️ 4. Presenter Environment & Window Hygiene

- [ ] **Window Framing & Scaling**:
  - Open the browser at 1080p (1920x1080) or 1440p (2560x1440) resolution.
  - Set browser zoom strictly to **100%**.
- [ ] **Clean Desktop**:
  - Close unrelated browser tabs, developer devtools (unless demonstrating network calls), and personal bookmarks bars.
  - Enable **Focus Assist / Do Not Disturb** in Windows to suppress desktop notifications.
- [ ] **Screenshots Captured Manually**:
  - If providing static slides or documentation, ensure screenshots were captured manually from the running application following [`docs/SCREENSHOT_CHECKLIST.md`](SCREENSHOT_CHECKLIST.md). Do not use mockups or synthetic graphics.

---

## ⚖️ 5. Scope & Disclosures Check

When presenting, ensure the following disclosures remain clear and visible:
- [ ] **No Amazon Affiliation**: Rehearsal is an independent open-source evaluation workbench. It is not affiliated with or endorsed by Amazon Alexa or Alexa+.
- [ ] **Deterministic Fixture Scope**: The 18 evaluation cases are deterministic offline fixtures; **high accuracy on fixtures does not prove real-world accuracy** across acoustic noise, regional accents, or open-ended user requests.
- [ ] **Heuristic Metric Scope**: Lint scores are rule-based heuristic calculations assessing input schema depth, parameter budgets, and spoken TTS output formatting.
