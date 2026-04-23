#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import json

# Add src to path
sys.path.append(os.getcwd())

from src.core.trie_engine import TrieEngine
from src.core.pos_rewrite_engine import POSRewriteEngine

def test_reordering():
    db_path = r"d:\Converter by DrDuc\data\dictionaries\_compiled\trie_cache.db"
    trie = TrieEngine()
    trie.load_from_sqlite(db_path)
    
    rewriter = POSRewriteEngine()
    
    # Test cases
    test_sentences = [
        "穿黑色风衣的男子",
        "老太的身躯",
        "惨白腐烂的双手",
        "两座墓碑面前",
        "发疯似的",
    ]
    
    results = []
    for sent in test_sentences:
        try:
            translation = trie.translate_enriched(sent, rewriter)
            tokens = trie.segment_to_tokens(sent)
            rewritten = rewriter.rewrite(list(tokens))
            
            results.append({
                "original": sent,
                "translated": translation,
                "tokens_before": [t.source for t in tokens],
                "tokens_after": [t.source for t in rewritten]
            })
        except Exception as e:
            results.append({"original": sent, "error": str(e)})

    output_path = "d:/Converter by DrDuc/pos_rewrite_test_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Test complete. Results written to {output_path}")

if __name__ == "__main__":
    test_reordering()
