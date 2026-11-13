# Curriculum — Aviation Quote Intelligence Assistant

Lessons follow the milestones in `docs/PROJECT_BRIEF.md`. Each lesson is small: you write the code, Claude tutors. A lesson is done when its **Done when** evidence exists and you can explain it without help (`/checkpoint`).

Use `/lesson` to start or resume the current lesson. Suggested commands are listed per lesson.

Test cases T01–T10 refer to `data/expected_results.json`.

---

## Milestone 0 — Workstation setup

### 0.1 Recreate the environment on this machine
- **Learn:** what a virtual environment isolates; why `.venv` is in `.gitignore`; interpreter vs. project environment.
- **Exercise:** create a Python 3.12 `.venv` with uv, activate it, and prove which interpreter runs `main.py`.
- **Done when:** `python --version` inside the venv shows 3.12.x and you can explain why it differs from the system `python3`.
- **Commands:** `/hint`

---

## Milestone 1 — Business rules in plain Python

### 1.1 Read your own program
- **Learn:** `csv.DictReader`, row dictionaries, the found-flag pattern, loop vs. after-loop meaning.
- **Exercise:** trace `main.py` by hand for `TRAIN-PN-001` and `TRAIN-PN-003` before running it.
- **Done when:** your predicted output matches the real output, line for line.
- **Commands:** `/read main.py`, `/explain`

### 1.2 Functions that return values
- **Learn:** functions, parameters, return values vs. printing, `pathlib.Path`.
- **Exercise:** write `load_quotes(path)` that returns a list of quote dicts; keep input/printing in the CLI part.
- **Done when:** the CLI still behaves the same, and you can call `load_quotes` from a Python shell.
- **Commands:** `/hint`, `/learn-review`

### 1.3 Filter by part number
- **Learn:** list building, exact case-sensitive matching, returning IDs in CSV order.
- **Exercise:** `filter_by_part_number(quotes, part_number)` → list of matching quote IDs.
- **Done when:** T01 and T10 pass when checked by hand.
- **Commands:** `/test` (design cases first), `/hint`

### 1.4 Eligibility rules
- **Learn:** compound conditions, `int` conversion, validating a positive whole-number request quantity, why stock from separate quotes is not combined.
- **Exercise:** decide whether one quote is eligible for a request (part, quantity ≥ requested, condition, currency, sale basis).
- **Done when:** you can list the eligible quote IDs for T03, T04, T05, T06, T08, T09 and they match.
- **Commands:** `/test`, `/hint`, `/debug`

### 1.5 Money and the cheapest offer
- **Learn:** why `float` is wrong for money; `decimal.Decimal`; `min`/sorting with a key; tie-break by quote ID; line total = unit price × requested quantity; a clear `no_eligible_quote` result.
- **Exercise:** `find_cheapest_eligible_quote(quotes, request)` returning a result shaped like the JSON `expected` blocks.
- **Done when:** T02 and T07 match exactly, including two-decimal money strings.
- **Commands:** `/api` (on `decimal`), `/hint`, `/learn-review`

### 1.6 Automate the ten checks
- **Learn:** `unittest`, loading JSON fixtures, one test per case, reading a failure message.
- **Exercise:** `tests/test_quotes.py` runs all of T01–T10 from `expected_results.json`.
- **Done when:** `python -m unittest` shows 10 passing; you deliberately break a rule and see the right test fail.
- **Commands:** `/test`, `/debug`

### 1.7 Consolidate
- **Exercise:** explain the full data flow (CSV → dicts → filters → result) from memory; autopsy one real bug you hit.
- **Done when:** `/explain` assessment shows no missing core concept; a `learning/mistakes.md` entry exists if a meaningful bug occurred.
- **Commands:** `/explain`, `/autopsy`, `/retrieve`

---

## Milestone 2 — First model API experiment (`model.py`)
Can run in parallel with Milestone 1 after 1.2.

### 2.1 Reach the model service
- **Learn:** client vs. service, endpoints, `localhost` meaning, verifying a running Ollama server and an installed model.
- **Exercise:** send one ordinary chat request, print the response object and identify its parts.
- **Done when:** you can explain where the request went and which field holds the text.
- **Commands:** `/api` (Ollama client), `/hint`

