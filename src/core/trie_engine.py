#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
trie_engine.py — Unicode-aware Trie for multi-priority dictionary lookup.

Features:
- CJK + Latin + Vietnamese diacritic support
- Longest-prefix matching (dual-pointer traversal)
- Priority override (P5 > P4 > P3 > P2 > P1)
- One-Mean mode (take first meaning before ';')
- Fast loading from compiled SQLite
- Hot-reload support
"""

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.core.dictionary_entry_filters import extract_concise_reference_fallback, looks_like_reference_gloss

try:
    from src.engine.number_converter import NumberConverter
except ImportError:
    from engine.number_converter import NumberConverter


# ─────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────

@dataclass
class TrieMatch:
    """Result of a Trie lookup."""
    source: str       # Matched source text
    target: str       # Translation
    priority: int     # Priority level (1-5)
    length: int       # Number of chars matched
    one_mean: bool    # Whether one_mean was applied


# ─────────────────────────────────────────────────
# Trie Node
# ─────────────────────────────────────────────────

class TrieNode:
    """A node in the Trie."""
    __slots__ = ['children', 'target', 'priority', 'one_mean', 'is_end']
    
    def __init__(self):
        self.children: dict[str, 'TrieNode'] = {}
        self.target: str = ""
        self.priority: int = 0
        self.one_mean: bool = False
        self.is_end: bool = False


# ─────────────────────────────────────────────────
# Trie Engine
# ─────────────────────────────────────────────────

class TrieEngine:
    """
    Unicode-aware Trie engine for Chinese → Vietnamese translation.
    
    Supports multi-priority entries where higher priority overrides lower.
    Uses longest-prefix matching for best translation quality.
    """
    
    def __init__(self, enable_number_converter: bool = True):
        self.root = TrieNode()
        self._size = 0
        self._load_time = 0.0
        self._reading_fallbacks: dict[str, str] = {}
        self._number_converter = NumberConverter() if enable_number_converter else None

    @classmethod
    def from_shared_sqlite(cls, db_path: str | Path, enable_number_converter: bool = True) -> "TrieEngine":
        cache_key = _shared_trie_cache_key(db_path, enable_number_converter)
        cached = _SHARED_TRIE_CACHE.get(cache_key)
        if cached is not None:
            return cached

        trie = cls(enable_number_converter=enable_number_converter)
        trie.load_from_sqlite(db_path)
        _SHARED_TRIE_CACHE[cache_key] = trie
        return trie
    
    @property
    def size(self) -> int:
        """Number of entries in the Trie."""
        return self._size
    
    @property
    def load_time(self) -> float:
        """Time taken to load the Trie (seconds)."""
        return self._load_time
    
    # ─── Build ───
    
    def insert(self, source: str, target: str, priority: int = 2, one_mean: bool = False):
        """
        Insert a word into the Trie.
        
        If the source already exists, only overrides if new priority >= existing.
        """
        if not source or not target:
            return
        
        node = self.root
        for char in source:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        # Only update if new priority is >= existing (higher wins)
        if not node.is_end or priority >= node.priority:
            node.target = target
            node.priority = priority
            node.one_mean = one_mean
            if not node.is_end:
                self._size += 1
            node.is_end = True
    
    def load_from_sqlite(self, db_path: str | Path) -> dict:
        """
        Load entries from compiled SQLite database into the Trie.
        
        Returns stats dict.
        """
        start = time.time()
        db_path = str(db_path)
        
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Load entries ordered by priority (low first so high overrides)
        c.execute("SELECT source, target, priority, one_mean, category FROM entries ORDER BY priority ASC")

        loaded = 0
        for source, target, priority, one_mean, category in c:
            if looks_like_reference_gloss(category or "", target or ""):
                continue
            self.insert(source, target, priority, bool(one_mean))
            loaded += 1

        reference_fallbacks = self._load_reference_fallbacks(c)
        self._load_reading_fallbacks(c)
        
        conn.close()
        
        self._load_time = time.time() - start
        
        return {
            "loaded": loaded,
            "reference_fallbacks": reference_fallbacks,
            "trie_size": self._size,
            "load_time": round(self._load_time, 3),
        }

    def _load_reference_fallbacks(self, cursor: sqlite3.Cursor) -> int:
        """Load short safe reference targets when runtime has no exact entry."""
        loaded = 0

        try:
            cursor.execute("""
                SELECT source, target, category
                FROM reference_entries
                ORDER BY
                    CASE
                        WHEN category = 'thieuchuu_reference' THEN 1
                        WHEN category = 'lacviet_reference' THEN 2
                        WHEN category = 'cedict_reference' THEN 3
                        ELSE 9
                    END ASC,
                    id ASC
            """)
        except sqlite3.OperationalError:
            return 0

        for source, target, category in cursor.fetchall():
            fallback = extract_concise_reference_fallback(category or "", target or "")
            if not fallback:
                continue
            if self._has_exact_entry(source):
                continue
            self.insert(source, fallback, priority=1, one_mean=True)
            loaded += 1

        return loaded

    def _load_reading_fallbacks(self, cursor: sqlite3.Cursor):
        """Load single-character reading fallbacks from compiled DB."""
        self._reading_fallbacks = {}

        try:
            cursor.execute("""
                SELECT source, pinyin, han_viet_readings, category
                FROM entry_readings
                ORDER BY
                    CASE
                        WHEN category = 'phien_am' THEN 1
                        WHEN category = 'thieuchuu_reference' THEN 2
                        WHEN category = 'lacviet_reference' THEN 3
                        ELSE 9
                    END ASC,
                    id ASC
            """)
        except sqlite3.OperationalError:
            return

        for source, pinyin, han_viet_readings, category in cursor.fetchall():
            if len(source) != 1:
                continue
            if source in self._reading_fallbacks:
                continue

            reading = self._choose_reading_value(han_viet_readings, pinyin)
            if reading:
                self._reading_fallbacks[source] = reading

    def _choose_reading_value(self, han_viet_readings: str, pinyin: str) -> str:
        """Pick the best fallback reading string."""
        for value in (han_viet_readings, pinyin):
            normalized = self._normalize_reading(value)
            if normalized:
                return normalized
        return ""

    @staticmethod
    def _normalize_reading(value: str) -> str:
        """Normalize multi-reading strings into a single fallback token."""
        if not value:
            return ""

        first = value
        for separator in ['|', ',', ';', '/']:
            if separator in first:
                first = first.split(separator, 1)[0]
        return first.strip()
    
    # ─── Lookup ───
    
    def lookup(self, text: str, pos: int = 0) -> TrieMatch | None:
        """
        Find the longest prefix match starting at position `pos` in `text`.
        
        Returns the longest match found, or None if no match.
        """
        node = self.root
        best_match: TrieMatch | None = None
        
        for i in range(pos, len(text)):
            char = text[i]
            if char not in node.children:
                break
            node = node.children[char]
            
            if node.is_end:
                target = node.target
                if node.one_mean and ';' in target:
                    target = target.split(';')[0].strip()
                
                best_match = TrieMatch(
                    source=text[pos:i+1],
                    target=target,
                    priority=node.priority,
                    length=i - pos + 1,
                    one_mean=node.one_mean,
                )
        
        if best_match is not None:
            return best_match

        if pos < len(text):
            reading = self.lookup_reading(text[pos])
            if reading:
                return TrieMatch(
                    source=text[pos],
                    target=reading,
                    priority=1,
                    length=1,
                    one_mean=True,
                )

        return None
    
    def lookup_exact(self, source: str) -> TrieMatch | None:
        """Look up an exact source string."""
        node = self.root
        for char in source:
            if char not in node.children:
                return self._lookup_exact_fallback(source)
            node = node.children[char]
        
        if not node.is_end:
            return self._lookup_exact_fallback(source)
        
        target = node.target
        if node.one_mean and ';' in target:
            target = target.split(';')[0].strip()
        
        return TrieMatch(
            source=source,
            target=target,
            priority=node.priority,
            length=len(source),
            one_mean=node.one_mean,
        )

    def _lookup_exact_fallback(self, source: str) -> TrieMatch | None:
        """Fallback for exact lookup using reading data."""
        if len(source) == 1:
            reading = self.lookup_reading(source)
            if reading:
                return TrieMatch(
                    source=source,
                    target=reading,
                    priority=1,
                    length=1,
                    one_mean=False,
                )
        return None

    def _has_exact_entry(self, source: str) -> bool:
        """Return True when the exact source already exists in the Trie."""
        node = self.root
        for char in source:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def lookup_reading(self, source: str) -> str | None:
        """Look up a fallback reading loaded from entry_readings."""
        return self._reading_fallbacks.get(source)
    
    def has_prefix(self, text: str, pos: int = 0) -> bool:
        """Check if any entry starts with the text from position pos."""
        node = self.root
        for i in range(pos, len(text)):
            char = text[i]
            if char not in node.children:
                return False
            node = node.children[char]
        return True
    
    # ─── Translate ───
    
    def translate_text(self, text: str, fallback_char: bool = True) -> str:
        """
        Translate a text using longest-prefix matching + algorithmic numbers.
        
        Priority logic at each position:
            1. Try Trie longest-prefix match
            2. Try NumberConverter (numbers, weekdays, lunar dates)
            3. Whichever consumed MORE characters wins
            4. If tied, Trie wins (dictionary has context-specific translations)
            5. Fallback: single CJK char → PhienAm lookup
        
        Args:
            text: Source text to translate.
            fallback_char: If True, unmatched CJK characters are looked up 
                          individually (P1 PhienAm fallback).
        
        Returns:
            Translated text.
        """
        if not text:
            return ""
        
        result = []
        i = 0
        length = len(text)
        
        while i < length:
            # 1. Trie longest-prefix match
            trie_match = self.lookup(text, i)
            trie_len = trie_match.length if trie_match else 0
            
            # 2. NumberConverter match (if enabled)
            num_result = None
            num_len = 0
            if self._number_converter:
                num_result = self._number_converter.try_convert(text, i)
                num_len = num_result.consumed if num_result else 0
            
            # 3. Pick the longer match (NumberConverter wins on tie-break
            #    only if Trie has no match at all)
            if num_len > trie_len:
                # NumberConverter consumed more → use it
                result.append(num_result.text)
                i += num_result.consumed
            elif trie_match:
                # Trie matched (or tied) → use Trie
                result.append(trie_match.target)
                i += trie_match.length
            else:
                # No match from either → single-char fallback
                char = text[i]
                
                if fallback_char and self._is_cjk(char):
                    # Try single-character lookup (PhienAm fallback)
                    single = self.lookup_exact(char)
                    if single:
                        result.append(single.target)
                    else:
                        reading = self.lookup_reading(char)
                        result.append(reading if reading else char)
                else:
                    result.append(char)
                
                i += 1
        
        return ''.join(result)
    
    @staticmethod
    def _is_cjk(char: str) -> bool:
        """Check if a character is CJK (Chinese/Japanese/Korean)."""
        cp = ord(char)
        return (
            (0x4E00 <= cp <= 0x9FFF) or      # CJK Unified Ideographs
            (0x3400 <= cp <= 0x4DBF) or      # CJK Extension A
            (0x20000 <= cp <= 0x2A6DF) or    # CJK Extension B
            (0xF900 <= cp <= 0xFAFF) or      # CJK Compatibility
            (0x2F800 <= cp <= 0x2FA1F)       # CJK Compatibility Supplement
        )
    
    # ─── Stats ───
    
    def get_stats(self) -> dict:
        """Get Trie statistics."""
        node_count = self._count_nodes(self.root)
        return {
            "entries": self._size,
            "reading_fallbacks": len(self._reading_fallbacks),
            "nodes": node_count,
            "load_time_ms": round(self._load_time * 1000, 1),
        }
    
    def _count_nodes(self, node: TrieNode) -> int:
        """Count total nodes in the Trie."""
        count = 1
        for child in node.children.values():
            count += self._count_nodes(child)
        return count


_SHARED_TRIE_CACHE: dict[tuple[str, bool], TrieEngine] = {}


def _shared_trie_cache_key(db_path: str | Path, enable_number_converter: bool) -> tuple[str, bool]:
    path = Path(db_path).resolve()
    stat = path.stat()
    return (f"{path}:{stat.st_mtime_ns}:{stat.st_size}", enable_number_converter)


# ─────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Trie Engine CLI")
    parser.add_argument("--db", required=True, help="Path to compiled SQLite database")
    parser.add_argument("--text", help="Text to translate")
    parser.add_argument("--lookup", help="Exact term to look up")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    
    args = parser.parse_args()
    
    trie = TrieEngine()
    stats = trie.load_from_sqlite(args.db)
    print(f"Loaded: {stats['loaded']:,} entries in {stats['load_time']}s")
    print(f"   Trie size: {trie.size:,} unique entries")
    
    if args.lookup:
        result = trie.lookup_exact(args.lookup)
        if result:
            print(f"Lookup: {result.source} -> {result.target} (P{result.priority})")
        else:
            print(f"Not found: {args.lookup}")
    
    if args.text:
        translated = trie.translate_text(args.text)
        print(f"\nSource: {args.text}")
        print(f"Result: {translated}")
    
    if args.benchmark:
        import time
        
        # Benchmark: 100 lookups
        test_terms = ["修为", "突破", "境界", "灵气", "丹田", "炼丹", "一个人", "天地", "大道", "太阳"]
        
        start = time.time()
        for _ in range(10000):
            for term in test_terms:
                trie.lookup_exact(term)
        elapsed = time.time() - start
        
        print(f"\nBenchmark: 100,000 lookups in {elapsed:.3f}s")
        print(f"   = {elapsed/100000*1000000:.1f} µs/lookup")


if __name__ == "__main__":
    main()
