# Curriculum — Aviation Quote Intelligence Assistant

Lessons follow the milestones in `docs/PROJECT_BRIEF.md`. Each lesson is small: you write the code, Claude tutors. A lesson is done when its **Done when** evidence exists and you can explain it without help (`/checkpoint`).

Use `/lesson` to start or resume the current lesson. Suggested commands are listed per lesson.

Test cases T01–T10 refer to `data/expected_results.json`.

## 24-week calendar

Suggested pace from the 24-week study plan (brief reference S25): 8–10 hours a week. Lesson numbers are identifiers; this table gives the suggested order. Where the calendar schedules a topic earlier than its milestone number (the API in week 4, Hugging Face/PyTorch in week 8, DeepEval in week 12, LangChain in week 16), follow the calendar if the functions it depends on already work.

| Weeks | Suggested dates | Lessons | Checkpoint |
| --- | --- | --- | --- |
| 1–4 | 2026-11-23 to 2026-12-20 | 1.2–1.7, 3.1–3.3, 5 | TRAIN-PN-001, OH, USD, OUTRIGHT: 1 unit → Q002, 2 units → Q001, 3 units → no eligible quote; all 10 cases pass |
| 5–8 | 2026-12-21 to 2027-01-17 | 2.3–2.4, 4.1, 4.2, 4.4, 12.1 | A price with no currency stays unknown and is flagged before ranking |
| 9–12 | 2027-01-18 to 2027-02-14 | 4.3, 6, 8 | For a wrong answer, show whether search or generation failed, with before/after counts |
| 13–16 | 2027-02-15 to 2027-03-14 | 7.1–7.4 | Walk one trace: who picked the tool, who authorized it, why the run stopped |
| 17–20 | 2027-03-15 to 2027-04-11 | 9, 10.1, 10.2, 11 | Cost of one successful result, p95 latency, and a rollback that keeps the quotes |
| 21–24 | 2027-04-12 to 2027-05-09 | 13.1–13.4, 12.2 | Five-minute walkthrough without notes |

Weekly split: 2 hours studying, 4–6 hours building, 1 hour testing a failure, 1 hour explaining the result. Save one short build note each week.

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
- **Learn:** system instructions vs. supplied quote text, a short role prompt (the broker and their vocabulary), examples, conversation history, tokens and context windows, output limits, temperature and sampling, prompt versions; reproducibility.
- **Exercise:** keep the extraction instructions separate from the quote text; run the same case with one changed instruction or setting and record model, settings, and outcome. Read a fictional email from a file, summarize it in three sentences, and check the figures against the source; optionally try translation or action-item extraction on the same email.
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
- **Exercise:** `database.py` that loads the CSV and answers the same comparison request in SQL. Make the import safe to rerun.
- **Done when:** all 10 tests pass with SQL as the backend, and running the import twice stores each quote once.
- **Commands:** `/hint`, `/learn-review`, `/test`

### 3.3 Grow the schema
- **Learn:** joins, foreign keys, grouping, indexes; when to add a suppliers table. Practice resource: SQLBolt.
- **Done when:** you write a grouping query (e.g. cheapest per condition) without help, explain a join, and show with SQL why a cheaper offer was excluded.
- **Commands:** `/retrieve`, `/explain`

---

## Milestone 4 — Quote extraction pipeline (`extraction.py`, `evals/`)

### 4.1 Checked extraction examples
- **Exercise:** write 5–10 invented quote texts with hand-checked expected fields in `evals/`; keep some held out.
- **Done when:** the dataset includes missing-field and tricky cases (EXCHANGE, EUR, ambiguous condition, two line items, a core charge separate from unit price). Grow the held-out set toward 20 fictional emails before 4.4.

### 4.2 Extract → validate → store with source
- **Exercise:** extraction feeds validated records into SQLite with source references; unknown fields stay unknown. Save the supporting phrase or line for each critical field; route missing or conflicting prices to human review instead of ranking them.
- **Done when:** you report field-level accuracy on your dataset, and a message with a price but no currency keeps the price, shows the original phrase, and is flagged before ranking.
- **Commands:** `/arch`, `/debug`, `/learn-review`