### 2.2 Structured extraction from a synthetic quote
- **Learn:** JSON schema, structured outputs, `pydantic` models, the difference between *valid* and *correct*.
- **Exercise:** give a short invented quote text, request part number, quantity, condition, currency, price, sale basis; validate with Pydantic; compare field by field with the source.
- **Done when:** you show one case where output is valid but wrong (or explain how it could be).
- **Commands:** `/api` (pydantic), `/explain`

### 2.3 Failure handling
- **Learn:** connection errors, timeouts, invalid responses, missing values, bounded retries.
- **Exercise:** make each failure happen on purpose and handle it.
- **Done when:** you can predict what your program does when the server is off.
- **Commands:** `/debug`, `/autopsy`

### 2.4 Context and request settings
- **Learn:** system instructions vs. supplied quote text, conversation history, tokens and context windows, temperature, prompt versions; reproducibility.
- **Exercise:** keep the extraction instructions separate from the quote text; run the same case with one changed instruction or setting and record model, settings, and outcome.
- **Done when:** you can reproduce a result and explain what context or setting changed it.
- **Commands:** `/explore`, `/explain`

---

## Milestone 3 — SQLite storage (`schema.sql`, `database.py`)

### 3.1 Design the table
- **Learn:** tables, types, primary keys, constraints (`CHECK`, `NOT NULL`), money as integer minor units.
- **Exercise:** write `schema.sql` for quotes with supplier and source information.
- **Done when:** you defend each column type and constraint in an `/arch` interview.
- **Commands:** `/arch`, `/explore`

### 3.2 Load and query
- **Learn:** `sqlite3`, inserts, parameterized queries (and why string formatting is dangerous), `WHERE`, `ORDER BY`, `LIMIT`.
- **Exercise:** `database.py` that loads the CSV and answers the same comparison request in SQL.
- **Done when:** all 10 tests pass with SQL as the backend.
- **Commands:** `/hint`, `/learn-review`, `/test`

### 3.3 Grow the schema
- **Learn:** joins, grouping, indexes; when to add a suppliers table.
- **Done when:** you write a grouping query (e.g. cheapest per condition) without help.
- **Commands:** `/retrieve`, `/explain`

---

## Milestone 4 — Quote extraction pipeline (`extraction.py`, `evals/`)

### 4.1 Checked extraction examples
- **Exercise:** write 5–10 invented quote texts with hand-checked expected fields in `evals/`; keep some held out.
- **Done when:** the dataset includes missing-field and tricky cases (EXCHANGE, EUR, ambiguous condition).

### 4.2 Extract → validate → store with source
- **Exercise:** extraction feeds validated records into SQLite with source references; unknown fields stay unknown.
- **Done when:** you report field-level accuracy on your dataset.
- **Commands:** `/arch`, `/debug`, `/learn-review`

### 4.3 Text-based PDFs
- **Learn:** `pypdf`, page references, why scanned PDFs need OCR.
- **Done when:** a PDF quote goes through the same pipeline with its page number recorded.

### 4.4 Model comparison (local and hosted)
- **Learn:** comparing models on the same checked examples; latency, usage, and cost; one hosted SDK (`openai` or `anthropic`), credentials, rate limits.
- **Exercise:** run the 4.1 examples on two local models and one hosted provider; write `docs/MODEL_COMPARISON.md`.
- **Done when:** you justify a model choice with measured quality, speed, and cost.
- **Commands:** `/api`, `/explore`

---

## Milestone 5 — HTTP API service (`api.py`)
- **Learn:** HTTP methods, endpoints, headers, JSON bodies, status codes, authentication; client vs. server responsibilities. `httpx` to inspect requests; `fastapi` + `uvicorn` to serve.
- **Exercise:** inspect a raw Ollama request with `httpx`; then expose quote search and cheapest-offer lookup as validated endpoints that call the *same* functions as the CLI.
- **Done when:** an HTTP request returns the same result as the CLI for T02 and T07, and a bad request gets a clear error status.
- **Commands:** `/api`, `/arch`, `/test`

---

