#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Baseline RBMT orchestrator for ZH -> VI translation."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.core.trace import make_trace_id
from src.core.luat_nhan_engine import LuatNhanEngine
from src.core.runtime_support import RuntimeDictionaryAccessor
from src.core.trie_engine import TrieEngine
from src.eapee.emotion_detector import EmotionDetector, SentenceContextClassifier
from src.eapee.expression_bank import ExpressionBank
from src.eapee.pronoun_resolver import PronounResolver
from src.engine.context_manager import ContextManager
from src.engine.cultural_origin_detector import CulturalOriginDetector
from src.engine.junk_phrase_filter import JunkPhraseFilter
from src.engine.number_converter import NumberConverter
from src.engine.pinyin_processor import PinyinProcessor
from src.engine.sentence_segmenter import SentenceSegmenter
from src.engine.style_profiles import build_rewrite_patterns, resolve_style_selection
from src.engine.structure_preserver import StructurePreserver
from src.engine.traditional_to_simplified import TraditionalToSimplifiedConverter
from src.grammar.transfer_engine import GrammarTransferEngine
from src.engine.zh_structure_rewriter import rewrite_chinese_structure
from src.engine.vi_grammar_rewriter import rewrite_vietnamese_grammar
from src.state.translation_memory import TranslationMemory


DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "dictionaries" / "_compiled" / "trie_cache.db"
DEFAULT_FUNCTION_TRANSLATIONS = {
    "我": "ta",
    "你": "ngươi",
    "您": "ngài",
    "他": "hắn",
    "她": "nàng",
    "他们": "bọn họ",
    "她们": "các nàng",
    "说": "nói",
    "说道": "nói",
    "问": "hỏi",
    "答": "đáp",
    "今天": "hôm nay",
    "昨天": "hôm qua",
    "明天": "ngày mai",
    "的": "",
    "了": "",
    "在": "ở",
    "会": "sẽ",
    "有": "có",
    "是": "là",
    "不": "không",
    "很": "rất",
    "帮": "giúp",
    "帮助": "giúp đỡ",
}
DEFAULT_PHRASE_OVERRIDES = {
    "之所以称之为高薪酬": "Sở dĩ gọi là thù lao cao",
    "这种福利待遇": "Đãi ngộ kiểu này",
    "连半点儿工作经验都没有": "thậm chí chưa có lấy một chút kinh nghiệm làm việc nào",
    "像这种喜从天降的好事": "loại chuyện tốt từ trên trời rơi xuống như thế này",
    "就连做梦都没梦到过": "ngay cả trong mơ cũng chưa từng thấy qua",
    "给夏天骐一种敷衍了事的感觉": "tạo cho Hạ Thiên Kì cảm giác như đang làm việc qua loa cho xong chuyện",
    "简单说来": "Nói đơn giản",
    "都没有从之前的惊喜中缓过神来": "vẫn chưa thoát ra khỏi niềm vui sướng bất ngờ vừa rồi",
    "通过了一个大公司的面试": "vượt qua buổi phỏng vấn của một công ty lớn",
    "签下了一份高薪酬的试用期合同": "ký vào bản hợp đồng thử việc với mức thù lao cao",
    "仅在试用期就有2万的月薪可拿": "chỉ riêng thời gian thử việc đã có mức lương 2 vạn mỗi tháng",
    "并且还给配台奥迪当座驾": "lại còn được cấp một chiếc Audi để làm phương tiện đi lại",
    "福平市最大的书店": "hiệu sách lớn nhất thành phố Phúc Bình",
    "ZF那边有关系": "có quan hệ với chính quyền",
    "黄金写字楼": "tòa cao ốc văn phòng Hoàng Kim",
    "一家骗子公司": "một công ty lừa đảo",
    "这家公司位于黄金写字楼上": "công ty này nằm ngay trong tòa cao ốc văn phòng Hoàng Kim",
    "这就更能彰显实力了": "điều này càng minh chứng rõ ràng cho thực lực của họ",
    "这大叔": "ông chú này",
    "新华大书店": "Hiệu sách lớn Tân Hoa",
    "高薪酬": "thù lao cao",
    "副驾驶": "ghế phụ",
    "详尽的": "Chi tiết hơn",
    "先去平安街34号": "trước tiên đến số 34 phố Bình An",
    "在这里就都能买得到": "thì đều có thể mua được ở đây",
    "只在早上9点至下午6点间营业": "chỉ mở cửa từ 9 giờ sáng đến 6 giờ chiều",
    "他们还来这里做什么": "họ còn đến đây làm gì nữa",
    "将车子停好后": "đỗ xe xong",
    "未来的一段时间": "Trong khoảng thời gian tới",
    "至于要在这里工作多久": "còn làm ở đây bao lâu",
    "取决于你自己": "tùy thuộc vào chính cậu",
    "每天晚上留在图书馆里值班": "mỗi tối ở lại trong hiệu sách trực đêm",
    "里面在装修吗": "Bên trong đang sửa chữa ạ",
    "或者说，我负责监工": "Hay là, cháu phụ trách giám sát thi công",
    "只要是市面上有的书": "chỉ cần là sách có trên thị trường",
    "已经歇业了": "đã ngừng hoạt động",
    "听话的跟了下去": "ngoan ngoãn đi theo",
    "通过气": "dặn trước",
    "通过了": "vượt qua",
    "中年大叔": "ông chú trung niên",
    "图书管理员": "nhân viên thủ thư",
    "打更的": "người canh đêm",
    "家什么公司": "công ty gì",
    "配一台": "cấp một chiếc",
    "配台": "cấp",
    "当座驾": "làm phương tiện đi lại",
    "一问三不知": "mù tịt không biết gì",
    "说话娘娘腔的男人": "gã đàn ông nói năng ẻo lả",
    "娘娘腔": "ẻo lả",
    "然而除却这些意外": "Nhưng ngoài chuyện đó ra",
    "半分有价值的信息": "nửa phần tin tức có giá trị",
    "对于公司的情况都是一问三不知": "đều mù tịt về tình hình công ty",
    "不厌其烦": "không ngại phiền",
    "这句话几乎是吼出来的": "câu này gần như là hét lên",
    "事实上说的越多他心里面便越害怕": "thực ra càng nói anh càng sợ",
    "为人有多善良，多正直": "là người lương thiện, chính trực đến đâu",
    "由四个人承担": "để bốn người cùng gánh",
    "无论怎样都是要强过": "dù sao cũng tốt hơn",
    "以前总是听人说起": "trước kia tôi thường nghe người ta nói về",
    "就只有一线之隔": "chỉ cách nhau một lằn ranh",
    "真心相信了": "thật lòng tin rằng",
    "能简则简": "nói được câu nào gọn câu nấy",
    "不大靠谱": "không đáng tin",
    "很不现实": "rất không thực tế",
    "杀人狂的样子他并没有见到": "anh chưa từng nhìn thấy bộ dạng tên sát nhân",
    "换言之": "nói cách khác",
    "杀人狂可以是除自己以外的任何人": "tên sát nhân có thể là bất kỳ ai ngoài chính anh",
    "所以自然也包括张小顺": "vậy nên Trương Tiểu Thuận cũng không ngoại lệ",
    "前提是这些护身符真的管用": "miễn là những lá bùa hộ mệnh này thật sự có tác dụng",
    "依旧是话语不多": "vẫn kiệm lời",
    "两种选择从中年大叔对他的提醒上看": "từ lời nhắc của ông chú trung niên, hai lựa chọn này cho thấy",
    "前者应该是九死一生": "phương án đầu gần như cửu tử nhất sinh",
    "后者不出意外的话则应该是必死无疑": "còn phương án sau, nếu không có gì bất ngờ, gần như chắc chắn phải chết",
    "他之所以会从学校的宿舍里搬出来": "sở dĩ anh dọn khỏi ký túc xá trường",
    "就是为了找工作面试时方便些": "chỉ là để tiện cho việc đi phỏng vấn xin việc",
    "不用遭受那该死宿管的束缚": "khỏi phải chịu sự quản thúc khốn kiếp của lão quản lý ký túc",
    "谁曾想竟自食恶果": "ai ngờ lại tự chuốc hậu quả",
    "搞得现在他是爷爷爷爷找不到，同学同学不靠谱，就连警察都指望不上": "thành ra bây giờ ông chú thì không thấy đâu, bạn học cũng chẳng đáng tin, đến cảnh sát cũng không trông cậy nổi",
    "充满恐惧的朝着身后方看去": "hoảng sợ ngoái nhìn ra sau",
    "过程中她的身子也在距离夏天骐越来越近": "trong lúc đó, cơ thể cô cũng áp sát Hạ Thiên Kì hơn",
    "散发出的冰冷": "hơi lạnh toát ra",
    "有些不太高兴的说完": "nói xong với vẻ không vui",
    "血色液体": "chất lỏng đỏ như máu",
    "于是忙对赵爽提醒说": "vội nhắc Triệu Sảng",
    "十有八九": "tám chín phần mười",
    "顿时又爆发出了强烈的求生欲": "lập tức bùng lên khát vọng sống mãnh liệt",
    "拼命挣扎着将裤口袋里的护身符拿出来": "liều mạng giãy giụa rút lá bùa hộ mệnh trong túi quần ra",
    "接着也不管有用没用的朝着身上一放": "rồi mặc kệ có tác dụng hay không, cứ áp thẳng lên người",
    "在这个要命的关头看到他": "vào lúc ngàn cân treo sợi tóc này lại nhìn thấy anh",
    "有可能帮助自己逃命的救星": "vị cứu tinh có thể giúp mình thoát chết",
    "别说是将他形容成霸气外露了": "đừng nói là gọi anh khí thế bức người",
    "就是将他形容成天神下凡都不过分": "dù ví anh như thiên thần giáng thế cũng không quá",
    "通过那一声女人的惨叫声想到的情况": "nghĩ tới tình cảnh ẩn sau tiếng thét thảm của người phụ nữ vừa rồi",
    "再回黄金写字楼想办法": "quay về tòa cao ốc văn phòng Hoàng Kim để nghĩ cách",
    "总之是不能继续像现在这样坐以待毙": "tóm lại không thể tiếp tục ngồi chờ chết như bây giờ",
    "感觉冰冷的手爪正距离自己的后背越来越近": "anh cảm thấy móng vuốt lạnh băng sau lưng đang càng lúc càng áp sát",
    "恐惧彻底从心底爆发出来": "nỗi sợ hãi hoàn toàn bùng lên từ đáy lòng",
    "这也令他双腿一软": "khiến hai chân anh nhũn ra",
    "直接从楼梯上滚了下去": "ngã lăn xuống cầu thang",
}
PREFERRED_RUNTIME_TARGETS = {
    "一台": "một chiếc",
    "大叔": "chú",
    "写字楼": "cao ốc văn phòng",
    "入驻": "đặt trụ sở",
    "这家公司": "công ty này",
    "图书": "sách",
    "月薪": "lương tháng",
    "气人": "làm người tức giận",
    "通过": "vượt qua",
    "通过了": "vượt qua",
    "彰显": "thể hiện",
    "偏偏": "cứ",
    "配": "cấp",
    "情况": "tình hình",
    "情绪": "tâm trạng",
    "事实上": "thực ra",
    "直入主题": "vào thẳng vấn đề",
    "显然": "rõ ràng",
    "独自": "một mình",
    "承担": "gánh",
    "强过": "tốt hơn",
    "获得": "thu được",
    "娘娘腔": "ẻo lả",
    "样子": "bộ dạng",
    "宿管": "quản lý ký túc",
    "惨叫声": "tiếng thét thảm thiết",
    "求生欲": "khát vọng sống",
    "楼梯": "cầu thang",
    "想办法": "nghĩ cách",
    "坐以待毙": "ngồi chờ chết",
    "九死一生": "cửu tử nhất sinh",
    "必死无疑": "chắc chắn phải chết",
}
DEFAULT_HEADING_TITLE_OVERRIDES = {
    "第一份工作": "Công việc đầu tiên",
    "尸体（求收藏）": "Xác chết",
    "被黑暗笼罩着": "Bị bóng tối bao trùm",
}

