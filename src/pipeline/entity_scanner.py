#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entity scanning on top of Trie and compiled metadata."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.core.runtime_support import RuntimeDictionaryAccessor
from src.core.trie_engine import TrieEngine


DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "dictionaries" / "_compiled" / "trie_cache.db"
COMMON_SURNAMES = set(
    "\u8d75\u94b1\u5b59\u674e\u5468\u5434\u90d1\u738b\u51af\u9648\u891a\u536b\u848b\u6c88\u97e9\u6768\u6731\u79e6\u5c24\u8bb8\u4f55\u5415\u5f20\u5b54\u66f9\u4e25\u534e\u91d1\u9b4f\u9676\u59dc\u621a\u8c22\u90b9\u55bb\u67cf\u6c34\u7aa6\u7ae0\u4e91\u82cf\u6f58\u845b\u595a\u8303\u5f6d\u90ce\u9c81\u97e6\u660c\u9a6c\u82d7\u51e4\u82b1\u65b9\u4fde\u4efb\u8881\u67f3"
    "\u9146\u9c8d\u53f2\u5510\u8d39\u5ec9\u5c91\u859b\u96f7\u8d3a\u502a\u6c64\u6ed5\u6bb7\u7f57\u6bd5\u90dd\u90ac\u5b89\u5e38\u4e50\u4e8e\u65f6\u5085\u76ae\u535e\u9f50\u5eb7\u4f0d\u4f59\u5143\u987e\u5b5f\u5e73\u9ec4\u548c\u7a46\u8427\u5c39\u59da\u90b5\u6e5b\u6c6a\u7941\u6bdb\u79b9\u72c4\u7c73\u8d1d\u660e\u81e7\u8ba1\u4f0f\u6210\u6234\u8c08\u5b8b\u8305\u5e9e\u718a"
    "\u7eaa\u8212\u5c48\u9879\u795d\u8463\u6881\u675c\u962e\u84dd\u95f5\u5e2d\u5b63\u9ebb\u5f3a\u8d3e\u8def\u5a04\u5371\u6c5f\u7ae5\u989c\u90ed\u6885\u76db\u6797\u949f\u5f90\u90b1\u9a86\u9ad8\u590f\u8521\u7530\u6a0a\u80e1\u51cc\u970d\u865e\u4e07\u652f\u67ef\u661d\u7ba1\u5362\u83ab\u7ecf\u623f\u88d8\u7f2a\u5e72\u89e3\u5e94\u5b97\u4e01\u5ba3\u8d32\u9093\u90c1\u5355\u676d"
    "\u6d2a\u5305\u8bf8\u5de6\u77f3\u5d14\u5409\u94ae\u9f9a\u7a0b\u5d47\u90a2\u6ed1\u88f4\u9646\u8363\u7fc1\u8340\u7f8a\u65bc\u60e0\u7504\u66f2\u5bb6\u5c01\u82ae\u7fbf\u50a8\u9773\u6c72\u90b4\u7cdc\u677e\u4e95\u6bb5\u5bcc\u5deb\u4e4c\u7126\u5df4\u5f13\u7267\u9697\u5c71\u8c37\u8f66\u4faf\u5b93\u84ec\u5168\u90d7\u73ed\u4ef0\u79cb\u4ef2\u4f0a\u5bab\u5b81\u4ec7\u683e\u66b4"
    "\u7518\u94ad\u5389\u620e\u7956\u6b66\u7b26\u5218\u666f\u8a79\u675f\u9f99\u53f6\u5e78\u53f8\u97f6\u90dc\u9ece\u84df\u8584\u5370\u5bbf\u767d\u6000\u84b2\u53f0\u4ece\u9102\u7d22\u54b8\u7c4d\u8d56\u5353\u853a\u5c60\u8499\u6c60\u4e54\u9634\u80e5\u80fd\u82cd\u53cc\u95fb\u8398\u515a\u7fdf\u8c2d\u8d21\u52b3\u9004\u59ec\u7533\u6276\u5835\u5189\u5bb0\u90e6\u96cd\u5374\u74a9"
    "\u6851\u6842\u6fee\u725b\u5bff\u901a\u8fb9\u6248\u71d5\u5180\u90cf\u6d66\u5c1a\u519c\u6e29\u522b\u5e84\u664f\u67f4\u77bf\u960e\u5145\u6155\u8fde\u8339\u4e60\u5ba6\u827e\u9c7c\u5bb9\u5411\u53e4\u6613\u614e\u6208\u5ed6\u5ebe\u7ec8\u66a8\u5c45\u8861\u6b65\u90fd\u803f\u6ee1\u5f18\u5321\u56fd\u6587\u5bc7\u5e7f\u7984\u9619\u4e1c\u6b27\u6bb3\u6c83\u5229\u851a\u8d8a\u5914"
    "\u9686\u5e08\u5de9\u538d\u8042\u6641\u52fe\u6556\u878d\u51b7\u8a3e\u8f9b\u961a\u90a3\u7b80\u9976\u7a7a\u66fe\u6bcb\u6c99\u4e5c\u517b\u97a0\u987b\u4e30\u5de2\u5173\u84af\u76f8\u67e5\u540e\u8346\u7ea2\u6e38\u7afa\u6743\u902f\u76d6\u76ca\u6853\u516c\u4ec9\u7763\u5cb3\u5e05\u7f11\u4ea2\u51b5\u90c8\u6709\u7434\u5f52\u6d77\u664b\u695a\u95eb"
)
COMPOUND_SURNAMES = {
    "\u6b27\u9633", "\u53f8\u9a6c", "\u4e0a\u5b98", "\u4e1c\u65b9", "\u72ec\u5b64", "\u5357\u5bab", "\u590f\u4faf", "\u8bf8\u845b", "\u5c09\u8fdf", "\u7687\u752b",
    "\u957f\u5b59", "\u5b87\u6587", "\u53f8\u5f92", "\u53f8\u7a7a", "\u516c\u5b59", "\u4ee4\u72d0", "\u8f69\u8f95", "\u4e1c\u90ed", "\u6155\u5bb9",
}
NAME_BOUNDARY_CHARS = set(
    "\uff0c\u3002\uff01\uff1f\uff1b\uff1a\u3001\u201c\u201d\u2018\u2019\uff08\uff09\u300a\u300b\u3008\u3009\u3010\u3011\u300e\u300f\u300c\u300d,.!?;:()[]{}<>\"' \n\r\t"
    "\u7684\u4e86\u7740\u8fc7\u90fd\u4e5f\u53c8\u5c31\u624d\u8fd8\u4fbf\u5e76\u4ece\u5411\u5bf9\u8ddf\u5728\u628a\u88ab\u7ed9\u6765\u53bb\u4f1a\u80fd\u53ef\u8981\u60f3\u662f\u8ba9\u540e\u524d"
    "\u62ff\u672c\u5f53\u5f80\u8fd9\u90a3\u5c06\u771f\u4e0d\u6ca1\u6253\u627e\u6293\u653e\u5417\u5462\u554a\u5440\u5427\u5566"
)
NAME_END_BOUNDARY_CHARS = set(
    "\uff0c\u3002\uff01\uff1f\uff1b\uff1a\u3001\u201c\u201d\u2018\u2019\uff08\uff09\u300a\u300b\u3008\u3009\u3010\u3011\u300e\u300f\u300c\u300d,.!?;:()[]{}<>\"' \n\r\t"
    "\u7684\u4e86\u7740\u8fc7\u4eec\u5417\u5462\u554a\u5440\u5427\u5566\u5728\u540e\u524d\u90fd\u4e5f\u53c8\u5c31\u624d\u8fd8\u4fbf\u5e76\u4ece\u5411\u5bf9\u8ddf\u628a\u88ab\u7ed9\u6765\u53bb\u4f1a\u80fd\u53ef\u8981\u60f3\u662f\u8ba9"
    "\u62ff\u672c\u5f53\u5f80\u8fd9\u90a3\u5c06\u771f\u4e0d\u6ca1\u6253\u627e\u6293\u653e"
)
NAME_INTRO_PREFIXES = {
    "\u53eb",
    "\u53eb\u505a",
    "\u53eb\u4f5c",
    "\u540d\u53eb",
    "\u540d\u4e3a",
}
STRONG_NAME_FOLLOW_CHARS = set("\u8bf4\u95ee\u770b\u8d70\u5750\u7ad9\u53eb\u558a\u7b11\u671b\u542c\u60f3\u62ff\u6253\u627e\u6293\u653e")
INVALID_NAME_CHARS = set(
    "\u7684\u4e00\u662f\u5728\u4e0d\u4e86\u6709\u548c\u4e0e\u53ca\u5e76\u6216\u4f46\u5c31\u53c8\u4e5f\u5f88\u8fd8\u5148\u518d\u5c06\u628a\u88ab\u8ba9\u7ed9\u8ddf\u4ece\u5230\u6765\u53bb\u8bf4\u95ee\u9053\u770b\u542c\u60f3\u4f1a\u80fd\u53ef\u56e0\u6240\u5982\u800c\u4e14\u53ea\u4ec0\u600e\u4e48\u54ea\u5417\u5462\u554a\u5440\u5427\u5566\u4e48\u5f97\u5730\u8fc7\u91cc\u90fd"
    "\u62ff\u672c\u8fd9\u90a3\u4e9b\u6ca1\u89c9\u4ef6\u4e2a"
    # Common verbs/adjectives that follow names but are NOT part of the name
    "\u9762"  # 面 (face/surface)
    "\u8eab"  # 身 (body)
    "\u70b9"  # 点 (dot/nod)
    "\u56de"  # 回 (return)
    "\u73b0"  # 现 (appear)
    "\u6b63"  # 正 (just/right)
    "\u8f6c"  # 转 (turn)
    "\u5012"  # 倒 (fall/pour)
    "\u4fbf"  # 便 (then/convenient)
    "\u521a"  # 刚 (just now)
    "\u80cc"  # 背 (back)
    "\u76b1"  # 皱 (wrinkle)
    "\u4ed6"  # 他 (he)
    "\u4f60"  # 你 (you)
    "\u63a5"  # 接 (receive)
    "\u6478"  # 摸 (touch)
    "\u677e"  # 松 (relax)
    "\u6447"  # 摇 (shake)
    "\u51b2"  # 冲 (rush)
    "\u5374"  # 却 (yet/but)
    "\u539f"  # 原 (original)
    "\u53f9"  # 叹 (sigh)
    "\u54ac"  # 咬 (bite)
    "\u5bb6"  # 家 (home)
    "\u5e26"  # 带 (bring)
    "\u5fae"  # 微 (tiny)
    "\u62b1"  # 抱 (hug)
    "\u8ba4"  # 认 (recognize)
    "\u8fdb"  # 进 (enter)
    "\u98de"  # 飞 (fly)
    "\u6307"  # 指 (point)
    "\u64e6"  # 擦 (wipe)
    "\u76ef"  # 盯 (stare)
    "\u773c"  # 眼 (eye)
    "\u8d8a"  # 越 (cross/more)
    "\u4e0b"  # 下 (down)
    "\u5411"  # 向 (toward)
    "\u9a91"  # 骑 (ride)
    "\u540e"  # 后 (after) — prevents swallowing temporal markers such as 后来
    "\u524d"  # 前 (before/front)
)
# Common word prefixes that should NEVER start a person name
COMMON_WORD_PREFIXES = {
    "\u6709",  # 有 (have)
    "\u548c",  # 和 (and)
    "\u80fd",  # 能 (can)
    "\u8fde",  # 连 (even)
    "\u76f8",  # 相 (mutual)
    "\u65b9",  # 方 (direction)
    "\u5f00",  # 开 (open)
    "\u8be5",  # 该 (should)
    "\u4e8e",  # 于 (at/in)
    "\u5f80",  # 往 (toward)
    "\u671d",  # 朝 (toward/dynasty) — often prefix in 朝着
    "\u901a\u77e5",  # 通知 (notify)
    "\u4eca\u5929",  # 今天 (today)
    "\u77e5\u9053",  # 知道 (know)
}
ENTITY_SUFFIX_FRAGMENTS = (
    "\u5b50\u5b66\u9662",
    "\u5b66\u9662",
    "\u5b66\u6821",
    "\u5927\u5b66",
    "\u4e2d\u5b66",
    "\u5c0f\u5b66",
    "\u533b\u9662",
    "\u516c\u53f8",
    "\u96c6\u56e2",
    "\u94f6\u884c",
    "\u4e66\u5e97",
    "\u5199\u5b57\u697c",
    "\u5927\u53a6",
    "\u5bbf\u820d\u697c",
    "\u5bbf\u820d",
    "\u516c\u5bd3",
    "\u7814\u7a76\u6240",
    "\u59d4\u5458\u4f1a",
    "\u534f\u4f1a",
    "\u5546\u573a",
)
DEMONSTRATIVE_NAME_PREFIX_CHARS = set("\u90a3\u8fd9\u67d0\u8be5\u6b64\u672c")
FALSE_NAME_START_BIGRAMS = {
    "\u5bf9\u4e8e",
    "\u5728\u4e8e",
}


