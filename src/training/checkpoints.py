"""Checkpoint discovery and validation.

The original experiment survived repeated interruptions because model and trainer
state were checkpointed. These helpers make the recovery decision explicit and
testable instead of relying on a hard-coded checkpoint path.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

CHECKPOINT_PATTERN = re.compile(r"^checkpoint-(\d+)$")
ADAPTER_FILES = ("adapter_config.json", "adapter_model.safetensors")
TRAINER_STATE_FILES = ("trainer_state.json", "optimizer.pt", "scheduler.pt")


def checkpoint_step(path: str | Path) -> int | None:
    """Return a checkpoint's numeric step, or ``None`` for another directory."""
    match = CHECKPOINT_PATTERN.match(Path(path).name)
    return int(match.group(1)) if match else None


def validate_checkpoint(path: str | Path, *, full_state: bool = True) -> list[str]:
    """Return missing or inconsistent checkpoint requirements.

    ``full_state=False`` accepts a weights-only adapter. A true Trainer resume
    requires optimizer, scheduler, and trainer state in addition to the adapter.
    """
    checkpoint = Path(path)
    problems: list[str] = []
    if not checkpoint.is_dir():
        return ["checkpoint directory does not exist"]
    if checkpoint_step(checkpoint) is None:
        problems.append("directory name must match checkpoint-<step>")

    required = ADAPTER_FILES + (TRAINER_STATE_FILES if full_state else ())
    for filename in required:
        candidate = checkpoint / filename
        if not candidate.is_file():
            problems.append(f"missing {filename}")
        elif candidate.stat().st_size == 0:
            problems.append(f"empty {filename}")

    state_path = checkpoint / "trainer_state.json"
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            directory_step = checkpoint_step(checkpoint)
            if directory_step is not None and state.get("global_step") != directory_step:
                problems.append("trainer_state global_step does not match directory")
        except (OSError, json.JSONDecodeError):
            problems.append("trainer_state.json is not valid JSON")
    return problems


def find_latest_valid_checkpoint(
    output_dir: str | Path, *, full_state: bool = True
) -> Path | None:
    """Find the highest-step checkpoint that passes validation."""
    root = Path(output_dir)
    if not root.is_dir():
        return None
    candidates = (
        path for path in root.iterdir() if path.is_dir() and checkpoint_step(path) is not None
    )
    for candidate in sorted(candidates, key=lambda path: checkpoint_step(path) or -1, reverse=True):
        if not validate_checkpoint(candidate, full_state=full_state):
            return candidate
    return None


def sha256_manifest(paths: Iterable[str | Path]) -> dict[str, str]:
    """Build a SHA-256 manifest for checkpoint integrity verification."""
    manifest: dict[str, str] = {}
    for raw_path in paths:
        path = Path(raw_path)
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        manifest[path.name] = digest.hexdigest()
    return manifest

