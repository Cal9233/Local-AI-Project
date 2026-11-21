# Aviation Quote Intelligence Assistant

Project and learning brief for the `Local-AI-Project` directory.

Progress below is based on the latest code and terminal output shared in this conversation. Proposed features and packages are identified separately from demonstrated work.

## Purpose and objectives

The main learning goal is to become able to write, debug, explain, and evaluate AI-powered business software independently. The project provides practical exercises in Python, SQL, model APIs, retrieval, and evaluation using aviation quotes as a familiar subject.

The software objective is an Aviation Quote Intelligence Assistant: an application that imports supplier quotes, stores their details, finds eligible offers, and answers questions using the quotes and supporting supplier documents.

The expanded learning plan develops the command-line application into a small API service, then adds agent integration, deployment, and operational measurements. Each extension reuses the quote rules and checked examples you wrote yourself.

The practical business goal is to reduce the work involved in reviewing quotes while keeping prices, quantities, conditions, currencies, and sale terms traceable to their sources. Its first audience is you as a learner and aviation broker.

The completed learning project should also provide evidence of your skills: understandable source code, a repeatable setup, a working demonstration, checked examples, and a record of defects you diagnosed and fixed.

The 24-week study plan adds a career objective: use the project as evidence for Applied AI Engineer, AI Engineer, and LLM Application Engineer roles. That means a demo another person can run, measured results, one failure you can explain, and interview practice in Python, SQL, and system design. [S25]

The study plan schedules the work across 24 weeks at 8 to 10 hours per week, with suggested dates from 2026-11-23 to 2027-05-09. The dates are a pacing guide. A lesson is complete only when its evidence exists.

The AI component will use existing models through APIs. Training a new foundation model is outside the planned learning scope.

## What you are trying to learn

| Area | Skills to practice | Evidence that you understand it |
| --- | --- | --- |
| Python | Variables, strings, integers, dictionaries, loops, conditions, indentation, functions, files, exceptions, and tests | Recreate the quote reader and filters yourself; explain their behavior and fix a bug |
| SQL | Tables, data types, keys, constraints, inserts, joins, filtering, grouping, indexes, and parameterized queries | Design a small quote database and write queries without an assistant |
| Model APIs | Requests, messages, responses, schemas, structured outputs, tool calling, timeouts, and bounded retries | Extract quote fields from text, validate them, and explain what happens when a request fails |
| Retrieval | Document extraction, chunking, embeddings, vector search, metadata filters, and source references | Find the relevant supplier passage and explain why a retrieved result supports an answer |
| Evaluation | Reference answers, automated scoring, error analysis, regression checks, latency, and repeatable comparisons | Show what improved after a change, what got worse, and which examples still fail |
| API architecture | HTTP methods, endpoints, JSON bodies, status codes, authentication, and client/server responsibilities | Explain and call an API, then expose your own quote lookup through an endpoint |
| Context and model selection | Instructions, evidence selection, history, token limits, request settings, and cost/quality comparisons | Reproduce an extraction result and explain what context or model choice changed it |
| Agents and MCP | Tool loops, argument validation, stopping conditions, and standardized tool connections | Complete a bounded quote-research task and expose a lookup through an MCP server |
| Deployment and cloud | Docker images and containers, configuration, persistent storage, networking, and AWS/GCP basics | Run the same app in a container and explain a deployment on one cloud provider |
| Operational measurement | Product events, request failures, p95 latency, token usage, provider charges, local GPU time, budgets, and model routing | Inspect how the app is used and state what one successful result costs |
| Release and recovery | Continuous integration, versioned releases, backups, restore, rollback, repeat-safe imports, queues, and concurrency | Tests run before a release; restore a backup and roll back a bad version without losing quotes |
| Safety and permissions | Keeping document text separate from instructions, read-only tools, tool authorization, and prompt-injection tests | Show a document that asks the app to ignore its task and explain why it gains no permissions |
| Supporting engineering | Virtual environments, dependency records, Git, readable modules, configuration, and documentation | Another person can understand and reproduce the project |
| Portfolio and interviews | README, architecture diagram, demo recording, user testing, timed Python and SQL practice, system design, and job-posting analysis | Give a five-minute walkthrough without notes and write a résumé bullet from a real measurement |

For learning, progress is measured by what you can implement and explain yourself. A small feature you understand is a useful milestone.

## Current progress

You are developing on your Mac in `/Users/cal/Local-AI-Project`.

| Item | Demonstrated status |
| --- | --- |
| Python environment | Created `.venv` with uv and activated it |
| Python interpreter | Confirmed Python 3.12.13 from the project's `.venv` |
| CSV reading | Imported `csv` and used `csv.DictReader` |
| Named fields | Accessed values through names such as `row['part_number']` |
| Quantity handling | Converted the CSV quantity to an integer for the availability display |
| Quote display | Printed the quote ID, part number, condition, quantity, currency, and price |
| Currency accuracy | Preserved USD and EUR from the source rows |
| Part-number search | Accepted a part number and displayed exact matches |
| No-match handling | Used a Boolean flag and checked it after the loop, producing one message |
| Manual checks | Demonstrated four matches for TRAIN-PN-001, one for TRAIN-PN-002, and one no-match message for TRAIN-PN-003 |

