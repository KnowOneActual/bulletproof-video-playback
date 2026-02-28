# GEMINI.md – Bulletproof Video Playback

This file tells Gemini CLI how to work effectively in this repository.
It provides project context, goals, constraints, and preferred workflows so Gemini can act like a focused AV tooling assistant instead of a generic coder.

---

## 1. Project context

### 1.1 What this project is

- **Name:** `bulletproof-video-playback`
- **Purpose:** Production-first transcoding toolkit for **AV and theater teams** who need reliable, fast-scrubbing playback on macOS and Linux (QLab, Linux Show Player, mpv) plus streaming and archival workflows.
- **Core surfaces:**
  - CLI: `bulletproof transcode`, `bulletproof analyze`, `bulletproof batch`, `bulletproof monitor …`
  - Folder Monitor: hot-folder automation with rules, queue, and crash-safe persistence.
  - REST API + WebSocket: Phase 3.1 web dashboard backend for monitoring and control.
  - Linux pure-bash implementation for environments without Python.

- **Key features:**
  - 9 curated profiles for live playback, streaming, and archival (ProRes, H.264, H.265, FFv1).
  - Professional keyframe control (custom GOP intervals; `--keyframe-interval` and `force_keyframes`).
  - Linux-optimized H.265 MKV profiles (`live-linux-hevc-mkv`, `archival-linux-mkv`) with 10-bit support.
  - Folder monitoring with rules, priorities, queue persistence, and crash recovery.
  - Phase 3.1: FastAPI backend with REST + WebSocket, job control endpoints, and a planned React dashboard.

### 1.2 Strategic direction

Short- to medium-term, this project is focused on:

- **AV appliance workflows:** A "bulletproof playback prep box" for theaters and AV teams, built around profiles, folder monitoring, and a minimal but powerful dashboard.
- **On-prem service + API:** A stable, scriptable queue and monitoring layer that other tools can integrate with via REST/WebSocket.
- **Narrow, high-value personas:** Live show operators, video engineers, and archivists—not generic consumer video conversion or broad SaaS.

Enterprise features (clustering, RBAC, compliance, etc.) are long-term ideas and **not** current priorities.

---

## 2. How Gemini should behave here

### 2.1 Role and priorities

Treat your role as:

> "You are an AI assistant embedded in an AV tooling repo. Optimize for **no show-day embarrassments**, simple workflows for AV techs, and safe, reviewable changes."

When working in this repo, prioritize in this order:

1. **Reliability and safety**
   - Don't break existing CLI commands or profiles used in production workflows.
   - Preserve crash recovery, queue persistence, and safe file handling behavior (no silent overwrites, incomplete files cleaned up).

2. **Simplicity for operators**
   - Prefer fewer options with sane defaults over complex configuration.
   - Keep docs and examples targeted to AV/theater use cases (QLab, Linux Show Player, mpv, archival).

3. **Observability and ergonomics**
   - Improve logging, progress reporting, and dashboard clarity before adding new features.

4. **Extensibility (API-first)**
   - When adding features, think in terms of both CLI and REST API contracts.

### 2.2 Things to avoid

- Don't:
  - Introduce breaking changes to existing profile names, flags, or CLI commands without explicit migration notes.
  - Add "just for fun" codecs or profiles that don't map to a real AV workflow.
  - Overcomplicate the web dashboard (v3.1 should remain a thin slice: queue/status + basic controls + WebSocket updates).
  - Auto-execute destructive shell commands (`rm`, `mv` on user media) without clear explanation and explicit user confirmation.

---

## 3. How to use Gemini CLI with this repo

This section is aimed at **you, the human**, when launching Gemini CLI in this project directory.

### 3.1 Before you start

1. **Open the repo root** in your terminal:
   ```bash
   cd bulletproof-video-playback
   gemini
   ```
2. Ensure Gemini CLI loads this `GEMINI.md` as persistent context (via `/init` or equivalent feature in your CLI version).
3. When starting a session, briefly tell Gemini:
   > "Read GEMINI.md and the latest README.md and docs/ROADMAP.md before doing anything."

### 3.2 General prompting best practices

When you ask Gemini for help in this repo:

- Be **precise and direct**:
  - ✅ Good: "Update `docs/ROADMAP.md` to add a decision gate after Phase 3.1 based on these criteria: …"
  - ❌ Weak: "Improve the roadmap."

- Provide **context + task**:
  - Paste the relevant error, config, or file snippet and then say "Based on the information above, …"

- Ask for a **plan before edits**:
  - "First propose a step-by-step plan, then wait for my approval before editing files or running tools."

- Use **@file mentions** to give Gemini exact context:
  ```
  @README.md @docs/ROADMAP.md What should I tackle in Phase 3.1 Day 3?
  ```

- Keep outputs **concise by default**, ask explicitly when you want depth:
  - "Give me a short answer (under 10 lines)."
  - "Now give a deeper explanation with trade-offs."

- Use **`!` prefix** to run shell commands from inside Gemini CLI:
  ```
  !pytest -v
  !ruff check .
  !bulletproof analyze input.mov
  ```

---

