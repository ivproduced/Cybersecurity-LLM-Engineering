# AI proof-of-concept evaluation plan

## Purpose

Use a time-boxed, on-premises POC to determine whether a cybersecurity language-model service produces enough mission value to justify further engineering and authorization work. The evaluation produces traceable evidence for a go, revise, or stop decision; it does not itself authorize production use.

This plan is designed for a workload hosted inside an agency-owned boundary and inheriting eligible protections from a common control provider (CCP). Inheritance reduces duplication, but the application still needs system-specific implementation, risk, assessment, and authorization evidence.

## Decision statement

At the end of the POC, the decision authority records one outcome:

- **Proceed:** predefined mission, quality, security, performance, and governance gates pass; residual risks have owners.
- **Proceed with conditions:** value is demonstrated, but named gaps require remediation before the next gate.
- **Revise and retest:** evidence is insufficient or a fix is likely to change the result materially.
- **Stop:** value does not justify cost or risk, a prohibited dependency exists, or a stop criterion is met.

## Scope and boundary assumptions

- Compute and storage are on premises and already inside an agency authorization boundary.
- The new AI application is a consumer of CCP services, not automatically covered merely because its hardware is inside the boundary.
- External connectivity, if approved, is limited to controlled model and dependency acquisition through an allowlisted, logged path.
- Production agency data is excluded until its owner, privacy, security, and records requirements are approved.
- POC users are named evaluators; no autonomous decisions or direct production actions are permitted.
- Public portfolio artifacts are sanitized derivatives, never the controlled evidence of record.

## Hypotheses

| ID | Testable hypothesis | Example measure | Predeclared gate |
|---|---|---|---|
| H1 | The service improves a defined analyst task. | blinded rubric score, task completion, correction rate | owner-defined improvement over baseline with no critical error |
| H2 | Outputs are sufficiently accurate and grounded. | factuality, citation validity, abstention, unsupported-claim rate | thresholds set before model testing |
| H3 | Unsafe or sensitive behavior is bounded. | prompt-injection success, data disclosure, prohibited-action rate | zero critical disclosure; residual rates within approved tolerance |
| H4 | The platform meets the workload service objective. | p50/p95/p99 latency, output tokens/s, error rate, saturation point | workload-specific SLO at defined concurrency |
| H5 | The service is operable and reviewable. | restart recovery, logging completeness, artifact provenance, rollback | mandatory events logged; recovery and rollback demonstrated |
| H6 | Cost and resource demand are acceptable. | energy, GPU-hours, storage, staff review time, cost per accepted task | within approved POC budget and capacity |

Populate exact gates in [`../templates/poc-evaluation-record.md`](../templates/poc-evaluation-record.md) before executing the evaluation. A threshold chosen after results are known is an observation, not an independent acceptance gate.

## Evaluation lanes

### 1. Mission utility

- Freeze representative tasks and a non-AI or current-process baseline.
- Blind and randomize outputs where practical.
- Score with a task-specific rubric and record inter-rater agreement.
- Track human corrections, time saved, and failure severity—not only preference.

### 2. Model quality

- Compare the base model, candidate model, and relevant configuration changes on the same held-out suite.
- Test factuality, control or topic mapping, citation support, calibrated abstention, and temporal/version awareness.
- Group evaluation splits by source and semantic similarity to reduce leakage.
- Preserve prompt-suite version, generation parameters, model digest, grader instructions, and raw score records.

### 3. Security, safety, privacy, and civil-rights review

- Exercise prompt injection, indirect instruction, secret extraction, memorization, malicious file or model artifacts, denial of service, and unsafe generated commands.
- Verify identity, least privilege, network egress, encryption, audit logging, incident handling, and data retention behavior.
- Complete privacy, records, legal, accessibility, and applicable rights-impact screening with the responsible officials.
- Document human oversight and prohibit the model from being the authorization or compliance decision-maker.

### 4. Performance and reliability

- Capture current hardware/software manifests and immutable model/container identifiers.
- Run warm-up, steady-state, burst, saturation, soak, restart, rollback, and degraded-capacity scenarios.
- Retain request-level timing and token counts plus GPU, CPU, memory, storage, thermal, and power telemetry.
- Report uncertainty across repetitions instead of selecting only the best run.

### 5. Governance and operations

- Register the use case, owner, purpose, data categories, model, version, dependencies, and risk classification.
- Record model acquisition, malware scanning, license review, hash verification, and promotion approvals.
- Define change triggers for model, prompt, data, runtime, hardware, interface, and mission use.
- Assign monitoring, incident, vulnerability, model retirement, and evidence-retention responsibilities.

## Entry criteria

- Named system, mission, security, privacy, data, and evaluation owners.
- Approved POC scope, users, data categories, connectivity, budget, and duration.
- Documented boundary and inherited-versus-system-specific responsibility matrix.
- Frozen evaluation suite, baselines, rubrics, acceptance thresholds, and stop criteria.
- Approved model acquisition path with provenance, license, digest, malware scan, and storage record.
- Logging, time synchronization, evidence storage, backup, rollback, and incident contacts tested.

## Stop criteria

Pause the POC and notify the responsible officials when a credential or controlled-data disclosure occurs; unapproved data or connectivity is used; artifact integrity cannot be established; a critical safety/security failure occurs; required logging is unavailable; the test escapes its approved boundary; or continued operation could affect a production mission.

## Evidence bundle

For every executed test, preserve:

1. approved test record and acceptance criterion;
2. system, model, dataset, prompt, and evaluator versions;
3. commands/configuration with secrets removed;
4. raw results in controlled storage plus SHA-256 hashes;
5. scripted summary and sanitized public derivative, if releasable;
6. deviations, incidents, limitations, and missing evidence;
7. reviewer identity, review date, and disposition; and
8. decision record tying findings to risks and next actions.

Use the machine-readable [`../evidence/evidence-register.yaml`](../evidence/evidence-register.yaml) to index claims without copying restricted source material into this repository.

## Federal alignment references

The agency determines which requirements apply. Useful anchors include [OMB M-25-21, Accelerating Federal Use of AI through Innovation, Governance, and Public Trust](https://www.whitehouse.gov/wp-content/uploads/2025/02/M-25-21-Accelerating-Federal-Use-of-AI-through-Innovation-Governance-and-Public-Trust.pdf), [OMB M-25-22, Driving Efficient Acquisition of Artificial Intelligence in Government](https://www.whitehouse.gov/wp-content/uploads/2025/02/M-25-22-Driving-Efficient-Acquisition-of-Artificial-Intelligence-in-Government.pdf?categoryid=2826672), the [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework), its [Generative AI Profile, NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf), and the agency's own AI, privacy, records, acquisition, security, and authorization policies.
