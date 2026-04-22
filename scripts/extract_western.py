#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
extract_western.py

Deep heuristic script to extract remaining Western names and locations
from _names_person_east.md.
"""

import os
from pathlib import Path
import re

OUTPUT_DIR = Path("d:/Converter by DrDuc/data/dictionaries/global/names")

VN_DIACRITICS = set("áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ")

# Characters purely used for Western transliterations in Chinese
WEST_PHONETIC_CHARS = set(
    "斯克尔特斯拉图格巴亚姆诺夫奇波顿瓦辛普罗伦维阿玛奥代盖德雷尼索曼提比吉卡佩霍基库苏柏布塔伊恩萨穆"
    "厄帕俄荷鲁席森萨多利吉普贝芬塔希马其逊阿史那丘比特墨尔本达鲁"
)

# Common western places identified from visual inspection
WEST_COUNTRIES_CITIES = [
    'ecuador', 'tuvalu', 'bulgaria', 'liberia', 'tahiti', 'antigua', 'mali', 'macedonia', 
    'turkey', 'ukraine', 'mongolia', 'angola', 'senegal', 'guinea', 'benin', 'egypt', 
    'mumbai', 'argentina', 'uruguay', 'monaco', 'melbourne', 'turing', 'portugal', 
    'versailles', 'cameroon', 'guatemala', 'malta', 'gabon', 'corcovado', 'haiti', 
    'guyana', 'yemen', 'sultan', 'burundi', 'hungary', 'columbia', 'peru', 'sierra leone', 
    'toronto', 'dubai', 'morocco', 'italy', 'chad', 'israel', 'comoros', 'uganda', 
    'georgia', 'cape verde', 'bhutan', 'lebanon', 'el salvador', 'somalia', 'philippines', 
    'libya', 'moldova', 'san marino', 'syria', 'suriname', 'bermuda', 'finland', 'nauru', 
    'namibia', 'utrecht', 'gambia', 'belgium', 'siberia', 'puerto rico', 'panama', 'ghana',
    "Ai Cập", "Bồ Đào Nha", "Tây Ban Nha", "Ý", "Nga", "Đức", "Phần Lan", "Thổ Nhĩ Kỳ"
]

def is_western(source, target):
    target_lower = target.lower()
    
    # 1. Matches known western countries
    for c in WEST_COUNTRIES_CITIES:
        if c in target_lower:
            return "loc_west"

    # 2. Check for English strings in target (e.g. "Mathison", "Hobbit", "Unilever")
    # Criteria: A word in target containing [a-z] but no Vietnamese diacritics, 
    # and length > 4 to skip most unaccented VN words like 'Thanh', 'Long'.
    # We will exclude common vn unaccented words.
    words = re.findall(r'[a-zA-Z]+', target)  # extract pure latin words
    common_vn_unaccented = {
        'thanh', 'phong', 'minh', 'long', 'khanh', 'giang', 'quang', 'hoang', 'trang',
        'chung', 'linh', 'hung', 'thang', 'thanh', 'phuong', 'huong', 'dung', 'tuan'
    }
    for w in words:
        w_lower = w.lower()
        if len(w) > 4 and w_lower not in common_vn_unaccented:
            # If it doesn't contain any diacritics in its original form, it's highly likely english/latin
            # Wait, the extracted `w` ALREADY is pure [a-zA-Z] due to regex!
            # So "Epeus" -> lengths 5, not common vn. This triggers!
            return "person_west"

    # 3. High percentage of Phonetic Characters in Chinese Source
    phonetic_cnt = sum(1 for c in source if c in WEST_PHONETIC_CHARS)
    if len(source) >= 2 and (phonetic_cnt / len(source)) >= 0.5:
        # Avoid things like "Ai Cập" falling into Person West without checks
        return "person_west"
        
    return None

def load_file(filepath: Path):
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
            entries.append((parts[0], parts[1]))
            
    return header_lines, entries

def write_entries(filepath: Path, entries: list, override_cat: str):
    header = [
        "---\n",
        "type: bulk_dictionary\n",
        "source_language: zh\n",
        "target_language: vi\n",
        "priority: 4\n",
        f"category: {override_cat}\n",
        f"entries_count: {len(entries)}\n",
        "compiled_from: \"_bulk_names.md\"\n",
        "last_compiled: \"2026-04-14\"\n",
        "notes: \"Extracted Western items\"\n",
        "---\n",
        "\n",
        "| source | target | category_target |\n",
        "| --- | --- | --- |\n"
    ]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(header)
        for row in entries:
             # Just unpack whatever size
            f.write("| " + " | ".join(row) + " |\n")

def main():
    person_fp = OUTPUT_DIR / "_names_person_east.md"
    headers, entries = load_file(person_fp)
    
    kept_person = []
    misplaced = []
    
    for src, tgt in entries:
        new_cat = is_western(src, tgt)
        if new_cat:
            misplaced.append((src, tgt, new_cat))
        else:
            kept_person.append((src, tgt))
            
    # Write back the pure person_east
    with open(person_fp, 'w', encoding='utf-8') as f:
        for h in headers:
            if h.startswith('entries_count:'):
                f.write(f"entries_count: {len(kept_person)}\n")
            else:
                f.write(h)
        for src, tgt in kept_person:
            f.write(f"| {src} | {tgt} |\n")
            
    # Save misplaced western names
    west_misplaced_fp = OUTPUT_DIR / "_names_western_misplaced.md"
    write_entries(west_misplaced_fp, misplaced, "western_misplaced")
    
    print(f"Total starting entries: {len(entries)}")
    print(f"Kept person_east: {len(kept_person)}")
    print(f"Western misclassified found: {len(misplaced)}")

if __name__ == '__main__':
    main()
