# Cybersecurity LLM Engineering

A portfolio case study in building, evaluating, and operating a cybersecurity-focused language-model pipeline. The repository distills a larger home-lab project into reviewable code, synthetic examples, measured results, and candid engineering decisions.

> **Project status:** the historical fine-tuning run is incomplete. It reached checkpoint 465,000 of 503,729 planned steps (92.3% of one epoch) before repeated power interruptions. The checkpoint is recoverable, but this repository does not present it as a finished or production-ready model.

## What this demonstrates

- Parameter-efficient fine-tuning of `google/gemma-7b-it` with LoRA and bfloat16
- Streaming quality analysis for multi-million-record JSONL datasets
- Checkpoint validation and automatic recovery after interrupted training
- Reproducible concurrency testing against OpenAI-compatible inference servers
- Model, dataset, security, and result documentation suitable for technical review

## Evidence at a glance

| Workstream | Recorded result | Interpretation |
|---|---:|---|
| Training progress | 465,000 / 503,729 steps | 92.3% of the planned epoch completed |
| Training loss | 1.0411 at step 5,000 to 0.6959 at step 465,000 | 33.2% decrease across the comparable recorded interval |
| Evaluation loss | 1.1516 at step 5,000 to 0.7556 at step 465,000 | 34.4% decrease; downstream task quality remains unmeasured |
| Dataset remediation | 581,076 unique Q&A pairs; 97.0% with answers of at least 150 characters | Mechanical quality improved; length is not a proxy for factual correctness |
| Inference benchmark | 55.23 requests/second at concurrency 350 on one RTX PRO 6000 Max-Q endpoint | Best measured throughput for the tested model and request shape |

The values above come from saved trainer state and historical benchmark/evaluation reports. They are summarized in [`results/`](results/README.md), where limitations and provenance are documented.

## Repository map

```text
case-studies/       Technical narratives and engineering decisions
src/training/       LoRA training and resilient checkpoint recovery
src/evaluation/     Streaming dataset-quality analysis
src/benchmarking/   OpenAI-compatible concurrency benchmark
configs/            Safe, machine-independent example configuration
sample-data/        Synthetic records only
results/            Sanitized metrics, charts, and provenance notes
tests/              Unit tests for recovery, quality, and metrics logic
```

## Quick start

Python 3.10 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest
python -m src.evaluation.dataset_quality sample-data/synthetic_examples.jsonl
```

To benchmark an authorized local vLLM endpoint:

```bash
python -m src.benchmarking.openai_compatible \
  --endpoint http://127.0.0.1:8000/v1/completions \
  --model your-approved-model \
  --concurrency 1,4,8,16 \
  --requests 100
```

Training dependencies and model weights are intentionally optional:

```bash
pip install -e '.[training]'
python -m src.training.train_lora --config configs/example.yaml
```

Review model licensing, weight provenance, data authorization, and compute-environment policy before running training. The sample configuration is an engineering example, not an authorization to download or process a model.

## Case studies

1. [Recoverable cybersecurity LoRA fine-tuning](case-studies/fine-tuning.md)
2. [Turning dataset-quality findings into a remediation pipeline](case-studies/dataset-quality.md)
3. [Finding inference concurrency sweet spots](case-studies/inference-benchmarking.md)

## Responsible disclosure

This repository contains no production credentials, agency data, model weights, or original training corpus. See [SECURITY.md](SECURITY.md), [MODEL_CARD.md](MODEL_CARD.md), and [DATASET_CARD.md](DATASET_CARD.md) for boundaries and limitations.

