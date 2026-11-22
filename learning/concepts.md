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