### 4.3 Text-based PDFs
- **Learn:** `pypdf`, page references, why scanned PDFs need OCR.
- **Done when:** a PDF quote goes through the same pipeline with its page number recorded.

### 4.4 Model comparison (local and hosted)
- **Learn:** comparing models on the same checked examples; latency, usage, and cost; one hosted SDK (`openai` or `anthropic`), keys in environment variables, streaming, usage counts, rate limits, timeouts, capped retries.
- **Exercise:** run the 4.1 examples on two local models and one hosted provider (two local models is enough while offline); simulate a timeout; write `docs/MODEL_COMPARISON.md` with per-field exact matches, unknowns, latency, and cost or local runtime on the held-out emails.
- **Done when:** you justify a model choice with measured quality, speed, and cost, and explain one wrong answer and the smallest change that helped.
- **Commands:** `/api`, `/explore`

---

## Milestone 5 — HTTP API service (`api.py`)
- **Learn:** HTTP methods, endpoints, headers, JSON bodies, status codes, authentication; client vs. server responsibilities. `httpx` or `curl` to inspect requests; `fastapi` + `uvicorn` to serve.
- **Exercise:** inspect a raw Ollama request with `httpx`; then expose quote search and cheapest-offer lookup as validated endpoints that call the *same* functions as the CLI. Call them with `httpx` and with `curl`.
- **Done when:** an HTTP request returns the same result as the CLI for T02 and T07, an empty search returns a clear no-match result, and a rejected quantity gets a clear error status.
- **Commands:** `/api`, `/arch`, `/test`

---

## Milestone 6 — Document retrieval with evidence (`retrieval.py`, `data/documents/`)
- **Learn:** chunking, a keyword-search baseline, embeddings (same model for docs and queries), cosine similarity, top-k search, Qdrant local mode, metadata filters (by supplier), source references (supplier, document version, page, original text), conflicting policies, insufficient-evidence answers.
- **Exercise:** index a few invented supplier policies with different return terms; build a keyword search first, then embedding search in Qdrant, and compare which finds the right return clause. Answer "what do this supplier's documents say about returns?" for two suppliers with cited passages, then ask about an unmentioned fee. Flag a scanned page with no extractable text for OCR or review. Reimport a document and show its passages are not duplicated.
- **Done when:** you can show a retrieval failure vs. a generation failure and explain the difference, and the app says the documents do not say when evidence is missing.
- **Commands:** `/api`, `/explore`, `/debug`

---

## Milestone 7 — Tools, agents, and MCP (`tools.py`, `agent.py`, `mcp_server.py`)

### 7.1 Direct tool calling
- **Learn:** tool definitions, argument validation, allow-lists, returning results to the model.
- **Exercise:** expose `find_cheapest_eligible_quote` (and one lookup) to the model; reject unknown tools/bad arguments.
- **Done when:** the model answers a natural-language request using your function, and you can show where business rules run.
- **Commands:** `/api`, `/arch`, `/test`

### 7.2 Bounded agent workflow
- **Learn:** tool loops, state, observations, step limits, a time limit, stopping conditions and a recorded stopping reason.
- **Exercise:** an agent that looks up eligible offers, retrieves supplier terms, and returns a supported answer within a step limit (three tool calls for this exercise). Both tools are read-only.
- **Done when:** you show a run that answers with evidence and one that stops cleanly after repeated or invalid requests.
- **Commands:** `/arch`, `/debug`

### 7.3 MCP server
- **Learn:** MCP host, client, and server responsibilities; tools vs. resources; tool discovery, input schemas, error responses; MCP standardizes the connection, not the workflow logic.
- **Exercise:** expose the quote lookup through a small `mcp` server and call it from a compatible client; the result matches the CLI. Optional: sketch (no build) the video's GitHub pull-request and Slack-notification tools and list the permissions each would need.
- **Done when:** you can explain what the server does, what the client does, and where validation happens.
- **Commands:** `/api`, `/explain`

