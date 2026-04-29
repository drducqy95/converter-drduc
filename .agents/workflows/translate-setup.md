---
description: 🌐 Khởi tạo project dịch thuật mới với Translation Engine
---

# WORKFLOW: /translate-setup — Khởi Tạo Project Dịch Thuật v2.0

Bạn là **Translation Project Manager**. Nhiệm vụ: Thiết lập project dịch thuật mới với đầy đủ state files, nhập glossary, và chuẩn bị character graph.

---

## ⚠️ PRIME DIRECTIVE

**TRƯỚC KHI BẮT ĐẦU:**
1. Đọc SKILL.md tại `global_skills/skills/translation/SKILL.md` → hiểu kiến trúc
2. Đọc `global_skills/skills/translation/resources/global_glossary.json` → tận dụng thuật ngữ cũ
3. Đọc `~/.gemini/antigravity/translation/global_pronouns.json` → tận dụng common pronoun groups liên project
4. Sau khi scaffold xong, rebuild `Translation Atlas` và `Translation Pronouns` để project có grounding note dùng cho recap/Obsidian ngay.

---

## Giai đoạn 0: Thu Thập Thông Tin

### 0.1. Nhận diện Input

```
User: /translate-setup [thư mục chứa source]
→ Quét thư mục, liệt kê files nguồn
→ Chế độ: Full Project Setup

User: /translate-setup
→ Hỏi thông tin từ user
→ Chế độ: Interactive Setup
```

### 0.2. Thu thập thông tin bắt buộc

```
"🌐 **KHỞI TẠO PROJECT DỊCH THUẬT MỚI**

Em cần biết mấy thông tin sau:

1️⃣ **Tên project:** (ví dụ: Y Thien Do Long Ky)
2️⃣ **Ngôn ngữ nguồn:** (zh/en/ja/ko/fr/de/...)
3️⃣ **Ngôn ngữ đích:** (mặc định: vi)
4️⃣ **Thể loại:** 
   - eastern_fiction (Truyện phương Đông)
   - western_fiction (Truyện phương Tây)
   - scientific (Khoa học)
   - medical (Y tế)
   - legal (Luật)
   - general (Tổng quát)
5️⃣ **Sub-genre:** (ví dụ: xianxia, wuxia, romance, sci_fi...)
6️⃣ **Xử lý tên riêng:** 
   - phien_am (Phiên âm Hán-Việt/Romaji)
   - keep_original (Giữ nguyên)
   - first_mention_both (Lần đầu: gốc + phiên âm, sau đó: phiên âm)
7️⃣ **Thư mục nguồn:** (đường dẫn chứa file source)"
```

*Nếu user cung cấp đủ trong lệnh → skip hỏi*

---

## Giai đoạn 1: Tạo Cấu Trúc Project

### 1.1. Tạo thư mục

```
[PROJECT_DIR]/
├── translation_config.json
├── glossary.json
├── pronouns.json
├── characters.json
├── context.json
├── worldbuilding.json          # 🆕 Wiki data: thế lực, vũ khí, công pháp, địa điểm
├── progress.json
├── source/
├── drafts/
├── output/
├── illustrations/               # 🆕 Hình minh họa tự động
│   ├── characters/              # Chân dung nhân vật
│   ├── diagrams/                # Sơ đồ quan hệ, gia phả, thế giới quan
│   └── maps/                    # Bản đồ thế giới
└── logs/
```

### 1.2. Tạo translation_config.json

```json
{
  "project_name": "[user input]",
  "source_language": "[user input]",
  "target_language": "vi",
  "genre": "[user input]",
  "sub_genre": "[user input]",
  "name_setting": "[user input]",
  "pronoun_mode": "hybrid",
  "reflection_max_iterations": 3,
  "created_at": "[timestamp]",
  "total_chapters": 0,
  "notes": ""
}
```

### 1.3. Tạo state files rỗng

**glossary.json:**
```json
{
  "metadata": {
    "source_language": "",
    "target_language": "vi",
    "genre": "",
    "last_updated": ""
  },
  "entries": []
}
```

**pronouns.json:**
```json
{
  "metadata": {
    "project_name": "",
    "source_language": "",
    "target_language": "vi",
    "genre": "",
    "sub_genre": "",
    "pronoun_mode": "hybrid",
    "last_updated": ""
  },
  "project_pronouns": []
}
```

**characters.json:**
```json
{
  "characters": [],
  "relationships": []
}
```

**context.json:**
```json
{
  "work_title": "",
  "genre": "",
  "tone": "",
  "global_themes": [],
  "current_arc": "",
  "chapter_summaries": [],
  "plot_threads": [],
  "world_building": {}
}
```

**progress.json:**
```json
{
  "total_chapters": 0,
  "completed_chapters": 0,
  "current_chapter": 0,
  "status": "initialized",
  "chapters": []
}
```

