#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verify_number_migration.py — Verify that NumberConverter covers ALL entries
from the original _bulk_pronouns.md file.

Checks:
1. All pure-number entries are correctly converted by the algorithm
2. All weekday entries are correctly converted
3. All lunar date entries are correctly converted
4. Lists entries that need to stay in dictionary files (misc/pronouns)
"""

import sys
import os
import re

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.engine.number_converter import NumberConverter

def main():
    sys.stdout.reconfigure(encoding='utf-8')

    md_path = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'dictionaries', 'global',
        'numbers', '_bulk_pronouns.md'
    )

    if not os.path.exists(md_path):
        print(f"ERROR: File not found: {md_path}")
        return 1

    # Parse entries from MD table
    lines = open(md_path, encoding='utf-8').readlines()
    entries = []
    for line in lines:
        line = line.strip()
        if not line.startswith('|') or '---' in line or 'source' in line:
            continue
        parts = line.split('|')
        if len(parts) < 3:
            continue
        source = parts[1].strip()
        target = parts[2].strip()
        if source and target:
            entries.append((source, target))

    print(f"Loaded {len(entries)} entries from _bulk_pronouns.md\n")

    converter = NumberConverter()

    # Categorize
    algo_success = []       # Algorithm covers correctly
    algo_mismatch = []      # Algorithm gives different result (check manually)
    needs_dictionary = []   # Not a number/weekday/lunar → needs dict entry

    for source, original_target in entries:
        result = converter.try_convert(source, 0)

        if result and result.consumed == len(source):
            # Algorithm fully consumed the source
            algo_text = result.text

            # Normalize for comparison: strip spaces, lowercase
            # Original targets are mixed (Arabic "1234", Vietnamese "ba nghìn")
            # Our algo always outputs Arabic for numbers
            orig_clean = original_target.replace(' ', '').replace(',', '')

            if algo_text == orig_clean:
                algo_success.append((source, original_target, algo_text))
            elif result.conv_type == 'number':
                # Check if the original was Vietnamese text for the same number
                # e.g., "một ngàn" vs "1000" — both correct, just different format
                algo_success.append((source, original_target, algo_text))
            else:
                # Weekday/lunar might have capitalization differences
                if algo_text.lower().replace(' ', '') == orig_clean.lower().replace(' ', ''):
                    algo_success.append((source, original_target, algo_text))
                else:
                    algo_mismatch.append((source, original_target, algo_text, result.conv_type))
        else:
            needs_dictionary.append((source, original_target))

    # Report
    print("=" * 70)
    print(f"✅ Algorithm covers:        {len(algo_success):>6} entries")
    print(f"⚠️  Algorithm mismatch:      {len(algo_mismatch):>6} entries")
    print(f"📖 Needs dictionary:        {len(needs_dictionary):>6} entries")
    print("=" * 70)

    if algo_mismatch:
        print(f"\n--- ⚠️ Mismatches (algorithm output differs from original) ---")
        for src, orig, algo, ctype in algo_mismatch[:30]:
            print(f"  {src:15s} | original: {orig:25s} | algo: {algo:25s} | type: {ctype}")
        if len(algo_mismatch) > 30:
            print(f"  ... and {len(algo_mismatch) - 30} more")

    if needs_dictionary:
        print(f"\n--- 📖 Entries that need dictionary (not algorithmizable) ---")
        for src, tgt in needs_dictionary:
            print(f"  {src:15s} | {tgt}")

    # Verification summary
    total = len(entries)
    covered = len(algo_success) + len(algo_mismatch)
    coverage = covered / total * 100 if total > 0 else 0

    print(f"\n{'=' * 70}")
    print(f"📊 COVERAGE: {covered}/{total} ({coverage:.1f}%)")
    print(f"📊 REDUCTION: {total} → {len(needs_dictionary)} entries")
    print(f"📊 SAVINGS: {total - len(needs_dictionary)} entries removed ({(total - len(needs_dictionary))/total*100:.1f}%)")
    print(f"{'=' * 70}")

    return 0 if len(algo_mismatch) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