### 7.4 Fixed workflow vs. agent; prompt-injection test
- **Learn:** when a fixed lookup-then-search flow beats an agent; comparing correctness, tool calls, latency, and ease of debugging; why document text is evidence, not instructions; who picks a tool vs. who authorizes it.
- **Exercise:** run the same cases through a fixed workflow and the 7.2 agent (optionally rebuild one path in LangChain, see 12.2). Add a fictional document that asks the app to ignore its task and record how the app keeps document text separate from tool permissions.
- **Done when:** you choose which version to ship and justify it with results, and you walk one trace from question to citation: who picked the tool, who authorized it, which arguments were accepted, why the run stopped.
- **Commands:** `/explore`, `/arch`, `/debug`

---

## Milestone 8 — Evaluation (`evaluate.py`)
- **Learn:** reference answers, scoring, regression checks, latency, comparing runs with recorded prompt/model/settings versions; then `deepeval` metrics and evaluator configuration/cost.
- **Exercise:** one command runs business-rule, extraction, and retrieval checks and writes a report; add one DeepEval metric alongside the exact checks (for example, flag an invented return fee). Label ten answerable questions with the correct passage plus two with no answer, held apart from the examples used for tuning. Count top-three retrieval hits, supported citations, and correctly declined questions; ask each question three times to check consistency; compare the results with a human review.
- **Done when:** you can show what improved, what got worse, which examples still fail, and why a model-based score doesn't replace exact field checks. For one wrong answer, you show whether the correct passage reached the prompt before changing anything.
- **Commands:** `/test`, `/explore`, `/learn-review`

---

## Milestone 9 — Docker (`Dockerfile`, `.dockerignore`)
- **Learn:** images vs. containers, build context, configuration via environment, networking, persistent volumes, health checks.
- **Learn (added):** ports, secrets, a health endpoint; the API and the inference endpoint as separate services.
- **Exercise:** containerize the API; keep quote data and model files outside the image; reach Ollama from inside the container. Start from a clean checkout, import a synthetic quote, restart the container.
- **Done when:** the container passes the API checks, quotes persist across a restart, and you can explain why `localhost` inside the container is not the host.
- **Commands:** `/explain`, `/debug`

---

## Milestone 10 — Cloud deployment and releases (`docs/DEPLOYMENT.md`)

### 10.1 Deploy one small cloud demo
- **Learn:** compute, identity, networking, storage, logs, budgets, deployment lifecycle. AWS first: EC2 compute, IAM permissions, network access, persistent disk, object storage, logs, AWS Budgets. Map the same concepts to Google Cloud (conceptual comparison).
- **Exercise:** set a budget alert before creating anything. Deploy the practice API on a single instance with persistent SQLite, authenticated access, and an explicitly chosen, reachable inference endpoint; use synthetic inputs. Document config, storage, health check, costs, and rollback. Then remove the demo resources.
- **Done when:** a remote request works, the demo resources are removed afterward, and you can explain where the app runs, where the model runs, and how to roll back.
- **Commands:** `/arch`, `/explain`

### 10.2 Release checks and recovery (`.github/workflows/`)
- **Learn:** continuous integration with GitHub Actions, versioned releases, backups and restore, rollback, queues and concurrency; why a retry must not import the same quote twice.
- **Exercise:** run the `unittest` suite in GitHub Actions before a release. Restore the database from a backup, roll back a bad version, and retest one quote. Sketch (no build) how a queue could protect a single GPU under simultaneous requests.
- **Done when:** a failing test blocks a release, a rollback preserves the quotes, and you can explain what the queue would protect and what it would cost in latency.
- **Commands:** `/arch`, `/debug`, `/explain`

---

## Milestone 11 — Telemetry and cost control
- **Learn:** product events vs. evaluation, request failures, p95 latency, token usage, provider charges, local GPU time, budgets, model routing; `posthog` (or Amplitude via `amplitude-analytics`; choose one).
- **Exercise:** record searches, no-match results, extraction outcomes, and durations using synthetic data; keep raw quote text out of analytics. Compare a low-cost model with a stronger one on ambiguous inputs and route by measured quality and cost; add a request or token cap; show one recoverable failure.
- **Done when:** you can answer "how is it used, how often does it fail, what does it cost" from your own measurements: name the slowest step, state the p95 latency, and give the cost per successful result with local GPU time metered separately.
- **Commands:** `/arch`, `/explore`

