# Model card: cybersecurity Gemma LoRA experiment

## Model details

- **Base model:** `google/gemma-7b-it`
- **Adaptation:** LoRA, rank 16, alpha 32, dropout 0.05
- **Target modules:** attention projections and feed-forward gate/up/down projections
- **Language:** English
- **Status:** incomplete research checkpoint; not distributed in this repository
- **Last retained step:** 465,000 of 503,729 planned steps

The base-model identity and LoRA values come from the retained adapter configuration. Planning documents that mention another model size are not execution evidence.

## Intended use

The experiment explored instruction responses about cybersecurity concepts, control implementation, secure configuration, vulnerability/attack relationships, and security documentation. Appropriate use is offline research and controlled evaluation by people qualified to review the answers.

## Out-of-scope use

Do not use the checkpoint as an autonomous compliance authority, production incident responder, vulnerability adjudicator, authorization decision-maker, or source of instructions for a live system. Do not assume generated control mappings or citations are correct.

## Training summary

The recorded run used bfloat16, a maximum sequence length of 2,048 tokens, an effective batch size of eight, a 2e-5 learning rate with cosine decay, and one planned epoch. Training and evaluation were recorded every 5,000 steps.

## Evaluation

| Metric | Step 5,000 | Step 465,000 |
|---|---:|---:|
| Training loss | 1.0411 | 0.6959 |
| Evaluation loss | 1.1516 | 0.7556 |

These loss curves show that the optimization objective improved. They do not measure factuality, control-mapping accuracy, citation quality, dangerous guidance, calibration, or operational benefit. No claim of superiority to the base model is made.

## Known limitations

- Training did not reach the planned end of the epoch.
- Dataset sources, licenses, and generated-record provenance require record-level review before redistribution.
- A long answer can still be wrong; mechanical length thresholds do not establish quality.
- Cybersecurity standards and threat information change over time.
- The dataset may encode duplicated phrasing, source imbalance, model-generated artifacts, and historical terminology.
- The retained validation split was randomized by row. Source-related or semantically similar records may occur in both training and validation data, so validation loss may be optimistic.
- The model may hallucinate requirements or produce insecure technical instructions.

## Required evaluation before release

A release decision would require a frozen held-out suite, comparison to the unmodified base model, expert rubric scoring, citation verification, leakage and memorization testing, adversarial safety testing, subgroup/topic analysis, and documented acceptance thresholds. The final checkpoint and evaluation records would need integrity hashes and independent review.
