# Security policy

## Scope

This is a portfolio and research repository. It is not an authorized production system, an authorization package, or a source of agency security requirements.

The repository intentionally excludes:

- model weights and optimizer state;
- original training and evaluation datasets;
- internal hostnames, IP addresses, credentials, and access tokens;
- system-specific security configurations; and
- nonpublic assessment or authorization artifacts.

## Safe operation

Before running the code in any environment:

1. Use only approved models, revisions, licenses, and acquisition paths.
2. Verify hashes and provenance before deserializing model artifacts.
3. Treat model files as untrusted supply-chain inputs; prefer safe serialization formats.
4. Keep endpoints private by default and require authentication, authorization, TLS, rate limits, and audit logging when exposed.
5. Never place controlled, sensitive, or production data in prompts or training files without explicit authorization.
6. Run experiments with least privilege and separate service, training, and administrative identities.
7. Store secrets outside source control and redact logs before sharing.
8. Define retention and deletion rules for prompts, outputs, checkpoints, and telemetry.

## Public release

Historical working files outside this repository contained credentials and private infrastructure identifiers. Those values are intentionally excluded here. Any credential ever stored in plaintext must be revoked or rotated before publishing a source archive, even if the value does not appear in this repository.

Before release, run:

```bash
python -m src.governance.evidence_register evidence/evidence-register.yaml
python -m src.governance.public_release .
```

The automated check is a guardrail, not a substitute for owner review, secret scanning across Git history, data-owner approval, or agency release procedures. See [`docs/public-release-checklist.md`](docs/public-release-checklist.md).

## AI-specific risks

Relevant risks include prompt injection, poisoned training data, sensitive-data memorization, unsafe generated commands, fabricated citations, overconfident compliance advice, model theft, denial of service, and dependency or weight compromise. Generated security guidance requires qualified human review before use.

## Vulnerability reporting

Do not open a public issue containing credentials, private infrastructure details, sensitive datasets, or exploit material for a live system. Contact the repository owner privately with a minimal reproduction, affected version, impact, and suggested mitigation.
