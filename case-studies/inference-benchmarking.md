# Case study: inference concurrency benchmarking

## Executive summary and evidence status

Historical notes summarize an OpenAI-compatible vLLM concurrency experiment across four individual GPU endpoints. The highest reported aggregate was 55.23 requests per second at concurrency 350 on an RTX PRO 6000 Max-Q endpoint, with 6.07-second mean latency and no reported failures.

**Evidence status: historical / rerun required.** The request-level observations, software manifest, model hash, launch arguments, and telemetry were not retained with the summary. The figures below are useful for designing a reproducible rerun, but they are not claimed as verified current performance or a universal hardware ranking.

## Method

- Model: `Qwen/Qwen2.5-3B-Instruct`
- Endpoint runtime: vLLM
- Request: one security-control Q&A generation prompt
- Prompt size: approximately 600–700 tokens in the historical test
- Maximum output: 256 tokens
- Sustained load: 60 seconds per concurrency level
- Concurrency levels: 50 through 400 in increments of 50
- Metrics: successful requests/second, requests/hour, mean latency, and failures

The historical notes say that the harness maintained the target number of in-flight requests, but the original request-level output is unavailable for independent recalculation. The sanitized implementation in [`src/benchmarking/openai_compatible.py`](../src/benchmarking/openai_compatible.py) reports p50, p95, p99, failures, and output-token throughput without private endpoint identifiers. It is the implementation to use for the rerun; it does not retroactively validate the historical table.

## Historical aggregate table

| Endpoint hardware | Best tested concurrency | Requests/s | Mean latency | Failures |
|---|---:|---:|---:|---:|
| RTX PRO 6000 Max-Q | 350 | 55.23 | 6.07 s | 0 |
| RTX 5090 | 300 | 26.02 | 10.62 s | 0 |
| Radeon AI PRO R9700 endpoint A | 300 | 4.66 | 47.75 s | 0 |
| Radeon AI PRO R9700 endpoint B | 250 | 4.67 | 40.84 s | 0 |

![Historical throughput and latency summary; rerun required](../results/throughput-latency.png)

The chart is a visualization of the retained aggregate CSV, not raw benchmark evidence.

## Interpretation

- The historical table suggests that the RTX PRO 6000 Max-Q saturated near 55 requests/second and that additional concurrency mostly increased latency.
- It suggests that the RTX 5090 plateaued near 26 requests/second and the two Radeon endpoints near 4.6 requests/second under their then-current stacks.
- These observations cannot isolate hardware from runtime maturity, kernels, quantization, clocks, power limits, CPU pressure, or configuration.
- Reported zero HTTP failures does not establish output correctness, multi-hour stability, failover behavior, or recovery.

For an interactive service I would select concurrency from a latency service-level objective, not maximum throughput alone. For offline batch generation, the higher-throughput operating point may be acceptable.

## Improvements to the next experiment

1. Create a sanitized system manifest for the current dual-GPU server: GPU model/count, VRAM, driver, CUDA, kernel, CPU, memory, storage, power limits, and thermal configuration.
2. Record exact vLLM version, container digest, model revision and SHA-256 digest, dtype or quantization, decoding settings, and launch arguments.
3. Warm each endpoint and repeat every level several times in randomized order.
4. Capture request-level prompt/output token counts, time to first token, inter-token latency, end-to-end latency, status, and timestamps.
5. Measure GPU utilization, VRAM, temperature, clock, power, CPU saturation, and host memory pressure.
6. Define latency and error acceptance thresholds before the run; report confidence intervals and raw-to-summary integrity hashes.
7. Run steady-state, burst, saturation, soak, restart/recovery, and degraded-capacity tests separately.
8. Retain the private raw bundle under controlled storage and publish only a reviewed derivative.

## Portfolio takeaway

The operational lesson is that **concurrency is an empirical control knob and evidence needs provenance**. A larger queue can raise aggregate throughput, but after saturation it mainly transfers delay to users. A defensible POC preserves the manifest, workload, raw measurements, hashes, acceptance criteria, and summarized decision together.
