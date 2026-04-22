#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Style preset metadata and sentence-naturalization rule selection."""

from __future__ import annotations


STYLE_RULE_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {
    "generic_cleanup": (
        (r"\bKiểu này phúc lợi đãi ngộ\b", "Đãi ngộ kiểu này"),
        (r"\bhắn nhóm\b", "họ"),
        (r"\bở vào\b", "nằm trong"),
        (r"\bcó thể thể hiện\b", "minh chứng"),
        (r"\btại đây trong\b", "ở đây"),
        (r"\blớn nhất tiệm sách\b", "hiệu sách lớn nhất"),
        (r"\bở giữa kinh doanh\b", "mở cửa"),
        (r"\bđem xe ngừng hảo\b", "đỗ xe xong"),
        (r"\bở ở đây làm việc\b", "làm việc ở đây"),
        (r"\bkhông có gì cả\b", "chẳng có gì"),
        (r"\bmột loại (.+?) cảm giác\b", r"cảm giác \1"),
        (r"\btự mình\b", "chính mình"),
    ),
    "modern_narration": (
        (r"\bđối với một mới vừa vặn năm thứ Ba đại học tốt nghiệp\b", "đối với một sinh viên vừa mới tốt nghiệp năm ba"),
        (r"\bkhông khác là trong 500 vạn thưởng lớn\b", "chẳng khác nào trúng số độc đắc 500 vạn"),
        (r"\bĐang chờ (.+?) còn nghĩ lại tiếp tục dư vị lúc\b", r"Ngay khi \1 còn đang muốn tiếp tục dư vị ngọt ngào"),
        (r"\btheo trước đó trong vui mừng tỉnh lại\b", "giật mình tỉnh lại từ cơn phấn khích"),
        (r"\bchợt hiểu nhớ ra\b", "sực nhớ ra"),
        (r"\bmột chừng bốn mươi tuổi chú\b", "một ông chú tầm bốn mươi tuổi"),
        (r"\bở có quan hệ với chính quyền\b", "có quan hệ mật thiết với chính quyền"),
        (r"\bđoạn sẽ không\b", "tuyệt đối không"),
        (r"\bđến từ đó trường đại học\b", "tốt nghiệp trường đại học nào"),
        (r"\bhọc là một loại nào chuyên nghiệp\b", "học chuyên ngành gì"),
        (r"\bVà (.+?) đỗ xe xong\b", r"Sau khi \1 đỗ xe xong"),
        (r"\bnghe lời với xuống đi\b", "ngoan ngoãn đi theo"),
        (r"\bdinh dính nhiệt khí đột nhiên kéo đi lên\b", "luồng khí nóng hầm hập lập tức ập tới"),
        (r"\bcho người tôi mấy phần cảm giác âm trầm\b", "cho người ta mấy phần cảm giác âm trầm"),
        (r"\bmột vạn cái không muốn\b", "một vạn cái không cam tâm"),
        (r"\bở tiệm tạp hoá trong\b", "ở cửa hàng tiện lợi"),
        (r"\bở đây ăn chút gì gì đó\b", "ngồi đây ăn chút đồ"),
        (r"\bquả quyết gọi điện thoại báo cảnh sát\b", "dứt khoát gọi điện thoại báo cảnh sát"),
        (r"\blà triệt để sợ hãi\b", "thực sự sợ hãi"),
        (r"\bxúi quẩy\b", "đen đủi"),
        (r"\bbộ đáng sau\b", "bộ dáng"),
        (r"\bcông tác chứng minh\b", "giấy chứng minh công tác"),
        (r"\bmột cái nhân tình huống\b", "tình hình cá nhân"),
        (r"\bmột nét không ít chi tiêu\b", "một khoản chi tiêu không nhỏ"),
        (r"\bnghẹn không ra đến một cái rắm người\b", "ngột đến mức không thốt nổi một câu"),
    ),
    "modern_dialogue": (
        (r"\bNhư là đã ký kết làm việc hợp đồng\b", "Đã ký hợp đồng lao động rồi"),
        (r"\bđi thực hiện cậu chức trách đi\b", "hãy đi thực hiện chức trách của cậu đi"),
        (r"\bkhông hỏi đề\b", "không vấn đề gì"),
        (r"\bCó thể cậu gì đều không nói với tôi, tôi cái này cũng không có cách làm việc a\b", "Nhưng chú chẳng nói gì với cháu cả, cháu làm sao mà làm việc được chứ"),
        (r"\banh mẹ như thế xâu\b", "mẹ nó, sao mà láo thế"),
        (r"\bmạo xưng một lát điện\b", "sạc một lát điện"),
    ),
    "suspense_horror": (
        (r"\bnương nương khang\b", "ẻo lả"),
        (r"\btình hình thực tế huống\b", "tình hình"),
        (r"\btình hình thực tế tự\b", "tâm trạng"),
        (r"\btrong nội tâm\b", "trong lòng"),
        (r"\bcơ hồ là hét ra\b", "gần như là hét lên"),
        (r"\bkhông sợ người khác làm phiền\b", "không ngại phiền"),
        (r"\bkhông có đạt được\b", "không thu được"),
        (r"\bhỏi gì cũng không biết\b", "mù tịt không biết gì"),
        (r"\btrước kia luôn luôn nghe người ta nói đến\b", "trước kia tôi thường nghe người ta nói về"),
        (r"\bcũng chỉ có cách nhau một đường\b", "chỉ cách nhau một lằn ranh"),
        (r"\blại là tình cảm chân thực tin tưởng\b", "lại thật lòng tin rằng"),
        (r"\blàm người có nhiều thiện lương, nhiều chính trực\b", "là người lương thiện, chính trực đến đâu"),
        (r"\bloại sự tình này nguyên do bốn người gánh chịu\b", "kiểu chuyện này để bốn người cùng gánh"),
        (r"\bbất kể thế nào đều là phải mạnh hơn\b", "dù sao cũng tốt hơn"),
        (r"\bnhưng mà không có gì ngoài những thứ này ngoài ý muốn\b", "nhưng ngoài chuyện đó ra"),
        (r"\banh thì tại không có đạt được nửa phần tin tức có giá trị\b", "anh vẫn không thu được nửa phần tin tức có giá trị"),
        (r"\btiếp theo giây lát\b", "ngay sau đó"),
        (r"\btiếp lấy\b", "tiếp đó"),
        (r"\bhướng phía\b", "về phía"),
        (r"\btheo trong\b", "từ trong"),
        (r"\bkhông còn nghi ngờ gì nữa\b", "rõ ràng"),
        (r"\bkhông chán ngại phiền\b", "không ngại phiền"),
    ),
}