## Milestone 6 — Document retrieval with evidence (`retrieval.py`, `data/documents/`)
- **Learn:** chunking, embeddings (same model for docs and queries), Qdrant local mode, metadata filters, source references, insufficient-evidence answers.
- **Exercise:** index a few invented supplier policies; answer "what do this supplier's documents say about returns?" with cited passages.
- **Done when:** you can show a retrieval failure vs. a generation failure and explain the difference.
- **Commands:** `/api`, `/explore`, `/debug`

---

## Milestone 7 — Tools, agents, and MCP (`tools.py`, `agent.py`, `mcp_server.py`)

### 7.1 Direct tool calling
- **Learn:** tool definitions, argument validation, allow-lists, returning results to the model.
- **Exercise:** expose `find_cheapest_eligible_quote` (and one lookup) to the model; reject unknown tools/bad arguments.
- **Done when:** the model answers a natural-language request using your function, and you can show where business rules run.
- **Commands:** `/api`, `/arch`, `/test`

### 7.2 Bounded agent workflow
- **Learn:** tool loops, state, observations, step limits, stopping conditions.
- **Exercise:** an agent that looks up eligible offers, retrieves supplier terms, and returns a supported answer within a step limit.
- **Done when:** you show a run that stops correctly at its limit and one that answers with evidence.
- **Commands:** `/arch`, `/debug`

### 7.3 MCP server
- **Learn:** MCP client/server responsibilities, tools vs. resources; MCP standardizes the connection, not the workflow logic.
- **Exercise:** expose the quote lookup through a small `mcp` server and call it from a compatible client.
- **Done when:** you can explain what the server does, what the client does, and where validation happens.
- **Commands:** `/api`, `/explain`

---

## Milestone 8 — Evaluation (`evaluate.py`)
- **Learn:** reference answers, scoring, regression checks, latency, comparing runs with recorded prompt/model/settings versions; then `deepeval` metrics and evaluator configuration/cost.
- **Exercise:** one command runs business-rule, extraction, and retrieval checks and writes a report; add one DeepEval metric alongside the exact checks.
- **Done when:** you can show what improved, what got worse, which examples still fail, and why a model-based score doesn't replace exact field checks.
- **Commands:** `/test`, `/explore`, `/learn-review`

---

## Milestone 9 — Docker (`Dockerfile`, `.dockerignore`)
- **Learn:** images vs. containers, build context, configuration via environment, networking, persistent volumes, health checks.
- **Exercise:** containerize the API; keep quote data and model files outside the image; reach Ollama from inside the container.
- **Done when:** the container passes the API checks, and you can explain why `localhost` inside the container is not the host.
- **Commands:** `/explain`, `/debug`

---

## Milestone 10 — Cloud deployment (`docs/DEPLOYMENT.md`)
- **Learn:** compute, identity, networking, storage, logs, budgets, deployment lifecycle on AWS or Google Cloud (pick one hands-on, compare the other conceptually).
- **Exercise:** deploy the practice API with an explicitly chosen, reachable inference endpoint; document config, storage, health check, costs, and rollback.
- **Done when:** a remote request works and you can explain where the app runs, where the model runs, and how to roll back.
- **Commands:** `/arch`, `/explain`

---

## Milestone 11 — Telemetry and cost control
- **Learn:** product events vs. evaluation, request failures, latency, token usage, budgets, model routing; `posthog`.
- **Exercise:** record searches, no-match results, extraction outcomes, and durations using synthetic data; add request limits and a model-routing rule.
- **Done when:** you can answer "how is it used, how often does it fail, what does it cost" from your own measurements.
- **Commands:** `/arch`, `/explore`

---

## Milestone 12 — Ecosystem modules and demonstration
- **Learn:** Hugging Face model cards, licensing, tokenizers, `transformers`; PyTorch tensors and device placement; LangChain abstractions compared to your plain-Python workflow.
- **Exercise:** run a small pretrained model directly; rebuild one working workflow in LangChain and compare; prepare the repository and a concise demo.
- **Done when:** README documents a reproducible demo with source evidence and evaluation results, and you can explain the design and its cost/quality tradeoffs.
- **Commands:** `/explore`, `/learn-review`
