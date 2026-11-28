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

## 2026-11-26 — Split one offer into two records, invented a condition code (Lesson 4.1)

- **Symptom:** For "2 EA OH exchange USD 1,200 each, USD 5,000 core charge; 1 EA as-removed USD 800 outright", wrote 3 records: exchange without core, exchange with core, and as-removed with condition `AR`.
- **My original explanation:** Treated the core charge as a separate offer, and used `AR` for as-removed.
- **Corrected understanding:** A record is one offer a buyer can accept on its own; the core charge is a term of the exchange offer, so it is a field on that record (2 records total). Condition allows only OH/SV/NE; as-removed or unstated → `null`, never a new code.
- **Rule going forward:** Before writing a record, check it against the `rules` in `evals/expected.json`; anything outside the allowed values is unknown (`null`), not invented.

## 2026-11-26 — Predicted a line-broken phrase would go to review (Lesson 4.2)

- **Symptom:** Asked where an E06 quote lands if its price phrase is split by a line break in the email; answered `review_quotes`.
- **My original explanation:** Text that doesn't match exactly fails the phrase check.
- **Corrected understanding:** `phrase_in_source` calls `_normalize`, which collapses all whitespace (including line breaks) on both sides first, so the phrase matches and the quote is ranked (`unit_price` 487500 cents).
- **Rule going forward:** Read the checking function before predicting its result.

## 2026-11-26 — Predicted the bigger model would be faster (Lesson 4.4)

- **Symptom:** Predicted qwen3.6:35b would respond faster than qwen3.5:9b.
- **My original explanation:** More parameters and more training means a faster response.
- **Corrected understanding:** Size alone does not predict speed. 35b is mixture-of-experts (uses only part of its weights per token, ~360 tok/s); 9b wrote ~2.4× more tokens, mostly thinking, at ~193 tok/s. 35b was ~4× faster warm.
- **Rule going forward:** Measure latency, tokens and tok/s before explaining speed.

## 2026-11-26 — Changed the design before writing a failing case (Lesson 4.4)

- **Symptom:** For a new pattern (unit on loan, back in 10 days), proposed adding a schema attribute first.
- **My original explanation:** Add a validation check for whether the unit is there.
- **Corrected understanding:** First add a dev email with its expected result and confirm it fails on the current prompt; then change prompt or schema, check dev, score held-out once. Also: quantity 0 fails `Field(gt=0)` and loses the whole email; no stock now means no record.
- **Rule going forward:** Failing eval case → confirm it fails → change → dev → held-out once.

## 2026-11-27 — Unquoted dict keys (Lesson 5)

- **Symptom:** `request = {part_number: part_number, ...}` → `KeyError: 'requested_quantity'` in `validate_request` (same error seen in 3.2).
- **My original explanation:** Asked what part number had to do with the quantity value; thought `= None` defaults were involved.
- **Corrected understanding:** An unquoted name in a dict literal is a variable, so its value becomes the key (`{"TRAIN-PN-001": ...}`). The KeyError names whichever key is looked up first.
- **Rule going forward:** Dict keys in quotes unless you mean a variable; on a KeyError, `print` the dict and compare its keys.

## 2026-11-27 — Ran code before predicting (Lesson 12.1)
- **Symptom:** ran the logits-shape and padding experiments before committing to a guess (twice).
- **Corrected understanding:** the prediction is the practice; running first turns it into reading answers.
- **Rule going forward:** write the guess down first, then run.

## 2026-11-28 — Thought a schema rule could catch an over-stated quantity (Lesson 12.2)

- **Symptom:** For a quote with quantity 3 from an email saying 2 in stock (third unit "in about 3 weeks"), proposed a schema rule as the fix.
- **My original explanation:** A schema rule would catch the wrong quantity.
- **Corrected understanding:** Trying to write the `Field` constraint showed the schema never sees the email, so it has no number to compare against. Matching the source is a code check (like `price_phrase` + `phrase_in_source`). Same family as 4.4: valid structure ≠ true values.
- **Rule going forward:** If the check needs the source text, it belongs in code, not the schema.

## 2026-11-28 — Assumed the production extractor retries (Lesson 12.2)

- **Symptom:** Said `extract_quotes` retries once and then flags for review.
- **My original explanation:** The retry-then-flag behaviour applies to the extraction pipeline.
- **Corrected understanding:** Tracing `extract_quotes` → `extract_quotes_with_reply` → `ask_model` showed one attempt that raises `pydantic.ValidationError`; the retry loop and "Flag for review" live only in the 2.x `main()` demo.
- **Rule going forward:** Read the function before predicting it (repeat of the 3.3 rule).