STYLE_PROFILES: dict[str, dict] = {
    "source_faithful": {
        "label": "Sat Nguon",
        "description": "Giu cau truc cau gan voi nguon, chi lam sach cac loi co hoc.",
        "rewrite_groups": (),
        "recommended_genres": ["general", "technical", "historical"],
        "naturalization_strength": "low",
    },
    "balanced_novel": {
        "label": "Can Bang",
        "description": "Van doc tu nhien hon nhung van han che tai cau truc manh.",
        "rewrite_groups": ("generic_cleanup",),
        "recommended_genres": ["general", "modern", "western_fantasy"],
        "naturalization_strength": "medium",
    },
    "modern_narrative": {
        "label": "Hien Dai Tu Su",
        "description": "Uu tien van tu su hien dai muot hon, giam calque phan noi ke.",
        "rewrite_groups": ("generic_cleanup", "modern_narration"),
        "recommended_genres": ["modern"],
        "naturalization_strength": "high",
    },
    "dialogue_natural": {
        "label": "Thoai Tu Nhien",
        "description": "Tap trung lam mem hoi thoai, xung ho va cau noi doi dap.",
        "rewrite_groups": ("generic_cleanup", "modern_dialogue"),
        "recommended_genres": ["modern", "general"],
        "naturalization_strength": "high",
    },
    "modern_novel_adaptive": {
        "label": "Tieu Thuyet Tu Nhien",
        "description": "Ket hop tu su va hoi thoai, uu tien van dich doc nhu tieu thuyet dich.",
        "rewrite_groups": ("generic_cleanup", "modern_narration", "modern_dialogue"),
        "recommended_genres": ["modern"],
        "naturalization_strength": "high",
    },
    "suspense_horror": {
        "label": "Kinh Di Can Thang",
        "description": "Uu tien nhac tinh canh nguy hiem, giam calque va giu nhip cau gon, gay suc ep.",
        "rewrite_groups": ("generic_cleanup", "modern_narration", "modern_dialogue", "suspense_horror"),
        "recommended_genres": ["modern", "horror", "suspense"],
        "naturalization_strength": "high",
    },
    "han_viet_balanced": {
        "label": "Han Viet Can Bang",
        "description": "Giu sac thai Han Viet va tiet che khau ngu, phu hop co phong hoac tien hiep.",
        "rewrite_groups": ("generic_cleanup",),
        "recommended_genres": ["xianxia", "historical"],
        "naturalization_strength": "medium",
    },
}


