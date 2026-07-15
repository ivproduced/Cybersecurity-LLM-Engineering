# Results and provenance

These are sanitized summaries of retained project artifacts. No model weights, raw prompts, private endpoints, or original dataset records are included.

## Training curves

`training-history.csv` contains 5,000-step and 25,000-step milestones selected from the retained `trainer_state.json` at checkpoint 465,000. The first step is omitted from percentage comparisons because warmup made it non-comparable. The source state recorded `max_steps=503729`, `epoch=0.9231167797`, `eval_steps=5000`, and `save_steps=5000`.

## Inference curves

`inference-benchmark.csv` transcribes the aggregate table from a November 14, 2025 vLLM benchmark. Each level ran for approximately 60 seconds with `Qwen/Qwen2.5-3B-Instruct`, a roughly 600–700-token security prompt, and a 256-token output cap. Software versions, clocks, and request-level observations were not retained in the summary, so the comparison is directional rather than a controlled hardware study.

## Dataset summary

`dataset-quality-summary.csv` records the initial diagnostic and later remediated validation. The two rows are not identical scoring runs: the later report emphasizes deterministic field and length checks. They should not be interpreted as a single composite score improving from one exact value to another.

## Rebuild charts

```bash
pip install -e '.[plots]'
python scripts/build_result_plots.py
```

