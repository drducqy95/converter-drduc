#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
classify_names.py 

Splits _bulk_names.md into 8 categories:
- Person, Location, Org, Misc
- Eastern vs Western
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Setup paths
PROJECT_ROOT = Path("d:/Converter by DrDuc")
INPUT_FILE = PROJECT_ROOT / "data/dictionaries/global/names/_bulk_names.md"
OUTPUT_DIR = PROJECT_ROOT / "data/dictionaries/global/names"

# ─── Heuristic Regex & Keywords ───

# Western indicators
# Letters not in Vietnamese alphabet, or common foreign endings
WESTERN_LETTERS = re.compile(r'[fFjJwWzZ]')
# Non-vietnamese consonant clusters (br, cr, dr, st, sh, th is VN but sh isn't, etc.)
WESTERN_CLUSTERS = re.compile(r'(?i)(bl|br|cl|cr|dr|fl|fr|gl|gr|pl|pr|sl|sm|sn|sp|st|sw|sh|ce$|ge$|ck|sh|tion|sion|ment|ness|ous|shire|land|ton|burg|stadt|ford)')
# Phonetic Chinese characters often used for western transliteration:
PHONETIC_CN = set('斯克尔特罗巴阿卡玛德伊弗夫索托波曼拉尼奥维基亚')
WESTERN_VN_KEYWORDS = {'cộng hoà', 'bang', 'châu', 'cực', 'nam mỹ', 'bắc mỹ', 'liên hiệp'}

# Categories: Locations
LOC_VN_KEYWORDS = {'thành phố', 'tỉnh', 'đảo', 'quần đảo', 'quận', 'bang', 'vương quốc', 'châu', 'địa ngục', 'núi', 'đền', 'biển', 'vịnh', 'đại dương', 'hồ', 'quảng trường', 'đại lộ', 'phân vùng', 'bán đảo', 'khu', 'sa mạc'}
LOC_CN_SUFFIXES = {'市', '区', '省', '国', '岛', '群岛', '洲', '州', '地狱', '山', '海', '湾', '洋', '广场', '大道', '湖', '海峡', '县', '镇', '村'}

# Categories: Organizations
ORG_VN_KEYWORDS = {'đại học', 'viện', 'tông', 'phái', 'công ty', 'giáo', 'đảng', 'quần chúng', 'chính phủ', 'bảo tàng', 'tập đoàn', 'câu lạc bộ', 'clb', 'trường', 'hiệp hội', 'liên minh', 'đại học'}
ORG_CN_SUFFIXES = {'大学', '院', '宗', '派', '教', '党', '公司', '集团', '俱乐部', '博物馆', '政府', '协会', '学会', '联盟'}

# Categories: Misc
MISC_VN_KEYWORDS = {'chòm sao', 'cung', 'sao', 'kinh', 'bản', 'tạp', 'phim', 'xe', 'lễ', 'truyện', 'tháp', 'kiếm', 'pháp bảo', 'đài', 'chùa', 'miếu', 'bitcoin', 'wechat', 'thương mại'}
MISC_CN_KEYWORDS = {'座', '宫', '星', '经', '舞曲', '节', '塔', '车', '剑', '传', '梦', '寺', '庙', '台', '号', '馆'}

# Categories: Persons
PERSON_VN_KEYWORDS = {'bồ tát', 'vương', 'đế', 'công chúa', 'nữ tướng', 'nhân vật', 'tiên', 'hoàng hậu', 'thần', 'phật', 'tiên sinh', 'sứ', 'thiếu'}
PERSON_CN_KEYWORDS = {'菩萨', '王', '帝', '公主', '仙', '后', '神', '佛', '皇', '妃'}