Your debugging exercise established an important control-flow distinction: inside the loop, `found == False` means a match has not been seen yet. After the loop, it means all rows were examined and no match was found.

The latest shared program has not yet demonstrated requested-quantity filtering, all eligibility filters, decimal price calculations, a database, model requests, document retrieval, or an automated evaluation runner. Those are upcoming milestones.

## What the finished application should do

1. Accept sample quote CSV files and quote text, with text-based PDF support added later.
2. Extract structured quote fields from unstructured text using a model.
3. Validate fields and preserve missing information explicitly.
4. Store accepted records with supplier and source information.
5. Accept a request containing part number, quantity, condition, currency, and sale basis.
6. Find the cheapest eligible offer using Python or SQL business rules.
7. Retrieve relevant terms from the selected supplier's supporting documents.
8. Present the result with its quote source and supporting document passages.
9. Run repeatable checks and report failures and performance.
10. Expose the existing lookup and extraction functions through a documented API.
11. Demonstrate a bounded agent workflow that combines quote lookup with document search.
12. Package the application with Docker and demonstrate deployment, useful telemetry, and cost controls.
13. Run its tests automatically before a release, and recover from a bad release or a repeated import without losing or duplicating stored quotes.
14. Treat supplier document text as evidence only. A document cannot change the task or the tool permissions.
15. Send missing or conflicting critical fields to human review, with the supporting phrase from the source.

Direct Hugging Face/PyTorch experiments and a LangChain comparison are additional learning modules. They provide experience with the wider ecosystem alongside the main application.

An example question for the finished app is: "Find an outright quote for two units of TRAIN-PN-001 in OH condition, priced in USD. Which eligible offer is cheapest, and what do that supplier's documents say about returns?"

In the existing synthetic dataset, Q001 is the eligible offer for those exact quote requirements: USD 1,250.00 per unit and a quoted line amount of USD 2,500.00. Supplier return terms require separate documents before the app can answer that part of the question.

## Responsibilities of each component

| Component | Responsibility in this project |
| --- | --- |
| Python application | Control the workflow, validate input, manage files, calculate values, and handle errors |
| SQL / SQLite | Store structured records and apply exact queries, eligibility filters, and ordering |
| Chat or instruction model | Extract information from quote text and produce explanations from supplied evidence |
| Tool-calling code | Validate a requested tool and its arguments, execute an allowed function, and return its result to the model |
| Embedding model | Create numeric representations used to compare document passages and questions |
| Vector store | Store and search those representations with document metadata |
| Evaluation code | Compare actual results with independently checked expected results |
| API service | Accept validated HTTP requests and call the same application functions used by the CLI |
| Agent workflow | Choose among allowed tools, use their results, and stop within defined limits |
| MCP server | Expose selected functions through a standard interface for compatible AI clients |
| Deployment and telemetry | Run the application consistently and measure requests, failures, usage, and resource costs |

Keep exact part-number matching, stock requirements, currency matching, sale basis, and arithmetic in application rules or SQL queries. Use model extraction and language generation around those rules.

Ollama provides structured-output and tool-calling interfaces. A JSON schema describes the expected response structure; Pydantic can validate types and constraints. Valid structure alone does not prove that extracted values match the source. [S4, S5, S6]

## Technologies and tools

| Technology | Why it belongs | When to use it |
| --- | --- | --- |
| Python 3.12 | Main implementation language | Already in use |
| uv | Create environments and install/manage dependencies | Already in use |
| `.venv` | Keep project packages separate | Already created |
| CSV and JSON | Learn file handling and represent sample data, requests, and expected results | Now |
| SQLite and SQL | Learn database design and exact querying | After the first comparison functions work |
| Ollama service | Run a selected existing model and expose an API | First model experiment can begin now |
| Chat/instruction model | Extract quote fields and use supported tools | Model stage |
| Embedding model | Support semantic document search | Retrieval stage |
| Qdrant local mode | Practice vector search with a local index | Retrieval stage |
| Keyword search baseline | Give embedding search a simple comparison point, written in plain Python | Retrieval stage, before Qdrant |
| curl | Send one HTTP request from the terminal and read the raw response | API stage, alongside HTTPX |
| Git | Record changes and practice reviewing differences | Alongside development |
| Your editor and terminal | Write, run, inspect, and debug the application | Throughout |

The Ollama service can run on your Mac or on your Ubuntu GPU workstation. The endpoint must be reachable from the machine running Python. Installing the Python client does not install or start the model service. A hostname of `localhost` refers to the machine running your Python process. Choose and verify the endpoint before the first request. [S3]

The current interface is a command-line program. A documented API is an upcoming learning milestone. A visual web interface can be a further extension after the core workflow and checks work.

## Expanded roadmap from the video

