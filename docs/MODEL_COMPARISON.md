# Model comparison: extraction (lesson 4.4)

Same task, prompt and checked emails for every model: extract supplier offers from fictional
emails (`evals/emails/`) and compare each field with `evals/expected.json`. Three runs per
email, because output varies between runs.

- **Date:** 2026-11-26
- **Hardware:** Ubuntu workstation, one 32 GB GPU, Ollama at `localhost:11434`
- **Data:** V2 runs used 20 emails (10 dev, 10 held-out). V3 runs used 22: two dev emails
  (E21, E22) were added to tune V3 without touching held-out. Held-out is the same 10 in both.
- **Command:** `python -m evals.run_eval --model <name> --runs 3 --warmup`
- **Hosted settings:** Anthropic API, structured output (`messages.parse` with `QuoteWrapper`),
  default effort, `max_retries=2`. Prices are in `PRICES_PER_MTOK` in `evals/run_eval.py`.

## Final results (prompt V3)

Field accuracy = exact matches ÷ expected records over all runs (dev 42, held-out 30).

| | qwen3.6:35b (local) | claude-opus-5-5 | claude-haiku-5-5 |
|---|---|---|---|
| Held-out: every field | **30/30 (100%)** | **30/30 (100%)** | **30/30 (100%)** |
| Dev: every field | **100%** | 100%, except condition **39/42** | **100%** |
| Invented values (all runs) | **0** | **3** (E01, every run) | **0** |
| Warm latency per email (median, held-out) | 5.3 s | 1.9 s | 1.8 s |
| Cold start (first call) | 27–35 s (model load) | 3.7 s | 4.1 s |
| Output tokens per email (median) | ~1,850–2,100 | ~120 | ~120 |
| Cost per email | $0 API (local GPU, power) | ~$0.0094 | ~$0.00027 |
| Cost of this eval (67 calls) | $0 | $0.62 | $0.018 |
| Supplier emails leave the building | no | yes | yes |

Results: `evals/results/2026-11-26T203724_qwen3.6-35b_V3.json`,
`…T201835_claude-opus-5-5_V3.json`, `…T202051_claude-haiku-5-5_V3.json`.

The 35b V3 run shared the GPU with another model (`granite4.1:30b`) for part of the
dev split, so its dev latency maximum (50.7 s) measures model swapping, not extraction.
Accuracy is unaffected. The held-out latency and the clean V2 run (5.5 s median) agree.

## Before the fix (prompt V2, 20 emails)

| | qwen3.5:9b | qwen3.6:35b | claude-opus-5-5 | claude-haiku-5-5 |
|---|---|---|---|---|
| Held-out: every field | 27/30 (90%) | 28/30 (93%) | 30/30 (100%) | 27/30 (90%) |
| Invented values | 1 | 0 | 3 | 0 |
| Warm latency (median) | 24 s | 5.5 s | 2.3 s | ~2 s |
| Output tokens (median) | ~4,700 | ~1,950 | ~120 | ~150 |
| Generation speed | ~193 tok/s | ~360 tok/s | not reported | not reported |

**`qwen3.5:9b` was dropped after V2.** It was the slowest model by 4× and no more accurate than 35b.
It produced ~2.4× more output tokens (mostly thinking) at about half the speed. The 35b is a
mixture-of-experts model (`ollama show`: `qwen35moe`), so it only uses some of its weights for
each token. Bigger did not mean slower; measure it.

## Wrong answers and the smallest change that helped

| Email | Failure on V2 | Cause | V3 change | After |
|---|---|---|---|---|
| E18 (held-out) "call us for pricing" | **Offer dropped**: 9b 3/3, 35b 2/3, Haiku 3/3 runs | Prompt: "no offer → empty list". Models read "no price" as "no offer" | + "A part that is in stock is an offer even if no price is given: return it with price null." | Fixed for every model, 0 drops |
| E13 (held-out) GBP price | Currency **null** (9b, 1/3) → wrong review reason | Prompt: "ISO code (USD or EUR)". The example list was read as the only allowed values | Currency: "the ISO code exactly as stated (e.g. USD, EUR, GBP, CAD)" | Fixed |
| E01 (dev) exchange unit | Condition **invented** (Opus 3/3, 9b 1/3); record ranked | Email gives "2 EA overhauled", then "one unit on exchange" with no condition | + "Use only the condition stated for this offer; never copy it from another offer" | Fixed for 35b/Haiku; **Opus still 3/3** |

**How the fix was made without touching held-out:** E21 (in stock, "price on request") and
E22 (CAD price) are dev copies of the held-out failures. On V2, 35b failed both: E21 dropped
2/3 times, and E22's currency was nulled 1/3 times. That confirms they reproduce the problem. V3 was checked on dev
only (35b: 100%), then held-out was scored once per model.

**Most important failure:** E18. A supplier who *has the part* disappeared silently, and the
broker would never see the offer. Failing safe (into review) is acceptable; disappearing is not.

**E01 expected value: kept as `condition: null`.** The exchange unit's condition is never
stated; it may or may not be one of the overhauled units. The "never invent" rule decides
this: a human checks it in review. Opus's persistent guess is a reason not to trust a strong
model's confident output over the code's review rules.

## Failure behaviour

- **Timeout:** `python -m evals.run_eval --cases E01 --timeout 1` →
  `E01 run 1: ERROR ReadTimeout: timed out`. The failure is recorded as an error with no records, the eval
  continues, and nothing is invented. Covered by `tests/test_model_comparison.py::TestTimeouts`.
- **Hosted retries:** `max_retries=2` for 429/5xx/connection errors, plus the same `--timeout`.

## Measurement bug found during this lesson

Two early "35b" runs (`2026-11-26T171525_V2.json`, `2026-11-26T180025_V2.json`) actually ran
9b. `extract_quotes` logged the chosen model but did not pass it to `ask_model`. The output,
log and results file all said "35b". Only the latency pattern (no cold start) and `ollama ps`
revealed it. Covered now by `TestModelSelectionWiring`.

## Recommendation

**Use `qwen3.6:35b` (local) with prompt V3.** It is now the default in `.env.linux`.

- **Quality:** 100% on held-out and dev, and 0 invented values, tied for best.
- **Speed:** ~5 s per email warm is fine for a broker. The cost is a ~30 s cold start after
  5 idle minutes (Ollama keep-alive).
- **Cost and privacy:** no API fees, and supplier emails stay on the workstation. The trade-off: it
  needs ~22 GB of GPU memory, and it slows badly when another large model shares the GPU.
- **Fallback:** `claude-haiku-5-5` matched it exactly on accuracy, at ~$0.00027 per email
  (about $0.01 a day at 50 emails) and ~2 s. Use it when the workstation is off or busy.
- **Not Opus** for this task: it costs about 35× more than Haiku and was the only model that still invented a value
  after V3.

Caveat: 10 held-out emails is a small test. "100%" means no errors on these 10, not
"never wrong". Grow the held-out set before relying on small differences.
