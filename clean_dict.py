#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Clean dictionary by removing entries the algorithm now handles."""
import unicodedata, re, sys
sys.path.insert(0, '.')
from src.engine.number_converter import NumberConverter

def normalize(s):
    s = unicodedata.normalize('NFC', s.strip())
    s = re.sub(r'\bmồng\b', 'mùng', s)
    s = re.sub(r'\bngày mùng\b', 'mùng', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip().lower()

def main():
    nc = NumberConverter()
    dict_path = 'data/dictionaries/global/vietphrase/_vietphrase_latin_num.md'
    with open(dict_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    kept, removed = [], []
    for line in lines:
        s = line.strip()
        if not s or s.startswith('#') or s.startswith('---') or s.startswith('category:') or s.startswith('priority:') or s.startswith('source:'):
            kept.append(line)
            continue
        if '|' in s:
            parts = s.split('|')
            if len(parts) >= 3:
                key, val = parts[1].strip(), parts[2].strip()
                if key and val:
                    result = nc.try_convert(key, 0)
                    if result and result.consumed >= len(key) and normalize(result.text) == normalize(val):
                        removed.append((key, val, result.text))
                        continue
        kept.append(line)
    print(f"\n=== Dictionary Cleanup ===")
    print(f"Total: {len(lines)} -> Kept: {len(kept)}, Removed: {len(removed)}")
    if removed:
        print(f"\n--- Sample removed (first 30) ---")
        for key, val, algo in removed[:30]:
            print(f"  {key} | {val}")
    with open(dict_path, 'w', encoding='utf-8') as f:
        f.writelines(kept)
    print(f"\nDone!")

if __name__ == '__main__':
    main()
