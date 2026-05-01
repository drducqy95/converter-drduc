#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Small chapter benchmark for the RBMT production path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter

from src.engine.rbmt_translator import RBMTTranslator


DEFAULT_SAMPLE = "韩立取出掌天瓶。萧炎看见异火。唐三召出魂环。克莱恩记录序列线索。"


def benchmark(text: str, *, iterations: int = 3) -> dict:
    translator = RBMTTranslator()
    timings: list[float] = []
    try:
        for _ in range(max(1, iterations)):
            started = perf_counter()
            result = translator.translate_text(text)
            timings.append((perf_counter() - started) * 1000)
    finally:
        translator.close()
    avg_ms = sum(timings) / len(timings)
    return {
        "iterations": len(timings),
        "chars": len(text),
        "avg_ms": round(avg_ms, 3),
        "min_ms": round(min(timings), 3),
        "max_ms": round(max(timings), 3),
        "chars_per_second": round((len(text) / avg_ms) * 1000, 3) if avg_ms else 0,
        "segments": len(result.segments),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark RBMT chapter translation")
    parser.add_argument("--input", help="Input text file")
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--out", default="reports/performance_benchmark.json")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8") if args.input else DEFAULT_SAMPLE
    report = benchmark(text, iterations=args.iterations)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