def analyze_entry(source: str, target: str) -> tuple[str, str]:
    """Returns (Category, Origin)"""
    source_clean = source.strip()
    target_clean = target.strip()
    target_lower = target_clean.lower()
    
    # --- Origin Analysis ---
    origin = 'east' # Default
    
    # 1. Has specific western letters or clusters
    if WESTERN_LETTERS.search(target_clean) or WESTERN_CLUSTERS.search(target_clean):
        origin = 'west'
    else:
        # Phonetic density check in source (e.g. 斯克尔)
        phonetic_count = sum(1 for ch in source_clean if ch in PHONETIC_CN)
        if len(source_clean) > 0 and phonetic_count / len(source_clean) >= 0.5 and len(source_clean) >= 2:
            origin = 'west'
            
        # Check specific VN keywords that are overwhelmingly western
        if any(kw in target_lower for kw in WESTERN_VN_KEYWORDS):
            origin = 'west'
    
    # Exception for pure Chinese history elements that might trigger accidentally
    EAST_EXCEP = {'hoàng đế', 'triều đại', 'hán', 'đường', 'tống', 'nguyên', 'minh', 'thanh'}
    if any(kw in target_lower for kw in EAST_EXCEP):
        origin = 'east'
        
    # --- Category Analysis ---
    
    # 1. Location
    if any(kw in target_lower for kw in LOC_VN_KEYWORDS) or any(source_clean.endswith(kw) for kw in LOC_CN_SUFFIXES):
        return ('loc', origin)
        
    # 2. Organization
    if any(kw in target_lower for kw in ORG_VN_KEYWORDS) or any(source_clean.endswith(kw) for kw in ORG_CN_SUFFIXES):
        return ('org', origin)
        
    # 3. Misc
    if any(kw in target_lower for kw in MISC_VN_KEYWORDS) or any(source_clean.endswith(kw) for kw in MISC_CN_KEYWORDS):
        return ('misc', origin)
        
    # 4. Person
    if any(kw in target_lower for kw in PERSON_VN_KEYWORDS) or any(source_clean.endswith(kw) for kw in PERSON_CN_KEYWORDS):
        return ('person', origin)
        
    # Fallbacks based on length
    if 2 <= len(source_clean) <= 4:
        return ('person', origin)
        
    # Default
    return ('misc', origin)

def main():
    print(f"Reading from {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Data structure: category_origin -> list of (source, target)
    categorized = defaultdict(list)
    
    header = []
    in_table = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('---'):
            if not in_table:
                # Still in frontmatter
                pass
            continue
            
        if line.startswith('|'):
            in_table = True
            # Skip header row and separator
            if 'source' in line.lower() and 'target' in line.lower():
                continue
            if '---' in line:
                continue
                
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 2:
                source = parts[0]
                target = parts[1]
                cat, orig = analyze_entry(source, target)
                categorized[f"{cat}_{orig}"].append((source, target))
                
    # Output structure
    categories = {
        'person_east': 'names_person_east',
        'person_west': 'names_person_west',
        'loc_east': 'names_loc_east',
        'loc_west': 'names_loc_west',
        'org_east': 'names_org_east',
        'org_west': 'names_org_west',
        'misc_east': 'names_misc_east',
        'misc_west': 'names_misc_west'
    }
    
    notes_mapping = {
        'person_east': 'Đông Phương: Tên người (Hán, Nhật, Hàn, Phật giáo)',
        'person_west': 'Phương Tây: Tên người (Phiên âm Hán-Việt, Latinh)',
        'loc_east': 'Đông Phương: Địa danh (Tỉnh, châu, địa ngục...)',
        'loc_west': 'Phương Tây: Địa danh (Nước, đảo, bang...)',
        'org_east': 'Đông Phương: Tổ chức (Môn phái, đại học...)',
        'org_west': 'Phương Tây: Tổ chức (Công ty, tổ chức...)',
        'misc_east': 'Đông Phương: Tên khác (Vật phẩm, bí kíp...)',
        'misc_west': 'Phương Tây: Tên khác (Chòm sao, thương hiệu...)'
    }
    
    total_parsed = 0
    for key, filename in categories.items():
        entries = categorized[key]
        total_parsed += len(entries)
        
        filepath = OUTPUT_DIR / f"_{filename}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"---\n")
            f.write(f"type: bulk_dictionary\n")
            f.write(f"source_language: zh\n")
            f.write(f"target_language: vi\n")
            f.write(f"priority: 4\n")
            f.write(f"category: {filename}\n")
            f.write(f"entries_count: {len(entries)}\n")
            f.write(f"compiled_from: \"_bulk_names.md (auto-classified)\"\n")
            f.write(f"last_compiled: \"2026-04-14\"\n")
            f.write(f"notes: \"{notes_mapping[key]}\"\n")
            f.write(f"---\n\n")
            f.write(f"| source | target |\n")
            f.write(f"| --- | --- |\n")
            for src, tgt in entries:
                f.write(f"| {src} | {tgt} |\n")
                
        print(f"Created {filepath.name}: {len(entries)} entries")
        
    print(f"\nTotal parsed exactly: {total_parsed}")

if __name__ == '__main__':
    main()
