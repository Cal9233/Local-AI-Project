# Progress

Status of each lesson in `learning/CURRICULUM.md`. Update through `/checkpoint` — mark a lesson done only with evidence.

Legend: `[x]` done · `[~]` in progress · `[ ]` not started

**Current lesson:** 2.2 — Structured extraction (Milestone 1 lessons 1.2–1.7 still open; skipped ahead by choice)

## Milestone 0 — Workstation setup
- [x] 0.1 Environment on this Linux machine — 2026-11-12: `.venv` created with uv on Python 3.12.16 (set up by Claude on request; system `python3` is 3.14, so activate the venv). Review: explain why the two interpreters differ.

## Milestone 1 — Business rules in plain Python
- [x] 1.1 Read your own program — *evidence from brief:* CSV reading with `DictReader`, named fields, int quantity, display, exact part search, found-flag no-match message; manual checks: 4 matches for TRAIN-PN-001, 1 for TRAIN-PN-002, no-match for TRAIN-PN-003. Debugging exercise established loop vs. after-loop meaning of `found == False`.
- [ ] 1.2 Functions that return values — `main.py` is still a single script.
- [ ] 1.3 Filter by part number (T01, T10)
- [ ] 1.4 Eligibility rules — requested-quantity filtering not yet demonstrated.
- [ ] 1.5 Money and the cheapest offer (T02, T07) — decimal pricing not yet demonstrated.
- [ ] 1.6 Automate the ten checks
- [ ] 1.7 Consolidate

## Milestone 2 — First model API experiment
- [x] 2.1 Reach the model service — 2026-11-12: `model.py` sends one chat request to `qwen3.5:9b` via the ollama client to `localhost:11434`; identified `message.content` vs `thinking`, ns durations, token counts (`eval_count` includes thinking). Checkpoint: predicted connection error with server off; explained remote host change (`Client(host=...)`/`OLLAMA_HOST`, bind 0.0.0.0); log `model`, verify content against source.
- [ ] 2.2 Structured extraction
- [ ] 2.3 Failure handling
- [ ] 2.4 Context and request settings

## Milestone 3 — SQLite storage
- [ ] 3.1 Design the table
- [ ] 3.2 Load and query
- [ ] 3.3 Grow the schema

## Milestone 4 — Quote extraction pipeline
- [ ] 4.1 Checked extraction examples
- [ ] 4.2 Extract → validate → store with source
- [ ] 4.3 Text-based PDFs
- [ ] 4.4 Model comparison (local and hosted)

## Milestone 5 — HTTP API service
- [ ] 5 API service

## Milestone 6 — Document retrieval with evidence
- [ ] 6 Retrieval

## Milestone 7 — Tools, agents, and MCP
- [ ] 7.1 Direct tool calling
- [ ] 7.2 Bounded agent workflow
- [ ] 7.3 MCP server

## Milestone 8 — Evaluation
- [ ] 8 Evaluation

## Milestone 9 — Docker
- [ ] 9 Docker

## Milestone 10 — Cloud deployment
- [ ] 10 Cloud deployment

## Milestone 11 — Telemetry and cost control
- [ ] 11 Telemetry and cost

## Milestone 12 — Ecosystem modules and demonstration
- [ ] 12 Ecosystem modules and demo

## Notes
- Decision 2026-11-12: `model.py` is the brief's `model_practice.py` (first model experiments).
- Decision 2026-11-12: brief expanded (API service, context/model selection, hosted providers, agents/MCP, Docker/cloud, DeepEval, PostHog, HF/PyTorch/LangChain). Milestones renumbered 5–12; no completed lessons affected.
