#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pinyin_cascade.py — Constructs Pinyin and Traditional Chinese fields for multi-character
phrases by looking up their constituent unigrams from the local dictionary cache.
"""
import sqlite3

class CascadeEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._pinyin_cache = {}
        self._trad_cache = {}

    def _preload_cache(self):
        # Fallback to DB
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT source, pinyin, traditional FROM entries WHERE length(source) = 1")
        for source, py, trad in c.fetchall():
            if py: self._pinyin_cache[source] = py
            if trad: self._trad_cache[source] = trad
        conn.close()

        # Load from CEDICT for comprehensive unigram coverage
        import re, os
        cedict_path = r"d:\Converter by DrDuc\data\external\cedict_ts.u8"
        if os.path.exists(cedict_path):
            with open(cedict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('#'): continue
                    parts = line.split(maxsplit=2)
                    if len(parts) < 3: continue
                    trad, simp, rest = parts[0], parts[1], parts[2]
                    if len(simp) == 1:
                        if trad != simp:
                            self._trad_cache[simp] = trad
                        
                        py_match = re.search(r'\[(.*?)\]', rest)
                        if py_match:
                            py = py_match.group(1)
                            # Only set if not already set, or overwrite? Overwrite is fine (latest def)
                            self._pinyin_cache[simp] = py
                            if trad != simp:
                                self._pinyin_cache[trad] = py
                                
        print(f"    CascadeEngine: Preloaded {len(self._pinyin_cache):,} pinyin and {len(self._trad_cache):,} traditional seeds from DB+CEDICT.")

    def cascade_all(self):
        self._preload_cache()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT source FROM entries WHERE (pinyin IS NULL OR traditional IS NULL) AND length(source) >= 2")
        rows = c.fetchall()
        
        updates = []
        for (source,) in rows:
            py_res = []
            trad_res = []
            can_pinyin = True
            
            # Decompose the word char by char
            for char in source:
                py = self._pinyin_cache.get(char)
                if py:
                    py_res.append(py)
                else:
                    can_pinyin = False
                
                trad = self._trad_cache.get(char)
                if trad:
                    trad_res.append(trad)
                else:
                    # In Chinese, simplified is often the same as traditional if unchanged
                    trad_res.append(char)
                    
            new_py = " ".join(py_res) if can_pinyin else None
            new_trad = "".join(trad_res)
            
            # Optimization: If traditional is mathematically identical to source, just set it to source instead of None
            # Wait, our schema allows NULL, so if it's the exact same, we might just store it.
            
            if new_py or new_trad:
                updates.append((new_py, new_trad, source))
                
        if updates:
            print(f"    CascadeEngine: Missing Pinyin/Traditional constructed for {len(updates):,} entries.")
            c.executemany("UPDATE entries SET pinyin = COALESCE(pinyin, ?), traditional = COALESCE(traditional, ?) WHERE source = ?", updates)
            conn.commit()
        conn.close()