The linked Sajjaad Khader video and the creator's companion article broaden the roadmap beyond the initial foundation. [S11, S12] Python, SQL, model APIs, RAG, and evaluation were already part of this project; the modules below add depth and additional technologies.

The named ecosystems come from that roadmap and its companion write-up. The concrete exercises and learning order are adapted to the quote assistant. HTTPX, FastAPI, and Uvicorn are implementation choices for practicing API architecture, rather than claims that those three names were specified in the video.

These are planned learning modules. They do not mark any package as installed or any feature as completed.

| Topic or technology | What to learn | Quote-assistant exercise and timing |
| --- | --- | --- |
| HTTP and API architecture | Requests, responses, methods, headers, JSON, status codes, and authentication | Inspect a model request, then expose a quote-search endpoint after the lookup becomes a reusable function |
| Context engineering | System instructions, supplied evidence, conversation history, context limits, and prompt versions | Keep extraction instructions separate from quote text; compare a prompt change against the same checked examples |
| Model selection and request settings | Tokens, context windows, temperature, model capabilities, latency, and cost | Compare two supported models on the same extraction cases and record the tradeoffs |
| OpenAI and Anthropic APIs | Hosted requests, credentials, errors, rate limits, streaming, and usage information | Repeat a synthetic extraction exercise with one hosted provider first; compare it with the local-model path [S13, S14] |
| Hugging Face | Model cards, licensing, model files, tokenizers, hardware requirements, and inference | Load and run a small compatible pretrained model in a separate experiment after basic API calls work [S15] |
| PyTorch | Tensors, device placement, and inference fundamentals | Inspect a small model's inputs and outputs; treat this as a later model-internals module [S15] |
| LangChain | Framework abstractions around model, tools, and context | Rebuild one already-working workflow as a comparison after you understand the plain Python version [S16] |
| AI agents | Repeated tool use, state, observations, step limits, and stopping conditions | Let a bounded workflow look up eligible offers, retrieve terms, and return a supported answer |
| MCP | Client/server responsibilities and standardized access to tools and resources | Expose the existing quote-lookup function through a small MCP server after direct tool calling works [S17] |
| Docker | Images, containers, configuration, networking, and persistent volumes | Containerize the API; keep persistent quote data and model files managed separately from the application image [S18] |
| AWS and Google Cloud | Compute, identity, networking, storage, logs, budgets, and deployment lifecycle | Learn both providers' basic concepts; choose one for the first hands-on deployment [S19, S20] |
| DeepEval | Evaluation cases, metrics, reference answers, and evaluator configuration | Add a correctness or evidence-support check after the deterministic comparison checks work [S21] |
| PostHog | Product events, usage analysis, errors, and request measurements | Measure searches, no-match results, extraction outcomes, and durations using synthetic practice data [S22] |
| Cost control and governance | Request limits, token usage, model routing, configuration, data access, and failure review | Track resource usage, choose a model based on measured needs, and demonstrate bounded request behavior |
| GitHub and project presentation | Change history, documentation, repeatable setup, and a concise demo | Prepare a repository and demonstrate a complete request with its source evidence and evaluation results |

A bounded agent exercise can use your existing lookup and retrieval functions. MCP provides a connection standard for tools; the workflow and stopping logic remain application responsibilities.

Docker is software installed outside the Python environment. AWS and Google Cloud are hosting platforms. Their deployment tools are separate from the packages imported by your application. Cloud access SDKs become relevant only when your code needs to call a specific cloud service.

The first cloud exercise should deploy the application with an explicitly chosen, reachable inference endpoint. The API container and a GPU model service can run on different machines; containerizing the app does not automatically provide model hosting or GPU access.

DeepEval adds model-output measurements alongside your exact field and business-rule checks. Configure the evaluator and record its model, settings, and request costs. Model-based scores complement checked examples and human review. PostHog records how the application is used; that usage information serves a different purpose from an accuracy test. [S21, S22]

## Additions from the 24-week study plan

The 24-week study plan follows the same video and article and adds a calendar and aviation exercises. [S25] Most of its technologies were already in this brief. The table below lists the tools, techniques, and practices that were missing. Week numbers refer to the calendar later in this brief.

Like the modules above, these are planned. Nothing here is marked as installed or completed.