---

## Milestone 12 — Ecosystem modules and demonstration

### 12.1 Run a model directly (calendar: week 8)
- **Learn:** Hugging Face model cards, licensing, hardware requirements, tokenizers, `transformers`; PyTorch tensors, device placement, GPU memory, inference; training vs. running a model.
- **Exercise:** run a small pretrained model directly and inspect its tokens and tensors.
- **Done when:** you can explain what the model card told you before you downloaded anything, and the difference between training and inference.
- **Commands:** `/api`, `/explore`

### 12.2 LangChain comparison and demonstration (calendar: week 16 and weeks 21–24)
- **Learn:** LangChain abstractions compared to your plain-Python workflow.
- **Exercise:** rebuild one working workflow in LangChain and compare (pairs with 7.4); prepare the repository and a concise demo.
- **Done when:** README documents a reproducible demo with source evidence and evaluation results, and you can explain the design and its cost/quality tradeoffs.
- **Commands:** `/explore`, `/learn-review`

---

## Milestone 13 — Portfolio and interviews

### 13.1 Test whether the assistant helps a broker
- **Learn:** defining success in business terms; manual vs. assisted review; observing a user without steering them.
- **Exercise:** have a broker or peer review the same small batch of fictional quotes manually and with the app. Count corrections and time; note where they hesitate; record one failure.
- **Done when:** you report the actual sample size, time, and accuracy for each approach, even if the app is slower.
- **Commands:** `/explore`, `/autopsy`

### 13.2 Package a reproducible portfolio project
- **Learn:** README, architecture diagram, setup and limitations, presenting evaluation results; fictional data only in anything public.
- **Exercise:** record a three-minute demo with one success and one failure; have a second person follow the setup instructions; publish a sanitized GitHub example or share a private demo with permission.
- **Done when:** the second person gets the demo running from the README alone.
- **Commands:** `/learn-review`, `/explain`

### 13.3 Coding and system-design interview practice
- **Learn:** Python lists, dictionaries, sets, runtime complexity, and SQL joins without assistance; rehearsing RAG, tool calling, queues, and cost; one design tradeoff and one incident.
- **Exercise:** a timed SQL join, a Python debugging task, and a mock design interview: handle ten simultaneous uploads, or replace the model without breaking clients.
- **Done when:** you give the five-minute walkthrough without notes (request, winning quote, cited policy, one measured failure, the fix), write the eligibility rule from memory, and describe recovery if the provider or database is unavailable.
- **Commands:** `/explain`, `/retrieve`, `/arch`

### 13.4 Get visible and apply
- **Learn:** reading postings for Applied AI Engineer, AI Engineer, and LLM Application Engineer; matching each required skill to a specific piece of your work.
- **Exercise:** write a résumé bullet using a real measurement; share a short build result on LinkedIn; attend a meetup or conference; ask for feedback or a referral; submit a first batch of tailored applications.
- **Done when:** each skill in three real postings maps to evidence in the repository or is listed as a gap.

Portfolio checklist (keep ready): a business decision (Q001 at USD 2,500.00, and why the USD 700.00 exchange quote and USD 1,100.00 one-unit quote do not qualify); a traced answer with document, page, and passage; measurements (test-set size, exact field accuracy, top-three hits, supported citations, p95 latency, cost per successful request); one engineering choice with its log or trace.

---

## After the first portfolio project (optional)

Not lessons yet. Pick from evidence after Milestone 13; see the brief's section of the same name.

- Own a live system: a small pilot across several releases, with a backup restore and one reliability-versus-cost decision explained to a nontechnical stakeholder.
- Model depth when error analysis justifies it: labeled data, train/dev/test splits, fine-tuning, overfitting.
- Systems depth: batching, caching, concurrency, model serving under load.
- Broaden: apply the same skills to VoiceDoc-AI; the video's optional capstones (a small language model from scratch, or several coordinated agents).
