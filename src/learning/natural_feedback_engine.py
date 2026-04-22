#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert natural-language feedback into reviewable translation rule suggestions."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.engine.style_profiles import STYLE_PROFILES


STYLE_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("source_faithful", ("bám sát nguồn", "sat nguon", "trung thành nguồn", "dịch sát", "literal")),
    ("dialogue_natural", ("hội thoại", "đối thoại", "xưng hô", "thoại tự nhiên", "khẩu ngữ")),
    ("modern_narrative", ("tự sự", "trần thuật", "lời kể", "narration")),
    ("suspense_horror", ("kinh dị", "rùng rợn", "u ám", "ngột ngạt", "căng thẳng", "horror", "suspense")),
    ("han_viet_balanced", ("hán việt", "co phong", "cổ phong", "tiên hiệp", "kiếm hiệp", "xianxia")),
    ("modern_novel_adaptive", ("tự nhiên hơn", "muot hon", "dịch thoáng", "tiểu thuyết", "van viet", "mượt hơn")),
)

GENRE_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("modern", ("hiện đại", "modern", "đô thị")),
    ("xianxia", ("tiên hiệp", "tu tiên", "xianxia", "cổ phong")),
    ("historical", ("cổ đại", "lịch sử", "historical")),
    ("horror", ("kinh dị", "horror", "rùng rợn")),
    ("suspense", ("căng thẳng", "suspense", "ngột ngạt")),
    ("light_novel", ("light novel", "trẻ", "nhẹ nhàng", "tuổi teen")),
)

COMPACT_HINTS = ("rút gọn", "ngắn gọn", "gọn hơn", "đỡ dài", "bớt dài", "ít dài dòng")
PROPER_NOUN_HINTS = ("tên", "nhân vật", "địa danh", "tổ chức", "company", "name", "entity")


@dataclass(slots=True)
class FeedbackSuggestion:
    rule_type: str
    title: str
    summary: str
    payload: dict[str, Any]
    confidence: float
    scope: str
    chapter_id: str | None
    origin: str = "heuristic"

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_type": self.rule_type,
            "title": self.title,
            "summary": self.summary,
            "payload": self.payload,
            "confidence": round(float(self.confidence), 3),
            "scope": self.scope,
            "chapter_id": self.chapter_id,
            "origin": self.origin,
        }