**🆕 worldbuilding.json:**
```json
{
  "factions": [],
  "weapons": [],
  "techniques": [],
  "cultivation_systems": [],
  "cultivation_resources": [],
  "power_ranking": {
    "last_updated_chapter": null,
    "ranking": [],
    "notes": ""
  },
  "locations": [],
  "world_map": {
    "generated": false,
    "image_path": null,
    "readiness_score": 0,
    "last_updated_chapter": null,
    "description": "",
    "scale": "unknown"
  },
  "relationship_diagrams": {
    "character_relationship": {
      "generated": false,
      "mermaid_path": null,
      "image_path": null,
      "last_updated_chapter": null,
      "min_characters_to_generate": 8
    },
    "family_tree": {
      "generated": false,
      "mermaid_path": null,
      "image_path": null,
      "last_updated_chapter": null,
      "families_tracked": []
    },
    "faction_relationship": {
      "generated": false,
      "mermaid_path": null,
      "image_path": null,
      "last_updated_chapter": null
    }
  }
}
```

---

## Giai đoạn 2: Import Global Glossary

```
1. Đọc global_glossary.json
2. Lọc entries theo:
   - source_language == project.source_language
   - category phù hợp với genre
3. Import vào glossary.json cục bộ
4. Báo user: "📚 Đã import [X] thuật ngữ từ kho toàn cục"
5. Đọc `~/.gemini/antigravity/translation/global_pronouns.json`
6. Lọc common pronoun groups phù hợp genre/sub-genre
7. Chuẩn bị `pronouns.json` cục bộ để chứa project-only overrides
```

---

## Giai đoạn 3: Pre-Scan Source (Nếu Có)

Nếu user cung cấp thư mục source:

```
1. Liệt kê tất cả files trong source/
2. Đếm tổng số chapters/sections
3. Update progress.json → total_chapters
4. Chạy script Auto-Scan toàn cục bằng lệnh (limit=100 hoặc theo ý user):
   `python "C:\Users\vanki\.gemini\antigravity\global_skills\skills\translation\scripts\source_analyzer.py" --source_dir "[PROJECT_DIR]/Source" --limit 100 --output "[PROJECT_DIR]/scan_results.json"`
5. Agent dùng lệnh view_file đọc `scan_results.json` để lấy thống kê tần suất.
6. 🆕 Dựa vào kết quả NLP, Agent tự suy luận để lọc ra các thực thể thực sự (loại bỏ từ rác do script nhận diện nhầm).
7. Trình bày đề xuất danh sách nhân vật, địa danh, thế lực, công pháp.
8. Hỏi user xác nhận nhân vật, glossary, và worldbuilding ban đầu
```

### 3.1. Xây dựng Character Graph ban đầu

```
"📋 Em phát hiện các nhân vật sau trong 3 chương đầu:

| # | Tên gốc | Dịch đề xuất | Giới tính | Vai trò |
|---|---------|-------------|-----------|---------|
| 1 | 张无忌 | Trương Vô Kỵ | Nam | Chính |
| 2 | 赵敏 | Triệu Mẫn | Nữ | Chính |

Anh muốn sửa gì không? (Tên dịch, giới tính, vai trò)"
```

Sau khi user confirm → ghi vào characters.json (Wiki-style v2 format)

### 3.2. 🆕 Xây dựng Worldbuilding ban đầu

```
"🌍 Em phát hiện các yếu tố thế giới quan sau:

🏰 **Thế lự:**
| # | Tên gốc | Dịch đề xuất | Loại | Lãnh đạo |
|---|---------|-------------|------|----------|
| 1 | ... | ... | ... | ... |

⚔️ **Vũ khí/Bảo vật:**
| # | Tên gốc | Dịch đề xuất | Loại | Chủ nhân |
|---|---------|-------------|------|----------|
| 1 | ... | ... | ... | ... |

📜 **Công pháp:**
| # | Tên gốc | Dịch đề xuất | Loại | Người dùng |
|---|---------|-------------|------|----------|
| 1 | ... | ... | ... | ... |

📍 **Địa điểm:**
| # | Tên gốc | Dịch đề xuất | Loại |
|---|---------|-------------|------|
| 1 | ... | ... | ... |

⬆️ **Hệ thống cảnh giới (nếu có):**
[Mô tả hệ thống sức mạnh nhận diện được]

Anh muốn sửa gì không?"
```

Sau khi user confirm → ghi vào worldbuilding.json

---

## Giai đoạn 4: Báo Cáo Hoàn Tất

```
"✅ **PROJECT DỊCH THUẬT ĐÃ KHỞi TẠO!**

📁 Project: [project_name]
🌍 Nguồn → Đích: [source] → [target]
📖 Thể loại: [genre] / [sub_genre]
📚 Thuật ngữ imported: [X] entries
👥 Nhân vật đã nhận diện: [Y] characters
📄 Tổng chapters: [Z]

🌍 **Worldbuilding đã khởi tạo:**
🏰 Thế lực: [A] entries
⚔️ Vũ khí: [B] entries
📜 Công pháp: [C] entries
📍 Địa điểm: [D] entries
⬆️ Hệ thống cảnh giới: [đã/chưa] nhận diện

📂 Thư mục: [PROJECT_DIR]

➡️ **Bắt đầu dịch:**
1️⃣ /translate [chapter_number] — Dịch chương cụ thể
2️⃣ /translate all — Dịch tất cả từ đầu
3️⃣ /translate next — Dịch chương tiếp theo
4️⃣ /translate-wiki character — Xem hồ sơ nhân vật
5️⃣ /translate-wiki worldview — Xem thế giới quan"
```
