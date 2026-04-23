#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import json

# Add src to path
sys.path.append(os.getcwd())

from src.core.trie_engine import TrieEngine

def main():
    db_path = r"d:\Converter by DrDuc\data\dictionaries\_compiled\trie_cache.db"
    print(f"Loading Trie from {db_path}...")
    
    trie = TrieEngine()
    stats = trie.load_from_sqlite(db_path)
    print(f"Loaded {stats['loaded']:,} entries in {stats['load_time']}s")
    
    test_words = ["的", "和", "我", "这", "本座", "灵气"]
    verification_results = []
    
    for word in test_words:
        match = trie.lookup_exact(word)
        if match:
            verification_results.append({
                "source": match.source,
                "target": match.target,
                "pos_tag": match.pos_tag,
                "pos_sub": match.pos_sub,
                "is_function_word": match.is_function_word,
                "reorder_role": match.reorder_role,
                "cultural_origin": match.cultural_origin
            })
        else:
            verification_results.append({"source": word, "status": "NOT FOUND"})

    output_path = "d:/Converter by DrDuc/trie_verification.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "stats": trie.get_stats(),
            "results": verification_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Verification results written to {output_path}")

if __name__ == "__main__":
    main()