| Topic or technology | What to learn | Quote-assistant exercise and timing |
| --- | --- | --- |
| curl | Sending a request from the terminal; reading the method, URL, headers, body, and status code | Call the quote API with curl and with HTTPX; show a valid winner, an empty search, and a rejected quantity (week 4) |
| Other model tasks | Summarization, translation, and action-item extraction using the same context design | Summarize one fictional email in three sentences, then check its figures against the source (week 5) |
| Evidence per field and human review | Saving the supporting phrase for each extracted field; sending missing or conflicting values to a person | Store the source phrase beside each field; add examples with two line items, an omitted field, and a core charge separate from unit price (week 6) |
| Held-out model comparison | Per-field exact matches, unknowns, latency, and cost or local runtime on examples the prompts never saw | Compare two extraction models on 20 held-out fictional emails and explain one wrong answer (week 8) |
| Keyword search baseline | Term matching as a comparison point; cosine similarity and top-k search for the embedding side | Build a keyword search first, then compare it with embedding search in Qdrant on the same return-clause questions (week 10) |
| Repeat-safe imports | Why running an import twice must store each record once | Rerun the quote import and the document import; show no duplicate quotes or passages (weeks 3, 9, and 19) |
| Retrieval test set | Labeled answerable and unanswerable questions, top-three hits, supported citations, declined questions, and repeat-run consistency | Label ten answerable questions and two with no answer; ask each three times; compare the counts with a human review (week 12) |
| Fixed workflow versus agent | Comparing correctness, tool calls, latency, and ease of debugging | Run the same cases through a lookup-then-search flow and the bounded agent; choose one to ship and justify it with results (week 16) |
| Prompt-injection testing | Keeping document text separate from instructions and tool permissions | Add a fictional document that asks the app to ignore its task; show that the tools and limits stay the same (week 16) |
| MCP permissions sketch (GitHub, Slack) | What access a pull-request tool or a Slack notification would need | Optional: sketch the video's GitHub pull request and Slack notification and list the permissions each needs; no build required (week 15) [S30] |
| AWS services | EC2 compute, IAM permissions, network access, persistent disk, object storage, logs, and AWS Budgets | Use AWS first: set a budget alert, deploy one instance with persistent SQLite and authenticated access, then remove the demo resources (week 18) [S31, S32] |
| GitHub Actions | Continuous integration: running the tests automatically for each change | Run the `unittest` suite before a release (week 19) [S33] |
| Releases, backups, and rollback | Versioned releases, backup and restore, and rolling back a bad version | Restore from a backup, roll back a bad version, and retest one quote; the quotes must survive (week 19) |
| Queues and concurrency | Why simultaneous requests need ordering when one GPU serves them | Sketch how a queue protects a single GPU; build it only if measurements call for it (week 19) |
| Amplitude | Product analytics; an alternative to PostHog | Choose PostHog or Amplitude, not both; keep raw quote text out of analytics (week 20) [S34, S35] |
| Operational metrics | Errors, p95 latency, tokens, provider charges, local GPU time, and cost per successful result | Name the slowest step, report p95 latency, and divide the run's cost by its successful results; meter local GPU time separately (week 20) |
| User testing | Defining success in business terms; manual review versus assisted review | Have a broker or peer review the same batch of fictional quotes both ways; report sample size, time, and accuracy even if the app is slower (week 21) |
| Portfolio packaging | README, architecture diagram, setup, limitations, and a demo recording | Record a three-minute demo with one success and one failure; have a second person follow the setup; publish only fictional data (week 22) |
| Interview practice | Python lists, dictionaries, sets, runtime complexity, SQL joins, and system design | Timed SQL join, Python debugging task, and a mock design interview on ten simultaneous uploads or a model swap (week 23) |
| Job search | Reading postings, matching each required skill to a piece of your work, and networking | Compare postings for three role titles; share a build result on LinkedIn; attend a meetup; submit tailored applications (week 24) |

curl and GitHub Actions are not Python packages. curl runs from the terminal, and GitHub Actions runs in the GitHub repository from a workflow file. Amplitude needs a package only if you choose it instead of PostHog.

The study plan names AWS as the first hands-on provider and Google Cloud as the conceptual comparison. Set the budget alert before creating any resource, and practice removing the demo resources afterward.

The plan lists study resources for each stage: the Python 3.12 tutorial, SQLBolt, the FastAPI tutorial, the Ollama quickstart, the hosted-provider quickstarts, the DeepEval quickstart, and Anthropic's article on workflows and agents. [S26-S30, S36, S37] The video's capstone repository and the DataCamp tracks and certification are optional. [S38, S39]

## Python modules already available

These standard-library modules are included with Python; import them when needed. [S1]

| Module | Planned use |
| --- | --- |
| `csv` | Read and write quote CSVs |
| `json` | Read expected results and serialize structured data |
| `decimal` | Calculate money using decimal arithmetic |
| `sqlite3` | Connect to SQLite and execute SQL |
| `pathlib` | Build file and directory paths |
| `unittest` | Automate checks of Python behavior |
| `os` | Read configuration from environment variables |
| `time` | Measure elapsed durations |
| `logging` | Record useful application events and errors |
| `datetime` | Handle dates when quote validity is added |

Do not list standard-library modules as external requirements.

## External Python packages to add by stage

