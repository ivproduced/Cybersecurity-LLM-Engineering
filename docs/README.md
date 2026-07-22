# POC and authorization evidence guide

This folder turns an AI experiment into a reviewable evidence package without pretending that a portfolio repository is an agency authorization package.

1. [`poc-evaluation-plan.md`](poc-evaluation-plan.md) defines hypotheses, gates, measures, acceptance criteria, and decisions before testing.
2. [`reference-architecture.md`](reference-architecture.md) identifies the system boundary, inherited common-control services, components, and data flows.
3. [`authorization-evidence-map.md`](authorization-evidence-map.md) maps engineering outputs to authorization evidence domains and owners.
4. [`evidence-handling.md`](evidence-handling.md) defines evidence states, sanitization, integrity, and retention.
5. [`public-release-checklist.md`](public-release-checklist.md) separates the controlled evidence bundle from its public portfolio derivative.

Reusable evaluation, system-manifest, benchmark, model-registry, risk, and evidence-integrity records live in [`../templates`](../templates). Public claims are indexed in [`../evidence/evidence-register.yaml`](../evidence/evidence-register.yaml).

This material is a technical starting point. The system owner, information system security officer, privacy officials, legal counsel, data owners, assessor, authorizing official, and AI governance officials determine the agency's actual artifacts and approval path.
