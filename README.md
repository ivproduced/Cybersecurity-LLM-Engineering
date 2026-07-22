# Cybersecurity LLM Engineering

An evidence-backed portfolio project for evaluating, operating, and authorizing an on-premises cybersecurity language-model capability. The repository distills a larger home-lab project into reviewable code, synthetic examples, measured results, POC decision records, and authorization-oriented evidence patterns.

> **Project status:** the historical fine-tuning run is incomplete. It reached checkpoint 465,000 of 503,729 planned steps (92.3% of one epoch) before repeated power interruptions. The checkpoint is recoverable, but this repository does not present it as a finished or production-ready model.

## What this demonstrates

- Parameter-efficient fine-tuning of `google/gemma-7b-it` with LoRA and bfloat16
- Streaming quality analysis for multi-million-record JSONL datasets
- Checkpoint validation and automatic recovery after interrupted training
- Reproducible concurrency testing against OpenAI-compatible inference servers
- Model, dataset, security, and result documentation suitable for technical review
- A reusable POC evaluation workflow with explicit acceptance criteria and stop conditions
- An authorization evidence map that separates inherited controls from system-specific responsibilities
- Automated checks for credentials, private infrastructure identifiers, and unsupported release artifacts

## Evidence at a glance

| Workstream | Recorded result | Evidence status |
|---|---:|---|
| Training progress | 465,000 / 503,729 steps; evaluation loss 1.1516 to 0.7556 | **Verified** from retained trainer state |
| Evaluation efficiency | 503,728-record evaluation: 34,271.6 s; seeded 5,000-record evaluation: 341.9 s | **Verified** scope reduction; about 100x lower wall time |
| Dataset split | 5,037,282 total records; 80/10/10 split with seed 42 | **Verified** from retained split metadata |
| Recovery run | Loaded 400,163 completed records and produced the final 100,045-record tranche | **Verified** from timestamped recovery log |
| Generation workload | 1,073 successful items in 520.255 s; 4,673 aggregate tokens/s | **Partially verified**; complete model/runtime/hardware manifest missing |
| GPU partition test | Three logical partitions exposed 48/24/24 GB | **Partially verified**; enumeration is not an isolation test |
| Inference concurrency | Historical peak of 55.23 requests/second in the retained summary | **Rerun required** because matching raw request data was not retained |

The values above come from saved trainer state and historical benchmark/evaluation reports. They are summarized in [`results/`](results/README.md), where limitations and provenance are documented.

## Repository map

```text
case-studies/       Technical narratives and engineering decisions
docs/               POC, authorization, architecture, and release workflows
evidence/           Machine-readable evidence register and status labels
templates/          Reusable evaluation, risk, registry, and evidence records
src/training/       LoRA training and resilient checkpoint recovery
src/evaluation/     Streaming dataset-quality analysis
src/benchmarking/   OpenAI-compatible concurrency benchmark
src/governance/     Evidence-register and public-release validation
configs/            Safe, machine-independent example configuration
sample-data/        Synthetic records only
results/            Sanitized metrics, charts, and provenance notes
tests/              Unit tests for recovery, quality, metrics, and release gates
```

## Quick start

Python 3.10 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest
python -m src.governance.evidence_register evidence/evidence-register.yaml
python -m src.governance.public_release .
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
4. [Converting POC measurements into authorization evidence](case-studies/poc-authorization-evidence.md)

## POC and authorization workflow

The [POC evaluation plan](docs/poc-evaluation-plan.md) defines mission hypotheses, acceptance criteria, evidence collection, stop conditions, and the final decision record. The [authorization evidence map](docs/authorization-evidence-map.md) shows how those outputs can support system documentation, assessment, inherited-control validation, POA&M development, and continuous monitoring.

These are reusable engineering artifacts, not an agency authorization package. The Authorizing Official, system owner, ISSO, control assessor, privacy officials, legal counsel, records officials, and mission owner remain responsible for agency-specific decisions.

## Responsible disclosure

This repository contains no production credentials, agency data, model weights, private infrastructure identifiers, or original training corpus. See [SECURITY.md](SECURITY.md), [MODEL_CARD.md](MODEL_CARD.md), [DATASET_CARD.md](DATASET_CARD.md), and the [public-release checklist](docs/public-release-checklist.md) for boundaries and limitations.
