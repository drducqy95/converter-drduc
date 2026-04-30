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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

PLACEHOLDER_RE = re.compile(r"\{(?:(?P<index>\d+)(?::(?P<typed>[A-Za-z_][\w-]*))?|(?P<named>[A-Za-z_][\w-]*))\}")
ENTITY_TYPE_ALIASES = {
    "character": "person",
    "name": "person",
    "person_name": "person",
    "place": "location",
    "loc": "location",
    "org": "organization",
    "organisation": "organization",
    "faction": "organization",
    "sect": "organization",
    "any": "",
    "entity": "",
}


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
    placeholder: str = "{0}"
    placeholder_type: str = ""
    specificity: tuple[int, int, int, int] = field(init=False, repr=False)
    
    def __post_init__(self):
        # Parse where the placeholder appears in the pattern.
        match = PLACEHOLDER_RE.search(self.pattern)
        if match:
            self.placeholder = match.group(0)
            self.placeholder_type = _normalize_entity_type(match.group("typed") or match.group("named") or "")
            self.prefix = self.pattern[:match.start()]
            self.suffix = self.pattern[match.end():]
        else:
            self.suffix = self.pattern

        self.specificity = self._specificity()

    def render(self, value: str) -> str:
        return self.replacement.replace("{0}", value).replace(self.placeholder, value)

    def _specificity(self) -> tuple[int, int, int, int]:
        placeholder_count = len(PLACEHOLDER_RE.findall(self.pattern))
        literal_text = PLACEHOLDER_RE.sub("", self.pattern)
        category_weight = 1 if "primary" in (self.category or "").lower() else 0
        return (
            len(literal_text),
            len(self.pattern),
            category_weight,
            -placeholder_count,
        )


@dataclass(slots=True)
class _RuleApplication:
    start: int
    end: int
    replacement: str
    rule: LuatNhanRule
    order: int

    @property
    def rank(self) -> tuple[int, int, int, int, int, int]:
        return (*self.rule.specificity, self.end - self.start, -self.order)


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
        self._entity_pairs: dict[str, str] = {}
        self._entity_types_by_source: dict[str, str] = {}
        self._compiled_source_signature: tuple[tuple[str, str], ...] = ()
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
        normalized_pairs = [self._normalize_entity_pair(item) for item in pairs]
        self._entity_pairs = {src: tgt for src, tgt, _entity_type in normalized_pairs if src}
        self._entity_types_by_source = {
            src: entity_type
            for src, _tgt, entity_type in normalized_pairs
            if src and entity_type
        }
        source_signature = tuple(
            sorted(
                ((src, entity_type) for src, _tgt, entity_type in normalized_pairs if src),
                key=lambda item: (len(item[0]), item[0], item[1]),
                reverse=True,
            )
        )
        if source_signature == self._compiled_source_signature:
            return
        self._compiled_source_signature = source_signature
        cache_key = (self._db_cache_key, source_signature)
        cached = _SHARED_COMPILED_PATTERNS.get(cache_key)
        if cached is not None:
            self._compiled_patterns = cached
            return
        self._compile_patterns_with_source(source_signature)
        _SHARED_COMPILED_PATTERNS[cache_key] = self._compiled_patterns

    def _normalize_entity_pair(self, item) -> tuple[str, str, str]:
        if isinstance(item, dict):
            return (
                str(item.get("source") or "").strip(),
                str(item.get("target") or item.get("source") or "").strip(),
                _normalize_entity_type(str(item.get("entity_type") or item.get("type") or "").strip()),
            )
        if len(item) >= 3:
            src, tgt, entity_type = item[0], item[1], item[2]
        else:
            src, tgt = item[0], item[1]
            entity_type = ""
        return (
            str(src or "").strip(),
            str(tgt or src or "").strip(),
            _normalize_entity_type(str(entity_type or "").strip()),
        )

    def _compile_patterns_with_source(self, source_signature: tuple[tuple[str, str], ...]):
        """Compile regex patterns using source entity names."""
        self._compiled_patterns = []
        
        for rule in self.rules:
            names = [
                source
                for source, entity_type in source_signature
                if self._entity_matches_rule_type(entity_type, rule.placeholder_type)
            ]
            name_pattern = '|'.join(re.escape(name) for name in names if name)
            if not name_pattern:
                continue

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
        self._sort_compiled_patterns()
    
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
        self._sort_compiled_patterns()
    
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
        return self._apply_compiled_patterns(text, translate_entity=True)

    def apply_with_source_entities(self, text: str) -> str:
        """Apply source-side templates while keeping entity placeholders in source form."""
        if not self._compiled_patterns:
            return text
        return self._apply_compiled_patterns(text, translate_entity=False)
    
    def apply_post_translation(self, text: str) -> str:
        """
        Apply LuatNhan rules on already-translated text.
        
        This is used when entities are already translated (Vietnamese)
        but surrounding Chinese text wasn't caught by Trie.
        """
        if not self._compiled_patterns:
            return text
        return self._apply_compiled_patterns(text, translate_entity=False)
    
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

    @staticmethod
    def _entity_matches_rule_type(entity_type: str, rule_type: str) -> bool:
        if not rule_type:
            return True
        return _normalize_entity_type(entity_type) == rule_type

    def _sort_compiled_patterns(self):
        self._compiled_patterns.sort(
            key=lambda item: (
                item[1].specificity,
                len(item[1].pattern),
            ),
            reverse=True,
        )

    def _apply_compiled_patterns(self, text: str, *, translate_entity: bool) -> str:
        applications: list[_RuleApplication] = []
        for order, (regex, rule) in enumerate(self._compiled_patterns):
            for match in regex.finditer(text):
                entity = match.group(1)
                value = self._entity_pairs.get(entity, entity) if translate_entity else entity
                applications.append(
                    _RuleApplication(
                        start=match.start(),
                        end=match.end(),
                        replacement=rule.render(value),
                        rule=rule,
                        order=order,
                    )
                )

        if not applications:
            return text

        applications.sort(key=lambda item: (item.start, item.end))
        selected: list[_RuleApplication] = []
        cursor = 0
        index = 0
        while index < len(applications):
            start = applications[index].start
            same_start: list[_RuleApplication] = []
            while index < len(applications) and applications[index].start == start:
                same_start.append(applications[index])
                index += 1
            if start < cursor:
                continue
            chosen = max(same_start, key=lambda item: item.rank)
            selected.append(chosen)
            cursor = chosen.end

        if not selected:
            return text

        parts: list[str] = []
        cursor = 0
        for item in selected:
            parts.append(text[cursor:item.start])
            parts.append(item.replacement)
            cursor = item.end
        parts.append(text[cursor:])
        return "".join(parts)


_SHARED_RULES_CACHE: dict[str, list[LuatNhanRule]] = {}
_SHARED_COMPILED_PATTERNS: dict[tuple[str, tuple[tuple[str, str], ...]], list[tuple[re.Pattern, LuatNhanRule]]] = {}


def _normalize_entity_type(value: str) -> str:
    normalized = (value or "").strip().lower().replace("-", "_")
    return ENTITY_TYPE_ALIASES.get(normalized, normalized)


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
