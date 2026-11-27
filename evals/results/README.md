# Eval results

Each run writes `<timestamp>_<model>_<prompt>.json` (since lesson 4.4). Older files
are named `<timestamp>_<prompt>.json` and record the model inside the file.

## Mislabeled files: do not use for model comparison

These two runs record `"model": "qwen3.6:35b"`, but `extract_quotes` did not pass
the model on to `ask_model` at the time, so **qwen3.5:9b actually ran**:

- `2026-11-26T171525_V2.json`
- `2026-11-26T180025_V2.json`

The bug was fixed on 2026-11-26. `tests/test_model_comparison.py` now covers it.
