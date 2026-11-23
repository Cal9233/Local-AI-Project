# Review

Keep short retrieval prompts or review metadata for meaningful topics.

## YYYY-MM-DD: Topic

- **Recall prompt:**
- **Last reviewed:**
- **Confidence:**
- **Next review or exercise:**

## 2026-11-12: Found-flag control flow

- **Recall prompt:** In the part-number search, what does `found == False` mean if checked *inside* the loop vs. *after* it? What goes wrong if the "No quotes found" message is printed inside the loop?
- **Last reviewed:** before 2026-11-12 (debugging exercise on the Mac)
- **Confidence:** medium
- **Next review or exercise:** predict the output of the search for TRAIN-PN-003 with the message moved into the loop.

## 2026-11-23: Temperature vs correctness

- **Recall prompt:** What does temperature control, and what doesn't it? With no system prompt at temperature 0, would `condition` be correct or only consistent? Where does a new allowed value like AR go first: prompt or schema?
- **Last reviewed:** 2026-11-23 (2.4 checkpoint; first answered "temperature = effort" and "maybe SV")
- **Confidence:** low
- **Next review or exercise:** run the no-prompt baseline at temperature 0 five times; predict the value first.
