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
