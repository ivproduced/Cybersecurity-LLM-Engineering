"""Rebuild the three portfolio charts from sanitized CSV metrics."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]


def load_training() -> list[dict[str, float]]:
    with (RESULTS / "training-history.csv").open(newline="", encoding="utf-8") as handle:
        return [
            {key: float(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def plot_loss(rows: list[dict[str, float]], field: str, label: str, filename: str) -> None:
    figure, axis = plt.subplots(figsize=(9, 5.2))
    axis.plot(
        [row["step"] for row in rows],
        [row[field] for row in rows],
        color="#2563eb" if field == "training_loss" else "#7c3aed",
        linewidth=2.4,
        marker="o",
        markersize=3.5,
    )
    axis.set_title(f"{label} — retained Gemma 7B LoRA run")
    axis.set_xlabel("Optimizer step")
    axis.set_ylabel("Cross-entropy loss")
    axis.grid(alpha=0.25)
    axis.ticklabel_format(style="plain", axis="x")
    axis.annotate(
        f"step 465,000\n{rows[-1][field]:.4f}",
        (rows[-1]["step"], rows[-1][field]),
        xytext=(-82, 24),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#475569"},
        fontsize=9,
    )
    figure.tight_layout()
    figure.savefig(RESULTS / filename, dpi=180)
    plt.close(figure)


def plot_inference() -> None:
    grouped: dict[str, list[dict[str, float]]] = defaultdict(list)
    with (RESULTS / "inference-benchmark.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            grouped[row["device"]].append(
                {
                    "concurrency": float(row["concurrency"]),
                    "throughput": float(row["throughput_rps"]),
                    "latency": float(row["average_latency_seconds"]),
                }
            )

    figure, (throughput_axis, latency_axis) = plt.subplots(1, 2, figsize=(13, 5.2))
    for color, (device, rows) in zip(COLORS, grouped.items()):
        concurrency = [row["concurrency"] for row in rows]
        throughput_axis.plot(
            concurrency, [row["throughput"] for row in rows], marker="o", label=device, color=color
        )
        latency_axis.plot(
            concurrency, [row["latency"] for row in rows], marker="o", label=device, color=color
        )

    throughput_axis.set_title("Throughput under sustained concurrency")
    throughput_axis.set_ylabel("Successful requests / second")
    latency_axis.set_title("Mean request latency")
    latency_axis.set_ylabel("Seconds")
    for axis in (throughput_axis, latency_axis):
        axis.set_xlabel("Concurrent requests")
        axis.grid(alpha=0.25)
    handles, labels = throughput_axis.get_legend_handles_labels()
    figure.legend(handles, labels, loc="lower center", ncol=2, frameon=False)
    figure.suptitle(
        "Historical vLLM summary · rerun required · Qwen2.5-3B-Instruct",
        fontsize=13,
    )
    figure.tight_layout(rect=(0, 0.12, 1, 0.95))
    figure.savefig(RESULTS / "throughput-latency.png", dpi=180)
    plt.close(figure)


def main() -> None:
    rows = load_training()
    plot_loss(rows, "training_loss", "Training loss", "training-loss.png")
    plot_loss(rows, "evaluation_loss", "Evaluation loss", "evaluation-loss.png")
    plot_inference()


if __name__ == "__main__":
    main()
