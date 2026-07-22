# Evidence handling and sanitization

## Evidence states

| State | Meaning |
|---|---|
| `verified` | retained source evidence supports the bounded claim and the public derivative was cross-checked |
| `historical_rerun_required` | a historical summary exists, but missing raw evidence or manifests prevent independent verification |
| `partially_verified` | one portion is supported while a broader claim still requires testing |
| `implementation_only` | code or design exists; no executed result is claimed |

Absence of evidence is recorded as a limitation, never converted into an estimate. Planning values do not override execution records.

## Sensitivity levels

| Level | Repository treatment |
|---|---|
| `public` | eligible for this repository after owner review |
| `internal` | describe at a high level; do not publish source record |
| `controlled` | retain only in the approved evidence store; publish an approved aggregate if permitted |
| `restricted` | never copy to the repository; reference by an internal evidence ID only |

Agency markings and handling rules supersede these repository labels.

## Evidence chain

1. Preserve raw evidence in access-controlled storage with its original timestamps and metadata.
2. Create a manifest containing evidence ID, file name, byte size, SHA-256 digest, source system clock, collector, command/test ID, and collection time.
3. Generate summaries with version-controlled code; retain the code revision and command.
4. Review the derivative for credentials, endpoints, host identifiers, user identifiers, controlled data, agency implementation details, and licensed content.
5. Record redactions or transformations so a reviewer can reconcile the derivative to the controlled source.
6. Sign or approve the review according to the agency workflow; do not place reviewer PII in the public copy.

## Public derivative rules

- Replace private paths, endpoints, device identifiers, usernames, and case-specific labels with neutral descriptions.
- Report only the minimum aggregate required to support the portfolio claim.
- Do not publish prompts or outputs derived from agency implementation data.
- Preserve meaningful caveats; sanitization must not turn an incomplete result into a stronger claim.
- Keep the internal evidence locator out of the public copy when it reveals system structure.
- Run automated checks against the working tree and Git history, followed by a human review.

The public [`../evidence/evidence-register.yaml`](../evidence/evidence-register.yaml) describes source evidence generically. An agency-local version can add controlled locators, hashes, reviewers, retention, and mappings.
