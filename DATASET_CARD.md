# Dataset card: cybersecurity instruction corpus

## Repository dataset

Only [`sample-data/synthetic_examples.jsonl`](sample-data/synthetic_examples.jsonl) is included here. Those records are newly written synthetic examples with fictional `EX-*` control identifiers. They contain no production, agency, or original corpus data and exist solely to exercise the public code.

## Historical training corpus

Project artifacts describe a consolidated English cybersecurity Q&A corpus of approximately 4.26 million records, split roughly 90/5/5. The executed training script reported approximately 3.84 million training records. Topic categories included NIST security controls, system-security-plan writing, STIG concepts, MITRE ATT&CK, CWE, CAPEC, and security-documentation patterns.

The historical corpus is not redistributed because source-level licensing, generated-content provenance, and data authorization must be reviewed before publication. Aggregate counts in project notes should be treated as experiment records rather than an independently audited dataset release.

## Earlier quality-remediation stage

A precursor dataset evaluation recorded 594,388 entries from 161 inventoried source documents. Initial source coverage and technical-depth heuristics were poor. After answer regeneration, merging, and deduplication, a validation report recorded:

- 581,076 unique Q&A pairs;
- 574,838 unique normalized questions;
- 563,416 answers (97.0%) with at least 150 characters;
- zero missing question or answer fields; and
- 195,729 answers improved over the original version.

These figures describe mechanical validation and pipeline history. They do not prove factual accuracy, legal redistribution rights, or suitability for model training.

## Expected schema

```json
{
  "question": "A security question or instruction",
  "answer": "The expected response",
  "control_id": "Optional normalized topic or control identifier",
  "source": "Required provenance identifier for governed datasets"
}
```

## Data-quality controls

- valid UTF-8 JSONL and required-field checks;
- empty and minimum-length checks;
- normalized duplicate-question detection;
- source and control-ID coverage reporting;
- split leakage analysis before evaluation;
- source-license and provenance review;
- stratified expert factuality sampling; and
- removal or quarantine of sensitive and unsafe content.

## Limitations and risks

Generated examples can amplify the generator's errors. Security-framework mappings are contextual and version dependent. Source imbalance can make aggregate metrics misleading. Apparent diversity from paraphrasing may not represent conceptual diversity. Training and test splits must be grouped by source and semantic similarity, not only randomized by row.

