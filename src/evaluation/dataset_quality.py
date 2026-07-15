"""Streaming quality checks for cybersecurity instruction datasets."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import fmean
from typing import Any, Iterable, Iterator


@dataclass
class QualityReport:
    records: int = 0
    valid_records: int = 0
    malformed_json: int = 0
    missing_required_fields: int = 0
    empty_questions: int = 0
    empty_answers: int = 0
    short_answers: int = 0
    duplicate_questions: int = 0
    control_id_coverage: float = 0.0
    source_coverage: float = 0.0
    average_question_chars: float = 0.0
    average_answer_chars: float = 0.0

    @property
    def valid_rate(self) -> float:
        return self.valid_records / self.records if self.records else 0.0

    def to_dict(self) -> dict[str, int | float]:
        result = asdict(self)
        result["valid_rate"] = self.valid_rate
        return result


def iter_jsonl(path: str | Path) -> Iterator[tuple[int, dict[str, Any] | None]]:
    """Yield line number and decoded object; malformed lines yield ``None``."""
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
                yield line_number, value if isinstance(value, dict) else None
            except json.JSONDecodeError:
                yield line_number, None


def _normalized_digest(value: str) -> bytes:
    normalized = " ".join(value.casefold().split())
    return hashlib.blake2b(normalized.encode("utf-8"), digest_size=16).digest()


def evaluate_records(
    records: Iterable[dict[str, Any] | None], *, minimum_answer_chars: int = 150
) -> QualityReport:
    """Evaluate schema, completeness, length, metadata coverage, and duplicates."""
    report = QualityReport()
    question_lengths: list[int] = []
    answer_lengths: list[int] = []
    question_digests: set[bytes] = set()
    control_ids = 0
    sources = 0

    for record in records:
        report.records += 1
        if record is None:
            report.malformed_json += 1
            continue
        if "question" not in record or "answer" not in record:
            report.missing_required_fields += 1
            continue

        question = str(record.get("question") or "").strip()
        answer = str(record.get("answer") or "").strip()
        if not question:
            report.empty_questions += 1
        if not answer:
            report.empty_answers += 1
        if not question or not answer:
            continue

        report.valid_records += 1
        question_lengths.append(len(question))
        answer_lengths.append(len(answer))
        if len(answer) < minimum_answer_chars:
            report.short_answers += 1

        digest = _normalized_digest(question)
        if digest in question_digests:
            report.duplicate_questions += 1
        question_digests.add(digest)

        if str(record.get("control_id") or "").strip():
            control_ids += 1
        if str(record.get("source") or record.get("source_document") or "").strip():
            sources += 1

    denominator = report.valid_records or 1
    report.control_id_coverage = control_ids / denominator
    report.source_coverage = sources / denominator
    report.average_question_chars = fmean(question_lengths) if question_lengths else 0.0
    report.average_answer_chars = fmean(answer_lengths) if answer_lengths else 0.0
    return report


def evaluate_jsonl(path: str | Path, *, minimum_answer_chars: int = 150) -> QualityReport:
    records = (record for _, record in iter_jsonl(path))
    return evaluate_records(records, minimum_answer_chars=minimum_answer_chars)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="JSONL dataset to inspect")
    parser.add_argument("--minimum-answer-chars", type=int, default=150)
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = evaluate_jsonl(args.dataset, minimum_answer_chars=args.minimum_answer_chars)
    rendered = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
