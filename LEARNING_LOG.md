# Learning Log

Dated milestones, decisions, and open questions. Detailed entries live in `learning/` (`concepts.md`, `mistakes.md`, `questions.md`, `review.md`); lesson status is in `learning/PROGRESS.md`.

## Before 2026-11-12 (on the Mac)
- Created a `.venv` with uv on Python 3.12.13.
- Built the part-number search in `main.py` with `csv.DictReader`, int quantity, and a found-flag no-match message.
- Debugging lesson: inside the loop, `found == False` means "no match yet"; after the loop it means "no match in any row".

## 2026-11-12
- Moved the project to the Linux workstation. Added the brief (`docs/PROJECT_BRIEF.md`), the curriculum, and the Claude Code learning toolkit.
- Decision: business rules (matching, stock, currency, money) stay in Python/SQL. Models only extract and explain.
- Recreated `.venv` (Python 3.12.16); installed ollama + pydantic, recorded in `requirements.txt`. Decision: `model.py` is the model-practice file.
- Installed pypdf 7.0.1 and qdrant-client 1.20.0 early (on request); recorded in `requirements.txt`.
- Completed 2.1 (out of order): first Ollama chat request; can explain the request path and response fields. Decision: continue with 2.2 before finishing Milestone 1.

## 2026-11-21
- Completed 2.2: forced Enum makes the model choose a code instead of "unknown"; same input can give different values across runs. Decision: map conditions in Python with a lookup table; unknown → None + review flag, keep raw text.

## 2026-11-22
- Completed 1.2 (functions that return values); next: 1.3.
- Completed 1.3 (filter by part number); decided input cleanup stays out of the filter.
- Completed 1.4 (eligibility rules); decided invalid requests raise instead of returning False.
- Completed 1.5 (cheapest offer); decided to add `eligible_quotes()` returning rows rather than change `find_eligible`'s ID contract.
- Completed 1.6 (automated checks); decided one test method per contract case via a run_case helper rather than a subTest loop, so the count shows 10.
- Completed 1.7 (consolidate): Milestone 1 done; rule adopted — every comparison gets an equal-values test.
- Completed 2.3 (failure handling): model.py fails loudly with specific exceptions and bounded retries; decided validation errors get one retry and are flagged, never defaulted.
- Completed 2.4 (context and request settings): Milestone 2 done; decided Mac runs LM Studio via the lmstudio SDK and Linux runs Ollama; rule adopted — temperature for consistency, prompt/schema for correctness.

## 2026-11-23
- Completed 3.1 (design the table): first SQLite schema; learned SQLite type affinity differs from MySQL (`INTEGER` converts `'3'` before CHECK runs); decided `UNIQUE(quote_id, supplier)` because suppliers assign quote numbers.

## 2026-11-25
- Completed 3.2 (load and query): SQL backend passes the same contract as Python; learned that DO NOTHING silently drops supplier corrections.

## 2026-11-26
- Completed 4.1 (checked extraction examples): eval set of 8 fictional emails; learned that schema-valid ≠ correct (3.45 vs 3450.00) and that a held-out case used for tuning must move to dev and be replaced.
- Completed 4.2 (extract → validate → store): unrankable quotes go to `review_quotes` with source phrase; learned a phrase check proves text exists, not that it describes this record (E01 exchange unit got an invented OH and was ranked).