| Package name to install | Name used in imports | Purpose | Stage |
| --- | --- | --- | --- |
| `ollama` | `ollama` | Send chat, tool, and embedding requests to Ollama | Model APIs |
| `pydantic` | `pydantic` | Define and validate quote/request/response schemas | Structured extraction |
| `pypdf` | `pypdf` | Extract text and page references from text-based PDFs | PDF ingestion |
| `qdrant-client` | `qdrant_client` | Store and search embeddings with metadata | Retrieval |
| `httpx` | `httpx` | Inspect and send HTTP requests directly | API foundations; project implementation choice |
| `fastapi` | `fastapi` | Expose existing functions through a typed HTTP API | API service; project implementation choice |
| `uvicorn` | `uvicorn` | Run the FastAPI application as an ASGI service | API service; project implementation choice |
| `openai` or `anthropic` | `openai` or `anthropic` | Use one hosted model provider's official SDK | Hosted API comparison; choose one first |
| `huggingface_hub` | `huggingface_hub` | Access model repositories and download selected files | Later local-model experiment |
| `transformers` | `transformers` | Load supported pretrained models and tokenizers | Later Hugging Face experiment |
| `torch` | `torch` | Tensor operations and a compatible model's inference backend | Later PyTorch/model-internals module |
| `langchain` | `langchain` | Compare framework-based orchestration with an understood workflow | Later framework comparison; provider integration packages chosen then |
| `mcp` | `mcp` | Implement an MCP server and client experiment | After direct tool calling |
| `deepeval` | `deepeval` | Organize model-output evaluations and metrics | After a working extraction or RAG baseline |
| `posthog` | `posthog` | Capture application events and measurements | Working API and deployment stage |
| `amplitude-analytics` | `amplitude` | Alternative to `posthog` for product analytics | Only if Amplitude is chosen instead of PostHog |

The currently demonstrated CSV and search features use the standard library. Installation of the listed external packages in the Mac project's environment has not been confirmed in the shared terminal output. This table is a staged learning inventory, not a single installation list. Check each module's current requirements when that exercise begins. [S3, S6, S7, S9, S13-S17, S21-S24, S34]

Add packages as their features are introduced. Inside the activated project environment, the staged installation commands are:

```bash
# At the model and validation stage
uv pip install ollama pydantic

# When adding PDF ingestion
uv pip install pypdf

# When adding document retrieval
uv pip install qdrant-client
```

Record project dependencies in `requirements.txt` as you introduce them, and record tested versions before sharing the project. With the current venv-based workflow, install recorded requirements using `uv pip install -r requirements.txt`. uv also supports resolving dependencies to pinned requirements for reproducibility. [S2]

Qdrant's local mode supports practice without a separate Qdrant server. [S7] Ollama can supply embeddings through an embedding model, and the same embedding model must be used for document and query vectors in a shared index. [S8]

Scanned PDFs need an OCR step because text extraction alone may return little or no text. Choose an OCR approach when those files become part of the exercise. [S9]

Evaluation begins with JSON fixtures, scoring functions, and `unittest`. DeepEval is a later learning module once an extraction or retrieval baseline exists. Keep deterministic tests of quantities, prices, currencies, and eligibility alongside model-based metrics.

## What models mean in this project

There are two AI model roles:

- A chat/instruction model reads quote text, produces structured fields, requests supported tools, and explains results.
- An embedding model turns text into vectors for document search.

A Pydantic model has a different role: it is a Python definition of expected data fields and validation rules.

The first model exercise belongs in a separate `model_practice.py`. Send one ordinary request and inspect the response. Then provide a short synthetic quote, request structured fields, compare them with the original text, and validate the result.

Practice connection errors, timeouts, invalid responses, missing values, and limited retries. Later, an optional hosted-provider exercise can introduce API keys, rate limits, token usage, and request costs.

Add context engineering and model comparison to that experiment: record instructions, supplied quote text, model identity, supported request settings, and measured outcomes. A hosted-provider comparison and a direct Hugging Face experiment can reuse the same synthetic examples.

## Quote comparison rules

The provided `expected_results.json` defines the initial exercise contract:

- Exact, case-sensitive matches for the already-normalized sample part numbers, conditions, currencies, and sale bases.
- CSV quantity represents available stock. A qualifying offer must have at least the requested positive whole-number quantity.
- One quote fulfills the entire request. Stock from separate quotes is not combined in this exercise.
- Rank only eligible quotes by numeric unit price. Break ties by quote ID.
- Compare the requested currency without exchange-rate conversion.
- Keep OUTRIGHT and EXCHANGE separate.
- Keep OH, SV, and NE as distinct condition labels.
- Calculate quoted line amount as unit price multiplied by requested quantity.
- Shipping, taxes, core deposits, and other unprovided fees are outside that line amount.
- Return a clear no-eligible-quote result when no offer qualifies.

Keep quantities numeric and availability labels as display text. Parse prices from decimal strings before calculations. When designing the database, choose a numeric representation that preserves money accurately; integer minor units are a suitable option for the sample USD/EUR prices.

Future requirements can add quote expiry, more currencies, duplicates, input normalization, and different fulfillment rules. Update their expected cases explicitly when changing the contract.

## Retrieval learning objective

Use a small set of supplier policies or catalog descriptions. Extract text, keep document/page metadata, split it into passages, create embeddings, and store the passages with their vectors. Search those passages for the user's question and provide the relevant evidence to the chat model.

