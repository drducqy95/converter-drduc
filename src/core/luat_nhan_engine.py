#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
luat_nhan_engine.py — Pattern-based template engine for {0} placeholder substitution.

LuatNhan patterns transform entity-containing phrases:
    {0}军团 + "Thiên Lang" → "quân đoàn Thiên Lang"
    {0}大人 + "Lâm Động"  → "Lâm Động đại nhân"

Features:
- Load patterns from compiled SQLite or parsed MD
- Chain: Primary LuatNhan (303) → Extended LuatNhanCu (15K)
- Context-aware: only apply when entity exists in sentence
- Sorted by pattern length (longer = more specific = first)
"""

import sqlite3
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────

@dataclass
class LuatNhanRule:
    """A single LuatNhan pattern rule."""
    pattern: str        # e.g., {0}军团
    replacement: str    # e.g., quân đoàn {0}
    pattern_key: str    # e.g., 军团 (the Chinese text without {0})
    category: str       # luat_nhan_primary or luat_nhan_extended
    prefix: str = ""    # Text before {0} in pattern
    suffix: str = ""    # Text after {0} in pattern
    
    def __post_init__(self):
        # Parse where {0} appears in the pattern
        idx = self.pattern.find('{0}')
        if idx >= 0:
            self.prefix = self.pattern[:idx]
            self.suffix = self.pattern[idx + 3:]
        else:
            self.suffix = self.pattern


# ─────────────────────────────────────────────────
# LuatNhan Engine
# ─────────────────────────────────────────────────

class LuatNhanEngine:
    """
    Pattern-based template engine for entity substitution.
    
    Processes text by finding patterns like "{0}军团" where {0} is an entity name,
    and replacing the whole match with the Vietnamese template (e.g., "quân đoàn {0}").
    """
    
    def __init__(self):
        self.rules: list[LuatNhanRule] = []
        self._compiled_patterns: list[tuple[re.Pattern, LuatNhanRule]] = []
        self._entity_set: set[str] = set()
        self._compiled_source_names: tuple[str, ...] = ()
        self._db_cache_key: str = ""
    
    def load_from_sqlite(self, db_path: str | Path) -> int:
        """Load grammar patterns from compiled SQLite database."""
        cache_key = _shared_db_cache_key(db_path)
        self._db_cache_key = cache_key
        cached = _SHARED_RULES_CACHE.get(cache_key)
        if cached is not None:
            self.rules = cached
            return len(self.rules)

        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT pattern, replacement, category, pattern_key 
                FROM grammar_patterns 
                ORDER BY LENGTH(pattern_key) DESC, category ASC
            """)
        except sqlite3.OperationalError:
            conn.close()
            return 0
        
        self.rules = []
        for pattern, replacement, category, pattern_key in c.fetchall():
            rule = LuatNhanRule(
                pattern=pattern,
                replacement=replacement,
                pattern_key=pattern_key,
                category=category,
            )
            self.rules.append(rule)
        
        conn.close()
        _SHARED_RULES_CACHE[cache_key] = self.rules
        return len(self.rules)
    
    def set_entities(self, entities: list[str]):
        """
        Set the list of known entity names for pattern matching.
        
        These are the values that can fill {0} in patterns.
        Entity names should already be in Vietnamese (translated).
        """
        self._entity_set = set(entities)
        self._compile_patterns(entities)
    
    def set_entity_pairs(self, pairs: list[tuple[str, str]]):
        """
        Set entity pairs: (source_name, target_name).
        
        Source names are used for pattern matching in the source text.
        Target names are used for replacement in the translated text.
        """
        self._entity_pairs = {src: tgt for src, tgt in pairs if src}
        source_names = tuple(sorted((src for src, _ in pairs if src), key=len, reverse=True))
        if source_names == self._compiled_source_names:
            return
        self._compiled_source_names = source_names
        cache_key = (self._db_cache_key, source_names)
        cached = _SHARED_COMPILED_PATTERNS.get(cache_key)
        if cached is not None:
            self._compiled_patterns = cached
            return
        self._compile_patterns_with_source(source_names)
        _SHARED_COMPILED_PATTERNS[cache_key] = self._compiled_patterns

    def _compile_patterns_with_source(self, source_names: list[str] | tuple[str, ...]):
        """Compile regex patterns using source entity names."""
        self._compiled_patterns = []

        # Escape names for regex
        name_pattern = '|'.join(re.escape(name) for name in source_names if name)
        
        if not name_pattern:
            return
        
        for rule in self.rules:
            if rule.prefix and rule.suffix:
                # Pattern has text on both sides of {0}: prefix{0}suffix
                regex = re.compile(
                    re.escape(rule.prefix) + 
                    f'({name_pattern})' + 
                    re.escape(rule.suffix)
                )
            elif rule.prefix:
                # Pattern has text before {0}: prefix{0}
                regex = re.compile(
                    re.escape(rule.prefix) + 
                    f'({name_pattern})'
                )
            elif rule.suffix:
                # Pattern has text after {0}: {0}suffix
                regex = re.compile(
                    f'({name_pattern})' + 
                    re.escape(rule.suffix)
                )
            else:
                continue
            
            self._compiled_patterns.append((regex, rule))
    
    def _compile_patterns(self, entity_names: list[str]):
        """Compile regex patterns with entity names (Vietnamese, for post-translation)."""
        self._compiled_patterns = []
        
        sorted_names = sorted(entity_names, key=len, reverse=True)
        name_pattern = '|'.join(re.escape(name) for name in sorted_names if name)
        
        if not name_pattern:
            return
        
        for rule in self.rules:
            if rule.suffix:
                regex = re.compile(
                    f'({name_pattern})' + 
                    re.escape(rule.suffix)
                )
                self._compiled_patterns.append((regex, rule))
    
    def apply(self, text: str) -> str:
        """
        Apply LuatNhan rules to the text.
        
        This should be called on the SOURCE text (Chinese), 
        matching source entity names in patterns.
        
        The output replaces matched patterns with Vietnamese templates 
        filled with the translated entity names.
        """
        if not self._compiled_patterns:
            return text
        
        for regex, rule in self._compiled_patterns:
            def replacer(match):
                entity = match.group(1)
                # Look up translated entity name
                translated = self._entity_pairs.get(entity, entity)
                return rule.replacement.replace('{0}', translated)

            text = regex.sub(replacer, text)

        return text

    def apply_with_source_entities(self, text: str) -> str:
        """Apply source-side templates while keeping entity placeholders in source form."""
        if not self._compiled_patterns:
            return text

        for regex, rule in self._compiled_patterns:
            def replacer(match):
                entity = match.group(1)
                return rule.replacement.replace('{0}', entity)

            text = regex.sub(replacer, text)

        return text
    
    def apply_post_translation(self, text: str) -> str:
        """
        Apply LuatNhan rules on already-translated text.
        
        This is used when entities are already translated (Vietnamese)
        but surrounding Chinese text wasn't caught by Trie.
        """
        if not self._compiled_patterns:
            return text
        
        for regex, rule in self._compiled_patterns:
            def replacer(match):
                entity = match.group(1)
                return rule.replacement.replace('{0}', entity)
            
            text = regex.sub(replacer, text)
        
        return text
    
    def get_stats(self) -> dict:
        """Return engine statistics."""
        primary = sum(1 for r in self.rules if r.category == 'luat_nhan_primary')
        extended = sum(1 for r in self.rules if r.category == 'luat_nhan_extended')
        return {
            "total_rules": len(self.rules),
            "primary_rules": primary,
            "extended_rules": extended,
            "compiled_patterns": len(self._compiled_patterns),
            "entities_registered": len(self._entity_set),
        }


