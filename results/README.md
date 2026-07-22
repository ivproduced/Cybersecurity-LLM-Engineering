# Results and provenance

These are sanitized summaries of retained project artifacts. No model weights, raw prompts, private endpoints, or original dataset records are included.

## Training curves

`training-history.csv` contains 5,000-step and 25,000-step milestones selected from the retained `trainer_state.json` at checkpoint 465,000. The first step is omitted from percentage comparisons because warmup made it non-comparable. The source state recorded `max_steps=503729`, `epoch=0.9231167797`, `eval_steps=5000`, and `save_steps=5000`.

## Inference curves

`inference-benchmark.csv` transcribes a historical aggregate table from a November 14, 2025 vLLM benchmark. Software versions, launch parameters, clocks, hashes, and request-level observations were not retained. The figures are marked **historical / rerun required** and must not be presented as current verified performance.

## Evaluation efficiency

`evaluation-efficiency.csv` records two retained evaluation runs. Reducing the routine evaluation scope from 503,728 records to a seeded 5,000-record subset reduced wall time from 34,271.6 to 341.9 seconds while sample throughput remained approximately 14.6–14.7 records/second. This supports a two-tier evaluation design: frequent deterministic subset checks and less frequent full-corpus gates.

## Recovery evidence

`recovery-summary.csv` records sanitized aggregate recovery evidence from a security-document generation run. It excludes prompts, outputs, host identifiers, and agency implementation details. The source log remains restricted and is not part of this repository.

## Dataset summary

`dataset-quality-summary.csv` records the initial diagnostic and later remediated validation. The two rows are not identical scoring runs: the later report emphasizes deterministic field and length checks. They should not be interpreted as a single composite score improving from one exact value to another.

Every public claim is indexed in [`../evidence/evidence-register.yaml`](../evidence/evidence-register.yaml) with a status, source-evidence description, limitation, and intended authorization reuse.

## Rebuild charts

```bash
pip install -e '.[plots]'
python scripts/build_result_plots.py
```