Filter evidence to the relevant supplier or document collection. Preserve source references and provide an insufficient-evidence response when the documents cannot support an answer.

Use exact identifiers and SQL queries for quote records. Practice semantic retrieval on descriptive text and policies. Compare retrieval choices against known relevant passages.

## Evaluation and testing

Two starter files have been provided:

- `data/sample_quotes.csv`: five fictional supplier quotes.
- `data/expected_results.json`: ten checked cases covering basic part filtering and eligible-quote selection.

Those fixtures define deterministic comparison exercises. They do not yet evaluate model extraction or document retrieval. The latest shared program has demonstrated three manual searches, rather than an automated run of all ten cases.

Add independently checked quote-text examples for extraction and question/passage/answer examples for retrieval. Keep development examples separate from held-out examples, including near-duplicate documents. Keep versions of prompts, models, and retrieval settings with each experiment.

| Check | What to measure |
| --- | --- |
| Business-rule correctness | Correct eligible offers, winning quote, and quoted line amount |
| Extraction accuracy | Correct part number, quantity, condition, currency, price, and sale basis |
| Response validation | Valid structure and permitted values |
| Missing information | Whether the app preserves unknown fields and avoids inventing answers |
| Retrieval success | Whether a known supporting passage is returned among the selected results |
| Evidence support | Whether answer claims follow from the returned passages |
| Reliability and speed | Failed requests and elapsed time |
| Declined questions | Whether questions the documents cannot answer are declined |
| Consistency | Whether the same question asked three times gives the same answer |
| Cost | Cost per successful result, with local GPU time metered separately |
| Usefulness | Time and corrections for a manual review versus an assisted review of the same quotes |

Assess retrieval and generated answers separately so you can locate failures. Start with exact checks for structured fields and manually reviewed examples for answers. Review failures individually and rerun the same cases after changes. [S10]

The study plan sets sizes for the first test sets: 20 held-out fictional emails for the model comparison, and ten answerable plus two unanswerable questions for retrieval. When an answer is wrong, first check whether the correct passage reached the prompt. If it did not, change the search and rerun the same questions. If it did, inspect the answer and citation. Keep the before-and-after counts, including any result that got worse. [S25]

## Files to grow toward

This is a guide to add files as responsibilities emerge, rather than an instruction to create every file immediately.

| File or directory | Responsibility |
| --- | --- |
| `README.md` | Objective, setup, usage, and current behavior |
| `LEARNING_LOG.md` | Lessons, errors, decisions, and remaining questions |
| `main.py` | Command-line interaction and application entry point |
| `model_practice.py` | First independent API experiments |
| `api.py` | Later HTTP endpoints that reuse the core application functions |
| `schema.sql` | Database tables and constraints |
| `database.py` | Connections and parameterized database operations |
| `extraction.py` | Model requests and extraction validation |
| `tools.py` | Functions exposed through controlled tool calling |
| `agent.py` | Later bounded model/tool workflow |
| `mcp_server.py` | Later standardized access to selected tools |
| `retrieval.py` | Document indexing and search |
| `evaluate.py` | Run datasets and produce accuracy/failure reports |
| `tests/` | Automated checks of application behavior |
| `data/sample_quotes.csv` | Synthetic quote input |
| `data/expected_results.json` | Expected comparison results |
| `data/documents/` | Supporting supplier documents for practice |
| `evals/` | Extraction and retrieval datasets and reports |
| `requirements.txt` | External dependencies and tested versions |
| `Dockerfile` and `.dockerignore` | Later container build and build-context exclusions |
| `docs/DEPLOYMENT.md` | Later run, configuration, storage, health-check, and rollback instructions |
| `docs/MODEL_COMPARISON.md` | Inputs, model settings, quality measurements, latency, and usage comparisons |
| `.github/workflows/` | Later GitHub Actions workflow that runs the tests before a release |
| `.gitignore` | Exclude the environment and generated local data from Git |

As the program grows, move repeated logic into functions that return values. This makes the same rules usable from the command line, tests, and model tools.

## Suggested milestones

1. Complete requested-quantity filtering and the remaining eligibility rules. Convert prices correctly and select the cheapest eligible quote.
2. Begin the separate first model API experiment now, alongside Python practice. Verify the endpoint and learn context engineering, request settings, and failure handling.
3. Build SQL tables and queries; preserve existing comparison behavior while moving storage to SQLite.
4. Add quote-text extraction, schema validation, source tracking, and checked examples. Introduce PDFs after text inputs work. A hosted-provider comparison can reuse the same examples.
5. Build a small HTTP API with FastAPI and Uvicorn; use HTTPX or curl to inspect requests and responses.
6. Add document retrieval and answers with evidence, first using a pipeline whose individual steps you understand. Build a keyword search baseline before the embedding search.
7. Expose lookup functions through direct tool calling, then build a bounded agent workflow and an MCP server experiment. Compare the agent with a fixed workflow and test a document that tries to redirect the app.
8. Expand the evaluation runner with DeepEval while preserving exact business-rule and field checks. Continue measuring quality at every earlier stage too.
9. Package the working application using Docker, including configuration, persistent data, and a health check.
10. Deploy a practice version on AWS first, after setting a budget alert; document networking, the inference endpoint, storage, logs, costs, and rollback, then remove the demo resources. Map the same concepts to Google Cloud before doing another deployment. Then practice release checks and recovery: tests in GitHub Actions, a backup restore, and a rollback.
11. Add PostHog or Amplitude measurements and cost/resource controls, report p95 latency and cost per successful result, then use observed failures to extend the checked examples.
12. Complete the later Hugging Face/PyTorch and LangChain comparison modules, and prepare a documented demonstration with a clear account of the design and results.
13. Turn the project into career evidence: test it with a broker or peer, package the portfolio, practice coding and system-design interviews, and begin targeted applications.

