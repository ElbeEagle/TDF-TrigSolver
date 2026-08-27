# Direct LLM baseline evaluation

This workflow evaluates Qwen3.5-Flash and DeepSeek-V3 on the 726 text-only
records selected from `data/CMM-Math/data.jsonl`. It never sends `answer`,
`analysis`, or `solution` fields to either model.

Configure `DASHSCOPE_API_KEY` and either `DASHSCOPE_BASE_URL` or
`OPENAI_BASE_URL` in the repository's `.env.local`. Credentials are read only
from that file and are never written to predictions or logs.

Build and validate the frozen ID/hash-only selection:

```bash
.venv/bin/python scripts/llm_eval/build_benchmark.py
```

Run a synthetic/API smoke test without consuming formal benchmark rows:

```bash
.venv/bin/python scripts/llm_eval/call_llm_api.py \
  --model all --run-dir results/llm_baselines/smoke --limit 0
```

Run or resume the formal calls:

```bash
.venv/bin/python scripts/llm_eval/call_llm_api.py \
  --model all --run-dir results/llm_baselines/cmm-trig-text-v1 --workers 4
```

Export conservative exact scores and the blinded review queue:

```bash
.venv/bin/python scripts/llm_eval/score_predictions.py stage-one \
  --run-dir results/llm_baselines/cmm-trig-text-v1
```

Complete a copy of `review/adjudications.template.jsonl` without opening the
private model map. The same blinded queue is split into 50-item files under
`review/batches/` for incremental Codex review. Every verdict must be `correct`
or `incorrect`; `uncertain` must be resolved by a human. Then finalize:

```bash
.venv/bin/python scripts/llm_eval/score_predictions.py finalize \
  --run-dir results/llm_baselines/cmm-trig-text-v1 \
  --adjudications results/llm_baselines/cmm-trig-text-v1/review/adjudications.completed.jsonl
```

Persistent API failures block scoring and must be rerun. They are never counted
as mathematical errors.