_SHARED_RULES_CACHE: dict[str, list[LuatNhanRule]] = {}
_SHARED_COMPILED_PATTERNS: dict[tuple[str, tuple[str, ...]], list[tuple[re.Pattern, LuatNhanRule]]] = {}


def _shared_db_cache_key(db_path: str | Path) -> str:
    path = Path(db_path).resolve()
    stat = path.stat()
    return f"{path}:{stat.st_mtime_ns}:{stat.st_size}"


# ─────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="LuatNhan Engine CLI")
    parser.add_argument("--db", required=True, help="Path to compiled SQLite database")
    parser.add_argument("--text", help="Text to apply patterns on") 
    parser.add_argument("--entities", nargs="+", help="Entity names (source:target pairs)")
    
    args = parser.parse_args()
    
    engine = LuatNhanEngine()
    count = engine.load_from_sqlite(args.db)
    print(f"📊 Loaded: {count} rules")
    
    stats = engine.get_stats()
    print(f"   Primary: {stats['primary_rules']}")
    print(f"   Extended: {stats['extended_rules']}")
    
    if args.text and args.entities:
        pairs = []
        for e in args.entities:
            src, tgt = e.split(':')
            pairs.append((src, tgt))
        
        engine.set_entity_pairs(pairs)
        result = engine.apply(args.text)
        print(f"\n📝 Input:  {args.text}")
        print(f"📝 Output: {result}")


if __name__ == "__main__":
    main()
