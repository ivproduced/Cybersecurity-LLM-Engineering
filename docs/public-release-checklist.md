# Public release checklist

Complete this checklist immediately before creating the public repository. Automated scanning is necessary but not sufficient.

## Content and authority

- [ ] Repository owner and applicable data/content owners approve public release.
- [ ] No agency, client, third-party, controlled, export-restricted, procurement-sensitive, or personal information is included.
- [ ] Raw prompts, outputs, datasets, model weights, assessment artifacts, logs, and authorization records remain in approved storage.
- [ ] Source licenses, generated-content provenance, model terms, trademarks, and redistribution rights were reviewed.
- [ ] A repository license was deliberately selected; no license is inferred from source dependencies.
- [ ] Federal references are explanatory and do not imply agency endorsement or authorization.

## Secrets and infrastructure

- [ ] Every credential historically stored in plaintext was revoked or rotated, including values outside this folder.
- [ ] No passwords, tokens, private keys, certificates, internal URLs, hostnames, IP addresses, MAC addresses, device UUIDs, usernames, or machine-specific paths remain.
- [ ] Example secrets are placeholders loaded from environment variables.
- [ ] Local Git history and every branch/tag were scanned, not just the current working tree.
- [ ] A clean clone was scanned independently with the organization's approved secret and sensitive-data tools.

## Evidence quality

- [ ] Every numerical claim has a status and entry in the evidence register.
- [ ] Verified claims have retained controlled source evidence and a reproducible derivation.
- [ ] Historical or incomplete claims are visibly labeled and cannot be mistaken for current results.
- [ ] Charts identify whether they visualize raw or transcribed aggregate evidence.
- [ ] Hardware, runtime, model, dataset, prompt, and test versions are included where a comparison depends on them.
- [ ] Limitations, deviations, missing evidence, and rerun requirements remain visible.

## Local checks

```bash
python -m src.governance.evidence_register evidence/evidence-register.yaml
python -m src.governance.public_release .
python -m pytest
git status --short
git diff --check
```

After `git init`, use an approved history-aware secret scanner before the first push and again in CI. Review staged content with `git diff --cached --stat` and `git diff --cached` before committing.
