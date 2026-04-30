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

import re
import sqlite3
import time
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from src.core.pos_rewrite_engine import POSRewriteEngine

from src.core.dictionary_entry_filters import extract_concise_reference_fallback, looks_like_reference_gloss

try:
    from src.engine.number_converter import NumberConverter
except ImportError:
    from engine.number_converter import NumberConverter


REPETITION_NORMALIZE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(哈){4,}"), "哈哈哈"),
    (re.compile(r"(啊){4,}"), "啊啊啊"),
    (re.compile(r"(呀){4,}"), "呀呀呀"),
    (re.compile(r"(呜){4,}"), "呜呜呜"),
    (re.compile(r"(哇){4,}"), "哇哇哇"),
    (re.compile(r"(……){2,}"), "……"),
    (re.compile(r"([！!]){4,}"), r"\1\1\1"),
    (re.compile(r"([？?]){4,}"), r"\1\1\1"),
)

ONE_MEAN_CONTEXT_HINTS: dict[str, tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]] = {
    "打": (
        (("电话", "電話", "手机", "手機"), ("gọi", "gọi điện")),
        (("折",), ("giảm giá",)),
    ),
}


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
    # Phase 09 Metadata
    pos_tag: str | None = None
    pos_sub: str | None = None
    entity_type: str | None = None
    is_function_word: int = 0
    luat_nhan_trigger: int = 0
    reorder_role: str | None = None
    cultural_origin: str | None = None
    register_level: str | None = None


# ─────────────────────────────────────────────────
# Trie Node
# ─────────────────────────────────────────────────

class TrieNode:
    """A node in the Trie."""
    __slots__ = [
        'children', 'target', 'priority', 'one_mean', 'is_end',
        'pos_tag', 'pos_sub', 'entity_type', 'is_function_word',
        'luat_nhan_trigger', 'reorder_role', 'cultural_origin', 'register_level'
    ]
    
    def __init__(self):
        self.children: dict[str, 'TrieNode'] = {}
        self.target: str = ""
        self.priority: int = 0
        self.one_mean: bool = False
        self.is_end: bool = False
        # Phase 09 Metadata
        self.pos_tag: str | None = None
        self.pos_sub: str | None = None
        self.entity_type: str | None = None
        self.is_function_word: int = 0
        self.luat_nhan_trigger: int = 0
        self.reorder_role: str | None = None
        self.cultural_origin: str | None = None
        self.register_level: str | None = None


# ─────────────────────────────────────────────────
# Trie Engine
# ─────────────────────────────────────────────────

