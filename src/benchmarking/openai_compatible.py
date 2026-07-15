"""Concurrency benchmark for a local OpenAI-compatible inference endpoint."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import fmean
from typing import Sequence


@dataclass(frozen=True)
class RequestMeasurement:
    success: bool
    latency_seconds: float
    output_tokens: int = 0
    error: str = ""


@dataclass(frozen=True)
class BenchmarkResult:
    concurrency: int
    requests: int
    successes: int
    failures: int
    throughput_rps: float
    output_tokens_per_second: float
    mean_latency_seconds: float
    p50_latency_seconds: float
    p95_latency_seconds: float
    p99_latency_seconds: float


def percentile(values: Sequence[float], quantile: float) -> float:
    """Compute a linearly interpolated percentile for 0 <= quantile <= 1."""
    if not values:
        return 0.0
    if not 0 <= quantile <= 1:
        raise ValueError("quantile must be between zero and one")
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def summarize(
    concurrency: int, measurements: Sequence[RequestMeasurement], elapsed_seconds: float
) -> BenchmarkResult:
    successful = [item for item in measurements if item.success]
    latencies = [item.latency_seconds for item in successful]
    successes = len(successful)
    safe_elapsed = max(elapsed_seconds, 1e-9)
    return BenchmarkResult(
        concurrency=concurrency,
        requests=len(measurements),
        successes=successes,
        failures=len(measurements) - successes,
        throughput_rps=successes / safe_elapsed,
        output_tokens_per_second=sum(item.output_tokens for item in successful) / safe_elapsed,
        mean_latency_seconds=fmean(latencies) if latencies else 0.0,
        p50_latency_seconds=percentile(latencies, 0.50),
        p95_latency_seconds=percentile(latencies, 0.95),
        p99_latency_seconds=percentile(latencies, 0.99),
    )


def request_completion(
    *, endpoint: str, model: str, prompt: str, max_tokens: int, timeout: float
) -> RequestMeasurement:
    payload = json.dumps(
        {"model": model, "prompt": prompt, "max_tokens": max_tokens, "temperature": 0.0}
    ).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(endpoint, data=payload, headers=headers, method="POST")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        usage = body.get("usage") or {}
        return RequestMeasurement(
            success=True,
            latency_seconds=time.perf_counter() - started,
            output_tokens=int(usage.get("completion_tokens") or 0),
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return RequestMeasurement(
            success=False,
            latency_seconds=time.perf_counter() - started,
            error=str(exc),
        )


def run_level(
    *, endpoint: str, model: str, prompt: str, concurrency: int,
    requests: int, max_tokens: int, timeout: float
) -> BenchmarkResult:
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(
                request_completion,
                endpoint=endpoint,
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                timeout=timeout,
            )
            for _ in range(requests)
        ]
        measurements = [future.result() for future in as_completed(futures)]
    return summarize(concurrency, measurements, time.perf_counter() - started)


def parse_concurrency(value: str) -> list[int]:
    levels = [int(item.strip()) for item in value.split(",") if item.strip()]
    if not levels or any(level < 1 for level in levels):
        raise argparse.ArgumentTypeError("provide positive comma-separated integers")
    return levels


def write_csv(results: Sequence[BenchmarkResult], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(result) for result in results)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000/v1/completions")
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt", default="Explain least privilege in one paragraph.")
    parser.add_argument("--concurrency", type=parse_concurrency, default=[1, 4, 8, 16])
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", type=Path, default=Path("results/benchmark.csv"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    results = [
        run_level(
            endpoint=args.endpoint,
            model=args.model,
            prompt=args.prompt,
            concurrency=level,
            requests=args.requests,
            max_tokens=args.max_tokens,
            timeout=args.timeout,
        )
        for level in args.concurrency
    ]
    write_csv(results, args.output)
    print(json.dumps([asdict(result) for result in results], indent=2))


if __name__ == "__main__":
    main()
