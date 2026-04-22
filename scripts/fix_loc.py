#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fix_loc.py 

Manually fixes misclassified entries in _names_loc_east.md and _names_loc_west.md.
Moves misclassified items to their proper category files.
"""

import os
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path("d:/Converter by DrDuc")
OUTPUT_DIR = PROJECT_ROOT / "data/dictionaries/global/names"

# Manual mapping mapping of source -> target category string
FIX_MAP = {
    # Move to loc_east
    "泰国": "loc_east",
    "孟加拉国": "loc_east",
    "杭州市": "loc_east",
    "杭州": "loc_east",
    "扬州市": "loc_east",
    "廣州": "loc_east",
    "扬州": "loc_east",
    "珠峰": "loc_east",
    "亚太地区": "loc_east",
    "兰州": "loc_east",
    "南沙群岛": "loc_east",
    "广州市": "loc_east",
    "泽州": "loc_east",
    "梧州市": "loc_east",
    "小州": "loc_east",
    "渝州": "loc_east",
    
    # Move to person_east
    "梁紅玉": "person_east",
    "胡志明": "person_east",
    "霍明海": "person_east",
    "阮珠江": "person_east",
    "珠珠": "person_east",
    "珠衡": "person_east",
    "罗洪": "person_east",
    
    # Move to misc_east
    "明鉴表": "misc_east",
    "鸣鸿": "misc_east",
    
    # Move to misc_west
    "大犬座": "misc_west",
    "大本钟": "misc_west",
    
    # Move to org_east
    "胡志明博物馆": "org_east",
    "香江集团": "org_east"
}

def load_file(filepath: Path) -> tuple[list[str], list[tuple[str, str]]]:
    """Loads a markdown dictionary file, returning its header lines and entries."""
    if not filepath.exists():
        return [], []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    frontmatter = []
    entries = []
    in_table = False
    
    # Read header and table structure
    header_end_idx = 0
    dash_count = 0
    for i, line in enumerate(lines):
        line = line.strip()
        if line == '---':
            dash_count += 1
            if dash_count == 2:
                header_end_idx = i
                break
                
    # Frontmatter + table headers
    for i, line in enumerate(lines):
        if line.startswith('| source'):
            header_end_idx = i + 1  # includes `| --- | --- |`
            break
            
    header_lines = lines[:header_end_idx+1]
    
    for line in lines[header_end_idx+1:]:
        line = line.strip()
        if not line or not line.startswith('|'):
            continue
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) >= 2:
            entries.append((parts[0], parts[1]))
            
    return header_lines, entries

def write_file(filepath: Path, base_header: list[str], entries: list[tuple[str, str]], cat_name: str):
    """Writes back the modified file with updated counts."""
    # Build updated frontmatter
    new_header = []
    for line in base_header:
        if line.startswith('entries_count:'):
            new_header.append(f"entries_count: {len(entries)}\n")
        else:
            new_header.append(line)
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_header)
        for src, tgt in entries:
            f.write(f"| {src} | {tgt} |\n")

def main():
    files_to_load = ["loc_east", "loc_west", "person_east", "misc_east", "misc_west", "org_east"]
    
    # Dict of Category -> (HeaderLines, EntriesList)
    mem_db = {}
    
    print("Loading files...")
    for cat in files_to_load:
        fp = OUTPUT_DIR / f"_names_{cat}.md"
        headers, entries = load_file(fp)
        mem_db[cat] = {
            'headers': headers,
            'entries': entries,
            'filepath': fp
        }
        
    print("Repairing entries...")
    for src_cat in ["loc_east", "loc_west"]:
        kept_entries = []
        for src, tgt in mem_db[src_cat]['entries']:
            if src in FIX_MAP:
                target_cat = FIX_MAP[src]
                print(f"Moving '{src}' from {src_cat} to {target_cat}")
                mem_db[target_cat]['entries'].append((src, tgt))
            else:
                kept_entries.append((src, tgt))
        mem_db[src_cat]['entries'] = kept_entries

    print("Saving updated files...")
    for cat in files_to_load:
        data = mem_db[cat]
        write_file(data['filepath'], data['headers'], data['entries'], cat)
        print(f"Updated _names_{cat}.md: {len(data['entries'])} entries")

if __name__ == '__main__':
    main()
