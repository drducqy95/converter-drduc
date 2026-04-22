#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path

def load_md_dict(filepath: Path) -> dict:
    if not filepath.exists():
        return {}
        
    db = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        # skip header
        in_header = True
        dash_count = 0
        lines = f.readlines()
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line == '---':
                dash_count += 1
                if dash_count == 2:
                    in_header = False
                    continue
            if not in_header and line.startswith('| source'):
                continue
            if not in_header and line.startswith('| ---'):
                continue
                
            if not in_header and line.startswith('|'):
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 2:
                    db[parts[0]] = parts[1]
    return db

def main():
    vp_path = Path("d:/Converter by DrDuc/data/dictionaries/global/vietphrase/_vietphrase_1char.md")
    pa_path = Path("d:/Converter by DrDuc/data/dictionaries/global/phien_am/_bulk_phienam.md")
    
    vp_dict = load_md_dict(vp_path)
    pa_dict = load_md_dict(pa_path)
    
    print(f"Tổng số từ trong _vietphrase_1char.md: {len(vp_dict)}")
    print(f"Tổng số từ trong _bulk_phienam.md: {len(pa_dict)}\n")
    
    in_both_keys = set(vp_dict.keys()).intersection(set(pa_dict.keys()))
    print(f"Số Hán tự xuất hiện ở CẢ HAI file: {len(in_both_keys)}")
    
    exact_matches = 0
    diff_matches = 0
    diff_examples = []
    
    for k in in_both_keys:
        v_vp = vp_dict[k].lower()
        v_pa = pa_dict[k].lower()
        
        # In Phien Am, meanings might be comma separated "đích, đắc"
        # In Vietphrase, "của/đích/những"
        
        # Check exact string match
        if v_vp == v_pa:
            exact_matches += 1
        else:
            diff_matches += 1
            if len(diff_examples) < 15:
                diff_examples.append((k, vp_dict[k], pa_dict[k]))
                
    print(f" -> Trùng lặp hoàn toàn (Cùng source, cùng target 100%): {exact_matches}")
    print(f" -> Cùng source, NHƯNG NGHĨA KHÁC NHAU: {diff_matches}\n")
    
    vp_only = set(vp_dict.keys()) - set(pa_dict.keys())
    print(f"Hán tự chỉ có trong Vietphrase_1char (không có trong Phiên Âm): {len(vp_only)}")
    print("=> Một số ví dụ:", list(vp_only)[:10], "\n")
    
    print("=== MỘT SỐ VÍ DỤ CÙNG CHỮ NHƯNG NGHĨA KHÁC Nhau ===")
    print(f"{'HÁN TỰ':<10} | {'VIETPHRASE 1 CHAR (Nghĩa Dịch)':<30} | {'PHIÊN ÂM (Âm Hán Việt)':<30}")
    print("-" * 75)
    for k, v_vp, v_pa in diff_examples:
        print(f"{k:<10} | {v_vp[:28]:<30} | {v_pa[:28]:<30}")

if __name__ == '__main__':
    main()
