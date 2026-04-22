#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
remove_numbers_1char.py

Removes Chinese counting numbers from _vietphrase_1char.md because the engine
handling numeric parsing natively interprets these.
"""

from pathlib import Path

CHINESE_NUMBERS = {
    '〇', '零', '一', '二', '两', '三', '四', '五', '六', '七', '八', '九', '十', 
    '百', '千', '万', '亿', '兆', '廿', '卅', '卌', '皕', 
    '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖', '拾', '佰', '仟'
}

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
    vp_headers, vp_entries = load_md_dict(vp_path)
    
    kept_entries = []
    removed_entries = []
    
    for src, tgt in vp_entries:
        if src in CHINESE_NUMBERS:
            removed_entries.append((src, tgt))
        else:
            kept_entries.append((src, tgt))
            
    print(f"Original dictionary size: {len(vp_entries)}")
    print(f"Numbers identified and removed: {len(removed_entries)}")
    if removed_entries:
        print("Removed words: ", [s for s, t in removed_entries])
    print(f"Optimized dictionary size: {len(kept_entries)}")
    
    # Rewrite the file
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
