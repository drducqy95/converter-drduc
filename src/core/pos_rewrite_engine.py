#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pos_rewrite_engine.py — Metadata-driven syntactic reordering engine.

This engine utilizes POS tags and morphological metadata from the TrieEngine 
to perform structural reordering (e.g., Modifier-Head inversion) before or 
during the translation process.
"""

from dataclasses import dataclass
from typing import List, Optional
from src.core.trie_engine import TrieMatch

# POS tags that CANNOT be a head noun after '的'
_NON_HEAD_TAGS = frozenset({
    "VERB", "ADJECTIVE", "ADJ", "ADV", "ADVERB",
    "PARTICLE", "PART", "PREPOSITION", "PREP",
    "CONJUNCTION", "CONJ",
})

# POS tags that can participate in a modifier chain before '的'
_MODIFIER_TAGS = frozenset({
    "VERB", "ADJ", "ADJECTIVE", "ADV", "ADVERB",
    "NOUN", "PRONOUN", "NUMBER", "CLF",
    "PARTICLE", "CONJUNCTION", "PREPOSITION",
})


class POSRewriteEngine:
    """
    Engine that reorders TrieMatch tokens based on linguistic rules.
    
    Replaces legacy regex blocks from zh_structure_rewriter.py with 
    metadata-conditioned logic.
    """
    
    def __init__(self):
        pass

    def rewrite(self, tokens: List[TrieMatch]) -> List[TrieMatch]:
        """Apply all reordering rules to the token stream."""
        if not tokens:
            return []
        
        # 1. Handle Structural Particles (的)
        tokens = self._rewrite_de_constructions(tokens)
        
        # 2. Handle Locative Postpositions (面前, 上, 下)
        tokens = self._rewrite_locatives(tokens)
        
        # 3. Handle Simulative Suffixes (似的, 一样)
        tokens = self._rewrite_simulatives(tokens)
        
        return tokens

    def _rewrite_de_constructions(self, tokens: List[TrieMatch]) -> List[TrieMatch]:
        """
        Handles [Modifier Chain] + 的 + [Head] -> [Head] + [Modifier Chain].
        
        Key improvements over v1:
        - Accepts NULL pos_tag as potential head noun (29% coverage means many nouns untagged)
        - Uses negative guard (_NON_HEAD_TAGS) instead of positive match
        - Single-ADJ modifier → simple inversion (no "của")
        - Single-PRONOUN/NOUN modifier → possessive ("của")
        """
        i = 0
        while i < len(tokens):
            match = tokens[i]
            if match.pos_tag == "PARTICLE" and match.source == "的":
                # 1. Find the Head Noun (next token)
                if i + 1 < len(tokens):
                    head = tokens[i + 1]
                    head_tag = (head.pos_tag or "").upper()
                    
                    # Accept as head: explicitly NOUN, or untagged (NULL),
                    # but reject if it's a known non-head tag
                    is_valid_head = (
                        head_tag == "NOUN"
                        or head_tag == ""  # NULL/untagged → likely noun
                        or head_tag == "PRONOUN"
                    )
                    # Reject tokens that are clearly not head nouns
                    if head_tag in _NON_HEAD_TAGS:
                        is_valid_head = False
                    
                    if is_valid_head:
                        # 2. Find the start of the Modifier Chain
                        mod_start = self._find_modifier_start(tokens, i)
                        if mod_start < i:
                            # 3. Extract Modifier Chain
                            modifier_chain = tokens[mod_start:i]
                            de_token = tokens[i]
                            head_token = tokens[i + 1]
                            
                            # Determine "của" versus simple inversion
                            is_possessive = self._is_possessive_modifier(modifier_chain)
                            
                            if is_possessive:
                                de_token.target = " của "
                            else:
                                de_token.target = " "  # Simple modifier swap
                            
                            # REORDER: [Head] + [的] + [Modifier Chain]
                            new_sequence = [head_token, de_token] + modifier_chain
                            
                            # Replace in original tokens list
                            tokens[mod_start : i + 2] = new_sequence
                            
                            # Skip ahead
                            i = mod_start + len(new_sequence)
                            continue
            i += 1
        return tokens

    @staticmethod
    def _is_possessive_modifier(modifier_chain: List[TrieMatch]) -> bool:
        """
        Determine if modifier chain represents possession (→ "của") vs description (→ simple swap).
        
        Possessive: 我的书, 老太的身躯 (PRONOUN/person-NOUN + 的 + NOUN)
        Descriptive: 美丽的女孩, 穿黑色风衣的男子 (ADJ/VERB + 的 + NOUN)
        """
        if len(modifier_chain) != 1:
            # Multi-token modifier → descriptive (穿黑色风衣的男子)
            return False
        
        mod = modifier_chain[0]
        mod_tag = (mod.pos_tag or "").upper()
        
        # ADJECTIVE/VERB modifiers → descriptive (no "của")
        if mod_tag in {"ADJECTIVE", "ADJ", "VERB", "ADV", "ADVERB", "NUMBER"}:
            return False
        
        # PRONOUN → possessive (我的, 他的)
        if mod_tag == "PRONOUN":
            return True
        
        # NOUN with name/person sub → possessive (老太的, 张三的)
        if mod_tag == "NOUN":
            if mod.pos_sub in {"name", "classifier", "location", "idiom", "abstract"}:
                return mod.pos_sub == "name"
            # Generic NOUN → possessive
            return True
        
        # Untagged single token — heuristic: short source (1-2 chars) likely a person/pronoun → possessive
        if mod_tag == "" and len(mod.source) <= 2:
            return True
        
        return False

    def _find_modifier_start(self, tokens: List[TrieMatch], de_index: int) -> int:
        """
        Find the start of the modifier block preceding '的'.
        
        Improved: also accepts untagged tokens (NULL pos_tag) as part of modifier
        chain, since 71% of entries have no tag yet. Uses a stop condition instead
        of a whitelist so untagged tokens can still participate.
        """
        start = de_index - 1
        
        while start >= 0:
            token = tokens[start]
            tag = (token.pos_tag or "").upper()
            
            # Stop at another '的' particle
            if token.source == "的":
                break
            
            # Known valid modifier tags → continue scanning
            if tag in _MODIFIER_TAGS:
                start -= 1
                continue
            
            # Untagged token (tag == "") → accept if source is CJK and short
            # This handles the 71% of entries with no POS tag
            if tag == "" and len(token.source) <= 4:
                start -= 1
                continue
            
            # Any other known non-modifier tag → stop
            break
        
        return start + 1

    def _rewrite_locatives(self, tokens: List[TrieMatch]) -> List[TrieMatch]:
        """
        Handles [NP chain] + [Locative] -> [Locative] + [NP chain].
        e.g., [两座墓碑] [面前] -> [面前] [两座墓碑]
        
        Improved: scans backward to collect full NP chain (NUM+CLF+NOUN)
        instead of just the immediately preceding token.
        """
        i = 0
        while i < len(tokens):
            match = tokens[i]
            tag = (match.pos_tag or "").upper()
            
            # Check for locative tokens
            is_locative = (
                (tag == "NOUN" and match.pos_sub == "location")
                or tag == "LOC"
            )
            
            if is_locative and i > 0:
                # Scan backward to find the start of the NP chain
                np_start = i - 1
                while np_start >= 0:
                    prev = tokens[np_start]
                    prev_tag = (prev.pos_tag or "").upper()
                    if prev_tag in {"NOUN", "PRONOUN", "NUMBER"}:
                        np_start -= 1
                        continue
                    # Untagged short token → likely part of NP
                    if prev_tag == "" and len(prev.source) <= 2:
                        np_start -= 1
                        continue
                    # Classifier tagged as NOUN/classifier
                    if prev_tag == "NOUN" and prev.pos_sub == "classifier":
                        np_start -= 1
                        continue
                    break
                np_start += 1
                
                if np_start < i:
                    # Extract: [NP chain] + [LOC]
                    np_chain = tokens[np_start:i]
                    loc_token = tokens[i]
                    
                    # REORDER: [LOC] + [NP chain]
                    new_sequence = [loc_token] + np_chain
                    tokens[np_start : i + 1] = new_sequence
                    i = np_start + len(new_sequence)
                    continue
            i += 1
        return tokens

    def _rewrite_simulatives(self, tokens: List[TrieMatch]) -> List[TrieMatch]:
        """
        Handles [X] + [似的/一样/一般] -> [như/giống như] + [X].
        """
        i = 0
        simulative_sources = {"似的", "一样", "一般"}
        
        while i < len(tokens):
            match = tokens[i]
            is_simulative = (
                match.source in simulative_sources
                or (match.pos_sub == "simulative")
            )
            if is_simulative and i > 0:
                marker = tokens.pop(i)
                marker.target = "như "
                x = tokens.pop(i - 1)
                tokens.insert(i - 1, marker)
                tokens.insert(i, x)
                i += 1
                continue
            i += 1
        return tokens
