#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import os
import json

def main():
    db_path = r"d:\Converter by DrDuc\data\dictionaries\_compiled\trie_cache.db"
    cedict_path = r"d:\Converter by DrDuc\data\external\cedict_ts.u8"
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("SELECT source FROM entries WHERE pos_tag IS NULL LIMIT 100")
    null_samples = [r[0] for r in c.fetchall()]
    
    with open(cedict_path, 'r', encoding='utf-8') as f:
        cedict_content = f.read()
    
    results = []
    for s in null_samples:
        in_cedict = s in cedict_content
        results.append({"source": s, "in_cedict": in_cedict})

    with open("d:/Converter by DrDuc/diagnose_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    conn.close()

if __name__ == "__main__":
    main()
