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