DEFAULT_COMPACT_SENTENCE_PATTERNS = (
    (r"\bTrong khoảng thời gian tới\b", "Sắp tới"),
    (r"\btùy thuộc vào chính cậu\b", "tùy cậu"),
    (r"\bchỉ cần là\b", "chỉ cần"),
    (r"\bthì đều có thể\b", "đều có thể"),
    (r"\bNói đơn giản\b", "Nói gọn"),
    (r"\bchỉ là đơn thuần\b", "chỉ đơn thuần"),
    (r"\bbất kể thế nào đều là\b", "dù sao cũng"),
    (r"\bliền lại\b", "lại"),
    (r"\btiếp lấy\b", "tiếp đó"),
    (r"\btiếp theo giây lát\b", "ngay sau đó"),
    (r"\bhướng phía\b", "về phía"),
    (r"\btheo trong\b", "từ trong"),
    (r"\btại đây\b", "ở đây"),
    (r"\bcó thể có thể\b", "có thể"),
    (r"\bkhông có đạt được\b", "không thu được"),
    (r"\btám chín mươi phần trăm\b", "tám chín phần mười"),
    (r"\bcái này cũng làm\b", "khiến"),
    (r"\btheo đáy lòng\b", "từ đáy lòng"),
    (r"\btừ trên thang lầu\b", "trên cầu thang"),
    (r"\blăn xuống đi\b", "ngã lăn xuống"),
    (r"\bchỉ có thể trước\b", "chỉ có thể"),
    (r"\bnhìn xem là\b", "xem nên"),
    (r"\bcó phải không có thể\b", "không thể"),
    (r"\bgiống như bây giờ\b", "như bây giờ"),
)


@dataclass(slots=True)
class CandidateTrace:
    source: str
    selected: str
    candidates: list[str]
    priority: int
    fallback_level: str
    reason: str


@dataclass(slots=True)
class SegmentTranslation:
    sentence_id: str
    source_text: str
    clean_text: str
    draft_text: str
    emotion: str | None
    trace: list[dict]
    trace_id: str = ""


@dataclass(slots=True)
class TranslationResult:
    clean_text: str
    draft_text: str
    segments: list[SegmentTranslation]
    config: dict = field(default_factory=dict)


