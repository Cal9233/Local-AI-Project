# Concepts

Record durable understanding, not every definition encountered.

## YYYY-MM-DD: Concept

- **Learner's explanation:**
- **Corrected understanding:**
- **Example:**
- **Related concepts:**

## 2026-11-12: Client vs. service

- **Learner's explanation:** `localhost` is this machine; a laptop couldn't reach the workstation's Ollama via `localhost`. Fix: use the workstation IP and expose Ollama on the network.
- **Corrected understanding:** Confirmed. The `ollama` package is only an HTTP client; the model runs in the Ollama server. Ollama binds to 127.0.0.1 by default, so remote use needs `OLLAMA_HOST=0.0.0.0` (plus firewall) on the server and `Client(host="http://<ip>:11434")` in code.
- **Example:** Server stopped → `chat()` raises a connection error; the venv package can't answer on its own.
- **Related concepts:** endpoints, response fields (`message.content`, `thinking`, `eval_count`), failure handling (2.3).
- 2026-11-21 Valid ≠ correct: Pydantic sees only the JSON, never the source. Rules (enum, >0) block impossible values; only comparison with the source proves values are true.
- 2026-11-22 unittest: discovery needs test*.py files, TestCase subclasses and test_ method names; the "Ran N tests" line is evidence too. Compare the whole result, since status alone hid the T02 bug.

## 2026-11-23: Context and request settings (Lesson 2.4)

- **Learner's explanation:** V1 worked "probably because it has condition codes and restrictions on what not to do"; written instructions are "not too reliable".
- **Corrected understanding:** Identical input varies run to run because of sampling (temperature). Context sets direction, rules remove guesses: condition SV 1/5 (quote only, qwen/qwen3-14b on LM Studio) → 5/7 (role-only system prompt) → 4/4 (V1 with IP → SV rule). Instructions are not guarantees: V1 said "only use values in the quote", yet `unit_price` 4875 was computed by the model, so arithmetic belongs in Python. Leftover prompt text changes output format (extraction prompt on a summary task produced JSON "per the schema").
- **Example:** Summary of `sample_email.txt` had correct numbers but dropped condition (OH, 8130-3) and RFQ 2026-1187, and turned "one unit on exchange" into "per unit". Correct figures ≠ faithful summary; invented `warranty` field passed validation.
- **Related concepts:** valid ≠ correct (2.2), system vs user messages, prompt versions, temperature (not yet tested).
