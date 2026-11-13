---
description: Start or resume the current lesson from the project curriculum.
---

# Lesson

Read `learning/PROGRESS.md` to find the current lesson, then read that lesson in `learning/CURRICULUM.md`. If the learner named a lesson (e.g. `/lesson 1.4`), use that one instead: $ARGUMENTS

Look at the relevant project files (e.g. `main.py`, `data/expected_results.json`) so your questions are concrete, but do not paste or write the solution.

1. In two or three sentences, state the lesson goal, why it matters for the Aviation Quote Assistant, and the **Done when** evidence.
2. Ask what the learner already knows or has tried for this lesson, and one prediction question tied to the real data (e.g. "Which quote IDs are eligible for T03, and why?").
3. Continue using the tutoring workflow the lesson suggests (`hint`, `test`, `debug`, `read`, `explain`, `api`, `arch`, `explore`, `learn-review`), one focused question at a time. Follow the intervention ladder in `CLAUDE.md`. The learner writes the code.
4. Do not introduce concepts or packages from later milestones unless asked.
5. When the learner believes the lesson is done, suggest running `/checkpoint`.
