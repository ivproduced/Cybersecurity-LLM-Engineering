import json
from pathlib import Path

from src.training.checkpoints import (
    checkpoint_step,
    find_latest_valid_checkpoint,
    validate_checkpoint,
)


def make_checkpoint(root: Path, step: int, *, complete: bool = True) -> Path:
    checkpoint = root / f"checkpoint-{step}"
    checkpoint.mkdir()
    files = {
        "adapter_config.json": "{}",
        "adapter_model.safetensors": "weights",
        "trainer_state.json": json.dumps({"global_step": step}),
        "optimizer.pt": "optimizer",
        "scheduler.pt": "scheduler",
    }
    if not complete:
        files.pop("optimizer.pt")
    for name, content in files.items():
        (checkpoint / name).write_text(content, encoding="utf-8")
    return checkpoint


def test_checkpoint_step_rejects_unrelated_names() -> None:
    assert checkpoint_step("checkpoint-465000") == 465000
    assert checkpoint_step("final-adapter") is None


def test_latest_checkpoint_skips_incomplete_state(tmp_path: Path) -> None:
    expected = make_checkpoint(tmp_path, 100)
    make_checkpoint(tmp_path, 200, complete=False)
    assert find_latest_valid_checkpoint(tmp_path) == expected


def test_validation_detects_step_mismatch(tmp_path: Path) -> None:
    checkpoint = make_checkpoint(tmp_path, 100)
    (checkpoint / "trainer_state.json").write_text('{"global_step": 99}', encoding="utf-8")
    assert "trainer_state global_step does not match directory" in validate_checkpoint(checkpoint)

