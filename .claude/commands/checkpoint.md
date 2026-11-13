---
description: Verify a lesson's evidence, check understanding, and record progress.
---

# Checkpoint

Lesson to check: the current lesson in `learning/PROGRESS.md`, or the one named here: $ARGUMENTS

1. Read the lesson's **Done when** in `learning/CURRICULUM.md`.
2. Verify the evidence yourself where possible: read the learner's code, run the program or `python -m unittest` and compare against `data/expected_results.json`. Report exactly what passed and failed. Do not fix the code.
3. Ask two or three short questions, one at a time: predict an output, explain why a rule works, and one transfer question (a variation of the lesson's problem). Wait for committed answers.
4. Verdict: **done** or **not yet**, with the single most important gap if not yet.
5. If done, propose the edits and apply them after the learner confirms:
   - `learning/PROGRESS.md`: mark the lesson `[x]` with one line of evidence and today's date; set the next **Current lesson**.
   - `LEARNING_LOG.md`: one dated line for the milestone or decision.
   - `learning/concepts.md` / `mistakes.md` / `review.md`: only if something meaningful emerged (follow the learning-log rules in `CLAUDE.md`).
