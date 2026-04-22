#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
optimize_1char.py

Removes redundant entries from _vietphrase_1char.md that perfectly match
the pronunciations in _bulk_phienam.md, reducing memory footprint for the Trie.
"""

import os
from pathlib import Path

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
    vp_path = Path("d:/Converter by DrDuc/data/dictionaries/global/vietphrase/_vietphrase_1char.md")
    pa_path = Path("d:/Converter by DrDuc/data/dictionaries/global/phien_am/_bulk_phienam.md")
    
    vp_headers, vp_entries = load_md_dict(vp_path)
    pa_headers, pa_entries = load_md_dict(pa_path)
    
    pa_dict = {src: tgt.lower() for src, tgt in pa_entries}
    
    kept_entries = []
    removed_count = 0
    
    for src, tgt in vp_entries:
        if src in pa_dict and tgt.lower() == pa_dict[src]:
            # Perfect overlap, redundant mapping
            removed_count += 1
        else:
            kept_entries.append((src, tgt))
            
    print(f"Original _vietphrase_1char.md size: {len(vp_entries)}")
    print(f"Redundant entries removed: {removed_count}")
    print(f"Optimized _vietphrase_1char.md size: {len(kept_entries)}")
    
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