class TrieEngine:
    """
    Unicode-aware Trie engine for Chinese → Vietnamese translation.
    
    Supports multi-priority entries where higher priority overrides lower.
    Uses longest-prefix matching for best translation quality.
    """
    
    def __init__(
        self,
        enable_number_converter: bool = True,
        *,
        max_viterbi_candidates_per_position: int = 64,
    ):
        self.root = TrieNode()
        self._size = 0
        self._load_time = 0.0
        self._reading_fallbacks: dict[str, str] = {}
        self._number_converter = NumberConverter() if enable_number_converter else None
        self.max_viterbi_candidates_per_position = max(1, int(max_viterbi_candidates_per_position))

    @classmethod
    def from_shared_sqlite(
        cls,
        db_path: str | Path,
        enable_number_converter: bool = True,
        *,
        max_viterbi_candidates_per_position: int = 64,
    ) -> "TrieEngine":
        cache_key = _shared_trie_cache_key(
            db_path,
            enable_number_converter,
            max_viterbi_candidates_per_position,
        )
        cached = _SHARED_TRIE_CACHE.get(cache_key)
        if cached is not None:
            return cached

        trie = cls(
            enable_number_converter=enable_number_converter,
            max_viterbi_candidates_per_position=max_viterbi_candidates_per_position,
        )
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
    
    def insert(self, source: str, target: str, priority: int = 2, one_mean: bool = False,
               pos_tag: str = None, pos_sub: str = None, entity_type: str = None,
               is_function_word: int = 0, luat_nhan_trigger: int = 0, reorder_role: str = None,
               cultural_origin: str = None, register_level: str = None):
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
            node.pos_tag = pos_tag
            node.pos_sub = pos_sub
            node.entity_type = entity_type
            node.is_function_word = is_function_word
            node.luat_nhan_trigger = luat_nhan_trigger
            node.reorder_role = reorder_role
            node.cultural_origin = cultural_origin
            node.register_level = register_level
            
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
        c.execute("""
            SELECT source, target, priority, one_mean, category,
                   pos_tag, pos_sub, entity_type, is_function_word, 
                   luat_nhan_trigger, reorder_role, cultural_origin, register_level
            FROM entries 
            ORDER BY priority ASC
        """)

        loaded = 0
        for (source, target, priority, one_mean, category, 
             pos_tag, pos_sub, ent, is_func, lnt, rrole, cult, reg) in c:
            if looks_like_reference_gloss(category or "", target or ""):
                continue
            self.insert(source, target, priority, bool(one_mean),
                        pos_tag, pos_sub, ent, is_func, lnt, rrole, cult, reg)
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
                source = text[pos : i + 1]
                target = self._resolve_one_mean_target(
                    source,
                    node.target,
                    node.one_mean,
                    right_context=text[i + 1:i + 7],
                )
                
                best_match = TrieMatch(
                    source=source,
                    target=target,
                    priority=node.priority,
                    length=i - pos + 1,
                    one_mean=node.one_mean,
                    pos_tag=node.pos_tag,
                    pos_sub=node.pos_sub,
                    entity_type=node.entity_type,
                    is_function_word=node.is_function_word,
                    luat_nhan_trigger=node.luat_nhan_trigger,
                    reorder_role=node.reorder_role,
                    cultural_origin=node.cultural_origin,
                    register_level=node.register_level,
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

    def lookup_viterbi(self, text: str, pos: int = 0) -> TrieMatch | None:
        """Return the first token from the highest-scoring Viterbi path."""
        if pos >= len(text):
            return None
        tokens = self.segment_viterbi(text[pos:])
        if not tokens:
            return None
        return tokens[0]

    def lookup_prefixes(self, text: str, pos: int = 0) -> list[TrieMatch]:
        """Return all trie prefix matches starting at `pos`, shortest to longest."""
        node = self.root
        matches: list[TrieMatch] = []

        for i in range(pos, len(text)):
            char = text[i]
            if char not in node.children:
                break
            node = node.children[char]

            if node.is_end:
                matches.append(self._match_from_node(text[pos:i + 1], node))

        return matches

    def _match_from_node(self, source: str, node: TrieNode, *, right_context: str = "") -> TrieMatch:
        target = self._resolve_one_mean_target(source, node.target, node.one_mean, right_context=right_context)

        return TrieMatch(
            source=source,
            target=target,
            priority=node.priority,
            length=len(source),
            one_mean=node.one_mean,
            pos_tag=node.pos_tag,
            pos_sub=node.pos_sub,
            entity_type=node.entity_type,
            is_function_word=node.is_function_word,
            luat_nhan_trigger=node.luat_nhan_trigger,
            reorder_role=node.reorder_role,
            cultural_origin=node.cultural_origin,
            register_level=node.register_level,
        )
    
    def lookup_exact(self, source: str) -> TrieMatch | None:
        """Look up an exact source string."""
        node = self.root
        for char in source:
            if char not in node.children:
                return self._lookup_exact_fallback(source)
            node = node.children[char]
        
        if not node.is_end:
            return self._lookup_exact_fallback(source)
        
        target = self._resolve_one_mean_target(source, node.target, node.one_mean)
        
        return TrieMatch(
            source=source,
            target=target,
            priority=node.priority,
            length=len(source),
            one_mean=node.one_mean,
            pos_tag=node.pos_tag,
            pos_sub=node.pos_sub,
            entity_type=node.entity_type,
            is_function_word=node.is_function_word,
            luat_nhan_trigger=node.luat_nhan_trigger,
            reorder_role=node.reorder_role,
            cultural_origin=node.cultural_origin,
            register_level=node.register_level,
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

    @classmethod
    def normalize_repetitions(cls, text: str) -> str:
        """Cap long expressive repetitions before dynamic-programming passes."""
        normalized = str(text or "")
        for pattern, replacement in REPETITION_NORMALIZE_PATTERNS:
            normalized = pattern.sub(replacement, normalized)
        return normalized

    @classmethod
    def _resolve_one_mean_target(
        cls,
        source: str,
        target: str,
        one_mean: bool,
        *,
        right_context: str = "",
    ) -> str:
        if not one_mean or ";" not in target:
            return target

        meanings = cls._split_meanings(target)
        if not meanings:
            return target
        if len(meanings) == 1:
            return meanings[0]

        contextual = cls._contextual_one_mean(source, right_context, meanings)
        return contextual or meanings[0]

    @staticmethod
    def _split_meanings(target: str) -> list[str]:
        return [part.strip() for part in str(target or "").split(";") if part.strip()]

    @staticmethod
    def _contextual_one_mean(source: str, right_context: str, meanings: list[str]) -> str | None:
        for prefixes, preferred_targets in ONE_MEAN_CONTEXT_HINTS.get(source, ()):
            if not any(str(right_context or "").startswith(prefix) for prefix in prefixes):
                continue
            for preferred in preferred_targets:
                for meaning in meanings:
                    if preferred in meaning:
                        return meaning
        return None
    
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
    
    def translate_text(self, text: str, fallback_char: bool = True, *, strategy: str = "viterbi") -> str:
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

        if strategy == "viterbi":
            return ''.join(token.target for token in self.segment_viterbi(text, fallback_char=fallback_char))
        if strategy != "greedy":
            raise ValueError(f"Unsupported trie translation strategy: {strategy}")
        
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
    
    # ─── Segmentation & Rich Translation ───
    
    def segment_viterbi(self, text: str, fallback_char: bool = True) -> list[TrieMatch]:
        """
        Segment text with dynamic-programming path scoring.

        This avoids greedy traps where a long medium-priority entry blocks a better
        sequence of shorter high-confidence entries.
        """
        if not text:
            return []
        text = self.normalize_repetitions(text)

        n = len(text)
        best_score = [float("-inf")] * (n + 1)
        best_choice: list[TrieMatch | None] = [None] * (n + 1)
        best_next: list[int | None] = [None] * (n + 1)
        best_score[n] = 0.0
        best_next[n] = n

        for pos in range(n - 1, -1, -1):
            candidates = self._viterbi_candidates(text, pos, fallback_char=fallback_char)
            for candidate in candidates:
                next_pos = pos + candidate.length
                if next_pos > n or best_next[next_pos] is None:
                    continue
                score = self._viterbi_token_score(candidate) + best_score[next_pos]
                if score > best_score[pos] or (
                    score == best_score[pos]
                    and best_choice[pos] is not None
                    and candidate.length > best_choice[pos].length
                ):
                    best_score[pos] = score
                    best_choice[pos] = candidate
                    best_next[pos] = next_pos

        path: list[TrieMatch] = []
        pos = 0
        while pos < n and best_choice[pos] is not None and best_next[pos] is not None:
            path.append(best_choice[pos])
            next_pos = best_next[pos]
            if next_pos <= pos:
                break
            pos = next_pos
        return path

    def _viterbi_candidates(self, text: str, pos: int, *, fallback_char: bool) -> list[TrieMatch]:
        candidates = self.lookup_prefixes(text, pos)

        if self._number_converter:
            num_result = self._number_converter.try_convert(text, pos)
            if num_result:
                candidates.append(TrieMatch(
                    source=text[pos:pos + num_result.consumed],
                    target=num_result.text,
                    priority=2,
                    length=num_result.consumed,
                    one_mean=False,
                    pos_tag="NUMBER",
                ))

        if candidates:
            if len(candidates) > self.max_viterbi_candidates_per_position:
                candidates = sorted(
                    candidates,
                    key=lambda item: (item.priority, item.length, bool(item.entity_type)),
                    reverse=True,
                )[: self.max_viterbi_candidates_per_position]
            return candidates

        char = text[pos]
        if fallback_char and self._is_cjk(char):
            reading = self.lookup_reading(char)
            return [TrieMatch(
                source=char,
                target=reading if reading else char,
                priority=1 if reading else 0,
                length=1,
                one_mean=bool(reading),
            )]

        return [TrieMatch(
            source=char,
            target=char,
            priority=0,
            length=1,
            one_mean=False,
        )]

    @staticmethod
    def _viterbi_token_score(match: TrieMatch) -> float:
        priority = max(0, int(match.priority or 0))
        length = max(1, int(match.length or 1))
        score = (priority * 6.0) + length - 6.0
        if match.pos_tag == "NUMBER":
            score += 2.0
        if match.entity_type:
            score += 1.5
        if match.luat_nhan_trigger:
            score += 1.0
        if priority <= 0:
            score -= 8.0
        return score

    def segment_to_tokens(self, text: str, *, strategy: str = "viterbi") -> List[TrieMatch]:
        """
        Segment a text into a sequence of TrieMatch tokens.
        Handles both Trie matches and NumberConverter algorithmic matches.
        """
        if not text:
            return []

        if strategy == "viterbi":
            return self.segment_viterbi(text)
        if strategy != "greedy":
            raise ValueError(f"Unsupported trie segmentation strategy: {strategy}")
        
        tokens = []
        i = 0
        length = len(text)
        
        while i < length:
            # 1. Trie match
            trie_match = self.lookup(text, i)
            trie_len = trie_match.length if trie_match else 0
            
            # 2. Number match
            num_result = None
            num_len = 0
            if self._number_converter:
                num_result = self._number_converter.try_convert(text, i)
                num_len = num_result.consumed if num_result else 0
            
            # 3. Decision
            if num_len > trie_len:
                tokens.append(TrieMatch(
                    source=text[i:i+num_len],
                    target=num_result.text,
                    priority=2, # Numbers usually P2
                    length=num_len,
                    one_mean=False,
                    pos_tag="NUMBER"
                ))
                i += num_len
            elif trie_match:
                tokens.append(trie_match)
                i += trie_match.length
            else:
                # Fallback char
                char = text[i]
                reading = self.lookup_reading(char)
                tokens.append(TrieMatch(
                    source=char,
                    target=reading if reading else char,
                    priority=0,
                    length=1,
                    one_mean=False
                ))
                i += 1
        
        return tokens

    def translate_enriched(self, text: str, rewriter: Optional['POSRewriteEngine'] = None) -> str:
        """Translate text using metadata-enriched reordering."""
        tokens = self.segment_to_tokens(text)
        if rewriter:
            tokens = rewriter.rewrite(tokens)
        
        return "".join(t.target for t in tokens)
    
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


_SHARED_TRIE_CACHE: dict[tuple[str, bool, int], TrieEngine] = {}


def _shared_trie_cache_key(
    db_path: str | Path,
    enable_number_converter: bool,
    max_viterbi_candidates_per_position: int,
) -> tuple[str, bool, int]:
    path = Path(db_path).resolve()
    stat = path.stat()
    return (
        f"{path}:{stat.st_mtime_ns}:{stat.st_size}",
        enable_number_converter,
        max_viterbi_candidates_per_position,
    )


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
