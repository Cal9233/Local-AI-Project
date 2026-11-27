"""Lesson 4.4 tests: model selection wiring, provider routing, timeouts, cost.

Every test uses a fake in place of the real model call, so nothing touches the
network and results repeat exactly.
"""
import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import httpx

import model
from evals import run_eval
from model import ModelReply, extract_quotes

EMPTY_REPLY = '{"quote_list": []}'


def fake_reply(llm_model: str = "fake-model", content: str = EMPTY_REPLY) -> ModelReply:
    """A ModelReply as a provider would return it, with made-up stats."""
    return ModelReply(content=content, model=llm_model, provider="fake",
                      input_tokens=100, output_tokens=50, generation_s=2.0, thinking_chars=10)


class TestModelSelectionWiring(unittest.TestCase):
    """The chosen model must reach the actual model call, not just the log line."""

    def test_extract_quotes_passes_model_to_ask_model(self):
        # Regression test: extract_quotes once logged the chosen model but called
        # ask_model without it, so every "--model qwen3.6:35b" run really used the default.
        with patch("model.ask_model", return_value=fake_reply("test-model")) as fake:
            extract_quotes("any email text", llm_model="test-model")
        fake.assert_called_once()
        self.assertIn("test-model", fake.call_args.args + tuple(fake.call_args.kwargs.values()))

    def test_run_case_passes_model_through(self):
        case = {"id": "E09", "file": "emails/E09.txt", "split": "dev", "records": []}
        with patch("model.ask_model", return_value=fake_reply("other-model")) as fake:
            run_eval.run_case(case, "other-model")
        self.assertIn("other-model", fake.call_args.args)


class TestProviderRouting(unittest.TestCase):
    def test_claude_models_go_to_anthropic(self):
        with patch("model._ask_anthropic", return_value=fake_reply("claude-opus-5-5")) as hosted, \
             patch("model.Client") as ollama_client:
            model.ask_model("text", llm_model="claude-opus-5-5")
        hosted.assert_called_once()
        ollama_client.assert_not_called()

    def test_local_models_do_not_go_to_anthropic(self):
        self.assertFalse(model.is_hosted("qwen3.6:35b"))
        self.assertTrue(model.is_hosted("claude-haiku-5-5"))


class TestTimeouts(unittest.TestCase):
    def test_timeout_value_reaches_ask_model(self):
        with patch("model.ask_model", return_value=fake_reply()) as fake:
            extract_quotes("text", llm_model="m", timeout=1.5)
        self.assertIn(1.5, fake.call_args.args)

    def test_timeout_is_recorded_as_an_error_not_a_result(self):
        case = {"id": "E09", "file": "emails/E09.txt", "split": "dev", "records": []}
        with patch("model.ask_model", side_effect=httpx.ReadTimeout("timed out")):
            r = run_eval.run_case(case, "m", timeout=0.01)
        self.assertIn("ReadTimeout", r["error"])
        self.assertNotIn("extracted", r)  # no invented records when the call failed


class TestCostAndStats(unittest.TestCase):
    def test_cost_uses_decimal_prices(self):
        cost = run_eval.call_cost_usd("claude-opus-5-5", input_tokens=1_000, output_tokens=500)
        # 1000 * $4/M + 500 * $20/M = 0.004 + 0.010
        self.assertEqual(cost, Decimal("0.014"))

    def test_local_model_has_no_cost(self):
        self.assertIsNone(run_eval.call_cost_usd("qwen3.5:9b", 1_000, 500))

    def test_tokens_per_second(self):
        self.assertEqual(fake_reply().tokens_per_s, 25.0)

    def test_tokens_per_second_unknown_when_not_reported(self):
        self.assertIsNone(ModelReply(content="", model="m", provider="lmstudio").tokens_per_s)

    def test_results_filename_is_safe_and_names_the_model(self):
        name = run_eval.results_filename(datetime(2026, 11, 26, 18, 0, 0), "qwen3.6:35b", "V2")
        self.assertEqual(name, "2026-11-26T180000_qwen3.6-35b_V2.json")


if __name__ == "__main__":
    unittest.main()
