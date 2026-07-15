import pytest

from src.benchmarking.openai_compatible import RequestMeasurement, percentile, summarize


def test_percentile_interpolates() -> None:
    assert percentile([1.0, 2.0, 3.0, 4.0], 0.5) == 2.5
    assert percentile([], 0.95) == 0.0
    with pytest.raises(ValueError):
        percentile([1.0], 1.1)


def test_summary_separates_failures_and_token_rate() -> None:
    measurements = [
        RequestMeasurement(True, 1.0, output_tokens=10),
        RequestMeasurement(True, 2.0, output_tokens=20),
        RequestMeasurement(False, 0.5, error="timeout"),
    ]
    result = summarize(4, measurements, elapsed_seconds=2.0)
    assert result.successes == 2
    assert result.failures == 1
    assert result.throughput_rps == 1.0
    assert result.output_tokens_per_second == 15.0
    assert result.mean_latency_seconds == 1.5