Milestone numbers identify lessons. The 24-week calendar below gives the suggested order and pace. Early model API practice can run alongside the Python exercises. Add later infrastructure and framework modules when the functions they depend on are understood and working.

## 24-week calendar

The study plan groups the milestones into six four-week blocks. [S25] Dates are suggestions.

| Weeks | Suggested dates | Focus | Milestones | What you can show |
| --- | --- | --- | --- | --- |
| 1-4 | 2026-11-23 to 2026-12-20 | Python, SQL, and HTTP | 1, 3, 5 | Find the cheapest eligible offer and pass all 10 starter cases |
| 5-8 | 2026-12-21 to 2027-01-17 | Model APIs and context | 2, 4, and the Hugging Face/PyTorch part of 12 | Extract checked fields and compare two models on unseen examples |
| 9-12 | 2027-01-18 to 2027-02-14 | Retrieval and evaluation | PDF part of 4, then 6 and 8 | Answer a policy question with the right supplier, page, and passage |
| 13-16 | 2027-02-15 to 2027-03-14 | Tool calling, agents, and MCP | 7, and the LangChain part of 12 | Combine lookup and policy search in a workflow you can trace and stop |
| 17-20 | 2027-03-15 to 2027-04-11 | Deployment and operations | 9, 10, 11 | Deploy a demo, observe cost and failures, and recover from a bad release |
| 21-24 | 2027-04-12 to 2027-05-09 | Portfolio and interviews | 13, and the demonstration part of 12 | Give a working demo, defend a design decision, and start targeted applications |

The calendar schedules four topics earlier than their milestone numbers suggest: the HTTP API in week 4, the direct Hugging Face/PyTorch experiment in week 8, DeepEval in week 12, and the LangChain comparison in week 16. Follow the calendar's order when the functions a topic depends on already work. Otherwise finish the prerequisite lesson first.

Suggested weekly split: 2 hours studying, 4 to 6 hours building, 1 hour testing a failure, and 1 hour explaining the result. Write the first attempt yourself, ask for a hint when stuck, and save one short build note each week.

| Block | Checkpoint |
| --- | --- |
| Weeks 1-4 | For TRAIN-PN-001 in OH, USD, OUTRIGHT: one unit selects Q002 at USD 1,100.00; two select Q001 at USD 1,250.00 each; three return no eligible quote. Explain every rejection and pass all 10 cases |
| Weeks 5-8 | A message with a price and no currency keeps the price, shows the original phrase, and flags the missing currency before ranking |
| Weeks 9-12 | For a wrong answer, show whether the search or the answer failed, with before-and-after counts |
| Weeks 13-16 | Walk one trace from question to citation: who picked the tool, who authorized it, which arguments were accepted, and why the run stopped |
| Weeks 17-20 | Show what one successful result costs, the p95 latency, and a rollback that preserves the quotes |
| Weeks 21-24 | Give a five-minute walkthrough without notes |

## How learning success will be judged

You can explain the program's data flow, write and debug its Python and SQL logic, identify why a model result is wrong, distinguish a search failure from an answer-generation failure, and show measured results from checked examples.

The software can import a quote, preserve and validate its fields, store it, find an eligible offer, retrieve relevant evidence, and report results with sources. It handles unknown or missing information clearly and can be exercised repeatedly through automated checks.

For the expanded roadmap, you can also explain the API boundary, a bounded agent's tool choices, an MCP connection, the container's persistent data, and a deployment on one provider. You can distinguish evaluation quality from product usage and describe the measured cost/quality tradeoff of a model choice.

For the study plan's portfolio checklist, keep four pieces of evidence ready. [S25]

| Evidence | What to show |
| --- | --- |
| A business decision | Two units of TRAIN-PN-001, OH, OUTRIGHT, USD returns Q001 with a USD 2,500.00 line amount before fees. Show why the USD 700.00 exchange quote and the USD 1,100.00 one-unit quote do not qualify |
| A traced answer | The winning supplier's document, page, and supporting passage for a returns question, and how the app handles a question about an unmentioned fee |
| Measurements | Test-set size, exact field accuracy, top-three retrieval hits, supported citations, p95 latency, and cost per successful request, with one before-and-after comparison including its failures |
| An engineering choice | A timeout or a bad extraction: the log or trace, what the user saw, and the evidence that the fix worked. Explain why SQL handles money and why the model reads prose |

