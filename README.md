# Aviation Quote Intelligence Assistant

A learning project: a command-line assistant that imports supplier quotes, finds the cheapest eligible offer, and (later) answers questions with evidence from supplier documents, using existing models via Ollama. Later milestones grow it into an HTTP API with a bounded agent, an MCP server, Docker/cloud deployment with tested releases, evaluation, usage/cost measurement, and a portfolio demo. The 24-week calendar is in `learning/CURRICULUM.md`.

The main goal is to learn to write, debug, explain, and evaluate AI-powered business software independently. See `docs/PROJECT_BRIEF.md` for the full brief.

## Layout

```
quote_assistant/   application package: main.py (rules + CLI), database.py + schema.sql,
                   extraction.py, model.py (model adapter), api.py (HTTP), config.py
scripts/           helper tools: api_client.py, summarize.py
experiments/       lesson practice that is not app code (e.g. 12.1 Hugging Face)
tests/  evals/  data/  docs/  learning/
```

Run everything from the project root as modules (`python -m quote_assistant.main`,
`uvicorn quote_assistant.api:app`, `python -m evals.run_eval`).

## Current behavior

`quote_assistant/main.py` asks for a part number and prints every matching quote from `data/sample_quotes.csv`, or a single "No quotes found" message.

## Setup

```bash
uv venv --python 3.12
source .venv/bin/activate
python -m quote_assistant.main
```

```bash
uv pip install -r requirements.txt   # packages added so far; later stages add more
```

External packages are added by stage and recorded in `requirements.txt`. `quote_assistant/model.py` holds the first model experiments (the brief calls it `model_practice.py`).

## Evals and model comparison

Run evals as a module from the project root, so `config` and `model` import:

```bash
python -m evals.run_eval --runs 3                                  # default model from .env.linux / .env.mac
python -m evals.run_eval --model qwen3.6:35b --runs 3 --warmup     # another local model; skip load time
python -m evals.run_eval --model claude-opus-5-5 --runs 1          # hosted; needs ANTHROPIC_API_KEY
python -m evals.run_eval --cases E01 --timeout 1                   # simulate a timeout
```

Results go to `evals/results/`. The comparison write-up is `docs/MODEL_COMPARISON.md`.

## Configuration

`quote_assistant/config.py` loads `.env.linux` or `.env.mac` (see `.env.example`): `MODEL_HOST`, `MODEL`.
The hosted provider reads `ANTHROPIC_API_KEY` from the environment. Never put it in code or git.

## Tests

```bash
python -m pytest tests
```

## Data

- `data/sample_quotes.csv`: five fictional supplier quotes
- `data/expected_results.json`: ten checked comparison cases (T01–T10) and the business rules they encode

## Learning workflow (Claude Code)

- `/lesson` starts or resumes the current lesson (`learning/CURRICULUM.md`, `learning/PROGRESS.md`)
- `/checkpoint` verifies a lesson and records progress
- `/hint`, `/debug`, `/test`, `/read`, `/explain`, `/learn-review`, `/retrieve`, … are tutoring workflows from Manware's AI Learning Toolkit

Claude acts as a tutor and the learner writes the implementation. Say "ship this" to get direct help.
