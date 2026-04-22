#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Phase 01 benchmark and rebuild workflow."""

import argparse
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.md_dictionary_compiler import DictionaryCompiler
from src.core.trie_engine import TrieEngine
from src.core.luat_nhan_engine import LuatNhanEngine


DEFAULT_DICT_ROOT = PROJECT_ROOT / "data" / "dictionaries"
DEFAULT_DB_PATH = DEFAULT_DICT_ROOT / "_compiled" / "trie_cache.db"
DEFAULT_REPORT_PATH = DEFAULT_DICT_ROOT / "_phase1_benchmark.json"


def benchmark_lookup(trie: TrieEngine, terms: list[str], rounds: int) -> dict:
    start = time.perf_counter()
    for _ in range(rounds):
        for term in terms:
            trie.lookup_exact(term)
    elapsed = time.perf_counter() - start
    total = rounds * len(terms)
    return {
        "total_lookups": total,
        "elapsed_seconds": round(elapsed, 6),
        "microseconds_per_lookup": round((elapsed / total) * 1_000_000, 3),
    }


def benchmark_translation(trie: TrieEngine, sample: str, rounds: int) -> dict:
    start = time.perf_counter()
    for _ in range(rounds):
        trie.translate_text(sample)
    elapsed = time.perf_counter() - start
    return {
        "rounds": rounds,
        "sample_length": len(sample),
        "elapsed_seconds": round(elapsed, 6),
        "milliseconds_per_translation": round((elapsed / rounds) * 1_000, 3),
    }


def load_sqlite_counts(db_path: Path) -> dict:
    import sqlite3

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    counts = {
        "entries": c.execute("SELECT COUNT(*) FROM entries").fetchone()[0],
        "reference_entries": c.execute("SELECT COUNT(*) FROM reference_entries").fetchone()[0],
        "grammar_patterns": c.execute("SELECT COUNT(*) FROM grammar_patterns").fetchone()[0],
        "normalization_rules": c.execute("SELECT COUNT(*) FROM normalization_rules").fetchone()[0],
        "audit_events": c.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0],
        "entry_readings": c.execute("SELECT COUNT(*) FROM entry_readings").fetchone()[0],
        "phienam_runtime": c.execute("SELECT COUNT(*) FROM entries WHERE category='phien_am'").fetchone()[0],
    }
    conn.close()
    return counts


def main():
    parser = argparse.ArgumentParser(description="Benchmark Phase 01 foundation workflow")
    parser.add_argument("--dict-root", default=str(DEFAULT_DICT_ROOT), help="Dictionary root path")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="Compiled SQLite path")
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH), help="Benchmark JSON report path")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild compiled DB before benchmarking")
    parser.add_argument("--lookup-rounds", type=int, default=10000, help="Exact lookup rounds")
    parser.add_argument("--translation-rounds", type=int, default=1000, help="Translation rounds")

    args = parser.parse_args()

    dict_root = Path(args.dict_root)
    db_path = Path(args.db)
    report_path = Path(args.report)

    report: dict = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dict_root": str(dict_root),
        "db_path": str(db_path),
        "rebuild": args.rebuild,
    }

    if args.rebuild:
        compiler = DictionaryCompiler(str(dict_root))
        compile_stats = compiler.compile()
        report["compile"] = compile_stats
        db_path = compiler.db_path
        print("Compile done")
        print(f"  entries_unique: {compile_stats['entries_unique']}")
        print(f"  reference_entries: {compile_stats['reference_entries']}")
        print(f"  audit_events: {compile_stats['audit_events']}")
        print(f"  entry_readings: {compile_stats['entry_readings']}")
        print(f"  phienam_runtime_after_reduction: {compile_stats['phienam_runtime_after_reduction']}")

    trie = TrieEngine()
    trie_load = trie.load_from_sqlite(db_path)
    trie_stats = trie.get_stats()

    luatnhan = LuatNhanEngine()
    luatnhan_count = luatnhan.load_from_sqlite(db_path)
    luatnhan_stats = luatnhan.get_stats()

    lookup_terms = ["修为", "突破", "境界", "灵气", "丹田", "炼丹", "一个人", "天地", "大道", "太阳"]
    translation_sample = "他的修为已经突破了境界，灵气在丹田之中旋转，天地之间的大道若隐若现。"

    lookup_stats = benchmark_lookup(trie, lookup_terms, args.lookup_rounds)
    translation_stats = benchmark_translation(trie, translation_sample, args.translation_rounds)
    db_counts = load_sqlite_counts(db_path)

    report["sqlite_counts"] = db_counts
    report["trie_load"] = trie_load
    report["trie_stats"] = trie_stats
    report["luatnhan"] = {
        "loaded_rules": luatnhan_count,
        **luatnhan_stats,
    }
    report["lookup_benchmark"] = lookup_stats
    report["translation_benchmark"] = translation_stats

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Benchmark summary")
    print(f"  trie_entries: {trie.size}")
    print(f"  reading_fallbacks: {trie_stats['reading_fallbacks']}")
    print(f"  luatnhan_rules: {luatnhan_count}")
    print(f"  lookup_us: {lookup_stats['microseconds_per_lookup']}")
    print(f"  translation_ms: {translation_stats['milliseconds_per_translation']}")
    print(f"  report: {report_path}")


if __name__ == "__main__":
    main()
