#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
split_vietphrase.py

Parses the gigantic _bulk_vietphrase.md and _bulk_vietphrase2.md and splits 
them into 6 specialized dictionary files based on `source` string length
and content type (Numbers/Latin).
"""

import os
from pathlib import Path
import re
import datetime

PROJECT_ROOT = Path("d:/Converter by DrDuc")
DICT_DIR = PROJECT_ROOT / "data/dictionaries/global/vietphrase"

FILES_TO_PROCESS = ["_bulk_vietphrase.md", "_bulk_vietphrase2.md"]

CATEGORIES = [
    "vietphrase_latin_num",
    "vietphrase_1char",
    "vietphrase_2char",
    "vietphrase_3char",
    "vietphrase_4char",
    "vietphrase_5plus"
]

def generate_header(cat: str, count: int) -> str:
    category_id = cat
    notes = {
        "vietphrase_latin_num": "Từ điển VietPhrase: Từ ghép có số hoặc chữ Latinh (Ngày tháng, định dạng số học).",
        "vietphrase_1char": "Từ điển VietPhrase: Từ đơn Hán Tự (1 ký tự).",
        "vietphrase_2char": "Từ điển VietPhrase: Từ ghép cơ bản (2 ký tự).",
        "vietphrase_3char": "Từ điển VietPhrase: Cụm từ (3 ký tự).",
        "vietphrase_4char": "Từ điển VietPhrase: Thành ngữ, điển cố, cụm từ dài (4 ký tự).",
        "vietphrase_5plus": "Từ điển VietPhrase: Câu dài, ngữ cảnh câu, tục ngữ (>= 5 ký tự)."
    }
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    return f"""---
type: bulk_dictionary
source_language: zh
target_language: vi
priority: 2
category: {category_id}
entries_count: {count}
compiled_from: "VietPhrase.txt & VietPhrase2.txt"
last_compiled: "{date_str}"
notes: "{notes.get(cat, '')}"
---

| source | target |
| --- | --- |
"""

def split_dictionaries():
    db = {cat: set() for cat in CATEGORIES} # use set to avoid duplicates across file 1 and 2
    
    # 1. Read files and classify
    for fname in FILES_TO_PROCESS:
        fp = DICT_DIR / fname
        if not fp.exists():
            print(f"! File không tồn tại: {fname}")
            continue
            
        print(f"Reading: {fname}...")
        with open(fp, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or not line.startswith('|'):
                    continue
                    
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 2 and parts[0] != 'source':
                    source, target = parts[0], parts[1]
                    
                    if re.search(r'[a-zA-Z0-9]', source):
                        db["vietphrase_latin_num"].add((source, target))
                    else:
                        lng = len(source)
                        if lng == 1:
                            db["vietphrase_1char"].add((source, target))
                        elif lng == 2:
                            db["vietphrase_2char"].add((source, target))
                        elif lng == 3:
                            db["vietphrase_3char"].add((source, target))
                        elif lng == 4:
                            db["vietphrase_4char"].add((source, target))
                        else:
                            db["vietphrase_5plus"].add((source, target))

    # 2. Write out to 6 specialized files
    for cat in CATEGORIES:
        out_fp = DICT_DIR / f"_{cat}.md"
        entries = sorted(list(db[cat]), key=lambda x: len(x[0]), reverse=True) # Sort descending by length for Trie optimization rule
        
        with open(out_fp, 'w', encoding='utf-8') as f:
            f.write(generate_header(cat, len(entries)))
            for src, tgt in entries:
                f.write(f"| {src} | {tgt} |\n")
        
        print(f"-> Đã xuất: _{cat}.md ({len(entries):,} mục)")

    # 3. Rename original files to prevent duplicate loads
    for fname in FILES_TO_PROCESS:
        fp = DICT_DIR / fname
        if fp.exists():
            bak_fp = DICT_DIR / fname.replace(".md", "_BACKUP.md")
            # In case backup already exists, remove it
            if bak_fp.exists():
                os.remove(bak_fp)
            os.rename(fp, bak_fp)
            print(f"Đã sao lưu an toàn: {fname} -> {bak_fp.name}")

if __name__ == '__main__':
    split_dictionaries()
