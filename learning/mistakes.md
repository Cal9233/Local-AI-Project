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
- 2026-11-22 Passed a Path to json.load (needs an open file object), then passed the JSON path to load_quotes (KeyError: 'quantity'). Lesson: know what each function expects to receive, and which file holds data vs answers.
- 2026-11-22 Copy-pasted ten methods all named test_T01: no error, but only the last survived (Ran 8 tests, T01 running 'T10'). Also used a list comprehension result as if it were the dict. Lesson: a repeated name silently overwrites the earlier one; always check the test count.

## 2026-11-22 — Stock check boundary (Lesson 1.6)

- **Symptom:** Changing `>=` to `>` in the stock check made T02 and T03 fail; the other 8 cases passed.
- **My original explanation:** I assumed a quote with exactly the requested stock couldn't fill the order.
- **Corrected understanding:** Exact stock fills the request, so `qty_available >= requested_qty` is correct.
  T02/T03 caught it because they request exactly the available stock: the boundary.
  The other cases are clearly above or below, so `>` and `>=` agree on them.
- **Rule going forward:** Every comparison rule needs a test where both sides are equal.

## 2026-11-22 — Timeout never applied (Lesson 2.3)

- **Symptom:** Created `Client(timeout=30)` but the request still had no timeout; no error was raised.
- **My original explanation:** None recorded; the bug went unnoticed until code review.
- **Corrected understanding:** The call used module-level `chat()`, which has its own default client with no timeout; only `client.chat()` uses the configured one. Found by reading the code, confirmed with `timeout=0.5` raising `httpx.ReadTimeout`.
- **Rule going forward:** An unused variable or import is a hint that the wiring is wrong.

## 2026-11-23 — System prompt silently dropped (Lesson 2.4)

- **Symptom:** With the role prompt "added", the run still returned `condition: NE`; no error.
- **My original explanation:** Assumed the prompt was being sent and asked whether the code was correct.
- **Corrected understanding:** `lms.Chat(prompt).from_history(text)` calls a classmethod that builds a brand-new chat from the text alone, discarding the instance holding the system prompt. Fix: `chat = lms.Chat(prompt)` then `chat.add_user_message(text)`. Related on the same day: `ollama.Client` sent `POST /api/chat` to LM Studio (config picked the host, not the API format), and `csv.reader` on a plain-text email would split `9,850.00` at the comma.
- **Rule going forward:** When an instruction seems to have no effect, first confirm it was actually sent (`print(chat)`), then judge the model.

## 2026-11-25 — staticmethod wrapped the wrong thing (Lesson 3.2)

- **Symptom:** 10 contract tests failed with `{'matching_quote_ids': <staticmethod([])>} != {'matching_quote_ids': []}`; a later version passed only because the wrapper did nothing.
- **My original explanation:** Wrapped function *results* (and `load_quotes` in a local variable inside `setUpClass`) in `staticmethod(...)`.
- **Corrected understanding:** `staticmethod` only matters for an uncalled function object assigned as a class attribute in the class body; it stops `self` being passed. Call it as `self.<attr>(...)` so a subclass override is picked up — a bare name resolves in the module, never on the class.
- **Rule going forward:** To make behavior swappable in a subclass, store it as a class attribute and always reach it through `self.`.