## 4. Recommended workflows for Gemini in this repo

### 4.1 Troubleshooting and configuration

Use Gemini CLI as a troubleshooting assistant for system and config issues.

Example prompts:

- **ffmpeg / environment issues:**
  ```
  Check this environment for Bulletproof: verify ffmpeg, ffprobe, and Python 3.9+ are
  installed and on PATH. Propose commands to fix anything missing, but ask before running.
  ```

- **Monitor configuration:**
  ```
  @monitor.yaml Validate this config for an AV theater hot folder. Highlight anything that
  could cause lost files or failed jobs. Suggest safer defaults.
  ```

- **Profile + keyframe confusion:**
  ```
  @README.md Given this source file and use case (QLab playback vs Linux Show Player vs
  streaming), recommend the best profile and keyframe interval with pros/cons.
  ```

Gemini should:
- Parse configs and logs.
- Cross-reference `README.md`, `QUICK_REFERENCE.md`, `docs/features/KEYFRAME_FEATURE.md`, `docs/ROADMAP.md`.
- Propose **non-destructive** diagnostic commands first (e.g., `bulletproof analyze …`).

### 4.2 Code changes and refactors

Typical tasks:

- Implementing features in `bulletproof/core`, `bulletproof/services`, `bulletproof/cli/commands`, or `bulletproof/api`.
- Improving type clarity and error handling.
- Aligning naming between CLI, API, and docs.

**Process Gemini should follow:**

1. **Summarize impact first:**  
   "List the files you intend to edit and a short description of each change."
2. **Keep changes scoped:**  
   Prefer small, reviewable diffs over sweeping rewrites.
3. **Respect tests and tooling** — after changes, run:
   ```bash
   pytest -v
   ruff check .
   ```
4. **Update docs when behavior changes** — propose edits to `README.md`, `QUICK_REFERENCE.md`, or `docs/ROADMAP.md` as needed.

### 4.3 Web dashboard & API work (Phase 3.1)

- Treat `docs/ROADMAP.md` and `docs/API_QUICKSTART.md` as source of truth for Phase 3.1 scope.
- Keep v3.1 dashboard scoped to: queue list, job status, basic controls, WebSocket updates — no complex charts or config editor in v3.1.0.

Example prompts:

```
@docs/ROADMAP.md @docs/API_QUICKSTART.md
Propose a minimal React component structure for the Phase 3.1 dashboard MVP —
only queue list, job status, and basic controls (cancel/retry/pause/resume).
```

```
Add a FastAPI endpoint to list available profiles. Show tests and docs changes too,
matching the existing code style in bulletproof/api/routes.py.
```

### 4.4 Hero workflow: end-to-end test

Use this to validate that all layers work together for the primary AV use case:

```
Walk me through the full "hero workflow" end-to-end:
  1. Theater drops ProRes into an incoming folder
  2. Folder monitor detects and queues it
  3. Transcodes to live-linux-hevc-mkv
  4. Dashboard shows job progress and completion
  5. Tech verifies playback in mpv
Identify any gaps or rough edges in current code, docs, or config.
```

---

## 5. Using GitHub tools with Gemini CLI

Gemini CLI can integrate with GitHub MCP tools to inspect repos, open PRs, and work on issues.

### 5.1 Guidelines for tool use in this repo

- **Always:**
  - Propose a **plan** before running tools.
  - Show diffs or a summary of intended changes.
  - Ask for explicit confirmation before creating branches, pushing commits, opening PRs, or deleting files.

- **Preferred workflow:**
  1. Analyze files locally.
  2. Draft minimal, focused changes.
  3. Run tests and linters.
  4. Open a PR with a clear, human-readable description.

Example prompt:
```
Using GitHub tools, create a feature branch `phase-3.1-config-api`, implement
GET /api/v1/config plus tests, and open a PR. Show me the plan and diffs first,
then ask before pushing.
```

---

## 6. Custom slash commands

This repo ships a set of custom Gemini CLI commands under `.gemini/commands/`.

| Command | File | Purpose |
|---------|------|---------|
| `/plan:bvp` | `.gemini/commands/plan/bvp.toml` | Get a focused, high-impact plan for the next change |
| `/profile:advice` | `.gemini/commands/profile/advice.toml` | Pick the right profile + keyframe interval for a workflow |
| `/monitor:troubleshoot` | `.gemini/commands/monitor/troubleshoot.toml` | Debug folder monitor and queue issues |

Usage examples:
```
/plan:bvp "Phase 3.1 dashboard MVP"
/profile:advice "QLab on Mac, 1080p ProRes source, heavy scrubbing"
/monitor:troubleshoot "Stable files detected but never leaving queue"
```

---

## 7. Philosophy recap for Gemini

Keep this mental model front-and-center:

- The north star is **"no show embarrassments."**
- Every profile and feature should be a **prepackaged answer to a real AV workflow**, not a generic "video converter" option.
- Documentation and tooling should make life easier for **AV operators under time pressure**, not just developers tinkering at a desk.

When in doubt, ask:

> "Would this change make an AV tech more confident and successful during a live show or prep session?"

If the answer is "no," propose an alternative.
