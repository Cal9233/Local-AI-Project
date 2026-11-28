# Progress

Status of each lesson in `learning/CURRICULUM.md`. Update through `/checkpoint` — mark a lesson done only with evidence.

Legend: `[x]` done · `[~]` in progress · `[ ]` not started

**Current lesson:** 4.3 — Text-based PDFs (calendar weeks 9–12: 4.3, 6, 8; 3.3 still deferred). Default model is `qwen3.6:35b` with prompt V3.

## Milestone 0 — Workstation setup
- [x] 0.1 Environment on this Linux machine — 2026-11-12: `.venv` created with uv on Python 3.12.16 (set up by Claude on request; system `python3` is 3.14, so activate the venv). Review: explain why the two interpreters differ.

## Milestone 1 — Business rules in plain Python
- [x] 1.1 Read your own program — *evidence from brief:* CSV reading with `DictReader`, named fields, int quantity, display, exact part search, found-flag no-match message; manual checks: 4 matches for TRAIN-PN-001, 1 for TRAIN-PN-002, no-match for TRAIN-PN-003. Debugging exercise established loop vs. after-loop meaning of `found == False`.
- [x] 1.2 Functions that return values — 2026-11-22: `load_quotes` returns typed rows (int qty, Decimal price); `Path(__file__)` locates the CSV; command-line output unchanged (4/1/no-match); imported from a shell without `input` running; explained the `__name__` guard and script-relative vs folder-relative paths.
- [x] 1.3 Filter by part number (T01, T10) — 2026-11-22: `filter_by_part_number` returns IDs in CSV order; T01, T10, small-match and case-sensitivity cases pass; explained the loop-order source and the effect of `return` inside the loop.
- [x] 1.4 Eligibility rules — 2026-11-22: `find_eligible` matches T03/T04/T05/T06/T08/T09; invalid qty (0, -1, '2') raises ValueError, validated once before the loop. Checkpoint: predicted SV/EXCHANGE case, explained bool-as-int, solved "either sale basis" by running twice.
- [x] 1.5 Money and the cheapest offer — 2026-11-22: `find_cheapest_eligible_quote` matches T02–T09 exactly; prices and totals quantized to two-decimal strings (1100.5 → "1100.50"); tie-break by (price, quote_id). Checkpoint: explained why T07 can't catch the key-order bug, float vs Decimal, transfer to line-total + max-stock tie-break (needed hint on negation/request in key).
- [x] 1.6 Automate the ten checks — 2026-11-22: tests/test_quotes.py runs T01–T10 as separate tests via run_case (17 total, OK); predicted and observed that >= → > fails exactly T02/T03; read -/+/? diffs. Checkpoint: string money catches '2500.0' (Decimal equality wouldn't); setUpClass vs setUp and shared-data risk; T11 expected correct but missed adding the case to the JSON contract first. Suite scaffold largely externally generated; learner fixed it and explained it.
- [x] 1.7 Consolidate — 2026-11-22: explained the CSV → typed rows → part filter → find_eligible → cheapest (price, quote_id) → two-decimal string pipeline from memory, plus why typing happens at load (str vs int TypeError; "10" >= "9" passes silently but is wrong); mistakes.md autopsy of the >= → > boundary bug (T02/T03); 17 tests pass. Checkpoint transfer: lead time "at most 10" → `<= 10`, tested at exactly 10.

## Milestone 2 — First model API experiment
- [x] 2.1 Reach the model service — 2026-11-12: `model.py` sends one chat request to `qwen3.5:9b` via the ollama client to `localhost:11434`; identified `message.content` vs `thinking`, ns durations, token counts (`eval_count` includes thinking). Checkpoint: predicted connection error with server off; explained remote host change (`Client(host=...)`/`OLLAMA_HOST`, bind 0.0.0.0); log `model`, verify content against source.
- [x] 2.2 Structured extraction — 2026-11-21: Enum-constrained Quote with Decimal price; showed valid-but-wrong (SV for "Inspected/Tested"; 0.00 price on 1 of 3 runs); explained schema checks shape, not truth vs source.
- [x] 2.3 Failure handling — 2026-11-22: predicted and confirmed server-off run (3 attempts, "Gave up", exit 1; server-on exit 0); found chat() outside try, finally→else NameError, exit-0-hides-failure, module chat() ignoring Client timeout; caught httpx.TimeoutException (pinned httpx==0.28.1). Retry loop written by Claude on request; learner explained for/else and sys.exit-in-loop. Not run: validation flag branch, timed run.
- [x] 2.4 Context and request settings — 2026-11-23: system prompt separate from quote (lms.Chat + add_user_message); condition SV 1/5 (no prompt) → 5/7 (role) → 4/4 (V1 rules), reproduced 2/2 by Claude; summary of sample_email.txt checked against 11 figures (missed condition, RFQ; "per unit" wrong); temperature 0.8→0.6 changed wording not facts. Checkpoint: predicted null for "As Removed"; gap: thought temperature = effort and that temp 0 would give the correct answer. Mac now on LM Studio (lmstudio SDK); retry loop originally Linux-only, since shared across Mac and Linux (PR #2).

## Milestone 3 — SQLite storage
- [x] 3.1 Design the table — 2026-11-23: `schema.sql` (id PK, `UNIQUE(quote_id, supplier)`, `typeof` + `> 0` checks, enum-style `IN` checks, file/row/created_at traceability, nullable `quote_date`); 9/9 accept/reject cases. Defended in `/arch`. Gap: predicted affinity text `'3'` rejected (fixed on retry); lead-time transfer needed the answer (`IS NULL OR ...`, `>= 0` boundary).
- [x] 3.2 Load and query — 2026-11-23: import done and rerun-safe (ON CONFLICT DO NOTHING, chosen over INSERT OR IGNORE after seeing it hide a CHECK failure); functions split out. 2026-11-24: `find_cheapest_sql` (two queries, option A: eligible list ORDER BY row_number, winner ORDER BY unit_price, quote_id LIMIT 1) written by Claude on request; matches T02 + no-match. Learner wrote `filter_by_part_number_sql` (matches T01/T10), debugging KeyError (requested_quantity), double fetchall, one-item tuple binding (12 bindings), `AND` vs `,` in SELECT. **Parked 2026-11-24** to start model work; resume before 4.2. Left: add ORDER BY row_number to filter; TestContractSQL subclass running T01–T10 on :memory:; show import twice stores each quote once. 2026-11-25: added ORDER BY row_number to filter; TestContract refactored (staticmethod class attrs + `source`); TestContractSQL (Claude-written on request) runs T01–T10 on `:memory:` + double-import test; 28/28 pass. Checkpoint: explained inherited tests/override, row_number vs quote_id, DO NOTHING hides corrections → DO UPDATE.
- [ ] 3.3 Grow the schema — deferred 2026-11-24 (not needed for extraction)

## Milestone 4 — Quote extraction pipeline
- [x] 4.1 Checked extraction examples — 2026-11-26: 8 emails (6 dev / 2 held out) cover EXCHANGE, EUR, ambiguous condition, two line items, core charge, missing currency, lot total, no-offer; E06 hand-checked (4875.00). Grow held-out toward 20 before 4.4.
- [x] 4.2 Extract → validate → store with source — 2026-11-26: E05 stored in `review_quotes` with price 2750.00, phrase and `missing_currency`, never ranked; field accuracy qwen3.5:9b V2 ×3: dev 100% except condition 23/24, held-out 100%; TIMEOUT 30→60 (learner). Design by learner (separate review table, optional price, review before `unit_price`, rule by data not case ID); code written by Claude on request. Checkpoint: whitespace-normalized phrase match (corrected after reading), `condition_phrase` transfer, GBP → `unsupported_currency`.
- [ ] 4.3 Text-based PDFs
- [x] 4.4 Model comparison (local and hosted) — 2026-11-26: chose qwen3.6:35b (100% held-out on V3, 0 invented, ~5 s/email, local); compared 9b, Opus 5.5, Haiku 5.5 over 22 emails × 3 runs (`docs/MODEL_COMPARISON.md`). E18 (dropped "call for pricing" offer) fixed by one prompt rule tuned on dev twin E21. Learner wired `--model`, found the `python -m` import fix and the model-not-passed bug; remaining work done by Claude on request. Checkpoint: justified the choice (privacy, ~5 s); explained E18 with help; gap: proposed a schema change before writing a failing eval case.

## Milestone 5 — HTTP API service
- [x] 5 API service — 2026-11-27: GET /quotes and GET /cheapest (required query params) call main.py rules; T01–T10 match over HTTP via httpx (`api_client.py`) and curl; no-match → 200 (`no_match` / `no_eligible_quote`); qty 0/−1 → 400 with `str(e)`, abc/missing → 422; `tests/test_api.py`, 53 pass. Learner designed methods, status codes, layering; debugged `load_quotes` without `()`, unquoted dict keys, `str(e)`; final fixes + tests by Claude on request. Checkpoint: case-sensitive `oh` → 200 `no_eligible_quote`; single formatting rule → tests fail on drift; transfer `max_lead_time_days` (rule in main.py, 400 via api.py).

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
- [x] 12.1 Run a model directly (Hugging Face, PyTorch) — 2026-11-27: `experiments/hf_practice.py` tokenizes quote strings, input_ids [1,16] → logits [1,16,151936]; padding/attention mask explained; model card: Apache 2.0, ~0.5B params, ~1 GB, CPU-capable.
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
- Decision 2026-11-23: Mac uses LM Studio via the `lmstudio` SDK (pinned in requirements.txt), Linux uses Ollama; machine is picked by `.env.mac` / `.env.linux`. Resolves the 2026-11-20 note.