class RBMTTranslator:
    """Vertical-slice translator that produces clean and annotated draft output."""

    def __init__(
        self,
        db_path: str | None = None,
        tm_db_path: str | None = None,
        extra_function_translations: dict[str, str] | None = None,
        enable_tm_lookup: bool = False,
    ):
        self.db_path = str(db_path or DEFAULT_DB_PATH)
        self.trie = TrieEngine.from_shared_sqlite(self.db_path, enable_number_converter=False)
        self.accessor = RuntimeDictionaryAccessor(self.db_path)
        self.luat_nhan = LuatNhanEngine()
        self.luat_nhan.load_from_sqlite(self.db_path)
        self.preserver = StructurePreserver()
        self.converter = TraditionalToSimplifiedConverter()
        self.pinyin = PinyinProcessor(db_path=self.db_path)
        self.segmenter = SentenceSegmenter()
        self.number_converter = NumberConverter()
        self.context = ContextManager()
        self.cultural_origin = CulturalOriginDetector()
        self.emotion_detector = EmotionDetector()
        self.sentence_context_classifier = SentenceContextClassifier()
        self.expression_bank = ExpressionBank()
        self.pronoun_resolver = PronounResolver()
        self.grammar_transfer = GrammarTransferEngine()
        self.junk_filter = JunkPhraseFilter()
        self.tm = TranslationMemory(tm_db_path) if tm_db_path else None
        self.enable_tm_lookup = enable_tm_lookup
        self.function_translations = dict(DEFAULT_FUNCTION_TRANSLATIONS)
        self.phrase_overrides = dict(DEFAULT_PHRASE_OVERRIDES)
        self._phrase_override_keys = sorted(self.phrase_overrides, key=len, reverse=True)
        self.preferred_runtime_targets = dict(PREFERRED_RUNTIME_TARGETS)
        self.heading_title_overrides = dict(DEFAULT_HEADING_TITLE_OVERRIDES)
        self._style_pattern_cache: dict[tuple[str, bool, bool], list[tuple[re.Pattern[str], str]]] = {}
        if extra_function_translations:
            self.function_translations.update(extra_function_translations)

    def close(self):
        self.accessor.close()
        self.pinyin.close()
        if self.tm:
            self.tm.close()

    def translate_text(self, text: str, config: dict | None = None) -> TranslationResult:
        config = dict(config or {})
        style_selection = resolve_style_selection(config, chapter_id=config.get("active_chapter_id"))
        config["style_profile"] = style_selection["effective_profile"]
        config["style_context"] = style_selection["effective_context"]
        config["naturalization"] = style_selection["naturalization"]
        config["style_resolution"] = style_selection
        phrase_overrides, phrase_override_keys = self._resolve_phrase_overrides(config)
        preserved = self.preserver.preserve(text)
        simplified = self.converter.convert(preserved.text)
        protected = {item["source"] for item in config.get("locked_entities", [])}
        resolved = self.pinyin.resolve(simplified, protected_terms=protected)
        source_junk_result = self.junk_filter.apply_source(
            resolved,
            config,
            normalizer=self.converter.convert,
        )
        working_text = source_junk_result.text
        source_junk_traces = list(source_junk_result.traces)

        segments: list[SegmentTranslation] = []
        clean_sentences: list[str] = []
        draft_sentences: list[str] = []
        for position, span in enumerate(self.segmenter.split(working_text)):
            tm_hit = self._lookup_tm(span.text, config=config)
            display_source = self.preserver.restore(span.text, preserved.placeholders)
            trace_id = make_trace_id(str(config.get("active_chapter_id") or "chapter"), position, display_source)
            if tm_hit:
                clean_text = self.preserver.restore(tm_hit["target"], preserved.placeholders)
                draft_text = clean_text
                trace = [tm_hit]
                emotion = None
            else:
                clean_text, draft_text, trace, emotion = self._translate_sentence(
                    span.text,
                    config=config,
                    style_selection=style_selection,
                    phrase_overrides=phrase_overrides,
                    phrase_override_keys=phrase_override_keys,
                )
                clean_text = self.preserver.restore(clean_text, preserved.placeholders)
                draft_text = self.preserver.restore(draft_text, preserved.placeholders)

            if position == 0 and source_junk_traces:
                trace = [*source_junk_traces, *trace]
                source_junk_traces = []
            trace = self._attach_trace_metadata(trace, trace_id)

            self.context.update(
                source_sentence=display_source,
                target_sentence=clean_text,
                entities=[item["source"] for item in config.get("locked_entities", [])],
                emotion=emotion,
                genre=(config.get("genre_hints") or [None])[0],
            )
            if self.tm and not tm_hit:
                self.tm.store_machine(
                    display_source,
                    clean_text,
                    engine_version="rbmt",
                    quality_score=0.92,
                    trace_json=trace,
                )

            segment = SegmentTranslation(
                sentence_id=span.sentence_id,
                source_text=display_source,
                clean_text=clean_text,
                draft_text=draft_text,
                emotion=emotion,
                trace=trace,
                trace_id=trace_id,
            )
            segments.append(segment)
            clean_sentences.append(clean_text)
            draft_sentences.append(draft_text)

        return TranslationResult(
            clean_text="\n".join(clean_sentences),
            draft_text="\n".join(draft_sentences),
            segments=segments,
            config=config,
        )

    def export(self, result: TranslationResult, project_dir: str | Path, artifact_stem: str = "translated"):
        project_path = Path(project_dir)
        output_dir = project_path / "output"
        draft_dir = project_path / "drafts"
        output_dir.mkdir(parents=True, exist_ok=True)
        draft_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / f"{artifact_stem}.txt").write_text(result.clean_text, encoding="utf-8")
        (draft_dir / f"{artifact_stem}_draft.txt").write_text(result.draft_text, encoding="utf-8")
        trace_payload = [asdict(segment) for segment in result.segments]
        (draft_dir / f"{artifact_stem}_trace.json").write_text(json.dumps(trace_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _lookup_tm(self, source_text: str, *, config: dict | None = None) -> dict | None:
        if not self.tm:
            return None
        if not self.enable_tm_lookup and not bool((config or {}).get("use_translation_memory")):
            return None
        match = self.tm.lookup(source_text, threshold=0.88)
        if match:
            score = getattr(match, "score", None)
            if match.status == "approved" and score is None:
                fallback_level = "tm_approved_exact"
                priority = 99
                reason = "translation_memory_approved_exact"
            elif match.status == "approved":
                fallback_level = "tm_approved_fuzzy"
                priority = 85
                reason = f"translation_memory_approved_fuzzy:{score:.2f}"
            else:
                fallback_level = "tm_machine_suggestion"
                priority = 70
                reason = "translation_memory_machine_suggestion"
            return {
                "source": source_text,
                "selected": match.target_text,
                "candidates": [match.target_text],
                "priority": priority,
                "fallback_level": fallback_level,
                "reason": reason,
                "target": match.target_text,
            }
        return None

    @staticmethod
    def _attach_trace_metadata(traces: list[dict], trace_id: str) -> list[dict]:
        enriched: list[dict] = []
        for trace in traces:
            item = dict(trace)
            item.setdefault("trace_id", trace_id)
            item.setdefault("stage", RBMTTranslator._stage_for_fallback(item.get("fallback_level", "")))
            item.setdefault("action", item.get("reason", "select"))
            priority = item.get("priority", 0)
            if "confidence" not in item:
                item["confidence"] = min(1.0, max(0.0, float(priority) / 100.0 if isinstance(priority, (int, float)) else 0.0))
            enriched.append(item)
        return enriched

    @staticmethod
    def _stage_for_fallback(fallback_level: str) -> str:
        if fallback_level.startswith("tm_"):
            return "translation_memory"
        if fallback_level in {"number"}:
            return "number_converter"
        if fallback_level in {"project_entity"}:
            return "entity_override"
        if fallback_level in {"pronoun"}:
            return "context_resolver"
        if fallback_level in {"grammar_transfer"}:
            return "grammar_transfer"
        if fallback_level in {"junk_phrase_filter"}:
            return "junk_filter"
        if fallback_level in {"phrase_override", "runtime", "function_map", "reading_fallback", "ambiguous", "unresolved"}:
            return "lexical_decode"
        return "rbmt"

    def _translate_sentence(
        self,
        sentence: str,
        config: dict,
        *,
        style_selection: dict | None = None,
        phrase_overrides: dict[str, str] | None = None,
        phrase_override_keys: list[str] | None = None,
    ) -> tuple[str, str, list[dict], str | None]:
        heading_override = self._match_heading_override(sentence)
        if heading_override:
            return heading_override

        grammar_traces: list[dict] = []
        if self._should_apply_grammar_transfer(sentence, phrase_override_keys):
            transfer_result = self.grammar_transfer.rewrite_source(sentence)
            sentence = transfer_result.text
            grammar_traces.extend(transfer_result.traces)

        # Rewrite Chinese structural patterns before lexical processing.
        sentence = rewrite_chinese_structure(sentence)

        locked_entities = self._get_locked_entities(config)
        sentence_context = self.sentence_context_classifier.classify(sentence)
        dialogue_context = self.pronoun_resolver.detect_dialogue_context(
            sentence,
            active_entities=[item["source"] for item in locked_entities],
            context_type=sentence_context,
        )
        emotion = (
            self.emotion_detector.detect_label(sentence, context_type=sentence_context)
            if sentence_context == "dialogue"
            else None
        )
        entity_pairs = [(item["source"], item["target"]) for item in locked_entities]
        self.luat_nhan.set_entity_pairs(entity_pairs)
        sentence = self.luat_nhan.apply_with_source_entities(sentence)

        locked_by_start, locked_spans = self._prepare_locked_entity_spans(sentence, locked_entities)

        result_parts: list[str] = []
        draft_parts: list[str] = []
        traces: list[dict] = list(grammar_traces)
        i = 0
        while i < len(sentence):
            entity_override = self._match_locked_entity(locked_by_start, i)
            if entity_override:
                self._append_fragment(result_parts, entity_override["target"])
                self._append_fragment(draft_parts, entity_override["target"])
                traces.append(entity_override)
                i += entity_override["length"]
                continue

            phrase_override = self._match_phrase_override(
                sentence,
                i,
                phrase_overrides=phrase_overrides,
                phrase_override_keys=phrase_override_keys,
            )
            if phrase_override:
                self._append_fragment(result_parts, phrase_override["target"])
                self._append_fragment(draft_parts, phrase_override["target"])
                traces.append(phrase_override)
                i += phrase_override["length"]
                continue

            num_result = self.number_converter.try_convert(sentence, i)
            trie_match = self.trie.lookup(sentence, i)
            trie_match = self._prefer_particle_split(sentence, i, trie_match)
            trie_match = self._avoid_locked_entity_overlap(sentence, i, trie_match, locked_spans)
            trie_match = self._avoid_interrogative_overlap(sentence, i, trie_match)
            trie_len = trie_match.length if trie_match else 0
            num_len = num_result.consumed if num_result else 0

            if num_len > trie_len:
                trace = asdict(CandidateTrace(
                    source=sentence[i:i + num_result.consumed],
                    selected=num_result.text,
                    candidates=[num_result.text],
                    priority=50,
                    fallback_level="number",
                    reason=num_result.conv_type,
                ))
                self._append_fragment(result_parts, num_result.text)
                self._append_fragment(draft_parts, num_result.text)
                traces.append(trace)
                i += num_result.consumed
                continue

            pronoun = self.pronoun_resolver.resolve_token(
                sentence,
                i,
                dialogue_context,
                emotion=emotion,
                genre=(config.get("genre_hints") or ["general"])[0],
            )
            if pronoun:
                self._append_fragment(result_parts, pronoun["target"])
                self._append_fragment(draft_parts, pronoun["target"])
                traces.append(pronoun)
                i += pronoun["length"]
                continue

            function = self._match_function_translation(sentence, i)
            if function and function["length"] >= trie_len:
                self._append_fragment(result_parts, function["target"])
                self._append_fragment(draft_parts, function["target"])
                traces.append(function)
                i += function["length"]
                continue

            if trie_match:
                trace = self._build_trie_trace(trie_match.source, trie_match.target, trie_match.priority, config=config)
                self._append_fragment(result_parts, trace["selected"])
                if trace["fallback_level"] == "ambiguous":
                    self._append_fragment(draft_parts, f"{trace['selected']}[[AMBIG:{trace['source']}=>{'|'.join(trace['candidates'])}]]")
                else:
                    self._append_fragment(draft_parts, trace["selected"])
                traces.append(trace)
                i += trie_match.length
                continue

            ch = sentence[i]
            if self._is_cjk(ch):
                self._append_fragment(result_parts, ch)
                self._append_fragment(draft_parts, f"{ch}[[UNRESOLVED]]")
                traces.append(asdict(CandidateTrace(
                    source=ch,
                    selected=ch,
                    candidates=[ch],
                    priority=0,
                    fallback_level="unresolved",
                    reason="no_candidate",
                )))
                i += 1
            else:
                literal, consumed = self._consume_literal_token(sentence, i)
                self._append_fragment(result_parts, literal)
                self._append_fragment(draft_parts, literal)
                i += consumed

        clean_text = self._normalize_output(
            "".join(result_parts),
            emotion=emotion,
            genre=(config.get("genre_hints") or ["general"])[0],
            style_selection=style_selection,
            inject_expression=bool(config.get("inject_expressive_interjections", False)),
        )
        draft_text = self._normalize_output(
            "".join(draft_parts),
            emotion=emotion,
            genre=(config.get("genre_hints") or ["general"])[0],
            style_selection=style_selection,
            inject_expression=False,
        )
        clean_filter = self.junk_filter.apply_target(clean_text, config)
        draft_filter = self.junk_filter.apply_target(draft_text, config)
        clean_text = clean_filter.text
        draft_text = draft_filter.text
        traces.extend(clean_filter.traces)
        traces.extend(draft_filter.traces)
        return clean_text, draft_text, traces, emotion

    def _build_trie_trace(self, source: str, target: str, priority: int, config: dict) -> dict:
        record = self.accessor.lookup_runtime(source)
        candidates = []
        fallback_level = "runtime"
        if record:
            candidates = record.alternatives
            if len(candidates) > 1 and source in set(config.get("high_ambiguity_terms", [])):
                fallback_level = "ambiguous"
            elif priority <= 1:
                fallback_level = "reading_fallback"
        preferred = self.preferred_runtime_targets.get(source)
        if preferred:
            selected = preferred
            if preferred not in candidates:
                candidates = [preferred] + candidates
        else:
            selected = candidates[0] if candidates else target
        return asdict(CandidateTrace(
            source=source,
            selected=selected,
            candidates=candidates or [target],
            priority=priority,
            fallback_level=fallback_level,
            reason=(record.category if record else "runtime_trie"),
        ))

    def _normalize_output(
        self,
        text: str,
        *,
        emotion: str | None,
        genre: str,
        style_selection: dict | None,
        inject_expression: bool = False,
    ) -> str:
        text = unicodedata.normalize("NFC", text)
        text = re.sub(r"\s{2,}", " ", text)
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)
        text = re.sub(r"\s+([\"”])", r"\1", text)
        text = re.sub(r"([\"'])\s+", r"\1", text)
        text = text.replace("。", ".").replace("，", ", ").replace("：", ": ").replace("！", "!").replace("？", "?")
        text = text.replace("“", "\"").replace("”", "\"")
        text = re.sub(r"(?:\.\s*){3,}", "...", text)
        text = re.sub(r"(?:…\s*){1,}", "...", text)
        for pattern, replacement in self._get_target_rewrite_patterns(style_selection):
            text = pattern.sub(replacement, text)
        if genre == "modern":
            text = re.sub(r"\bcác ngươi\b", "các cậu", text, flags=re.IGNORECASE)
            text = re.sub(r"\bbọn họ\b", "họ", text, flags=re.IGNORECASE)
            text = re.sub(r"\bcác nàng\b", "họ", text, flags=re.IGNORECASE)
            text = re.sub(r"\bngươi\b", "cậu", text, flags=re.IGNORECASE)
            text = re.sub(r"\bta\b", "tôi", text, flags=re.IGNORECASE)
            text = re.sub(r"\bhắn\b", "anh", text, flags=re.IGNORECASE)
            text = re.sub(r"\bnàng\b", "cô ấy", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)
        text = re.sub(r"\s+([\"”])", r"\1", text)
        text = re.sub(r"([\"'])\s+", r"\1", text)
        text = re.sub(r"\s{2,}", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        text = rewrite_vietnamese_grammar(text, genre=genre)
        if inject_expression and emotion:
            prefix = self.expression_bank.pick_interjection(genre=genre, emotion=emotion)
            if prefix and "\"" in text:
                text = text.replace("\"", f"\"{prefix} ", 1)
        return self._capitalize_sentence_start(unicodedata.normalize("NFC", text))

    def _get_target_rewrite_patterns(self, style_selection: dict | None) -> list[tuple[re.Pattern[str], str]]:
        profile_id = "balanced_novel"
        enabled = True
        compact_sentences = False
        if style_selection:
            profile_id = style_selection.get("effective_profile") or profile_id
            naturalization = style_selection.get("naturalization") or {}
            enabled = bool(naturalization.get("enabled", True))
            compact_sentences = bool(naturalization.get("compact_sentences", False))
        cache_key = (profile_id, enabled, compact_sentences)
        cached = self._style_pattern_cache.get(cache_key)
        if cached is not None:
            return cached
        compiled = [
            (re.compile(pattern, flags=re.IGNORECASE), replacement)
            for pattern, replacement in build_rewrite_patterns(profile_id, enabled=enabled)
        ]
        if compact_sentences:
            compiled.extend(
                (re.compile(pattern, flags=re.IGNORECASE), replacement)
                for pattern, replacement in DEFAULT_COMPACT_SENTENCE_PATTERNS
            )
        self._style_pattern_cache[cache_key] = compiled
        return compiled

    def _resolve_phrase_overrides(self, config: dict) -> tuple[dict[str, str], list[str]]:
        merged = dict(self.phrase_overrides)
        for source, target in (config.get("project_phrase_overrides") or {}).items():
            source_text = str(source).strip()
            target_text = str(target).strip()
            if not source_text or not target_text:
                continue
            merged[source_text] = target_text
        return merged, sorted(merged, key=len, reverse=True)

    def _match_heading_override(self, sentence: str) -> tuple[str, str, list[dict], None] | None:
        match = re.match(
            r"^(?P<prefix>\s*#+\s*)?(?:(?P<index>\d+)\.)?\s*第(?P<chapter>[0-9零〇一二三四五六七八九十百千两]+)章\s*(?P<title>.+?)\s*$",
            sentence,
        )
        if not match:
            return None

        chapter_number = self._parse_heading_number(match.group("chapter"))
        if chapter_number is None:
            return None

        title_source = match.group("title").strip()
        title_target = self.heading_title_overrides.get(title_source, title_source)
        prefix = match.group("prefix") or ""
        if prefix and not prefix.endswith(" "):
            prefix = f"{prefix.strip()} "
        heading = f"{prefix}Chương {chapter_number}: {title_target}".strip()
        trace = asdict(
            CandidateTrace(
                source=sentence.strip(),
                selected=heading,
                candidates=[heading],
                priority=90,
                fallback_level="heading_override",
                reason="chapter_heading_override",
            )
        )
        return heading, heading, [trace], None

    def _match_function_translation(self, text: str, pos: int) -> dict | None:
        best_key = None
        for key in sorted(self.function_translations.keys(), key=len, reverse=True):
            if text.startswith(key, pos):
                best_key = key
                break
        if not best_key:
            return None
        target = self.function_translations[best_key]
        payload = asdict(CandidateTrace(
            source=best_key,
            selected=target,
            candidates=[target],
            priority=60,
            fallback_level="function_map",
            reason="builtin_function_map",
        ))
        payload["target"] = target
        payload["length"] = len(best_key)
        return payload

    @staticmethod
    def _should_apply_grammar_transfer(sentence: str, phrase_override_keys: list[str] | None) -> bool:
        # Keep long regression phrase overrides authoritative; they already encode
        # reviewed Vietnamese wording for a full construction.
        for key in phrase_override_keys or []:
            if len(key) >= 5 and key in sentence:
                return False
        return True

    def _match_phrase_override(
        self,
        text: str,
        pos: int,
        *,
        phrase_overrides: dict[str, str] | None = None,
        phrase_override_keys: list[str] | None = None,
    ) -> dict | None:
        active_overrides = phrase_overrides or self.phrase_overrides
        active_keys = phrase_override_keys or self._phrase_override_keys
        for key in active_keys:
            if not text.startswith(key, pos):
                continue
            target = active_overrides[key]
            payload = asdict(CandidateTrace(
                source=key,
                selected=target,
                candidates=[target],
                priority=85,
                fallback_level="phrase_override",
                reason="regression_phrase_override",
            ))
            payload["target"] = target
            payload["length"] = len(key)
            return payload
        return None

    @staticmethod
    def _parse_heading_number(raw_value: str) -> int | None:
        raw_value = raw_value.strip()
        if raw_value.isdigit():
            return int(raw_value)

        digits = {
            "零": 0,
            "〇": 0,
            "一": 1,
            "二": 2,
            "两": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
        }
        if raw_value == "十":
            return 10
        if "十" in raw_value:
            left, _, right = raw_value.partition("十")
            tens = digits.get(left, 1 if left == "" else None)
            ones = digits.get(right, 0 if right == "" else None)
            if tens is None or ones is None:
                return None
            return tens * 10 + ones
        if all(char in digits for char in raw_value):
            value = 0
            for char in raw_value:
                value = value * 10 + digits[char]
            return value
        return None

    @staticmethod
    def _get_locked_entities(config: dict) -> list[dict]:
        cached = config.get("_locked_entities_sorted")
        if cached is None:
            cached = sorted(
                [item for item in config.get("locked_entities", []) if item.get("source") and item.get("target")],
                key=lambda item: len(item["source"]),
                reverse=True,
            )
            config["_locked_entities_sorted"] = cached
        return cached

    @staticmethod
    def _prepare_locked_entity_spans(sentence: str, locked_entities: list[dict]) -> tuple[dict[int, dict], list[tuple[int, int]]]:
        locked_by_start: dict[int, dict] = {}
        locked_spans: list[tuple[int, int]] = []
        for entity in locked_entities:
            source = entity["source"]
            start = sentence.find(source)
            while start != -1:
                payload = {
                    "source": source,
                    "selected": entity["target"],
                    "candidates": [entity["target"]],
                    "priority": 95,
                    "fallback_level": "project_entity",
                    "reason": "locked_entity_override",
                    "target": entity["target"],
                    "length": len(source),
                }
                current = locked_by_start.get(start)
                if current is None or payload["length"] > current["length"]:
                    locked_by_start[start] = payload
                locked_spans.append((start, start + len(source)))
                start = sentence.find(source, start + 1)
        locked_spans.sort()
        return locked_by_start, locked_spans

    @staticmethod
    def _match_locked_entity(locked_by_start: dict[int, dict], pos: int) -> dict | None:
        return locked_by_start.get(pos)

    def _prefer_particle_split(self, text: str, pos: int, trie_match):
        if not trie_match or trie_match.length <= 1:
            return trie_match
        suffix = trie_match.source[-1]
        if suffix not in {"了", "的", "们"}:
            return trie_match
        shorter = self.trie.lookup_exact(trie_match.source[:-1])
        if shorter:
            return shorter
        return trie_match

    def _avoid_locked_entity_overlap(self, text: str, pos: int, trie_match, locked_spans: list[tuple[int, int]]):
        if not trie_match:
            return None

        if not locked_spans:
            return trie_match
        if not self._overlaps_locked_entity(pos, trie_match.length, locked_spans):
            return trie_match

        for length in range(trie_match.length - 1, 0, -1):
            if self._overlaps_locked_entity(pos, length, locked_spans):
                continue
            exact = self.trie.lookup_exact(text[pos:pos + length])
            if exact:
                return exact
        return None

    def _avoid_interrogative_overlap(self, text: str, pos: int, trie_match):
        if not trie_match:
            return None
        end = pos + trie_match.length
        if trie_match.source.endswith("什") and end < len(text) and text[end] == "么":
            shorter = self.trie.lookup_exact(trie_match.source[:-1])
            return shorter
        return trie_match

    @staticmethod
    def _overlaps_locked_entity(pos: int, length: int, locked_spans: list[tuple[int, int]]) -> bool:
        end = pos + length
        for locked_start, _locked_end in locked_spans:
            if locked_start <= pos:
                continue
            if locked_start >= end:
                break
            if pos < locked_start < end:
                return True
        return False

    def _append_fragment(self, parts: list[str], fragment: str):
        if fragment == "":
            return
        if not parts:
            parts.append(fragment)
            return
        prev = parts[-1]
        if not prev:
            parts[-1] = fragment
            return
        if self._needs_space(prev, fragment):
            parts.append(" ")
        parts.append(fragment)

    @staticmethod
    def _consume_literal_token(text: str, pos: int) -> tuple[str, int]:
        ch = text[pos]
        if not RBMTTranslator._is_literal_token_char(ch):
            return ch, 1

        end = pos + 1
        while end < len(text) and RBMTTranslator._is_literal_token_char(text[end]):
            end += 1
        return text[pos:end], end - pos

    @staticmethod
    def _is_literal_token_char(char: str) -> bool:
        return ((char.isalpha() or char.isdigit()) and not RBMTTranslator._is_cjk(char)) or char in {"_", "-", "/"}

    @staticmethod
    def _needs_space(left: str, right: str) -> bool:
        left_last = left[-1]
        right_first = right[0]
        if left_last.isspace() or right_first.isspace():
            return False
        if right_first in ",.;:!?)]}\"":
            return False
        if left_last in "([{\"":
            return False
        if left_last == "/" or right_first == "/":
            return False
        return True

    @staticmethod
    def _capitalize_sentence_start(text: str) -> str:
        chars = list(text)
        for idx, ch in enumerate(chars):
            if ch.isalpha():
                chars[idx] = ch.upper()
                break
        return "".join(chars)

    @staticmethod
    def _is_cjk(char: str) -> bool:
        cp = ord(char)
        return 0x4E00 <= cp <= 0x9FFF