You can also write the eligibility rule from memory, explain your model choice, and describe how to recover if the provider or the database is unavailable.

The tutoring preference is to use plain explanations, small tasks, hints, and code review. You write the implementation. Full feature implementations should be supplied only when you explicitly request them. Sample data, expected results, documentation, and small explanatory examples support the learning process.

## After the first portfolio project

These are optional directions from the study plan. [S25] They start only after milestone 13.

- Own a live system: operate a small pilot across several releases, track user outcomes, investigate failures, restore a backup, and explain one reliability-versus-cost decision to a nontechnical stakeholder.
- Model depth, when your error analysis justifies it: labeled data, train/dev/test splits, fine-tuning, and overfitting.
- Systems depth: batching, caching, concurrency, and model serving under load.
- A second portfolio project: apply the same skills to VoiceDoc-AI.
- The video's optional capstones: build a small language model from scratch to study transformers and optimization, or coordinate several agents to plan, implement, and review one task. [S38]

Fine-tuning and a small from-scratch model are study exercises. Training a new foundation model stays outside the scope.

## Technical references

- [S1: Python standard library](https://docs.python.org/3.12/library/index.html)
- [S2: uv dependency declarations](https://docs.astral.sh/uv/pip/dependencies/) and [locking requirements](https://docs.astral.sh/uv/pip/compile/)
- [S3: Ollama Python client](https://github.com/ollama/ollama-python)
- [S4: Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs)
- [S5: Ollama tool calling](https://docs.ollama.com/capabilities/tool-calling)
- [S6: Pydantic validation](https://pydantic.dev/docs/validation/latest/get-started/)
- [S7: Qdrant Python client and local mode](https://github.com/qdrant/qdrant-client)
- [S8: Ollama embeddings](https://docs.ollama.com/capabilities/embeddings)
- [S9: pypdf text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
- [S10: Evaluating retrieval and answer quality](https://qdrant.tech/documentation/search-evaluation/pipeline-output-quality/)
- [S11: User-supplied video — How to Become a $300K AI Engineer in 2026](https://www.youtube.com/watch?v=E6lvgbayD04)
- [S12: Creator's companion article — The four-level stack behind a $300K AI engineer job](https://sajjaad.substack.com/p/the-four-level-stack-behind-a-300k)
- [S13: OpenAI SDKs](https://developers.openai.com/api/docs/libraries)
- [S14: Anthropic SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview)
- [S15: Hugging Face Transformers quickstart](https://huggingface.co/docs/transformers/en/quicktour)
- [S16: LangChain overview](https://docs.langchain.com/oss/python/langchain/overview)
- [S17: MCP overview](https://modelcontextprotocol.io/docs/getting-started/intro) and [official Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [S18: Docker getting started](https://docs.docker.com/get-started/)
- [S19: AWS EC2 concepts](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)
- [S20: Google Cloud overview](https://docs.cloud.google.com/docs/overview)
- [S21: DeepEval](https://github.com/confident-ai/deepeval)
- [S22: PostHog Python SDK](https://posthog.com/docs/libraries/python)
- [S23: HTTPX](https://www.python-httpx.org/)
- [S24: FastAPI, including its Uvicorn server integration](https://fastapi.tiangolo.com/)
- S25: Your AI engineering roadmap, a 24-week study plan for this project (PDF created 2026-11-21; suggested dates 2026-11-23 to 2027-05-09)
- [S26: Python 3.12 tutorial](https://docs.python.org/3.12/tutorial/)
- [S27: SQLBolt exercises](https://sqlbolt.com/)
- [S28: FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [S29: Ollama quickstart](https://docs.ollama.com/quickstart)
- [S30: Anthropic on workflows and agents](https://www.anthropic.com/research/building-effective-agents)
- [S31: AWS EC2 first instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html)
- [S32: AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [S33: GitHub Actions](https://docs.github.com/en/actions)
- [S34: Amplitude Python SDK](https://amplitude.com/docs/sdks/analytics/python)
- [S35: PostHog product analytics](https://posthog.com/docs/product-analytics)
- [S36: OpenAI quickstart](https://developers.openai.com/api/docs/quickstart) and [Anthropic quickstart](https://platform.claude.com/docs/en/get-started)
- [S37: DeepEval quickstart](https://deepeval.com/docs/getting-started)
- [S38: Capstone repository from the video](https://github.com/rohitg00/ai-engineering-from-scratch)
- S39: Optional DataCamp resources: [Python fundamentals](https://www.datacamp.com/tracks/python-programming-fundamentals), [SQL fundamentals](https://www.datacamp.com/tracks/sql-fundamentals), [Associate AI Engineer for Developers track](https://www.datacamp.com/tracks/associate-ai-engineer-for-developers), and [certification](https://www.datacamp.com/certification/ai-engineer-for-developers-associate)
