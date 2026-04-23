#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
component_tagger.py — Recursively decompose multi-character phrases into head components
to infer their POS tags (Head-Final Rule).
"""
import sqlite3

class ComponentTagger:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._cache = {}
        # Preload all tagged words into cache for fast lookup
        self._preload_cache()

    def _preload_cache(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT source, pos_tag FROM entries WHERE pos_tag IS NOT NULL")
        for source, pos_tag in c.fetchall():
            self._cache[source] = pos_tag
        conn.close()
        print(f"    ComponentTagger: Preloaded {len(self._cache):,} known POS tags.")

    def get_tag(self, text: str) -> str | None:
        """Lookup POS tag from cache."""
        return self._cache.get(text)

    def decompose(self, source: str) -> str | None:
        """
        Decompose a word recursively using Head-Final logic.
        If word is length N, check [1:N], [2:N], etc for head noun/adjective.
        Returns the inferred pos_tag or None.
        """
        n = len(source)
        if n <= 1:
            return None

        # Head-Final strategy: Start checking the largest suffix
        # ABC -> check BC -> check C
        head_tag = None
        for i in range(1, n):
            suffix = source[i:]
            tag = self.get_tag(suffix)
            if tag:
                # 1. Exception: Check if head is a Particle or Classifier
                # if so, the phrase is likely a Noun Phrase taking properties of the prefix
                if tag in ("PARTICLE"):
                    prefix = source[:i]
                    if prefix_tag := self.get_tag(prefix):
                        return prefix_tag
                
                # 2. Main Rule: Follow the head
                head_tag = tag
                break
        
        if not head_tag:
            return None

        # Exception: Check if the word starts with a Verb
        # Verb + Noun = VERB (Verb phrase) e.g., "đánh nhau"
        # Since Chinese is often SVO, verb phrases start with verbs.
        for i in range(1, n):
            prefix = source[:i]
            prefix_tag = self.get_tag(prefix)
            if prefix_tag == "VERB":
                return "VERB"

        return head_tag

    def process_all_untagged(self) -> list[tuple[str, str]]:
        """
        Fetch all untagged records and decompose them.
        Returns list of (pos_tag, source) for SQL updating.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT source FROM entries WHERE pos_tag IS NULL AND length(source) >= 2")
        untagged = [row[0] for row in c.fetchall()]
        conn.close()

        print(f"    ComponentTagger: Analyzing {len(untagged):,} multi-character entries...")
        updates = []
        for source in untagged:
            tag = self.decompose(source)
            if tag:
                updates.append((tag, source))
        
        return updates
