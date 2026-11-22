# Progress

Status of each lesson in `learning/CURRICULUM.md`. Update through `/checkpoint` — mark a lesson done only with evidence.

Legend: `[x]` done · `[~]` in progress · `[ ]` not started

**Current lesson:** 1.7 — Consolidate

## Milestone 0 — Workstation setup
- [x] 0.1 Environment on this Linux machine — 2026-11-12: `.venv` created with uv on Python 3.12.16 (set up by Claude on request; system `python3` is 3.14, so activate the venv). Review: explain why the two interpreters differ.

## Milestone 1 — Business rules in plain Python
- [x] 1.1 Read your own program — *evidence from brief:* CSV reading with `DictReader`, named fields, int quantity, display, exact part search, found-flag no-match message; manual checks: 4 matches for TRAIN-PN-001, 1 for TRAIN-PN-002, no-match for TRAIN-PN-003. Debugging exercise established loop vs. after-loop meaning of `found == False`.
- [x] 1.2 Functions that return values — 2026-11-22: `load_quotes` returns typed rows (int qty, Decimal price); `Path(__file__)` locates the CSV; command-line output unchanged (4/1/no-match); imported from a shell without `input` running; explained the `__name__` guard and script-relative vs folder-relative paths.
- [x] 1.3 Filter by part number (T01, T10) — 2026-11-22: `filter_by_part_number` returns IDs in CSV order; T01, T10, small-match and case-sensitivity cases pass; explained the loop-order source and the effect of `return` inside the loop.
- [x] 1.4 Eligibility rules — 2026-11-22: `find_eligible` matches T03/T04/T05/T06/T08/T09; invalid qty (0, -1, '2') raises ValueError, validated once before the loop. Checkpoint: predicted SV/EXCHANGE case, explained bool-as-int, solved "either sale basis" by running twice.
- [x] 1.5 Money and the cheapest offer — 2026-11-22: `find_cheapest_eligible_quote` matches T02–T09 exactly; prices and totals quantized to two-decimal strings (1100.5 → "1100.50"); tie-break by (price, quote_id). Checkpoint: explained why T07 can't catch the key-order bug, float vs Decimal, transfer to line-total + max-stock tie-break (needed hint on negation/request in key).
- [x] 1.6 Automate the ten checks — 2026-11-22: tests/test_quotes.py runs T01–T10 as separate tests via run_case (17 total, OK); predicted and observed that >= → > fails exactly T02/T03; read -/+/? diffs. Checkpoint: string money catches '2500.0' (Decimal equality wouldn't); setUpClass vs setUp and shared-data risk; T11 expected correct but missed adding the case to the JSON contract first. Suite scaffold largely externally generated; learner fixed it and explained it.
- [ ] 1.7 Consolidate

## Milestone 2 — First model API experiment
- [x] 2.1 Reach the model service — 2026-11-12: `model.py` sends one chat request to `qwen3.5:9b` via the ollama client to `localhost:11434`; identified `message.content` vs `thinking`, ns durations, token counts (`eval_count` includes thinking). Checkpoint: predicted connection error with server off; explained remote host change (`Client(host=...)`/`OLLAMA_HOST`, bind 0.0.0.0); log `model`, verify content against source.
- [x] 2.2 Structured extraction — 2026-11-21: Enum-constrained Quote with Decimal price; showed valid-but-wrong (SV for "Inspected/Tested"; 0.00 price on 1 of 3 runs); explained schema checks shape, not truth vs source.
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
- [ ] 7.4 Fixed workflow vs. agent; prompt-injection test

## Milestone 8 — Evaluation
- [ ] 8 Evaluation

## Milestone 9 — Docker
- [ ] 9 Docker

## Milestone 10 — Cloud deployment and releases
- [ ] 10.1 Deploy one small cloud demo (AWS first)
- [ ] 10.2 Release checks and recovery (GitHub Actions, backup, rollback)

## Milestone 11 — Telemetry and cost control
- [ ] 11 Telemetry and cost

## Milestone 12 — Ecosystem modules and demonstration
- [ ] 12.1 Run a model directly (Hugging Face, PyTorch)
- [ ] 12.2 LangChain comparison and demonstration

## Milestone 13 — Portfolio and interviews
- [ ] 13.1 Test whether the assistant helps a broker
- [ ] 13.2 Package a reproducible portfolio project
- [ ] 13.3 Coding and system-design interview practice
- [ ] 13.4 Get visible and apply

## Notes
- Decision 2026-11-12: `model.py` is the brief's `model_practice.py` (first model experiments).
- Decision 2026-11-12: brief expanded (API service, context/model selection, hosted providers, agents/MCP, Docker/cloud, DeepEval, PostHog, HF/PyTorch/LangChain). Milestones renumbered 5–12; no completed lessons affected.
- 2026-11-20: Working on a Mac with no Ollama installed (`ollama` not on PATH, nothing on :11434). LM Studio runs `qwen/qwen3-14b` at `localhost:1234` (OpenAI-compatible `/v1/*`). Undecided: install Ollama, use the Linux machine, or switch 2.x to LM Studio.
- Decision 2026-11-21: roadmap aligned with the 24-week study plan PDF (brief reference S25; suggested dates 2026-11-23 to 2027-05-09). Added lessons 7.4, 10.2, and Milestone 13; split 10 into 10.1/10.2 and 12 into 12.1/12.2; added curl, a keyword-search baseline, named AWS services, GitHub Actions, and Amplitude as a PostHog alternative. No completed lessons affected. The calendar in `CURRICULUM.md` gives the suggested order.
