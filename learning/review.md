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

## 2026-11-23: SQLite type affinity and optional-value CHECKs

- **Recall prompt:** Why does the text `'3'` pass `CHECK (typeof(quantity) = 'integer')` on an `INTEGER` column while `'abc'` fails? Write a `CHECK` for an optional, non-negative whole number (e.g. lead time in days).
- **Last reviewed:** 2026-11-23 (3.1 checkpoint; predicted `'3'` rejected, corrected on retry; lead-time CHECK needed the answer)
- **Confidence:** low
- **Next review or exercise:** predict, then test, inserts of NULL, 0, -1, '7', 'abc' against your own optional-column CHECK; test the exact boundary value first.

## 2026-11-26: Eval-first changes and whole-wrapper validation

- **Recall prompt:** What is the first step before changing a prompt for a new failure pattern? Why would `quantity: 0` lose every offer in that email, not just one?
- **Last reviewed:** 2026-11-26 (4.4 checkpoint; proposed a schema change first; predicted a record with quantity 0)
- **Confidence:** low
- **Next review or exercise:** write the loan-unit email as dev E23 with its expected result, predict the 35b output, run it, then decide whether any change is needed.

