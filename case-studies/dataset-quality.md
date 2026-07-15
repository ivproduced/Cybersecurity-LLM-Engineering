# Case study: dataset quality as an engineering control

## Executive summary

An initial evaluation of a 594,388-record cybersecurity Q&A dataset found excellent question form but weak source coverage, short answers, and limited technical depth. I used those findings to prioritize source tagging, answer regeneration, deduplication, and validation. A later remediated dataset contained 581,076 unique pairs, 97.0% of answers met the 150-character mechanical threshold, and critical fields were complete.

This was a measurable improvement in dataset hygiene. It was not proof that 97% of answers were factually correct.

## Initial diagnostic

The October 2025 evaluator reported:

| Metric | Initial result |
|---|---:|
| Records | 594,388 |
| Represented source documents | 17 of 161 |
| Completeness score | 10.6% |
| Relevance score | 28.0% |
| Overall heuristic quality | 52.1% |
| Question quality | 89% |
| Answer quality | 53% |
| Technical-depth heuristic | 18% |

The important insight was that volume hid imbalance. Roughly 400,000 records traced to a small number of generic source labels, while most inventoried documents had no measurable coverage.

## Remediation strategy

1. Repair source-document tagging so coverage could be measured.
2. Identify answers below 150 characters for regeneration or removal.
3. Generate more implementation-oriented questions and answers.
4. Merge improved records with the original dataset using an explicit precedence rule.
5. Deduplicate normalized questions and validate required fields.
6. Retain before/after reports instead of overwriting evidence.

## Recorded outcome

| Metric | Remediated result |
|---|---:|
| Unique Q&A pairs | 581,076 |
| Unique questions | 574,838 (98.9%) |
| Answers at least 150 characters | 563,416 (97.0%) |
| Average answer length | 671 characters |
| Missing questions | 0 |
| Missing answers | 0 |
| Answers improved over original | 195,729 |

The validation report also exposed a taxonomy-cleaning issue: control-family values contained case variants and nonstandard labels. “All families present” therefore did not mean the metadata was normalized. That is exactly why raw distributions must accompany top-line pass rates.

## Public implementation

[`src/evaluation/dataset_quality.py`](../src/evaluation/dataset_quality.py) performs a streaming JSONL check for:

- malformed JSON and missing required fields;
- empty questions and answers;
- short answers using a configurable threshold;
- normalized duplicate questions;
- control-ID and source-metadata coverage; and
- average question and answer length.

It uses bounded per-record processing. Exact duplicate detection retains a compact digest per question, which is a deliberate memory/accuracy tradeoff that should be replaced with an external sort or probabilistic structure at much larger scales.

```bash
python -m src.evaluation.dataset_quality \
  sample-data/synthetic_examples.jsonl \
  --minimum-answer-chars 150 \
  --output results/sample-quality-report.json
```

## What remains

Mechanical validation cannot establish correctness. A production evaluation would add stratified human review, source-grounded factuality checks, train/evaluation leakage detection, license and provenance validation, harmful-content screening, and inter-rater agreement. Thresholds would be set by task risk rather than answer length alone.

## Portfolio takeaway

This case study shows an iterative data-governance loop: **inventory → measure → diagnose → remediate → re-measure → document limitations**. The willingness to publish the poor initial score is part of the work; it shows that the evaluation changed the pipeline instead of merely validating a preferred conclusion.

