#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate universe fingerprints from term-bank JSONL data."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.pipeline.han_variants import han_variants

DEFAULT_UNIVERSES_ROOT = REPO_ROOT / "data" / "term_bank" / "universes"
DEFAULT_OUTPUT = DEFAULT_UNIVERSES_ROOT / "fingerprints.json"

TYPE_WEIGHTS = {
    "person": 2.4,
    "location": 1.8,
    "organization": 1.8,
    "realm": 1.5,
    "technique": 1.5,
    "item": 1.4,
    "weapon": 1.4,
    "creature": 1.2,
    "title": 1.1,
    "term": 1.0,
}

MANUAL_SEEDS = {
    "pham_nhan_tu_tien": [
        ("韓立", "person", 3.2),
        ("南宮婉", "person", 2.8),
        ("厲飛雨", "person", 2.4),
        ("掌天瓶", "item", 2.5),
        ("黃楓谷", "location", 2.0),
        ("靈根", "realm", 1.7),
        ("築基", "realm", 1.6),
        ("元嬰", "realm", 1.6),
    ],
    "dau_pha_thuong_khung": [
        ("蕭炎", "person", 3.2),
        ("藥塵", "person", 2.8),
        ("藥老", "person", 2.6),
        ("異火", "item", 2.2),
        ("斗氣", "realm", 1.9),
        ("斗之氣", "realm", 1.7),
        ("斗帝", "realm", 1.7),
        ("烏坦城", "location", 1.8),
    ],
    "bleach": [
        ("黑崎一護", "person", 3.2),
        ("朽木露琪亞", "person", 2.4),
        ("斬魄刀", "weapon", 2.4),
        ("死神", "title", 1.8),
        ("尸魂界", "location", 1.8),
    ],
    "naruto": [
        ("漩渦鳴人", "person", 3.2),
        ("宇智波佐助", "person", 2.7),
        ("旗木卡卡西", "person", 2.3),
        ("影分身", "technique", 2.4),
        ("螺旋丸", "technique", 2.2),
        ("火影", "title", 1.9),
        ("木葉忍者村", "location", 1.8),
    ],
    "one_piece": [
        ("蒙奇·D·路飛", "person", 3.2),
        ("草帽海賊團", "organization", 2.4),
        ("惡魔果實", "item", 2.2),
        ("霸氣", "technique", 2.0),
    ],
    "harry_potter": [
        ("哈利·波特", "person", 3.2),
        ("霍格沃茨", "location", 2.5),
        ("魔法部", "organization", 2.0),
        ("魔杖", "item", 1.8),
    ],
    "marvel": [
        ("鋼鐵俠", "person", 3.0),
        ("雷神", "title", 0.6),
        ("復仇者", "organization", 2.3),
        ("阿斯加德", "location", 2.0),
    ],
}

MANUAL_PAIRS = {
    "pham_nhan_tu_tien": [("韓立", "南宮婉", 0.99), ("韓立", "掌天瓶", 0.95)],
    "dau_pha_thuong_khung": [("蕭炎", "藥塵", 0.99), ("蕭炎", "異火", 0.92)],
    "bleach": [("黑崎一護", "斬魄刀", 0.92)],
    "naruto": [("漩渦鳴人", "影分身", 0.92)],
}


def load_records(universes_root: Path) -> dict[str, list[dict]]:
    by_universe: dict[str, list[dict]] = {}
    for terms_path in sorted(universes_root.glob("*/terms.jsonl")):
        universe_id = terms_path.parent.name
        rows: list[dict] = []
        for line in terms_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            payload = json.loads(stripped)
            if isinstance(payload, dict):
                rows.append(payload)
        by_universe[universe_id] = rows
    return by_universe


def collect_terms(record: dict) -> list[str]:
    terms: list[str] = []
    for key in ("source",):
        value = str(record.get(key) or "").strip()
        if value:
            terms.append(value)
    for key in ("aliases", "context_markers", "co_occurring_entities"):
        values = record.get(key) or []
        if isinstance(values, list):
            terms.extend(str(item).strip() for item in values if str(item).strip())
    return [term for term in dict.fromkeys(terms) if len(term) >= 2]


def build_universe_fingerprint(universe_id: str, records: list[dict], global_counts: Counter[str]) -> dict:
    work = next((str(row.get("work") or "") for row in records if row.get("work")), universe_id)
    franchise = next((str(row.get("franchise") or "") for row in records if row.get("franchise")), work)
    term_candidates: dict[str, dict] = {}

    for record in records:
        entity_type = str(record.get("entity_type") or "term")
        confidence = float(record.get("confidence") or 0.86)
        base = TYPE_WEIGHTS.get(entity_type, 1.0)
        for term in collect_terms(record):
            if len(term) < 2:
                continue
            uniqueness = 0.6 if global_counts[term] == 1 and entity_type == "person" else 0.0
            weight = base + uniqueness + (confidence * 0.25)
            current = term_candidates.get(term)
            if current is None or weight > current["weight"]:
                term_candidates[term] = {"term": term, "weight": weight, "type": entity_type, "manual": False}

    for term, entity_type, weight in MANUAL_SEEDS.get(universe_id, []):
        term_candidates[term] = {"term": term, "weight": weight, "type": entity_type, "manual": True}

    ordered_terms = sorted(
        term_candidates.values(),
        key=lambda item: (bool(item.get("manual")), float(item["weight"]), len(str(item["term"]))),
        reverse=True,
    )
    fingerprint_terms = [
        {
            "term": item["term"],
            "weight": round(float(item["weight"]), 3),
            "type": item["type"],
            "variants": han_variants(str(item["term"])),
        }
        for item in ordered_terms[:80]
    ]

    canonical = [
        item["term"]
        for item in ordered_terms
        if item["type"] == "person" and (item.get("manual") or float(item["weight"]) >= 2.2)
    ]
    canonical_chars = list(dict.fromkeys(canonical))[:24]

    pairs = [
        {"pair": [left, right], "confidence": confidence}
        for left, right, confidence in MANUAL_PAIRS.get(universe_id, [])
    ]
    for left, right in zip(canonical_chars, canonical_chars[1:5], strict=False):
        pair = [left, right]
        if left != right and all(existing["pair"] != pair for existing in pairs):
            pairs.append({"pair": pair, "confidence": 0.78})
        if len(pairs) >= 8:
            break

    return {
        "work": work,
        "franchise": franchise,
        "fingerprint_terms": fingerprint_terms,
        "canonical_chars": canonical_chars,
        "co_occurrence_seeds": pairs,
        "exclusion_terms": [],
    }


def generate_fingerprints(universes_root: Path = DEFAULT_UNIVERSES_ROOT, output: Path = DEFAULT_OUTPUT) -> dict:
    records_by_universe = load_records(universes_root)
    global_counts: Counter[str] = Counter()
    for records in records_by_universe.values():
        seen = {term for record in records for term in collect_terms(record)}
        global_counts.update(seen)

    payload = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "universes": {
            universe_id: build_universe_fingerprint(universe_id, records, global_counts)
            for universe_id, records in sorted(records_by_universe.items())
        },
        "config": {
            "multi_universe_threshold": 0.65,
            "min_confidence_for_active": 0.4,
            "fingerprint_base_divisor": 2.0,
            "canonical_char_boost": 3.0,
            "co_occurrence_pair_boost": 5.0,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate data/term_bank/universes/fingerprints.json")
    parser.add_argument("--universes-root", type=Path, default=DEFAULT_UNIVERSES_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    payload = generate_fingerprints(args.universes_root, args.out)
    print(
        json.dumps(
            {"out": str(args.out), "universes": len(payload["universes"])},
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
