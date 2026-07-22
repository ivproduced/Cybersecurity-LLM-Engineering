"""Scan a repository derivative for common public-release hazards."""

from __future__ import annotations

import argparse
import ipaddress
import re
from dataclasses import dataclass
from pathlib import Path


SKIP_DIRECTORIES = {
    ".git",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}
BINARY_SUFFIXES = {
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".pyc",
    ".so",
    ".zip",
}
FORBIDDEN_ARTIFACT_SUFFIXES = {
    ".cer",
    ".ckpt",
    ".crt",
    ".key",
    ".p12",
    ".pem",
    ".pfx",
    ".pt",
    ".pth",
    ".safetensors",
}
FORBIDDEN_DIRECTORIES = {"raw", "private", "evidence/raw", "security-reports"}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str

    def display(self, root: Path) -> str:
        return f"{self.path.relative_to(root)}:{self.line}: {self.rule}"


def _patterns() -> list[tuple[str, re.Pattern[str]]]:
    # Build credential markers in pieces so this scanner does not flag its own source.
    token_prefix = "h" + "f" + "_"
    openai_prefix = "s" + "k" + "-"
    github_prefix = "g" + "h"
    absolute_root = "/" + r"(?:home|Users|Volumes|srv)/[^\s'\"`]+"
    return [
        ("possible Hugging Face credential", re.compile(r"\b" + token_prefix + r"[A-Za-z0-9]{20,}\b")),
        ("possible API credential", re.compile(r"\b" + openai_prefix + r"(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
        ("possible cloud access key", re.compile(r"\b" + "A" + "K" + "I" + "A" + r"[A-Z0-9]{16}\b")),
        ("possible source-host credential", re.compile(r"\b" + github_prefix + r"[pousr]_[A-Za-z0-9]{20,}\b")),
        ("private machine path", re.compile(absolute_root)),
        ("local-network hostname", re.compile(r"\b(?:[A-Za-z0-9-]+\.)+local\b", re.IGNORECASE)),
        ("private device identifier", re.compile(r"\b(?:GPU|MIG)-[0-9A-Fa-f-]{32,}\b")),
        ("MAC address", re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b")),
    ]


IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(?:password|passwd|secret|token|api[_-]?key|master[_-]?key)\b"
    r"\s*[:=]\s*[\"']?([^\s,\"'\]}]+)"
)
SAFE_VALUE_MARKERS = (
    "${",
    "{{",
    "<",
    "replace",
    "redacted",
    "change_me",
    "example",
    "pending",
    "os.environ",
    "getenv(",
)


def _is_private_address(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    if address.is_loopback:
        return False
    shared_space = ipaddress.ip_network("100" + ".64.0.0/10")
    return address.is_private or address in shared_space


def _assignment_is_safe(value: str) -> bool:
    normalized = value.strip().lower()
    return not normalized or any(marker in normalized for marker in SAFE_VALUE_MARKERS)


def _text_findings(path: Path, root: Path) -> list[Finding]:
    try:
        content = path.read_bytes()
    except OSError:
        return [Finding(path, 1, "file could not be read")]
    if b"\x00" in content or path.suffix.lower() in BINARY_SUFFIXES:
        return []
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return [Finding(path, 1, "non-UTF-8 text or unrecognized binary")]

    findings: list[Finding] = []
    patterns = _patterns()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule, pattern in patterns:
            if pattern.search(line):
                findings.append(Finding(path, line_number, rule))
        for candidate in IPV4.findall(line):
            if _is_private_address(candidate):
                findings.append(Finding(path, line_number, "private or shared-space IP address"))
        for match in SECRET_ASSIGNMENT.finditer(line):
            if not _assignment_is_safe(match.group(1)):
                findings.append(Finding(path, line_number, "literal secret-like assignment"))
    return findings


def scan_repository(root: Path) -> list[Finding]:
    """Scan files beneath root and return release-hazard findings."""
    root = root.resolve()
    findings: list[Finding] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRECTORIES for part in relative.parts):
            continue
        relative_parent = relative.parent.as_posix()
        if path.is_file() and (
            relative_parent in FORBIDDEN_DIRECTORIES
            or any(relative_parent.startswith(f"{item}/") for item in FORBIDDEN_DIRECTORIES)
        ):
            findings.append(Finding(path, 1, "file stored in a forbidden release directory"))
            continue
        if not path.is_file():
            continue
        if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
            findings.append(Finding(path, 1, "environment file must not be released"))
            continue
        if path.suffix.lower() in FORBIDDEN_ARTIFACT_SUFFIXES:
            findings.append(Finding(path, 1, "model, credential, or checkpoint artifact"))
            continue
        if path.suffix.lower() == ".jsonl" and relative.as_posix() != "sample-data/synthetic_examples.jsonl":
            findings.append(Finding(path, 1, "non-sample JSONL data artifact"))
            continue
        findings.extend(_text_findings(path, root))
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    findings = scan_repository(root)
    if findings:
        for finding in findings:
            print(f"ERROR: {finding.display(root)}")
        print(f"Public release check failed: {len(findings)} finding(s)")
        return 1
    print("Public release check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
