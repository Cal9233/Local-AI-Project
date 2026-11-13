# Aviation Quote Intelligence Assistant

A learning project: a command-line assistant that imports supplier quotes, finds the cheapest eligible offer, and (later) answers questions with evidence from supplier documents, using existing models via Ollama. Later milestones grow it into an HTTP API with a bounded agent, an MCP server, Docker/cloud deployment, evaluation, and usage/cost measurement.

The main goal is to learn to write, debug, explain, and evaluate AI-powered business software independently. See `docs/PROJECT_BRIEF.md` for the full brief.

## Current behavior

`main.py` asks for a part number and prints every matching quote from `data/sample_quotes.csv`, or a single "No quotes found" message.

## Setup

```bash
uv venv --python 3.12
source .venv/bin/activate
python main.py
```

```bash
uv pip install -r requirements.txt   # packages added so far; later stages add more
```

External packages are added by stage and recorded in `requirements.txt`. `model.py` holds the first model experiments (the brief calls it `model_practice.py`).

## Data

- `data/sample_quotes.csv`: five fictional supplier quotes
- `data/expected_results.json`: ten checked comparison cases (T01–T10) and the business rules they encode

## Learning workflow (Claude Code)

- `/lesson` starts or resumes the current lesson (`learning/CURRICULUM.md`, `learning/PROGRESS.md`)
- `/checkpoint` verifies a lesson and records progress
- `/hint`, `/debug`, `/test`, `/read`, `/explain`, `/learn-review`, `/retrieve`, … are tutoring workflows from Manware's AI Learning Toolkit

Claude acts as a tutor and the learner writes the implementation. Say "ship this" to get direct help.
