from pathlib import Path

from src.governance.evidence_register import load_register, validate_register


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_repository_evidence_register_is_valid() -> None:
    document = load_register(REPOSITORY_ROOT / "evidence/evidence-register.yaml")
    assert validate_register(document, REPOSITORY_ROOT) == []


def test_validator_rejects_duplicate_ids_and_missing_artifacts(tmp_path: Path) -> None:
    document = {
        "schema_version": 1,
        "states": [
            "verified",
            "historical_rerun_required",
            "partially_verified",
            "implementation_only",
        ],
        "records": [],
    }
    record = {
        "id": "EVD-TST-001",
        "title": "Test evidence",
        "domain": "test",
        "status": "verified",
        "sensitivity": "public",
        "claim": "A bounded claim.",
        "public_artifacts": ["missing.txt"],
        "source_evidence": "Test fixture.",
        "limitations": "Test limitation.",
        "authorization_reuse": "Test reuse.",
    }
    document["records"] = [record, dict(record)]
    errors = validate_register(document, tmp_path)
    assert any("duplicates evidence id" in error for error in errors)
    assert any("artifact does not exist" in error for error in errors)
