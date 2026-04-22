#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
clean_latin_num.py

Uses the newly injected ArabicUnitConverter logic inside NumberConverter
to dynamically test every entry in _vietphrase_latin_num.md.
If the engine can parse it out-of-the-box (consumed == len), the entry
is safely deleted from the dictionary.
"""

import sys
from pathlib import Path

# Add project root to path so we can import src
PROJECT_ROOT = Path("d:/Converter by DrDuc")
sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.number_converter import NumberConverter

def load_md_dict(filepath: Path) -> tuple[list[str], list[tuple[str, str]]]:
    if not filepath.exists():
        return [], []
        
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        in_header = True
        dash_count = 0
        lines = f.readlines()
        
        header_lines = []
        
        for i, line in enumerate(lines):
            line_str = line.strip()
            if in_header:
                header_lines.append(line)
                if line_str == '---':
                    dash_count += 1
                    if dash_count == 2:
                        in_header = False
                continue
                
            if line_str.startswith('| source'):
                header_lines.append(line)
                continue
            if line_str.startswith('| ---'):
                header_lines.append(line)
                continue
                
            if line_str.startswith('|'):
                parts = [p.strip() for p in line_str.split('|') if p.strip()]
                if len(parts) >= 2:
                    entries.append((parts[0], parts[1]))
                    
    return header_lines, entries

def main():
    vp_path = PROJECT_ROOT / "data/dictionaries/global/vietphrase/_vietphrase_latin_num.md"
    vp_headers, vp_entries = load_md_dict(vp_path)
    
    converter = NumberConverter()
    
    kept_entries = []
    removed_entries = 0
    
    for src, tgt in vp_entries:
        stripped_src = src.strip()
        result = converter.try_convert(stripped_src, 0)
        
        # If the Arabic Unit Parser successfully consumed the ENTIRE source string
        if result and result.conv_type in ("arabic_unit", "arabic_date") and result.consumed == len(stripped_src):
            removed_entries += 1
        else:
            kept_entries.append((src, tgt))
            
    print(f"Original _vietphrase_latin_num.md size: {len(vp_entries)}")
    print(f"Dynamically parsed entries cleanly removed: {removed_entries}")
    print(f"Optimized _vietphrase_latin_num.md size: {len(kept_entries)}")
    
    # Write back optimized file
    new_header = []
    for line in vp_headers:
        if line.startswith("entries_count:"):
            new_header.append(f"entries_count: {len(kept_entries)}\n")
        else:
            new_header.append(line)
            
    with open(vp_path, 'w', encoding='utf-8') as f:
        f.writelines(new_header)
        for src, tgt in kept_entries:
            f.write(f"| {src} | {tgt} |\n")

if __name__ == '__main__':
    main()