@dataclass(slots=True)
class EntitySuggestion:
    source: str
    target: str
    entity_type: str
    confidence: float
    source_dict: str
    ambiguity_flag: bool
    count: int = 0
    positions: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class EntityScanner:
    """Scan for high-priority names and candidate terminology."""

    def __init__(self, db_path: str | None = None):
        self.db_path = str(db_path or DEFAULT_DB_PATH)
        self.trie = TrieEngine.from_shared_sqlite(self.db_path, enable_number_converter=False)
        self.accessor = RuntimeDictionaryAccessor(self.db_path)

    def scan(self, text: str) -> list[EntitySuggestion]:
        found: dict[str, EntitySuggestion] = {}
        idx = 0
        while idx < len(text):
            match = self.trie.lookup(text, idx)
            if not match:
                idx += 1
                continue

            record = self.accessor.lookup_runtime(match.source)
            category = record.category if record else ""
            if not self._is_entity_candidate(match.source, category, match.priority):
                idx += max(match.length, 1)
                continue

            entity_type = self._map_entity_type(category)
            ambiguity = ";" in match.target
            confidence = 0.98 if match.priority >= 4 else 0.75
            existing = found.get(match.source)
            raw_target = match.target.split(";", 1)[0].strip()
            if any("\u4e00" <= ch <= "\u9fff" for ch in raw_target):
                mapped_target = self.accessor.get_han_viet_for_text(raw_target)
            else:
                mapped_target = raw_target
                
            if existing is None:
                found[match.source] = EntitySuggestion(
                    source=match.source,
                    target=mapped_target,
                    entity_type=entity_type,
                    confidence=confidence,
                    source_dict=category or f"priority_{match.priority}",
                    ambiguity_flag=ambiguity,
                    count=1,
                    positions=[idx],
                )
            else:
                existing.count += 1
                existing.positions.append(idx)
            idx += match.length

        self._fallback_name_mining(text, found)
        self._fallback_location_mining(text, found)
        return sorted(found.values(), key=lambda item: (-item.confidence, -item.count, item.source))

    def _fallback_name_mining(self, text: str, found: dict[str, EntitySuggestion]):
        candidates: dict[str, dict[str, object]] = {}
        for idx in range(len(text)):
            # Check common word prefixes that should never be names
            if any(text[idx:].startswith(prefix) for prefix in COMMON_WORD_PREFIXES):
                continue

            surname_len = self._surname_prefix_length(text, idx)
            if surname_len == 0:
                continue

            start_score = self._score_name_start(text, idx)
            if start_score == 0:
                continue
            if self._looks_like_false_name_prefix(text, idx, start_score):
                continue

            lengths = (4, 3) if surname_len == 2 else (3, 2)
            best_candidate: tuple[str, int, int] | None = None
            for length in lengths:
                candidate = text[idx:idx + length]
                if len(candidate) != length:
                    continue
                if not self._looks_like_person_name(candidate, surname_len):
                    continue
                if self._is_known_non_name(candidate):
                    continue
                if self._looks_like_embedded_named_term(text, idx, candidate):
                    continue

                next_char = text[idx + length:idx + length + 1]
                end_score = self._score_name_end(next_char)
                if end_score == 0:
                    continue

                score = start_score + end_score + length
                if (
                    best_candidate is None
                    or score > best_candidate[1]
                    or (score == best_candidate[1] and len(candidate) < len(best_candidate[0]))
                ):
                    best_candidate = (candidate, score, end_score)

            if best_candidate is None:
                continue

            candidate, _, end_score = best_candidate
            payload = candidates.setdefault(candidate, {
                "positions": [],
                "strong_context": False,
            })
            payload["positions"].append(idx)
            if start_score >= 2 or end_score >= 2:
                payload["strong_context"] = True

        for source, payload in candidates.items():
            if source in found:
                continue
            positions = payload["positions"]
            if len(positions) < 2 and not payload["strong_context"]:
                continue
            found[source] = EntitySuggestion(
                source=source,
                target=self.accessor.get_han_viet_for_text(source),
                entity_type="person",
                confidence=0.72,
                source_dict="heuristic_name_mining",
                ambiguity_flag=False,
                count=len(positions),
                positions=list(positions),
            )

    def _fallback_location_mining(self, text: str, found: dict[str, EntitySuggestion]):
        LOCATION_SUFFIXES = {"城", "县", "镇", "村", "市", "省", "郡", "街", "山", "河", "江", "湖", "海", "谷", "岛", "州", "崖", "桥", "路", "区", "国", "星", "界", "宗", "派", "门", "庙", "洞", "府", "殿", "阁"}
        LOCATION_MARKERS_BEFORE = {"在", "去", "回", "到", "离", "赴", "入", "出", "向", "从", "由", "往", "过", "经", "是", "和", "让", "与"}
        
        candidates: dict[str, dict[str, object]] = {}
        for idx in range(len(text)):
            if text[idx] not in LOCATION_SUFFIXES:
                continue
                
            best_candidate: tuple[str, int, int] | None = None
            for prefix_len in (3, 2, 1):
                start_idx = idx - prefix_len
                if start_idx < 0:
                    continue
                    
                prefix = text[start_idx:idx]
                if not all("\u4e00" <= ch <= "\u9fff" for ch in prefix):
                    continue
                if any(ch in INVALID_NAME_CHARS for ch in prefix):
                    continue
                    
                before_char = text[start_idx - 1] if start_idx > 0 else " "
                
                start_score = 0
                if before_char in LOCATION_MARKERS_BEFORE:
                    start_score = 2
                elif before_char in NAME_BOUNDARY_CHARS:
                    start_score = 1
                    
                if start_score == 0:
                    continue
                    
                candidate = text[start_idx:idx + 1]
                if self._is_known_non_name(candidate):
                    continue
                    
                if best_candidate is None or start_score > best_candidate[1]:
                    best_candidate = (candidate, start_score, start_idx)
                    
            if best_candidate is None:
                continue
                
            candidate, start_score, start_idx = best_candidate
            payload = candidates.setdefault(candidate, {
                "positions": [],
                "strong_context": False,
            })
            payload["positions"].append(start_idx)
            if start_score >= 2:
                payload["strong_context"] = True
                
        for source, payload in candidates.items():
            if source in found:
                continue
            positions = payload["positions"]
            if len(positions) < 2 and not payload["strong_context"]:
                continue
            found[source] = EntitySuggestion(
                source=source,
                target=self.accessor.get_han_viet_for_text(source),
                entity_type="location",
                confidence=0.72,
                source_dict="heuristic_location_mining",
                ambiguity_flag=False,
                count=len(positions),
                positions=list(positions),
            )

    def _surname_prefix_length(self, text: str, idx: int) -> int:
        if idx + 1 < len(text) and text[idx:idx + 2] in COMPOUND_SURNAMES:
            return 2
        return 1 if text[idx] in COMMON_SURNAMES else 0

    def _looks_like_person_name(self, candidate: str, surname_len: int) -> bool:
        if len(candidate) <= surname_len or len(candidate) > surname_len + 2:
            return False
        if not all("\u4e00" <= ch <= "\u9fff" for ch in candidate):
            return False
        given_name = candidate[surname_len:]
        return not any(ch in INVALID_NAME_CHARS for ch in given_name)

    def _score_name_start(self, text: str, idx: int) -> int:
        if idx <= 0:
            return 1
        if text[max(0, idx - 2):idx] in NAME_INTRO_PREFIXES:
            return 2
        if text[idx - 1] in NAME_BOUNDARY_CHARS:
            return 1
        return 0

    def _score_name_end(self, next_char: str) -> int:
        if not next_char:
            return 1
        if next_char in STRONG_NAME_FOLLOW_CHARS:
            return 2
        if next_char in NAME_END_BOUNDARY_CHARS:
            return 1
        return 0

    def _is_known_non_name(self, candidate: str) -> bool:
        record = self.accessor.lookup_runtime(candidate)
        return bool(record and "names" not in record.category and record.priority < 4)

    def _looks_like_embedded_named_term(self, text: str, idx: int, candidate: str) -> bool:
        tail = text[idx + len(candidate):idx + len(candidate) + 5]
        if any(tail.startswith(fragment) for fragment in ENTITY_SUFFIX_FRAGMENTS):
            return True

        longer = self.trie.lookup(text, idx)
        if not longer or longer.length <= len(candidate) or not longer.source.startswith(candidate):
            return False

        record = self.accessor.lookup_runtime(longer.source)
        category = (record.category if record else "").lower()
        return any(marker in category for marker in ("org", "loc", "company", "school", "building"))

    def _looks_like_false_name_prefix(self, text: str, idx: int, start_score: int) -> bool:
        if start_score < 2 and text[idx] in DEMONSTRATIVE_NAME_PREFIX_CHARS:
            return True
        if idx <= 0:
            return False
        return text[idx - 1:idx + 1] in FALSE_NAME_START_BIGRAMS

    def _is_entity_candidate(self, source: str, category: str, priority: int) -> bool:
        if len(source) < 2:
            return False
        if "names" in category or priority >= 4:
            return True
        return category in {"cultivation", "realm", "items", "techniques"}

    def _map_entity_type(self, category: str) -> str:
        if "person" in category:
            return "person"
        if "loc" in category:
            return "location"
        if "org" in category:
            return "organization"
        if "weapon" in category:
            return "weapon"
        if "technique" in category:
            return "technique"
        if "cultivation" in category:
            return "realm"
        return "term"
