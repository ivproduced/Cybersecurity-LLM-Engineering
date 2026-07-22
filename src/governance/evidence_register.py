"""Validate the public evidence register and its artifact references."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


ALLOWED_STATUSES = {
    "verified",
    "historical_rerun_required",
    "partially_verified",
    "implementation_only",
}
ALLOWED_SENSITIVITIES = {"public", "internal", "controlled", "restricted"}
REQUIRED_FIELDS = {
    "id",
    "title",
    "domain",
    "status",
    "sensitivity",
    "claim",
    "public_artifacts",
    "source_evidence",
    "limitations",
    "authorization_reuse",
}
EVIDENCE_ID = re.compile(r"^EVD-[A-Z]{3}-\d{3}$")


def load_register(path: Path) -> dict[str, Any]:
    """Load a YAML evidence register."""
    with path.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    if not isinstance(document, dict):
        raise ValueError("evidence register must be a YAML mapping")
    return document


def validate_register(document: dict[str, Any], repository_root: Path) -> list[str]:
    """Return human-readable validation errors; an empty list means valid."""
    errors: list[str] = []
    if document.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    declared_states = document.get("states")
    if not isinstance(declared_states, list) or set(declared_states) != ALLOWED_STATUSES:
        errors.append("states must declare exactly the supported evidence states")

    records = document.get("records")
    if not isinstance(records, list) or not records:
        errors.append("records must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    root = repository_root.resolve()
    for index, record in enumerate(records, start=1):
        label = f"record {index}"
        if not isinstance(record, dict):
            errors.append(f"{label} must be a mapping")
            continue

        missing = sorted(REQUIRED_FIELDS - record.keys())
        if missing:
            errors.append(f"{label} is missing fields: {', '.join(missing)}")

        evidence_id = record.get("id")
        if not isinstance(evidence_id, str) or not EVIDENCE_ID.fullmatch(evidence_id):
            errors.append(f"{label} has an invalid evidence id")
        elif evidence_id in seen_ids:
            errors.append(f"{label} duplicates evidence id {evidence_id}")
        else:
            seen_ids.add(evidence_id)
            label = evidence_id

        if record.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{label} has an unsupported status")
        if record.get("sensitivity") not in ALLOWED_SENSITIVITIES:
            errors.append(f"{label} has an unsupported sensitivity")

        for field in ("title", "domain", "claim", "source_evidence", "limitations", "authorization_reuse"):
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label} field {field} must be non-empty text")

        artifacts = record.get("public_artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            errors.append(f"{label} public_artifacts must be a non-empty list")
            continue
        for artifact in artifacts:
            if not isinstance(artifact, str) or not artifact.strip():
                errors.append(f"{label} contains an invalid public artifact")
                continue
            candidate = (root / artifact).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"{label} artifact escapes the repository: {artifact}")
                continue
            if not candidate.is_file():
                errors.append(f"{label} artifact does not exist: {artifact}")

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "register",
        nargs="?",
        type=Path,
        default=Path("evidence/evidence-register.yaml"),
        help="path to the evidence register",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    register_path = args.register.resolve()
    try:
        document = load_register(register_path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"evidence register error: {exc}")
        return 1

    repository_root = register_path.parent.parent
    errors = validate_register(document, repository_root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Evidence register valid: {len(document['records'])} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
