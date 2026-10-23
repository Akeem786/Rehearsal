# Rehearsal — 3-Minute Hackathon Presentation Script

**Presentation Format:** 3-Minute Live Technical Walkthrough  
**Target Audience:** Hackathon Judges, MCP Engineers, and Conversational AI Reviewers  
**Live URL:** `http://127.0.0.1:5173/`  
**Backend Endpoint:** `http://127.0.0.1:8000/api/health`

---

## 🎙️ Spoken Presentation Script

### [0:00 – 0:35] 1. The Problem: The Voice Trap in Model Context Protocol
*(Action: Open `http://127.0.0.1:5173/` to the Overview page. Let the IDE testing workbench header and benchmark pill settle on screen.)*

> "Hi everyone. Model Context Protocol—MCP—has rapidly become the open standard for connecting LLMs to external tools and APIs. But almost every MCP tool built today is designed for visual chat clients: tools that expect complex nested JSON objects as inputs, and return multi-kilobyte JSON payloads, raw Markdown tables, or URLs as outputs.
>
> In a text window, that works fine. But when an agent speaks those responses through Text-to-Speech—on a smart speaker, in a car, or through a hands-free voice assistant—it causes immediate conversational breakdown. Users can’t speak deeply nested parameters in a single breath, and listening to raw JSON or 200-word flight tables causes acute ear fatigue.
>
> We built **Rehearsal**: an independent, open-source testing workbench designed specifically to evaluate and benchmark MCP tools for voice readiness."

---

### [0:35 – 1:15] 2. The Reference Server & Flawed vs. Corrected Benchmark
*(Action: Point to the 3-column benchmark grid on the Overview page, then click the Smart Home IoT card to expand the Active Inspector Telemetry.)*

> "To demonstrate this problem concretely, Rehearsal includes an official Python MCP SDK reference server with six paired tools across three common domains: Weather Services, Smart Home IoT, and Flight Booking.
>
> Each domain implements a visual chatbot anti-pattern paired against a voice-optimized alternative:
> - In **Weather**, the flawed tool requires nested geodetic coordinates ($defs/NestedCoord) and dumps raw telemetry; our voice-first tool accepts a simple city name and returns a concise, 25-word spoken summary.
> - In **Smart Home**, the flawed tool expects low-level 16-bit register masks and hex GUIDs (`0x4A9F`); the voice-first tool maps directly to natural spoken device names and rooms.
> - And in **Travel**, we replace a 200-word global flight matrix with two clear spoken options and a voice confirmation prompt.
>
> On the Compare screen, our benchmark quantifies this architectural shift: lifting the average voice-readiness score from a **60.0 baseline to 100.0**, a net gain of **+40 points**."

---

### [1:15 – 1:55] 3. Static Analysis: The Voice-Readiness Linter
*(Action: Click `Voice Linter` in the left sidebar. Select `Flawed Only (3)` and click `Run Linter`.)*

> "Before executing a tool at runtime, developers need static analysis. Rehearsal provides a dedicated Voice Linter evaluating five conversational design rules:
> - **RULE-001**: Schema Nesting Depth—restricting parameter depth to ensure voice entities can be extracted directly.
> - **RULE-002**: Required Argument Budget—limiting required inputs to what a user can naturally say in one turn.
> - **RULE-003**: TTS Hostility—detecting unparsed Markdown, URLs, and raw JSON that sound terrible when read aloud.
> - **RULE-004 & RULE-005**: Parameter Ergonomics and Description Clarity.
>
> When we scan the flawed tools, the linter identifies 9 distinct issues, providing line-level evidence and concrete remediation recommendations. Scanning our voice-first tools confirms zero findings and a clean 100/100 score."

---

### [1:55 – 2:35] 4. Runtime Evaluation: Natural Utterances & TTS Playback
*(Action: Click `Evaluation Runner` in the left sidebar. Ensure `Live MCP Execution` is checked, and click `Run Test Suite`.)*

> "Static linting is only half the battle. We also need to test how tools handle casual, natural human speech.
>
> In the Evaluation Runner, Rehearsal evaluates **18 deterministic test fixtures**. Notice what happens when we execute: Rehearsal connects in-memory to the live reference MCP server using the official MCP Python client connector.
>
> Across all 18 cases, Rehearsal evaluates:
> - **Tool Selection Accuracy**: verifying whether casual phrases like *'turn off the kitchen lights'* correctly route to the right tool.
> - **Exact Argument Matching & Slot F1**: extracting entity parameters without non-deterministic LLM variance.
> - **Speech Duration Estimation**: calculated at 150 words per minute to measure conversational brevity.
>
> We can click the **Listen** button on any case to hear the browser's speech synthesis speak the concise response aloud."

---

### [2:35 – 3:00] 5. Verifiable Persistence, Scope & Future Work
*(Action: Click `Run History` in the left sidebar. Click `Inspect` on the top run, and show the Export JSON button.)*

> "Every evaluation is automatically recorded in a local SQLite audit trail. Teams can inspect full telemetry and export the report as a verifiable JSON artifact for CI/CD gating.
>
> Finally, two important technical disclosures:
> 1. Rehearsal is an **independent open-source project**—it is not an official Amazon product and has no Amazon Alexa or Alexa+ affiliation.
> 2. Our 18 deterministic fixtures evaluate offline baseline logic; **they do not prove real-world accuracy** across acoustic background noise or regional accents.
>
> Our next steps include adding acoustic latency profiling under simulated weak network conditions and testing against noisy ASR transcripts.
>
> Rehearsal gives developers the tooling they need to build MCP tools that don't just look good in chat, but sound great aloud. Thank you!"

---

## ⏱️ Timing & Transition Milestones

| Timestamp | Screen / Route | Core Message |
| :---: | :--- | :--- |
| **0:00 – 0:35** | `Overview` | The problem: visual MCP tools cause ear fatigue and fail in voice turn-taking. |
| **0:35 – 1:15** | `Overview` ➔ `Compare` | The 6 reference tools, 3 domains, and the 60.0 to 100.0 (+40 pt) benchmark lift. |
| **1:15 – 1:55** | `Voice Linter` | Static analysis: 5 heuristic rules (`RULE-001` through `RULE-005`), evidence, and remediation. |
| **1:55 – 2:35** | `Evaluation Runner` | Runtime execution: 18 fixtures, live MCP connector, slot F1, speech duration, and TTS playback. |
| **2:35 – 3:00** | `Run History` | SQLite persistence, verifiable JSON export, independent disclaimer, and future work. |