def list_style_profiles() -> list[dict]:
    profiles: list[dict] = []
    for style_id, metadata in STYLE_PROFILES.items():
        item = dict(metadata)
        item["id"] = style_id
        profiles.append(item)
    return profiles


def default_style_profile(genre_hints: list[str] | None, cultural_origin_hint: str | None) -> str:
    hints = set(genre_hints or [])
    if "xianxia" in hints or cultural_origin_hint == "han_viet":
        return "han_viet_balanced"
    if "horror" in hints or "suspense" in hints:
        return "suspense_horror"
    if "modern" in hints:
        return "modern_novel_adaptive"
    return "balanced_novel"


def default_style_preferences(genre_hints: list[str] | None, cultural_origin_hint: str | None) -> dict:
    project_profile = default_style_profile(genre_hints, cultural_origin_hint)
    return {
        "project_profile": project_profile,
        "project_context": {
            "genre_hints": list(genre_hints or ["general"]),
            "cultural_origin_hint": cultural_origin_hint or "general",
        },
        "chapter_overrides": {},
        "selection_policy": "chapter_override > project_profile > inferred_default",
        "available_profiles": list_style_profiles(),
    }


def build_rewrite_patterns(profile_id: str, *, enabled: bool = True) -> tuple[tuple[str, str], ...]:
    if not enabled:
        return ()
    metadata = STYLE_PROFILES.get(profile_id) or STYLE_PROFILES["balanced_novel"]
    patterns: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for group_name in metadata.get("rewrite_groups", ()):
        for pattern in STYLE_RULE_GROUPS.get(group_name, ()):
            if pattern in seen:
                continue
            seen.add(pattern)
            patterns.append(pattern)
    return tuple(patterns)


def resolve_style_selection(config: dict, chapter_id: str | None = None) -> dict:
    genre_hints = list(config.get("genre_hints") or ["general"])
    cultural_origin_hint = config.get("cultural_origin_hint")
    inferred_profile = default_style_profile(genre_hints, cultural_origin_hint)

    style_preferences = dict(config.get("style_preferences") or {})
    project_profile = config.get("style_profile") or style_preferences.get("project_profile") or inferred_profile
    if project_profile not in STYLE_PROFILES:
        project_profile = inferred_profile

    chapter_overrides = {}
    chapter_overrides.update(config.get("chapter_style_overrides") or {})
    chapter_overrides.update(style_preferences.get("chapter_overrides") or {})
    chapter_override = dict(chapter_overrides.get(chapter_id, {})) if chapter_id else {}

    effective_profile = chapter_override.get("style_profile") or project_profile
    if effective_profile not in STYLE_PROFILES:
        effective_profile = inferred_profile

    project_context = _deep_merge(style_preferences.get("project_context") or {}, config.get("style_context") or {})
    effective_context = _deep_merge(project_context, chapter_override.get("style_context") or {})
    naturalization = _deep_merge(
        {"enabled": effective_profile != "source_faithful"},
        config.get("naturalization") or {},
        chapter_override.get("naturalization") or {},
    )

    if chapter_override.get("style_profile"):
        resolved_from = "chapter_override"
    elif config.get("style_profile") or style_preferences.get("project_profile"):
        resolved_from = "project_profile"
    else:
        resolved_from = "inferred_default"

    return {
        "chapter_id": chapter_id,
        "inferred_profile": inferred_profile,
        "project_profile": project_profile,
        "effective_profile": effective_profile,
        "resolved_from": resolved_from,
        "effective_context": effective_context,
        "naturalization": naturalization,
        "profile_metadata": dict(STYLE_PROFILES[effective_profile]),
    }


def _deep_merge(base: dict, *overrides: dict) -> dict:
    merged = dict(base)
    for override in overrides:
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = _deep_merge(merged[key], value)
            else:
                merged[key] = value
    return merged
