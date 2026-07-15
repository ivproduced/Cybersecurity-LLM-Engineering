from pathlib import Path

from src.evaluation.dataset_quality import evaluate_records, iter_jsonl


def test_quality_report_finds_schema_and_content_issues() -> None:
    records = [
        {
            "question": "How should access be reviewed?",
            "answer": "Use an approved, periodic review process with an accountable owner.",
            "control_id": "EX-1",
            "source": "synthetic",
        },
        {
            "question": "  HOW should access be reviewed? ",
            "answer": "Duplicate question with normalized spacing and case.",
        },
        {"question": "Missing answer"},
        None,
    ]
    report = evaluate_records(records, minimum_answer_chars=80)
    assert report.records == 4
    assert report.valid_records == 2
    assert report.malformed_json == 1
    assert report.missing_required_fields == 1
    assert report.duplicate_questions == 1
    assert report.short_answers == 2
    assert report.control_id_coverage == 0.5
    assert report.source_coverage == 0.5


def test_empty_dataset_has_zero_rates() -> None:
    report = evaluate_records([])
    assert report.valid_rate == 0.0
    assert report.average_answer_chars == 0.0


def test_jsonl_reader_ignores_blank_lines(tmp_path: Path) -> None:
    dataset = tmp_path / "sample.jsonl"
    dataset.write_text('\n{"question": "q", "answer": "a"}\n\n', encoding="utf-8")
    assert list(iter_jsonl(dataset)) == [(2, {"question": "q", "answer": "a"})]
