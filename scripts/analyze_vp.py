import os
from pathlib import Path
import re

OUTPUT_DIR = Path("d:/Converter by DrDuc/data/dictionaries/global/vietphrase")

def analyze():
    files = ["_bulk_vietphrase.md", "_bulk_vietphrase2.md"]
    counts = {
        'latin_num': 0,
        '1char': 0,
        '2char': 0,
        '3char': 0,
        '4char': 0,
        '5plus': 0
    }
    
    for fname in files:
        fp = OUTPUT_DIR / fname
        if not fp.exists(): continue
        with open(fp, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.startswith('|'): continue
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3 and parts[1] != 'source':
                    source = parts[1]
                    # Check latin/num
                    if re.search(r'[a-zA-Z0-9]', source):
                        counts['latin_num'] += 1
                    else:
                        lng = len(source)
                        if lng == 1: counts['1char'] += 1
                        elif lng == 2: counts['2char'] += 1
                        elif lng == 3: counts['3char'] += 1
                        elif lng == 4: counts['4char'] += 1
                        else: counts['5plus'] += 1
                        
    print("Statistics:")
    for k, v in counts.items():
        print(f"{k}: {v}")

if __name__ == '__main__':
    analyze()