class NaturalFeedbackEngine:
    """Analyze reviewer feedback and emit structured rule candidates."""

    def analyze(
        self,
        *,
        feedback_text: str,
        source_text: str = "",
        current_translation: str = "",
        preferred_translation: str = "",
        chapter_id: str | None = None,
        scope: str = "project",
        rule_type_hint: str = "auto",
        llm: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_feedback = str(feedback_text or "").strip()
        if not normalized_feedback:
            raise ValueError("feedback_text is required")

        warnings: list[str] = []
        suggestions: list[FeedbackSuggestion] = []

        llm_suggestions = self._analyze_with_llm(
            feedback_text=normalized_feedback,
            source_text=source_text,
            current_translation=current_translation,
            preferred_translation=preferred_translation,
            chapter_id=chapter_id,
            scope=scope,
            rule_type_hint=rule_type_hint,
            llm=llm or {},
            warnings=warnings,
        )
        if llm_suggestions:
            suggestions.extend(llm_suggestions)
        else:
            suggestions.extend(
                self._analyze_heuristically(
                    feedback_text=normalized_feedback,
                    source_text=source_text,
                    current_translation=current_translation,
                    preferred_translation=preferred_translation,
                    chapter_id=chapter_id,
                    scope=scope,
                    rule_type_hint=rule_type_hint,
                )
            )

        if not suggestions:
            suggestions.append(
                FeedbackSuggestion(
                    rule_type="style_guidance",
                    title="Lưu ghi chú biên tập",
                    summary="Không suy ra được rule chắc chắn; lưu feedback để tham khảo ở vòng duyệt sau.",
                    payload={
                        "guidance": normalized_feedback,
                        "source_text": source_text.strip(),
                        "current_translation": current_translation.strip(),
                        "preferred_translation": preferred_translation.strip(),
                    },
                    confidence=0.45,
                    scope=scope,
                    chapter_id=chapter_id,
                )
            )

        deduped = self._dedupe_suggestions(suggestions)
        return {
            "feedback_text": normalized_feedback,
            "scope": scope,
            "chapter_id": chapter_id,
            "rule_type_hint": rule_type_hint,
            "llm_used": bool(llm_suggestions),
            "warnings": warnings,
            "suggestions": [item.to_dict() for item in deduped],
        }

    def _analyze_heuristically(
        self,
        *,
        feedback_text: str,
        source_text: str,
        current_translation: str,
        preferred_translation: str,
        chapter_id: str | None,
        scope: str,
        rule_type_hint: str,
    ) -> list[FeedbackSuggestion]:
        lowered = self._normalize_text(feedback_text)
        source = str(source_text or "").strip()
        current = str(current_translation or "").strip()
        preferred = str(preferred_translation or "").strip()
        suggestions: list[FeedbackSuggestion] = []

        direct_rewrite = self._extract_direct_rewrite(feedback_text)
        if direct_rewrite and rule_type_hint in {"auto", "phrase", "term", "entity"}:
            source_candidate, target_candidate = direct_rewrite
            rule_type = "locked_entity" if self._looks_like_locked_entity(source_candidate, target_candidate, lowered) else "phrase_override"
            suggestions.append(
                self._make_term_suggestion(
                    rule_type=rule_type,
                    source_text=source_candidate,
                    target_text=target_candidate,
                    chapter_id=chapter_id,
                    scope=scope,
                    confidence=0.92,
                )
            )

        if source and preferred and rule_type_hint in {"auto", "phrase", "term", "entity"}:
            if self._is_phrase_scope(source, preferred):
                rule_type = "locked_entity" if self._looks_like_locked_entity(source, preferred, lowered) else "phrase_override"
                suggestions.append(
                    self._make_term_suggestion(
                        rule_type=rule_type,
                        source_text=source,
                        target_text=preferred,
                        chapter_id=chapter_id,
                        scope=scope,
                        confidence=0.88 if current and current != preferred else 0.82,
                    )
                )

        style_profile = self._detect_style_profile(lowered)
        if style_profile and rule_type_hint in {"auto", "style"}:
            suggestions.append(
                FeedbackSuggestion(
                    rule_type="style_profile",
                    title=f"Đổi profile sang {style_profile}",
                    summary=f"Feedback cho thấy chương/project này hợp hơn với profile `{style_profile}`.",
                    payload={"style_profile": style_profile},
                    confidence=0.76,
                    scope=scope,
                    chapter_id=chapter_id,
                )
            )

        naturalization = self._detect_naturalization(lowered)
        if naturalization and rule_type_hint in {"auto", "style", "naturalization"}:
            suggestions.append(
                FeedbackSuggestion(
                    rule_type="naturalization",
                    title="Tinh chỉnh naturalization",
                    summary="Feedback gợi ý chỉnh mức naturalization để câu dịch gọn và tự nhiên hơn.",
                    payload={"naturalization": naturalization},
                    confidence=0.71,
                    scope=scope,
                    chapter_id=chapter_id,
                )
            )

        style_context = self._detect_style_context(lowered)
        if style_context and rule_type_hint in {"auto", "style"}:
            suggestions.append(
                FeedbackSuggestion(
                    rule_type="style_context",
                    title="Bổ sung ngữ cảnh phong cách",
                    summary="Lưu thêm genre/tone để pipeline chọn profile và naturalization phù hợp hơn.",
                    payload={"style_context": style_context},
                    confidence=0.67,
                    scope=scope,
                    chapter_id=chapter_id,
                )
            )

        if feedback_text and (not suggestions or rule_type_hint in {"auto", "style"}):
            suggestions.append(
                FeedbackSuggestion(
                    rule_type="style_guidance",
                    title="Lưu ghi chú biên tập",
                    summary="Giữ feedback gốc để UI và các vòng học sau có thể tham chiếu lại.",
                    payload={
                        "guidance": feedback_text.strip(),
                        "source_text": source,
                        "current_translation": current,
                        "preferred_translation": preferred,
                    },
                    confidence=0.55,
                    scope=scope,
                    chapter_id=chapter_id,
                )
            )

        return suggestions

    def _analyze_with_llm(
        self,
        *,
        feedback_text: str,
        source_text: str,
        current_translation: str,
        preferred_translation: str,
        chapter_id: str | None,
        scope: str,
        rule_type_hint: str,
        llm: dict[str, Any],
        warnings: list[str],
    ) -> list[FeedbackSuggestion]:
        endpoint = str(llm.get("endpoint") or "").strip()
        model = str(llm.get("model") or "").strip()
        token = str(llm.get("token") or "").strip()
        if not endpoint or not model or not token:
            return []

        try:
            suggestions = self._call_chat_completions(
                endpoint=endpoint,
                model=model,
                token=token,
                auth_header=str(llm.get("auth_header") or "Authorization"),
                auth_prefix=str(llm.get("auth_prefix") or "Bearer "),
                prompt_payload={
                    "task": "Convert editor feedback into structured translation rule suggestions.",
                    "feedback_text": feedback_text,
                    "source_text": source_text,
                    "current_translation": current_translation,
                    "preferred_translation": preferred_translation,
                    "chapter_id": chapter_id,
                    "scope": scope,
                    "rule_type_hint": rule_type_hint,
                    "allowed_rule_types": [
                        "phrase_override",
                        "locked_entity",
                        "style_profile",
                        "style_context",
                        "naturalization",
                        "style_guidance",
                    ],
                    "allowed_style_profiles": sorted(STYLE_PROFILES),
                },
            )
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            warnings.append(f"LLM feedback analysis failed: {exc}")
            return []

        parsed: list[FeedbackSuggestion] = []
        for item in suggestions:
            rule_type = str(item.get("rule_type") or "").strip()
            payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
            if rule_type not in {
                "phrase_override",
                "locked_entity",
                "style_profile",
                "style_context",
                "naturalization",
                "style_guidance",
            }:
                continue
            parsed.append(
                FeedbackSuggestion(
                    rule_type=rule_type,
                    title=str(item.get("title") or self._title_for_rule(rule_type)),
                    summary=str(item.get("summary") or "LLM-generated suggestion"),
                    payload=payload,
                    confidence=float(item.get("confidence") or 0.7),
                    scope=str(item.get("scope") or scope),
                    chapter_id=str(item.get("chapter_id") or chapter_id) if item.get("chapter_id") or chapter_id else None,
                    origin="llm",
                )
            )
        return parsed

    def _call_chat_completions(
        self,
        *,
        endpoint: str,
        model: str,
        token: str,
        auth_header: str,
        auth_prefix: str,
        prompt_payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        request_payload = {
            "model": model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return strict JSON only. Produce an object with a single `suggestions` array. "
                        "Each item must include rule_type, title, summary, payload, confidence, scope, and chapter_id."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt_payload, ensure_ascii=False),
                },
            ],
        }
        request = Request(
            endpoint,
            data=json.dumps(request_payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                auth_header: f"{auth_prefix}{token}",
            },
            method="POST",
        )
        with urlopen(request, timeout=45) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        if not content:
            raise ValueError("Empty LLM response")
        cleaned = self._strip_json_fence(str(content))
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict) or not isinstance(parsed.get("suggestions"), list):
            raise ValueError("LLM response did not contain a `suggestions` array")
        return parsed["suggestions"]

    @staticmethod
    def _strip_json_fence(content: str) -> str:
        stripped = content.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
            stripped = re.sub(r"\s*```$", "", stripped)
        return stripped.strip()

    @staticmethod
    def _normalize_text(text: str) -> str:
        lowered = str(text or "").lower()
        return lowered.replace("_", " ").replace("-", " ")

    @staticmethod
    def _extract_direct_rewrite(text: str) -> tuple[str, str] | None:
        patterns = (
            r"[\"“”'`「『](.+?)[\"“”'`」』]\s*(?:->|=>|→|dịch thành|thành)\s*[\"“”'`「『](.+?)[\"“”'`」』]",
            r"([^\r\n]{1,40}?)\s*(?:->|=>|→)\s*([^\r\n]{1,80})",
        )
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if not match:
                continue
            source = str(match.group(1)).strip()
            target = str(match.group(2)).strip()
            if source and target:
                return source, target
        return None

    @staticmethod
    def _looks_like_locked_entity(source_text: str, target_text: str, lowered_feedback: str) -> bool:
        source = str(source_text).strip()
        target = str(target_text).strip()
        if any(marker in lowered_feedback for marker in PROPER_NOUN_HINTS):
            return True
        if not source or not target:
            return False
        if not all("\u4e00" <= char <= "\u9fff" for char in source if char.strip()):
            return False
        return bool(target[:1].isupper() and len(source) <= 8)

    @staticmethod
    def _is_phrase_scope(source_text: str, preferred_translation: str) -> bool:
        source = str(source_text).strip()
        target = str(preferred_translation).strip()
        if not source or not target:
            return False
        if len(source) <= 24 and "\n" not in source:
            return True
        return len(source.split()) <= 6 and len(target.split()) <= 10

    def _detect_style_profile(self, lowered_feedback: str) -> str | None:
        for style_profile, markers in STYLE_HINTS:
            if any(marker in lowered_feedback for marker in markers):
                return style_profile
        return None

    @staticmethod
    def _detect_naturalization(lowered_feedback: str) -> dict[str, Any] | None:
        if any(marker in lowered_feedback for marker in COMPACT_HINTS):
            return {"enabled": True, "compact_sentences": True}
        if "ít rewrite" in lowered_feedback or "đừng rewrite mạnh" in lowered_feedback:
            return {"enabled": True, "compact_sentences": False}
        return None

    @staticmethod
    def _detect_style_context(lowered_feedback: str) -> dict[str, Any] | None:
        matched_genres = [
            genre
            for genre, markers in GENRE_HINTS
            if any(marker in lowered_feedback for marker in markers)
        ]
        tone = None
        if "u ám" in lowered_feedback or "ngột ngạt" in lowered_feedback:
            tone = "gloomy"
        elif "hài" in lowered_feedback or "vui" in lowered_feedback:
            tone = "light"
        elif "căng thẳng" in lowered_feedback or "rùng rợn" in lowered_feedback:
            tone = "suspense"

        if not matched_genres and not tone:
            return None
        payload: dict[str, Any] = {}
        if matched_genres:
            payload["genre_hints"] = matched_genres
        if tone:
            payload["tone"] = tone
        return payload

    @staticmethod
    def _make_term_suggestion(
        *,
        rule_type: str,
        source_text: str,
        target_text: str,
        chapter_id: str | None,
        scope: str,
        confidence: float,
    ) -> FeedbackSuggestion:
        payload = {"source": source_text.strip(), "target": target_text.strip()}
        if rule_type == "locked_entity":
            payload["entity_type"] = "project_term"
        return FeedbackSuggestion(
            rule_type=rule_type,
            title="Khoá thuật ngữ/tên riêng" if rule_type == "locked_entity" else "Thêm phrase override",
            summary=f"Áp `{source_text.strip()} -> {target_text.strip()}` vào pipeline cho các lần chạy sau.",
            payload=payload,
            confidence=confidence,
            scope=scope,
            chapter_id=chapter_id,
        )

    @staticmethod
    def _title_for_rule(rule_type: str) -> str:
        mapping = {
            "phrase_override": "Phrase override",
            "locked_entity": "Locked entity",
            "style_profile": "Style profile",
            "style_context": "Style context",
            "naturalization": "Naturalization",
            "style_guidance": "Style guidance",
        }
        return mapping.get(rule_type, rule_type)

    @staticmethod
    def _dedupe_suggestions(items: list[FeedbackSuggestion]) -> list[FeedbackSuggestion]:
        deduped: list[FeedbackSuggestion] = []
        seen: set[str] = set()
        for item in items:
            key = json.dumps(
                {
                    "rule_type": item.rule_type,
                    "scope": item.scope,
                    "chapter_id": item.chapter_id,
                    "payload": item.payload,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)
        return deduped
