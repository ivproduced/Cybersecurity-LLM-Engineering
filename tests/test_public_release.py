from pathlib import Path

from src.governance.public_release import scan_repository


def test_scanner_flags_credentials_and_private_infrastructure(tmp_path: Path) -> None:
    credential = "h" + "f" + "_" + "A" * 24
    machine_path = "/" + "Volumes/" + "internal-share/private.txt"
    private_address = ".".join(("10", "20", "30", "40"))
    (tmp_path / "unsafe.txt").write_text(
        f"credential={credential}\nsource={machine_path}\nendpoint={private_address}\n",
        encoding="utf-8",
    )
    rules = {finding.rule for finding in scan_repository(tmp_path)}
    assert "possible Hugging Face credential" in rules
    assert "private machine path" in rules
    assert "private or shared-space IP address" in rules


def test_scanner_allows_placeholders_loopback_and_synthetic_sample(tmp_path: Path) -> None:
    sample_directory = tmp_path / "sample-data"
    sample_directory.mkdir()
    (sample_directory / "synthetic_examples.jsonl").write_text(
        '{"question":"example","answer":"example"}\n', encoding="utf-8"
    )
    (tmp_path / ".env.example").write_text(
        "API_KEY=${MODEL_API_KEY}\nENDPOINT=http://127.0.0.1:8000\n",
        encoding="utf-8",
    )
    assert scan_repository(tmp_path) == []


def test_scanner_rejects_weight_files_and_non_sample_jsonl(tmp_path: Path) -> None:
    (tmp_path / "weights.safetensors").write_bytes(b"placeholder")
    (tmp_path / "records.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / ".env.production").write_text("", encoding="utf-8")
    rules = {finding.rule for finding in scan_repository(tmp_path)}
    assert "model, credential, or checkpoint artifact" in rules
    assert "non-sample JSONL data artifact" in rules
    assert "environment file must not be released" in rules
