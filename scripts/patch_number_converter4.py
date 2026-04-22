#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

def patch_file():
    fp = Path("d:/Converter by DrDuc/src/engine/number_converter.py")
    if not fp.exists(): return
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()

    # Disable "年": "năm {n}"
    if '"年": "năm {n}",' in content:
        content = content.replace('"年": "năm {n}",', '')
        
    # Inject new suffixes
    if '"万": "{n} vạn",' in content:
        content = content.replace(
            '"万": "{n} vạn",', 
            '"万": "{n} vạn",\n    "寸": "{n} tấc",\n    "码": "{n} yard",\n    "点多": "hơn {n} giờ",\n    "年多": "hơn {n} năm",\n    "年左右": "khoảng {n} năm",\n    "年内": "trong khoảng {n} năm",'
        )
        
    # Inject 乘以 to prefix
    if '"楼": "tầng {n}",' in content:
        content = content.replace(
            '"楼": "tầng {n}",',
            '"楼": "tầng {n}",\n    "乘以": "nhân với {n}",'
        )

    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Patched units.")

if __name__ == '__main__':
    patch_file()
