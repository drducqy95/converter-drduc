#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
filter_person_east.py

Filters out remaining Locations, Organizations, and Miscs from _names_person_east.md
using specific Chinese/Vietnamese suffix and keyword matching.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path("d:/Converter by DrDuc")
OUTPUT_DIR = PROJECT_ROOT / "data/dictionaries/global/names"

MISC_CN_SUFFIXES = {
    '剑', '刀', '枪', '阵', '鼎', '印', '镜', '塔', '录', '诀', '诀', '功', '法', '经', '书', '图', '符',
    '丹', '药', '酒', '茶', '车', '船', '舰', '琴', '笛', '钟', '网', '扇', '冠', '甲', '衣', '靴', '珠',
    '环', '石', '木', '金', '火', '水', '土', '风', '雷', '电', '光', '暗', '兽', '龙', '凤', '虎', '龟',
    '花', '草', '树', '叶', '果'
}
LOC_CN_SUFFIXES = {
    '界', '域', '洲', '州', '星', '山', '峰', '谷', '崖', '海', '湖', '渊', '泉', '河', '川', '江',
    '城', '镇', '村', '府', '都', '国', '岛', '林', '荒', '原', '沙漠', '洞', '窟', '宫', '殿', '阁', '楼', '塔'
}
ORG_CN_SUFFIXES = {
    '宗', '派', '门', '教', '帮', '会', '阁', '楼', '殿', '宫', '家', '族', '氏', '院', '堂', '庄', '堡', '盟', '国'
}

# Some overlaps exist (e.g. 宫, 殿, 阁). We'll handle them carefully.

def load_file(filepath: Path) -> tuple[list[str], list[tuple[str, str]]]:
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
            entries.append((parts[0], parts[1]))
            
    return header_lines, entries

def reevaluate_entry(source: str, target: str) -> str:
    # If the target has explicit Person words, it's a person
    target_lower = target.lower()
    person_keywords = ['đế', 'tôn', 'thần', 'tiên', 'ma', 'vương', 'hoàng', 'chúa', 'ca', 'tỷ', 'muội', 'đệ', 'gia', 'lão', 'tổ', 'tử', 'nữ', 'nhân', 'đạo']
    
    # We will just use Chinese suffix check. It's often more reliable for Cultivation terms.
    # Exclude common names if they happen to end in these characters, but 2-char names might be tricky.
    # E.g., '叶木' (Ye Mu) is a person, but ends in '木' (Wood).
    # So we only filter if it has length > 2 AND ends in suffix, OR specific target keywords match.
    
    # 1. Check Misc (Techniques, Items)
    misc_viet_keywords = ['kiếm', 'đao', 'thương', 'trận', 'đỉnh', 'ấn', 'gương', 'tháp', 'lục', 'quyết', 'công', 'pháp', 'kinh', 'thư', 'đồ', 'phù', 'đan', 'dược', 'rượu', 'trà', 'xe', 'thuyền', 'hạm', 'đàn', 'chuông', 'áo', 'đá']
    if any(f" {kw} " in f" {target_lower} " or target_lower.startswith(f"{kw} ") for kw in misc_viet_keywords):
        return 'misc_east'
        
    for suff in MISC_CN_SUFFIXES:
        if source.endswith(suff) and len(source) >= 3:
            return 'misc_east'

    # 2. Check Orgs
    org_viet_keywords = ['tông', 'phái', 'môn', 'giáo', 'bang', 'hội', 'các', 'gia tộc', 'thị tộc', 'viện', 'đường', 'sơn trang', 'bảo', 'liên minh']
    if any(f" {kw} " in f" {target_lower} " or target_lower.startswith(f"{kw} ") for kw in org_viet_keywords):
        return 'org_east'
        
    for suff in ORG_CN_SUFFIXES:
        if source.endswith(suff) and len(source) >= 3:
            return 'org_east'

    # 3. Check Locs
    loc_viet_keywords = ['giới', 'vực', 'châu', 'tinh', 'sơn', 'phong', 'cốc', 'nhai', 'vực', 'hải', 'hồ', 'hà', 'xuyên', 'giang', 'thành', 'trấn', 'thôn', 'phủ', 'đô', 'đảo', 'lâm', 'sa mạc', 'động']
    if any(f" {kw} " in f" {target_lower} " or target_lower.startswith(f"{kw} ") for kw in loc_viet_keywords):
        return 'loc_east'
        
    for suff in LOC_CN_SUFFIXES:
        if source.endswith(suff) and len(source) >= 3:
            return 'loc_east'

    return 'person_east'

def write_file(filepath: Path, base_header: list[str], entries: list[tuple[str, str]], override_cat: str = None):
    if not base_header:
        # Create default header
        base_header = [
            "---\n",
            "type: bulk_dictionary\n",
            "source_language: zh\n",
            "target_language: vi\n",
            "priority: 4\n",
            f"category: {override_cat}\n",
            "entries_count: 0\n",
            "compiled_from: \"_bulk_names.md\"\n",
            "last_compiled: \"2026-04-14\"\n",
            "notes: \"Auto-generated MISPLACED bucket\"\n",
            "---\n",
            "\n",
            "| source | target | category_target |\n",
            "| --- | --- | --- |\n"
        ]
        
    new_header = []
    for line in base_header:
        if line.startswith('entries_count:'):
            new_header.append(f"entries_count: {len(entries)}\n")
        else:
            new_header.append(line)
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_header)
        for row in entries:
            # If 3 items, write 3, else 2
            if len(row) == 3:
                f.write(f"| {row[0]} | {row[1]} | {row[2]} |\n")
            else:
                f.write(f"| {row[0]} | {row[1]} |\n")

def main():
    person_fp = OUTPUT_DIR / "_names_person_east.md"
    headers, entries = load_file(person_fp)
    
    kept_person = []
    misplaced = []
    
    for src, tgt in entries:
        new_cat = reevaluate_entry(src, tgt)
        if new_cat != 'person_east':
            misplaced.append((src, tgt, new_cat))
        else:
            kept_person.append((src, tgt))
            
    # Load existing misplaced to append
    misplaced_fp = OUTPUT_DIR / "_names_person_east_misplaced.md"
    
    print(f"Total starting entries: {len(entries)}")
    print(f"Kept person_east: {len(kept_person)}")
    print(f"Misclassified found: {len(misplaced)}")
    
    write_file(person_fp, headers, kept_person)
    write_file(misplaced_fp, [], misplaced, override_cat="names_person_east_misplaced")

if __name__ == '__main__':
    main()
