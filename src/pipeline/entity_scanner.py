#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entity scanning on top of Trie and compiled metadata."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.core.runtime_support import RuntimeDictionaryAccessor
from src.core.trie_engine import TrieEngine
from src.pipeline.name_reading import (
    HanVietNameResolver,
    first_target_variant,
    has_cjk,
    looks_like_latin_transliteration_source,
)
from src.pipeline.term_bank import PROPER_ENTITY_TYPES, TermBank, TermBankRecord
from src.pipeline.universe import resolve_project_universe_id, slugify_universe_id


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
NAME_TITLE_FOLLOWERS = {
    "\u9662\u58eb",  # 院士
    "\u5c40\u957f",  # 局长
    "\u79d8\u4e66",  # 秘书
    "\u5c45\u58eb",  # 居士
    "\u5927\u4eba",  # 大人
    "\u65bd\u4e3b",  # 施主
    "\u4e66\u751f",  # 书生
    "\u771f\u4eba",  # 真人
    "\u79d1\u957f",  # 科长
}
STRONG_NAME_FOLLOW_CHARS = set(
    "\u8bf4\u95ee\u770b\u8d70\u5750\u7ad9\u53eb\u558a\u7b11\u671b\u542c\u60f3\u62ff\u6253\u627e\u6293\u653e"
    "\u70b9\u6447\u62ac\u76b1\u53f9\u54ac\u63a5\u8f6c\u51b2"
)
INVALID_NAME_CHARS = set(
    "\u7684\u4e00\u662f\u5728\u4e0d\u4e86\u6709\u548c\u4e0e\u53ca\u5e76\u6216\u4f46\u5c31\u53c8\u4e5f\u5f88\u8fd8\u5148\u518d\u5c06\u628a\u88ab\u8ba9\u7ed9\u8ddf\u4ece\u5230\u6765\u53bb\u8bf4\u95ee\u9053\u770b\u542c\u60f3\u4f1a\u80fd\u53ef\u56e0\u6240\u5982\u800c\u4e14\u53ea\u4ec0\u600e\u4e48\u54ea\u5417\u5462\u554a\u5440\u5427\u5566\u4e48\u5f97\u5730\u8fc7\u91cc\u90fd"
    "\u5bf9\u5fcd\u76f4\u6487\u8d76\u7d27\u522b\u5750\u5b83\u5f31"
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
    "\u6211"  # 我 (I/me)
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
    "\u65f6",  # 时 (temporal marker) — avoids swallowing 这时/同时 before a name
    "\u901a\u77e5",  # 通知 (notify)
    "\u4eca\u5929",  # 今天 (today)
    "\u77e5\u9053",  # 知道 (know)
    "\u6210\u4e3a",  # 成为 (become)
    "\u5bb9\u6613",  # 容易 (easy)
    "\u6bd5\u7adf",  # 毕竟 (after all)
    "\u597d\u50cf",  # 好像 (seems like)
    "\u8ba1\u5176",  # 计其 (as in 不计其数)
    "\u7518\u793a",  # 甘示 (as in 不甘示弱)
    "\u8f66\u4e4b",  # 车之 (as in 前车之鉴)
    "\u5374",  # 却 (but/yet)
    "\u90fd",  # 都 (all)
    "\u522b",  # 别 (do not/other)
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
COMMON_NON_PERSON_NAME_TERMS = {
    "\u4ed6\u4eec",
    "\u5979\u4eec",
    "\u6211\u4eec",
    "\u4f60\u4eec",
    "\u5927\u5bb6",
    "\u4e00\u822c\u4eba",
    "\u8fd9\u4e9b\u4eba",
    "\u90a3\u4e9b\u4eba",
    "\u5929\u4e0b\u4eba",
    "\u4f17\u4eba",
    "\u4e16\u4eba",
    "\u5e38\u4eba",
    "\u666e\u901a\u4eba",
    "\u51e1\u4eba",
    "\u8def\u4eba",
    "\u4fee\u70bc\u8005",
    "\u6b66\u8005",
    "\u9053\u58eb",
    "\u548c\u5c1a",
    "\u4fa0\u5ba2",
    "\u6ca1\u6709\u4eba",
    "\u4efb\u4f55\u4eba",
    "\u6bcf\u4e2a\u4eba",
    "\u5929\u5730",
    "\u4e16\u754c",
    "\u65f6\u95f4",
    "\u4eca\u65e5",
    "\u660e\u65e5",
    "\u5929\u9053",
    "\u5927\u9053",
    "\u738b\u9053",
    "\u7075\u6c14",
    "\u5143\u6c14",
    "\u5c71\u6cb3",
    "\u4e3b\u795e",
    "\u7cfb\u7edf",
    "\u4efb\u52a1",
    "\u6c5f\u6e56",
    "\u5929\u4e0b",
    "\u9ed1\u6697",
    "\u5149\u660e",
    "\u8111\u6d1e",
}
DICTIONARY_ENTITY_TYPE_OVERRIDES = {
    "\u5730\u7403": "location",  # 地球
    "\u6606\u4ed1": "location",  # 昆仑
    "\u5357\u5b8b": "location",  # 南宋
    "\u987b\u5f25": "location",  # 须弥
}
DICTIONARY_NON_ENTITY_SOURCES = {
    "\u6587\u6b66",  # 文武
    "\u957f\u751f",  # 长生
    "\u96f7\u9706",  # 雷霆
}
LOCATION_COMMON_PHRASES = {
    "\u8111\u6d1e",  # 脑洞
    "\u4e16\u754c\u5404\u56fd",  # 世界各国
    "\u4e94\u5ea7\u795e\u5c71",  # 五座神山
    "\u56db\u4f4d\u5b97",  # 四位宗
    "\u65e5\u6708\u661f",  # 日月星
    "\u4e8c\u5341\u516b\u661f",  # 二十八星
    "\u5b9e\u4e16\u754c",  # 实世界
    "\u6d6e\u7a7a\u57ce\u5e02",  # 浮空城市
    "\u6d9b\u6d9b\u51a5\u6cb3",  # 涛涛冥河
}
FALLBACK_PERSON_ENTITY_SOURCES = {
    "\u592a\u767d\u91d1\u661f",  # 太白金星
}
CHINESE_NUMERAL_CHARS = set("\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e\u5343\u4e07\u4e24")
LOCATION_CLASSIFIER_CHARS = set("\u5ea7\u4f4d")
PERSON_TITLE_SUFFIXES = tuple(NAME_TITLE_FOLLOWERS)
PERSON_NON_NAME_SUFFIXES = (
    "\u65f6\u95f4",  # 时间
    "\u5c40",  # 局
    "\u5c71",  # 山
    "\u53f0",  # 台
    "\u699c",  # 榜
    "\u9600",  # 阀
    "\u7bad",  # 箭
    "\u836f",  # 药
    "\u5178",  # 典
)
LOCATION_SUFFIXES = {"\u57ce", "\u53bf", "\u9547", "\u6751", "\u5e02", "\u7701", "\u90e1", "\u8857", "\u5c71", "\u6cb3", "\u6c5f", "\u6e56", "\u6d77", "\u8c37", "\u5c9b", "\u5dde", "\u5d16", "\u6865", "\u8def", "\u533a", "\u56fd", "\u661f", "\u754c", "\u5b97", "\u6d3e", "\u95e8", "\u5e99", "\u6d1e", "\u5e9c", "\u6bbf", "\u9601"}
ORGANIZATION_SUFFIXES = {"\u5c40", "\u9662", "\u5bfa", "\u6559", "\u4f1a", "\u76df", "\u90e8", "\u53f8"}
LOCATION_BAD_PREFIXES = (
    "\u5bf9\u7740",  # 对着
    "\u5f00\u8f9f",  # 开辟
    "\u597d\u50cf",  # 好像
    "\u4e16\u754c\u5404",  # 世界各
    "\u6d9b\u6d9b",  # 涛涛
    "\u603b\u7406",  # 总理
    "\u603b\u7edf",  # 总统
    "\u4e07\u519b",  # 万军
    "\u4e3b\u5bb0",  # 主宰
    "\u6267\u638c",  # 执掌
)
LOCATION_INVALID_START_CHARS = set("\u65f6\u6211\u4f60\u4ed6\u5979\u5b83\u8fd9\u90a3\u6b64\u4e3a\u4ece\u968f\u5c31\u90fd\u5bf9\u7740\u5f00\u597d\u5904\u4f4d\u65b9")
LOCATION_INVALID_INTERIOR_CHARS = set("\u6211\u4f60\u4ed6\u5979\u5b83\u4eec")


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
    universe: str = ""
    work: str = ""
    review_status: str = "pending"
    enrichment_ready: bool = False
    suggested_tags: list[str] = field(default_factory=list)
    suggested_context_markers: list[str] = field(default_factory=list)
    qa_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class EntityScanner:
    """Scan for high-priority names and candidate terminology."""

    def __init__(
        self,
        db_path: str | None = None,
        *,
        project_id: str | None = None,
        project_dir: str | Path | None = None,
        universe_id: str | None = None,
    ):
        self.db_path = str(db_path or DEFAULT_DB_PATH)
        self.trie = TrieEngine.from_shared_sqlite(self.db_path, enable_number_converter=False)
        self.accessor = RuntimeDictionaryAccessor(self.db_path)
        self.term_bank = TermBank(project_id=project_id, project_dir=project_dir)
        self.name_resolver = HanVietNameResolver(self.accessor, self.term_bank)
        self.default_universe_id = slugify_universe_id(universe_id) or resolve_project_universe_id(
            project_id=project_id,
            project_dir=project_dir,
        )

    def set_project_context(
        self,
        *,
        project_id: str | None = None,
        project_dir: str | Path | None = None,
        universe_id: str | None = None,
    ) -> None:
        self.term_bank.set_project_context(project_id=project_id, project_dir=project_dir)
        self.name_resolver.set_term_bank(self.term_bank)
        self.default_universe_id = slugify_universe_id(universe_id) or resolve_project_universe_id(
            project_id=project_id,
            project_dir=project_dir,
        )

    def close(self):
        self.accessor.close()

    def scan(self, text: str) -> list[EntitySuggestion]:
        found: dict[str, EntitySuggestion] = {}
        active_universes = [
            universe
            for universe, confidence in self.term_bank.detect_universe(text)
            if confidence >= 0.5
        ]
        if self.default_universe_id and self.default_universe_id not in active_universes:
            active_universes.append(self.default_universe_id)
        self._scan_term_bank(text, found, active_universes=active_universes)
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

            entity_type = self._map_entity_type(match.source, category)
            ambiguity = ";" in match.target
            confidence = 0.98 if match.priority >= 4 else 0.75
            existing = found.get(match.source)
            if existing is not None and "term_bank" in existing.source_dict:
                idx += match.length
                continue
            raw_target = first_target_variant(match.target)
            mapped_target = self.name_resolver.resolve_word_by_word(raw_target) if has_cjk(raw_target) else raw_target
            mapped_target = self.name_resolver.resolve_entity_target(
                match.source,
                entity_type=entity_type,
                source_dict=category or f"priority_{match.priority}",
                current_target=mapped_target,
            )
                
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
        self._drop_shadowed_term_bank_prefixes(found)
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
                if self._looks_like_non_person_entity_shape(candidate):
                    continue
                if self._is_known_non_name(candidate):
                    continue
                if self._looks_like_common_non_person_phrase(candidate):
                    continue
                if self._looks_like_embedded_named_term(text, idx, candidate):
                    continue

                end_score = self._score_name_end(text, idx + length)
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
            if self._looks_like_common_non_person_phrase(source):
                continue
            latin_target = self.name_resolver.resolve_latin_target(
                source,
                allow_phonetic=looks_like_latin_transliteration_source(source),
                entity_type="person",
            )
            source_dict = "heuristic_latin_name_mining" if latin_target else "heuristic_name_mining"
            found[source] = EntitySuggestion(
                source=source,
                target=latin_target or self.name_resolver.resolve_entity_target(
                    source,
                    entity_type="person",
                    source_dict=source_dict,
                    current_target=source,
                ),
                entity_type="person",
                confidence=0.72,
                source_dict=source_dict,
                ambiguity_flag=False,
                count=len(positions),
                positions=list(positions),
            )

    def detect_universe(self, text: str) -> list[tuple[str, float]]:
        return self.term_bank.detect_universe(text)

    def _scan_term_bank(self, text: str, found: dict[str, EntitySuggestion], *, active_universes: list[str] | None = None) -> None:
        sources: dict[str, str] = {}
        active_set = {slugify_universe_id(item) for item in (active_universes or []) if item}
        active_set.discard("unknown")
        for record in self.term_bank.iter_active():
            if record.scope == "universe" and active_set and slugify_universe_id(record.universe) not in active_set:
                continue
            if record.entity_type not in PROPER_ENTITY_TYPES and record.entity_type != "term":
                continue
            sources.setdefault(record.source, record.entity_type)
            for alias in record.aliases:
                sources.setdefault(alias, record.entity_type)

        for source_text, entity_type in sorted(sources.items(), key=lambda item: len(item[0]), reverse=True):
            positions = self._find_all_positions(text, source_text)
            if not positions:
                continue
            context_window = self._context_window(text, positions)
            ranked = self.term_bank.rank_with_context(
                source_text,
                context_window=context_window,
                entity_type=entity_type if entity_type in PROPER_ENTITY_TYPES else None,
                active_universes=active_universes,
            )
            if not ranked:
                continue
            selected, selected_score = ranked[0]
            ambiguity = len(ranked) > 1 and abs(selected_score - ranked[1][1]) < 0.0001
            self._add_term_bank_suggestion(
                found,
                selected,
                positions,
                source=source_text,
                ambiguity=ambiguity,
                context_window=context_window,
            )

    def _add_term_bank_suggestion(
        self,
        found: dict[str, EntitySuggestion],
        record: TermBankRecord,
        positions: list[int],
        *,
        source: str | None = None,
        ambiguity: bool = False,
        context_window: str = "",
    ) -> None:
        source_text = source or record.source
        existing = found.get(source_text)
        if existing is not None:
            existing.count += len(positions)
            existing.positions.extend(positions)
            if ambiguity and "ambiguous_entity_resolution" not in existing.qa_flags:
                existing.ambiguity_flag = True
                existing.qa_flags.append("ambiguous_entity_resolution")
            return
        qa_flags = ["ambiguous_entity_resolution"] if ambiguity else []
        found[source_text] = EntitySuggestion(
            source=source_text,
            target=record.target,
            entity_type=record.entity_type,
            confidence=max(0.72, min(record.confidence, 0.99)),
            source_dict=record.source_dict,
            ambiguity_flag=ambiguity,
            count=len(positions),
            positions=list(positions),
            universe=record.universe,
            work=record.work,
            enrichment_ready=record.active,
            suggested_tags=list(record.tags),
            suggested_context_markers=[
                marker
                for marker in [*record.context_markers, *record.co_occurring_entities]
                if marker and marker in context_window
            ],
            qa_flags=qa_flags,
        )

    @staticmethod
    def _find_all_positions(text: str, source: str) -> list[int]:
        if not source:
            return []
        positions: list[int] = []
        start = 0
        while True:
            idx = text.find(source, start)
            if idx < 0:
                break
            positions.append(idx)
            start = idx + max(len(source), 1)
        return positions

    @staticmethod
    def _context_window(text: str, positions: list[int], *, radius: int = 200) -> str:
        windows: list[str] = []
        for position in positions[:5]:
            start = max(0, position - radius)
            end = min(len(text), position + radius)
            windows.append(text[start:end])
        return "\n".join(windows)

    @staticmethod
    def _drop_shadowed_term_bank_prefixes(found: dict[str, EntitySuggestion]) -> None:
        term_bank_items = [
            item for item in found.values()
            if "term_bank" in item.source_dict and item.entity_type in PROPER_ENTITY_TYPES
        ]
        if not term_bank_items:
            return
        for source, item in list(found.items()):
            if "term_bank" in item.source_dict:
                continue
            if item.entity_type not in PROPER_ENTITY_TYPES:
                continue
            for protected in term_bank_items:
                if len(protected.source) <= len(source) or not protected.source.startswith(source):
                    continue
                if set(item.positions).issubset(set(protected.positions)):
                    found.pop(source, None)
                    break

    def _fallback_location_mining(self, text: str, found: dict[str, EntitySuggestion]):
        LOCATION_MARKERS_BEFORE = {"在", "去", "回", "到", "离", "赴", "入", "出", "向", "从", "由", "往", "过", "经", "是", "和", "让", "与"}
        entity_suffixes = LOCATION_SUFFIXES | ORGANIZATION_SUFFIXES
        
        candidates: dict[str, dict[str, object]] = {}
        for idx in range(len(text)):
            if text[idx] not in entity_suffixes:
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
                title_tail = text[idx:idx + 3]
                if any(title_tail.startswith(title) for title in NAME_TITLE_FOLLOWERS):
                    continue
                    
                candidate = text[start_idx:idx + 1]
                if any(candidate.startswith(prefix) for prefix in LOCATION_BAD_PREFIXES):
                    continue
                if candidate[0] in LOCATION_INVALID_START_CHARS:
                    continue
                if any(ch in LOCATION_INVALID_INTERIOR_CHARS for ch in candidate):
                    continue
                if self._looks_like_bad_location_candidate(candidate):
                    continue
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
            entity_type = self._map_fallback_place_entity_type(source)
            source_dict = "heuristic_name_mining" if entity_type == "person" else "heuristic_location_mining"
            found[source] = EntitySuggestion(
                source=source,
                target=self.name_resolver.resolve_entity_target(
                    source,
                    entity_type=entity_type,
                    source_dict=source_dict,
                    current_target=source,
                ),
                entity_type=entity_type,
                confidence=0.72,
                source_dict=source_dict,
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

    @staticmethod
    def _looks_like_non_person_entity_shape(candidate: str) -> bool:
        if candidate.endswith(PERSON_TITLE_SUFFIXES):
            return True
        if candidate.endswith(PERSON_NON_NAME_SUFFIXES):
            return True
        if len(candidate) == 2 and candidate.endswith("\u56fd"):
            return True
        return False

    def _score_name_start(self, text: str, idx: int) -> int:
        if idx <= 0:
            return 1
        if text[max(0, idx - 2):idx] in NAME_INTRO_PREFIXES:
            return 2
        if text[idx - 1] in NAME_BOUNDARY_CHARS:
            return 1
        return 0

    def _score_name_end(self, text: str, next_idx: int) -> int:
        tail = text[next_idx:next_idx + 3]
        if any(tail.startswith(title) for title in NAME_TITLE_FOLLOWERS):
            return 2
        next_char = text[next_idx:next_idx + 1]
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

    @staticmethod
    def _looks_like_common_non_person_phrase(candidate: str) -> bool:
        if candidate in COMMON_NON_PERSON_NAME_TERMS:
            return True
        return any(candidate.endswith(suffix) for suffix in ("\u9053", "\u6c14", "\u754c", "\u6cd5", "\u529b"))

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

    @staticmethod
    def _map_fallback_place_entity_type(source: str) -> str:
        if source in FALLBACK_PERSON_ENTITY_SOURCES:
            return "person"
        return "organization" if source.endswith(tuple(ORGANIZATION_SUFFIXES)) else "location"

    @staticmethod
    def _looks_like_bad_location_candidate(candidate: str) -> bool:
        if candidate in FALLBACK_PERSON_ENTITY_SOURCES:
            return False
        if candidate in LOCATION_COMMON_PHRASES:
            return True
        if any(candidate.startswith(prefix) for prefix in LOCATION_BAD_PREFIXES):
            return True
        if len(candidate) >= 2 and candidate[0] in CHINESE_NUMERAL_CHARS and candidate[1] in LOCATION_CLASSIFIER_CHARS:
            return True
        return False

    def _looks_like_false_name_prefix(self, text: str, idx: int, start_score: int) -> bool:
        if start_score < 2 and text[idx] in DEMONSTRATIVE_NAME_PREFIX_CHARS:
            return True
        if idx <= 0:
            return False
        return text[idx - 1:idx + 1] in FALSE_NAME_START_BIGRAMS

    def _is_entity_candidate(self, source: str, category: str, priority: int) -> bool:
        if len(source) < 2:
            return False
        if source in DICTIONARY_NON_ENTITY_SOURCES:
            return False
        if self._looks_like_common_non_person_phrase(source):
            return False
        if "names" in category or priority >= 4:
            return True
        return category in {"cultivation", "realm", "items", "techniques"}

    def _map_entity_type(self, source: str, category: str) -> str:
        if source in DICTIONARY_ENTITY_TYPE_OVERRIDES:
            return DICTIONARY_ENTITY_TYPE_OVERRIDES[source]
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
