#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pos_seeder.py — Automatically seed POS tags for dictionary entries.

Supports 4 tiers of tagging:
1. Hardcoded Seeds (High precision, particles/conjunctions)
2. Category Inference (Names, Locations, etc.)
3. CC-CEDICT Cross-Ref (Standard dictionary POS)
4. Vietnamese Heuristics (Analyzing target Vietnamese words)
"""

import sqlite3
import re
import json
import os
from pathlib import Path

# ─────────────────────────────────────────────────
# Tier 1: Hardcoded Seeds
# ─────────────────────────────────────────────────
TIER1_SEEDS = {
    # ── Structural Particles ──
    "的": {"pos_tag": "PARTICLE", "pos_sub": "possessive", "is_function_word": 1},
    "了": {"pos_tag": "PARTICLE", "pos_sub": "aspect", "is_function_word": 1},
    "着": {"pos_tag": "PARTICLE", "pos_sub": "aspect", "is_function_word": 1},
    "过": {"pos_tag": "PARTICLE", "pos_sub": "aspect", "is_function_word": 1},
    "地": {"pos_tag": "PARTICLE", "pos_sub": "adverbial", "is_function_word": 1},
    "得": {"pos_tag": "PARTICLE", "pos_sub": "complement", "is_function_word": 1},
    "吗": {"pos_tag": "PARTICLE", "pos_sub": "question", "is_function_word": 1},
    "吧": {"pos_tag": "PARTICLE", "pos_sub": "suggestion", "is_function_word": 1},
    "呢": {"pos_tag": "PARTICLE", "pos_sub": "question", "is_function_word": 1},
    # ── Conjunctions ──
    "和": {"pos_tag": "CONJUNCTION", "is_function_word": 1},
    "与": {"pos_tag": "CONJUNCTION", "is_function_word": 1},
    "或": {"pos_tag": "CONJUNCTION", "is_function_word": 1},
    "但": {"pos_tag": "CONJUNCTION", "is_function_word": 1},
    "但是": {"pos_tag": "CONJUNCTION", "is_function_word": 1},
    "而": {"pos_tag": "CONJUNCTION", "is_function_word": 1},
    # ── Prepositions (including 把/被 = function words) ──
    "在": {"pos_tag": "PREPOSITION", "pos_sub": "locative", "is_function_word": 1},
    "从": {"pos_tag": "PREPOSITION", "pos_sub": "temporal", "is_function_word": 1},
    "对": {"pos_tag": "PREPOSITION", "pos_sub": "target", "is_function_word": 1},
    "向": {"pos_tag": "PREPOSITION", "pos_sub": "direction", "is_function_word": 1},
    "把": {"pos_tag": "PREPOSITION", "pos_sub": "ba_construction", "is_function_word": 1},
    "被": {"pos_tag": "PREPOSITION", "pos_sub": "passive", "is_function_word": 1},
    # ── Demonstratives ──
    "这": {"pos_tag": "PRONOUN", "pos_sub": "demonstrative", "is_function_word": 1},
    "那": {"pos_tag": "PRONOUN", "pos_sub": "demonstrative", "is_function_word": 1},
    # ── Personal / Indefinite Pronouns ──
    "我们": {"pos_tag": "PRONOUN", "pos_sub": "personal", "is_function_word": 1},
    "你": {"pos_tag": "PRONOUN", "pos_sub": "personal", "is_function_word": 1},
    "他": {"pos_tag": "PRONOUN", "pos_sub": "personal", "is_function_word": 1},
    "自己": {"pos_tag": "PRONOUN", "pos_sub": "reflexive", "is_function_word": 1},
    "别人": {"pos_tag": "PRONOUN", "pos_sub": "indefinite"},
    "您": {"pos_tag": "PRONOUN", "pos_sub": "personal", "is_function_word": 1},
    "咱们": {"pos_tag": "PRONOUN", "pos_sub": "personal", "is_function_word": 1},
    "您们": {"pos_tag": "PRONOUN", "pos_sub": "personal", "is_function_word": 1},
    "大伙儿": {"pos_tag": "PRONOUN", "pos_sub": "indefinite"},
    "自个儿": {"pos_tag": "PRONOUN", "pos_sub": "reflexive", "is_function_word": 1},
    "你娘亲": {"pos_tag": "PRONOUN", "pos_sub": "personal"},
    # ── Classifiers ──
    "个": {"pos_tag": "NOUN", "pos_sub": "classifier"},
    "座": {"pos_tag": "NOUN", "pos_sub": "classifier"},
    "块": {"pos_tag": "NOUN", "pos_sub": "classifier"},
    "根": {"pos_tag": "NOUN", "pos_sub": "classifier"},
    "只": {"pos_tag": "NOUN", "pos_sub": "classifier"},
    "双": {"pos_tag": "NOUN", "pos_sub": "classifier"},
    "条": {"pos_tag": "NOUN", "pos_sub": "classifier"},
    "张": {"pos_tag": "NOUN", "pos_sub": "classifier"},
    "位": {"pos_tag": "NOUN", "pos_sub": "classifier"},
    "道": {"pos_tag": "NOUN", "pos_sub": "classifier"},
    # ── Suffix (simulative) ──
    "似的": {"pos_tag": "ADJECTIVE", "pos_sub": "simulative"},
    "一样": {"pos_tag": "ADJECTIVE", "pos_sub": "simulative"},
    "一般": {"pos_tag": "ADJECTIVE", "pos_sub": "simulative"},
    # ── Xianxia Self-References ──
    "本座": {"pos_tag": "PRONOUN", "pos_sub": "honorific", "reorder_role": "head"},
    "本尊": {"pos_tag": "PRONOUN", "pos_sub": "honorific", "reorder_role": "head"},
    "本圣": {"pos_tag": "PRONOUN", "pos_sub": "honorific", "reorder_role": "head"},
    "本帝": {"pos_tag": "PRONOUN", "pos_sub": "honorific", "reorder_role": "head"},
    "本王": {"pos_tag": "PRONOUN", "pos_sub": "honorific", "reorder_role": "head"},
    "朕": {"pos_tag": "PRONOUN", "pos_sub": "honorific", "reorder_role": "head"},
    "孤": {"pos_tag": "PRONOUN", "pos_sub": "honorific", "is_function_word": 1},
    # ── Misc Quick Wins ──
    "老师们": {"pos_tag": "NOUN"},
    "同学们": {"pos_tag": "NOUN"},
    "少爷": {"pos_tag": "NOUN"},
    "伤天": {"pos_tag": "NOUN"},
}

# ─────────────────────────────────────────────────
# Tier 4: Vietnamese Heuristics
# ─────────────────────────────────────────────────

# VERB heuristic markers (prefixes)
VI_VERB_PREFIXES = {
    "đang", "đã", "sẽ", "được", "bị", "hãy", "chớ", "đừng", "vừa", "mới", 
    "muốn", "cần", "nên", "phải", "có thể", "biết", "cho", "làm", "thôi",
    "mặc", "đeo", "mang", "cầm", "nắm", "đi", "đứng", "ngồi", "nằm",
    "đánh", "bắt", "giết", "chém", "phá", "kéo", "đẩy", "ném", "cắt", "đấm", "xé", "bóp"
}

# ADVERB heuristic markers
VI_ADV_MARKERS = {
    "đã", "đang", "sẽ", "vẫn", "cũng", "lại", "chỉ", "mới", "còn", "từng", "luôn", "thường"
}

# LOCATIVE heuristic markers
VI_LOCATIVE_MARKERS = {
    "trước", "sau", "trên", "dưới", "trong", "ngoài", "phía", "bên"
}

# ADJECTIVE heuristic markers (intensifiers)
VI_ADJ_MARKERS = {
    "rất", "hơi", "quá", "lắm", "nhất", "cực kỳ", "vô cùng", "vô hạn", 
    "tuyệt đối", "đặc biệt", "khá", "hơi hơi", "tương đối",
    "thật", "hết sức"
}

# NOUN heuristic markers (abstract noun prefixes)
VI_NOUN_PREFIXES = {
    "sự", "cuộc", "nỗi", "niềm", "cái", "việc", "mối", "luồng", "tấm", "đám"
}

# NOUN classifiers
VI_CLASSIFIERS = {
    "cái", "con", "chiếc", "tấm", "ngọn", "đóa", "pho", "bức", "viên", "hột", 
    "quả", "trái", "cây", "quyển", "cuốn", "bài", "tờ", "lá", "nhánh"
}

# ─────────────────────────────────────────────────
# CEDICT Adjective Hints
# ─────────────────────────────────────────────────

# Common English adjective words that appear as CEDICT meanings
_CEDICT_ADJ_HINTS = {
    "beautiful", "pretty", "ugly", "big", "small", "large", "tiny",
    "long", "short", "tall", "wide", "narrow", "thick", "thin",
    "hot", "cold", "warm", "cool", "wet", "dry",
    "fast", "slow", "quick", "hard", "soft", "heavy", "light",
    "bright", "dark", "clean", "dirty", "new", "old",
    "strong", "weak", "rich", "poor", "young", "deep", "shallow",
    "sharp", "dull", "smooth", "rough", "sweet", "bitter", "sour",
    "round", "flat", "full", "empty", "white", "black", "red",
    "green", "blue", "yellow", "fierce", "gentle", "cruel",
    "pale", "dim", "rotten", "decayed", "withered",
    "happy", "sad", "angry", "scared", "brave", "cowardly", "proud", "humble",
    "clever", "stupid", "smart", "dumb", "wise", "foolish", "crazy", "sane",
    "good", "bad", "great", "terrible", "awesome", "awful", "excellent", "poor",
    "clear", "vague", "certain", "unsure", "sure", "doubtful", "true", "false",
    "real", "fake", "genuine", "artificial", "natural", "synthetic", "pure", "impure",
    "safe", "dangerous", "secure", "insecure", "protected", "vulnerable", "hidden", "exposed",
    "easy", "difficult", "simple", "complex", "complicated", "basic", "advanced",
    "right", "wrong", "correct", "incorrect", "fair", "unfair", "just", "unjust",
}

# English adjective suffix patterns
_ADJ_SUFFIXES = ("ful", "less", "ous", "ive", "able", "ible", "ent", "ant", "ish", "al", "ory")


def _is_english_adjective(meaning: str) -> bool:
    """Heuristic: detect if a CEDICT meaning string is an adjective."""
    meaning = meaning.strip().rstrip(".")
    # Skip multi-word meanings (likely definitions, not POS hints)
    words = meaning.split()
    if len(words) > 2:
        return False
    first = words[0].lower()
    # Direct match
    if first in _CEDICT_ADJ_HINTS:
        return True
    # Suffix-based
    for suffix in _ADJ_SUFFIXES:
        if first.endswith(suffix) and len(first) > len(suffix) + 2:
            return True
    return False


def infer_pos_from_vi(vi_text: str) -> dict:
    """Infer POS tag from Vietnamese translation using linguistic prefixes."""
    vi_text = vi_text.lower().strip()
    
    if "/" in vi_text:
        parts = [p.strip() for p in vi_text.split('/') if p.strip()]
        votes = {}
        for part in parts:
            res = _infer_single_vi(part)
            if res and "pos_tag" in res:
                tag = res["pos_tag"]
                votes[tag] = votes.get(tag, 0) + 1
        if votes:
            best_tag = max(votes, key=votes.get)
            return {"pos_tag": best_tag}
        return {}
    
    return _infer_single_vi(vi_text)

def _infer_single_vi(vi_text: str) -> dict:
    words = vi_text.split()
    if not words:
        return {}

    # 1. NOUN (Classification/Abstraction)
    if words[0] in VI_NOUN_PREFIXES or words[0] in VI_CLASSIFIERS:
        return {"pos_tag": "NOUN", "pos_sub": "classifier" if words[0] in VI_CLASSIFIERS else "abstract"}

    # 2. VERB (Markers)
    if words[0] in VI_VERB_PREFIXES:
        return {"pos_tag": "VERB"}
    
    # 2.5 ADVERB (Markers)
    if words[0] in VI_ADV_MARKERS:
        return {"pos_tag": "ADVERB"}
    
    # 3. ADJECTIVE (Intensifiers at start)
    if words[0] in VI_ADJ_MARKERS:
        return {"pos_tag": "ADJECTIVE"}
    
    # 4. ADJECTIVE (Intensifiers at end)
    if words[-1] in {"lắm", "quá", "thay", "nhất", "nhỉ"}:
        return {"pos_tag": "ADJECTIVE"}

    # 5. LOCATIVE (Location markers)
    if words[0] in VI_LOCATIVE_MARKERS:
        return {"pos_tag": "NOUN", "pos_sub": "location"}

    return {}

# ─────────────────────────────────────────────────
# Seeder Class
# ─────────────────────────────────────────────────

class POSSeeder:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _parse_cedict(self, cedict_path: str) -> dict[str, dict]:
        """Parse CC-CEDICT and extract inferred POS tags."""
        cedict_data = {}
        if not os.path.exists(cedict_path):
            print(f"    Warning: CEDICT file not found at {cedict_path}")
            return {}

        print(f"    Reading {cedict_path}...")
        with open(cedict_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                
                # Use split to be safer than regex
                # CC-CEDICT: Traditional Simplified [pinyin] /meanings/
                try:
                    parts = line.split(maxsplit=2)
                    if len(parts) < 3: continue
                    trad, simp = parts[0], parts[1]
                    rest = parts[2]
                    
                    # Meanings are between /.../
                    m_start = rest.find('/')
                    m_end = rest.rfind('/')
                    if m_start == -1 or m_end == -1: continue
                    
                    meanings_raw = rest[m_start+1 : m_end]
                    meanings = [m.strip() for m in meanings_raw.split('/') if m.strip()]
                    if not meanings: continue
                    
                    pinyin_match = re.search(r'\[(.*?)\]', rest)
                    pinyin = pinyin_match.group(1) if pinyin_match else None
                    
                except Exception as e:
                    continue
                
                pos_info = {}
                # Extract pinyin and traditional
                if pinyin:
                    pos_info["pinyin"] = pinyin
                if trad and trad != simp:
                    pos_info["traditional"] = trad

                # Heuristics for CEDICT meanings
                for m in meanings:
                    ml = m.lower()
                    if "(idiom)" in ml:
                        pos_info = {"pos_tag": "NOUN", "pos_sub": "idiom"}
                        break
                    if ml[:3] == "to " or ml[:4] == "to /" or " to " in ml:
                        pos_info = {"pos_tag": "VERB"}
                        break
                    if "(adv)" in ml or ml.rstrip() in {"immediately", "suddenly", "already", "very", "truly", "gradually", "still", "yet"}:
                        pos_info["pos_tag"] = "ADVERB"
                        break
                    if "surname " in ml:
                        pos_info = {"pos_tag": "NOUN", "pos_sub": "name", "entity_type": "person"}
                        break
                    if "classifier for " in ml or "cl:" in ml:
                        pos_info = {"pos_tag": "NOUN", "pos_sub": "classifier"}
                        break
                    # ADJ detection: English adjective patterns
                    if "(adj)" in ml or ml.rstrip() in _CEDICT_ADJ_HINTS:
                        pos_info = {"pos_tag": "ADJECTIVE"}
                        break
                    # ADJ heuristic: meanings that ARE adjectives
                    if _is_english_adjective(ml):
                        pos_info = {"pos_tag": "ADJECTIVE"}
                        break
                    if "(math.)" in ml or "(physics)" in ml or "(chem.)" in ml:
                        pos_info["pos_tag"] = "NOUN"
                        pos_info["register_level"] = "technical"
                    if "(archaic)" in ml or "(dialect)" in ml:
                        pos_info["cultural_origin"] = "archaic"
                    if "variant of " in ml:
                        continue
                    
                # Broad Fallback for CEDICT
                if "pos_tag" not in pos_info and meanings:
                    first_meaning = meanings[0].lower().strip()
                    words = first_meaning.split()
                    if len(words) <= 3:
                         pos_info["pos_tag"] = "NOUN"

                if pos_info:
                    cedict_data[simp] = pos_info
                    cedict_data[trad] = pos_info
        
        return cedict_data

    def seed(self):
        conn = sqlite3.connect(self.db_path)
        conn.create_function("REGEXP", 2, lambda expr, item: 1 if item is not None and re.search(expr, str(item)) else 0)
        c = conn.cursor()
        
        print("Starting POS Seeding...")
        
        # 1. Tier 1: Hardcoded
        print("  Applying Tier 1: Hardcoded Seeds...")
        for source, meta in TIER1_SEEDS.items():
            fields = ", ".join([f"{k} = ?" for k in meta.keys()])
            values = list(meta.values()) + [source]
            c.execute(f"UPDATE entries SET {fields} WHERE source = ?", values)
        
        # 2. Tier 2: Category Inference
        print("  Applying Tier 2: Category Inference...")
        # Names (Person)
        c.execute("""
            UPDATE entries 
            SET pos_tag = 'NOUN', pos_sub = 'name', entity_type = 'person', reorder_role = 'head', luat_nhan_trigger = 1
            WHERE (category LIKE '%names_person%' OR category = 'characters')
        """)
        # Names (Location)
        c.execute("""
            UPDATE entries 
            SET pos_tag = 'NOUN', pos_sub = 'location', entity_type = 'location', reorder_role = 'head', luat_nhan_trigger = 1
            WHERE (category LIKE '%names_loc%' OR category = 'locations')
        """)
        # Names (Organization)
        c.execute("""
            UPDATE entries 
            SET pos_tag = 'NOUN', pos_sub = 'name', entity_type = 'organization', reorder_role = 'head', luat_nhan_trigger = 1
            WHERE category LIKE '%names_org%'
        """)
        # Names (Misc / Artifacts)
        c.execute("""
            UPDATE entries 
            SET pos_tag = 'NOUN', pos_sub = 'name', entity_type = 'artifact', reorder_role = 'head', luat_nhan_trigger = 1
            WHERE category LIKE '%names_misc%'
        """)
        # PhienAm (single char)
        c.execute("""
            UPDATE entries 
            SET pos_tag = 'NOUN', pos_sub = 'component'
            WHERE category = 'phien_am' AND length(source) = 1 AND pos_tag IS NULL
        """)
        # Idioms (trichdan_idioms)
        c.execute("""
            UPDATE entries
            SET pos_tag = 'NOUN', pos_sub = 'idiom'
            WHERE category = 'trichdan_idioms' AND pos_tag IS NULL
        """)
        # Latin Num Patterns (X月, X市) and pure digits/latin
        c.execute("""
            UPDATE entries
            SET pos_tag = 'NOUN', pos_sub = 'time'
            WHERE category = 'vietphrase_latin_num' AND source LIKE '%月' AND pos_tag IS NULL
        """)
        c.execute("""
            UPDATE entries
            SET pos_tag = 'NOUN', pos_sub = 'location'
            WHERE category = 'vietphrase_latin_num' AND source LIKE '%市' AND pos_tag IS NULL
        """)
        c.execute(r"""
            UPDATE entries
            SET pos_tag = 'NUMBER'
            WHERE category = 'vietphrase_latin_num' AND pos_tag IS NULL
              AND source REGEXP '^[0-9]+(\.[0-9]+)?$'
        """)
        # Fallback for remaining latin_num
        c.execute("""
            UPDATE entries
            SET pos_tag = 'NOUN', pos_sub = 'misc'
            WHERE category = 'vietphrase_latin_num' AND pos_tag IS NULL
        """)
        
        # 3. Tier 3: CC-CEDICT Cross-Ref
        print("  Applying Tier 3: CC-CEDICT Cross-Ref...")
        cedict_path = r"d:\Converter by DrDuc\data\external\cedict_ts.u8"
        cedict_pos_map = self._parse_cedict(cedict_path)
        print(f"    Loaded {len(cedict_pos_map):,} POS tags from CEDICT.")
        
        # CRITICAL: Use COALESCE in SQL so we never overwrite existing data
        # We fetch rows missing ANY metadata (pos_tag, pinyin, or traditional)
        c.execute("SELECT source FROM entries WHERE pos_tag IS NULL OR pinyin IS NULL OR traditional IS NULL")
        null_rows = c.fetchall()
        cedict_updates = []
        log_path = "cedict_seeding_debug.txt"
        with open(log_path, "w", encoding="utf-8") as debug_f:
            debug_f.write(f"Scanning {len(null_rows):,} NULL entries against CEDICT map...\n")
            debug_count = 0
            for (source,) in null_rows:
                if source in cedict_pos_map:
                    meta = cedict_pos_map[source]
                    if debug_count < 100:
                        debug_f.write(f"Matched: {source} -> {meta}\n")
                        debug_count += 1
                    cedict_updates.append((
                        meta.get("pos_tag"),
                        meta.get("pos_sub"),
                        meta.get("entity_type"),
                        meta.get("is_function_word", 0),
                        meta.get("reorder_role"),
                        meta.get("cultural_origin"),
                        meta.get("register_level"),
                        meta.get("pinyin"),
                        meta.get("traditional"),
                        source
                    ))
            
            for check in ["男子", "女子", "灵气", "身躯", "美丽", "把", "被"]:
                if check in cedict_pos_map:
                    status = f"[CHECK] {check} is in map: {cedict_pos_map[check]}\n"
                else:
                    status = f"[CHECK] {check} is NOT in map\n"
                debug_f.write(status)
        
        if cedict_updates:
            print(f"    Updating {len(cedict_updates):,} entries from CEDICT...")
            c.executemany("""
                UPDATE entries 
                SET pos_tag = COALESCE(pos_tag, ?), 
                    pos_sub = COALESCE(pos_sub, ?), 
                    entity_type = COALESCE(entity_type, ?), 
                    is_function_word = COALESCE(is_function_word, ?), 
                    reorder_role = COALESCE(reorder_role, ?), 
                    cultural_origin = COALESCE(cultural_origin, ?), 
                    register_level = COALESCE(register_level, ?),
                    pinyin = COALESCE(pinyin, ?),
                    traditional = COALESCE(traditional, ?)
                WHERE source = ?
            """, cedict_updates)

        # 4. Tier 4: Vietnamese Heuristics (Slow)
        print("  Applying Tier 4: Vietnamese Heuristics...")
        # Now checking even if pos_tag is set, to fill pos_sub if NULL
        c.execute("SELECT source, target, pos_tag, pos_sub FROM entries WHERE (pos_tag IS NULL OR pos_sub IS NULL)")
        rows = c.fetchall()
        print(f"    Checking {len(rows):,} entries for missing POS/Sub...")
        
        update_data = []
        for source, target, cur_tag, cur_sub in rows:
            inferred = infer_pos_from_vi(target)
            if inferred:
                # Only update if current is NULL
                new_tag = cur_tag if cur_tag else inferred['pos_tag']
                new_sub = cur_sub if cur_sub else inferred.get('pos_sub')
                if new_tag != cur_tag or new_sub != cur_sub:
                    update_data.append((new_tag, new_sub, source))
        
        if update_data:
            print(f"    Applying {len(update_data):,} heuristic updates...")
            c.executemany("UPDATE entries SET pos_tag = ?, pos_sub = ? WHERE source = ?", update_data)
        
        # 5. Tier 5: Component Decomposition (3-5+ length)
        print("  Applying Tier 5: Component Decomposition...")
        from src.tools.component_tagger import ComponentTagger
        tagger = ComponentTagger(self.db_path)
        decomp_updates = tagger.process_all_untagged()
        if decomp_updates:
            print(f"    Applying {len(decomp_updates):,} decomposition updates...")
            c.executemany("UPDATE entries SET pos_tag = ? WHERE source = ?", decomp_updates)
            
        # 6. Tier 6: Collocations and Idioms for Remaining Long Phrases
        print("  Applying Tier 6: Collocation & Idiom Fallback...")
        # 4-char CJK characters are likely idioms
        c.execute("""
            UPDATE entries
            SET pos_tag = 'NOUN', pos_sub = 'idiom'
            WHERE pos_tag IS NULL AND length(source) = 4
        """)
        # Long phrases that are 4+ length and untagged map to NOUN/collocation
        c.execute("""
            UPDATE entries
            SET pos_tag = 'NOUN', pos_sub = 'collocation'
            WHERE pos_tag IS NULL AND category IN ('vietphrase_5plus', 'vietphrase_4char')
        """)
            
        conn.commit()
        
        # Check coverage
        c.execute("SELECT COUNT(*) FROM entries")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM entries WHERE pos_tag IS NOT NULL")
        tagged = c.fetchone()[0]
        
        print(f"\nSeeding Complete!")
        print(f"  Tagged: {tagged:,} / {total:,} ({tagged/total:.1%})")
        
        conn.close()

        # 7. Tier 7: Pinyin & Traditional Cascade Construction
        print("  Applying Tier 7: Pinyin/Traditional Cascade...")
        from src.tools.pinyin_cascade import CascadeEngine
        cascade = CascadeEngine(self.db_path)
        cascade.cascade_all()

if __name__ == "__main__":
    db_path = r"d:\Converter by DrDuc\data\dictionaries\_compiled\trie_cache.db"
    seeder = POSSeeder(db_path)
    seeder.seed()
