#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
route_misplaced.py

Reads all temporary _misplaced markdown files, extracts the intended target
category from the 3rd column, appends the entries to the correct dictionary
files, and recalculates entry counts.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path("d:/Converter by DrDuc")
OUTPUT_DIR = PROJECT_ROOT / "data/dictionaries/global/names"

MISPLACED_FILES = [
    "_names_org_misplaced.md",
    "_names_misc_misplaced.md",
    "_names_person_misplaced.md",
    "_names_person_east_misplaced.md",
    "_names_western_misplaced.md"
]

CORE_CATEGORIES = [
    "loc_east", "loc_west", 
    "org_east", "org_west", 
    "misc_east", "misc_west", 
    "person_east", "person_west"
]

def load_file(filepath: Path) -> tuple[list[str], list[list[str]]]:
    if not filepath.exists():
        return [], []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    entries = []
    header_end_idx = 0
    dash_count = 0
    for i, line in enumerate(lines):
        line = line.strip()
        if line == '---':
            dash_count += 1
            if dash_count == 2:
                header_end_idx = i
                break
                
    for i, line in enumerate(lines):
        if line.startswith('| source'):
            header_end_idx = i + 1
            break
            
    header_lines = lines[:header_end_idx+1]
    
    for line in lines[header_end_idx+1:]:
        line = line.strip()
        if not line or not line.startswith('|'):
            continue
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) >= 2:
            entries.append(parts)
            
    return header_lines, entries

def main():
    # 1. Load core files into memory
    core_db = {}
    for cat in CORE_CATEGORIES:
        fp = OUTPUT_DIR / f"_names_{cat}.md"
        headers, entries = load_file(fp)
        # Store just [source, target]
        core_db[cat] = {
            'headers': headers,
            'entries': [(r[0], r[1]) for r in entries if len(r) >= 2],
            'filepath': fp
        }
        
    routed_count = 0
    
    # 2. Process misplaced files
    for m_file in MISPLACED_FILES:
        fp = OUTPUT_DIR / m_file
        if not fp.exists():
            print(f"Skipping {m_file}, not found.")
            continue
            
        _, entries = load_file(fp)
        for row in entries:
            if len(row) < 3:
                # Fallback to person_east if no category specified by accident
                target_cat = "person_east"
            else:
                cat_raw = row[2]
                # Cleanup string: "Tương lai -> loc_east" -> "loc_east"
                cat_clean = cat_raw.replace("Tương lai ->", "").strip()
                # Cleanup string: "loc_east/person_east" -> "loc_east"
                cat_clean = cat_clean.split('/')[0].strip()
                target_cat = cat_clean
                
            if target_cat not in core_db:
                print(f"Warning: Unknown category '{target_cat}' for {row[0]}. Defaulting to person_east.")
                target_cat = "person_east"
                
            core_db[target_cat]['entries'].append((row[0], row[1]))
            routed_count += 1
            
        # Optional: delete misplaced file after processing
        os.remove(fp)
        print(f"Routed entries from {m_file} and deleted the file.")

    # 3. Rewrite core files
    for cat in CORE_CATEGORIES:
        data = core_db[cat]
        headers = data['headers']
        entries = data['entries']
        
        new_header = []
        for line in headers:
            if line.startswith('entries_count:'):
                new_header.append(f"entries_count: {len(entries)}\n")
            else:
                new_header.append(line)
                
        with open(data['filepath'], 'w', encoding='utf-8') as f:
            f.writelines(new_header)
            for src, tgt in entries:
                f.write(f"| {src} | {tgt} |\n")
                
        print(f"Updated _names_{cat}.md -> {len(entries)} items")
        
    print(f"\nSuccessfully routed {routed_count} misplaced items across all dictionaries!")

if __name__ == '__main__':
    main()
