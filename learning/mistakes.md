# Mistakes

Record meaningful bugs or recurring misconceptions. Preserve the original reasoning.

## YYYY-MM-DD: Short title

- **Problem:**
- **Mistake:**
- **Original mental model:**
- **Correct mental model:**
- **Category:**
- **Prevention:**
- **Follow-up exercise:**
- 2026-11-21 Original: "valid schema doesn't prove correctness because validation isn't set up correctly." Corrected: even perfect validation can't detect a plausible wrong value (SV passed a correct Enum).
- 2026-11-22 Passed the folder path (`file_path`) to `load_quotes` instead of the CSV path, and left off the `.csv` extension. Lesson: name variables for what they hold.
- 2026-11-22 Original: the function would return True, then the whole quote dict, then case-insensitive matching. Corrected: the return value must match the contract (a list of `quote_id` strings), and matching is exact/case-sensitive per the rules. Lesson: re-read the contract before predicting outputs.
- 2026-11-22 Original: wrapped `raise ValueError` in a `try/except ValueError` in the same function (four tries, once with `finally: return`), so the caller never saw the error. Corrected: the function that finds the problem raises it; the caller decides whether to catch it. Claude applied the fix when asked; learner then explained it correctly.
- 2026-11-22 Wrote `quote["quantity"] <= requested` for the stock check: ran without error, logic backwards (Q002 accepted for T03). Lesson: plausible output isn't correct output — check against expected results.
- 2026-11-22 Confused selecting one item by index (`q_rows[1]`, `q_rows["unit_price"]`) with mapping over all items; also put `quote_id` before price in the `min` key. Corrected: indexing picks one element; a loop/comprehension transforms every element. The key function receives one item, `min` receives the whole list, and tuple order sets comparison priority.
