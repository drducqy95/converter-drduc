#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyze how much of the current PhienAm layer is covered by richer references.

Outputs:
- JSON report under data/dictionaries/_phienam_coverage_report.json
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.md_dictionary_compiler import parse_bulk_md


DICT_ROOT = PROJECT_ROOT / "data" / "dictionaries"
REPORT_PATH = DICT_ROOT / "_phienam_coverage_report.json"


def load_sources() -> dict[str, set[str]]:
    """Load source keys from relevant Markdown dictionary files."""
    files = {
        "phienam": DICT_ROOT / "global" / "phien_am" / "_bulk_phienam.md",
        "thieuchuu": DICT_ROOT / "global" / "phien_am" / "_bulk_thieuchuu.md",
        "lacviet": DICT_ROOT / "global" / "reference_vi" / "_bulk_lacviet.md",
        "cedict": DICT_ROOT / "global" / "en_vi" / "_bulk_cedict.md",
    }

    loaded: dict[str, set[str]] = {}
    for name, path in files.items():
        if not path.exists():
            loaded[name] = set()
            continue
        loaded[name] = {entry.source for entry in parse_bulk_md(str(path))}

    return loaded


def main():
    loaded = load_sources()

    phienam = loaded["phienam"]
    thieuchuu = loaded["thieuchuu"]
    lacviet = loaded["lacviet"]
    cedict = loaded["cedict"]

    rich_union = thieuchuu | lacviet | cedict
    covered_any = phienam & rich_union
    residual = phienam - rich_union

    report = {
        "phienam_total": len(phienam),
        "thieuchuu_total": len(thieuchuu),
        "lacviet_total": len(lacviet),
        "cedict_total": len(cedict),
        "covered_by_thieuchuu": len(phienam & thieuchuu),
        "covered_by_lacviet": len(phienam & lacviet),
        "covered_by_cedict": len(phienam & cedict),
        "covered_by_any_rich_reference": len(covered_any),
        "residual_after_rich_reference_union": len(residual),
        "coverage_ratio": round(len(covered_any) / len(phienam), 6) if phienam else 0.0,
        "residual_ratio": round(len(residual) / len(phienam), 6) if phienam else 0.0,
        "residual_sample": sorted(residual)[:200],
    }

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("PhienAm coverage analysis")
    print(f"  phienam_total: {report['phienam_total']}")
    print(f"  covered_by_thieuchuu: {report['covered_by_thieuchuu']}")
    print(f"  covered_by_lacviet: {report['covered_by_lacviet']}")
    print(f"  covered_by_cedict: {report['covered_by_cedict']}")
    print(f"  covered_by_any_rich_reference: {report['covered_by_any_rich_reference']}")
    print(f"  residual_after_union: {report['residual_after_rich_reference_union']}")
    print(f"  coverage_ratio: {report['coverage_ratio']}")
    print(f"  report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
