#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import re
from pathlib import Path

def main():
    fp = Path("d:/Converter by DrDuc/data/dictionaries/global/vietphrase/_vietphrase_latin_num.md")
    if not fp.exists():
        print("File not found")
        return
        
    date_patterns = 0
    unit_patterns = collections.defaultdict(int)
    english_words = 0
    other = 0
    
    with open(fp, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line or not line.startswith('|') or line.startswith('| source') or line.startswith('| ---'):
            continue
            
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) < 2: continue
        
        src = parts[0]
        
        # Check Date pattern: e.g. 01月 01 号 or 01月1日
        if re.search(r'\d+月\s*\d+\s*[号日]', src):
            date_patterns += 1
            continue
            
        # Check Decimal / Integer + Unit: e.g. 1 米, 1.5 米, 10 斤重
        m = re.match(r'^[\d\.]+\s*(.+)$', src)
        if m:
            unit = m.group(1).strip()
            # If unit contains no digits (just characters like 米, 公分, W, 万)
            if not any(char.isdigit() for char in unit):
                unit_patterns[unit] += 1
                continue
                
        # Pure English / Latin characters (no numbers): e.g. "bitch", "A级"
        if re.match(r'^[a-zA-Z\s]+$', src):
            english_words += 1
            continue
            
        # Other
        other += 1

    print(f"Total Date Patterns (e.g. 01月 01 号): {date_patterns}")
    print(f"Total English Only (e.g. bitch): {english_words}")
    print(f"Total Unknown/Mixed: {other}")
    
    print("\nTop 50 Most Frequent Hardcoded Units (Number + Unit):")
    sorted_units = sorted(unit_patterns.items(), key=lambda x: x[1], reverse=True)
    c = 0
    total_unit_entries = 0
    for unit, count in sorted_units:
        total_unit_entries += count
        if c < 50:
            print(f"[{unit}]: {count} entries")
            c += 1
            
    print(f"\nTotal Hardcoded Unit Entries: {total_unit_entries}")

if __name__ == '__main__':
    main()
