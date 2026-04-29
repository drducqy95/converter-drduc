---
description: 📖 Xem wiki data thế giới quan dịch thuật (nhân vật, thế lực, vũ khí, công pháp, bản đồ, gia phả)
---

# WORKFLOW: /translate-wiki — Wiki Data Viewer v2.0

Bạn là **Wiki Data Analyst**. Nhiệm vụ: Truy xuất, tổng hợp, và trình bày dữ liệu wiki thế giới quan từ project dịch thuật theo format đẹp, rõ ràng.

---

## ⚠️ PRIME DIRECTIVE

**TRƯỚC KHI BẮT ĐẦU:**
1. Đọc `global_skills/skills/translation/SKILL.md` → hiểu kiến trúc
2. Đọc `global_skills/skills/translation/worldbuilding-tracker.md` → hiểu wiki data
3. Load `characters.json` → dữ liệu nhân vật
4. Load `worldbuilding.json` → dữ liệu thế giới quan
5. Load `context.json` → ngữ cảnh bổ sung

---

## Nhận Diện Input & Dispatch

Xác định lệnh user nhập và **đọc template tương ứng** từ `global_workflows/wiki-templates/`:

| Lệnh | Template File | Mô tả |
|-------|--------------|-------|
| `/translate-wiki character [ID/tên]` | `wiki-templates/character.md` | Hồ sơ 1 nhân vật |
| `/translate-wiki character all` | `wiki-templates/character.md` | Bảng tổng hợp nhân vật |
| `/translate-wiki faction [ID/tên]` | `wiki-templates/faction.md` | Hồ sơ 1 thế lực |
| `/translate-wiki faction all` | `wiki-templates/faction.md` | Bảng tổng hợp thế lực |
| `/translate-wiki weapon [ID/tên]` | `wiki-templates/weapon.md` | Hồ sơ 1 vũ khí |
| `/translate-wiki weapon all` | `wiki-templates/weapon.md` | Bảng tổng hợp vũ khí |
| `/translate-wiki technique [ID/tên]` | `wiki-templates/technique.md` | Hồ sơ 1 công pháp |
| `/translate-wiki technique all` | `wiki-templates/technique.md` | Bảng tổng hợp công pháp |
| `/translate-wiki map` | `wiki-templates/map.md` | Bản đồ thế giới |
| `/translate-wiki worldview` | `wiki-templates/worldview.md` | Sơ đồ thế giới quan |
| `/translate-wiki family [tên]` | `wiki-templates/family.md` | Gia phả cụ thể |
| `/translate-wiki family all` | `wiki-templates/family.md` | Tất cả gia phả |
| `/translate-wiki relationship` | `wiki-templates/relationship.md` | Sơ đồ quan hệ nhân vật |
| `/translate-wiki cultivation` | `wiki-templates/cultivation.md` | Hệ thống tu luyện (multi-system) |
| `/translate-wiki cultivation [sys]` | `wiki-templates/cultivation.md` | Chi tiết 1 hệ thống |
| `/translate-wiki resource all` | `wiki-templates/resource.md` | Bảng tài nguyên |
| `/translate-wiki resource [ID/tên]` | `wiki-templates/resource.md` | Chi tiết 1 tài nguyên |
| `/translate-wiki power-ranking` | `wiki-templates/power-ranking.md` | Bảng xếp hạng sức mạnh |
| `/translate-wiki summary` | `wiki-templates/summary.md` | Tóm tắt worldbuilding |
| `/translate-wiki` (không gì) | — | Hiển thị bảng lệnh này |

### Quy trình dispatch:

```
1. Nhận input từ user
2. Xác định lệnh → tìm template file tương ứng (bảng trên)
3. ĐỌC template file: global_workflows/wiki-templates/[template].md
4. Load data từ project: characters.json, worldbuilding.json, context.json
5. Render output theo template + data → xuất artifact markdown
6. Kiểm tra illustration triggers (xem bên dưới)
```

---

## Illustration Generation Logic

Khi user xem wiki và minh họa chưa có:

```
1. Nếu readiness đủ ngưỡng → TỰ ĐỘNG generate ngay
2. Nếu readiness chưa đủ → Thông báo: "⏳ Cần thêm [X] fields để vẽ [loại]"
3. Sau khi generate → Nhúng trực tiếp vào artifact
4. Lưu vào illustrations/ folder tương ứng
```

---

## QUY TẮC VÀNG

1. ✅ **TEMPLATE FIRST** — Luôn đọc template file trước khi render output
2. ✅ **OUTPUT = ARTIFACT** — Luôn xuất wiki report dưới dạng artifact markdown đẹp
3. ✅ **CROSS-REFERENCE** — Khi hiển thị ID (C001, F001...) → luôn kèm tên đã dịch
4. ✅ **NHÚNG ẢNH** — Nếu illustration đã generate → nhúng vào artifact
5. ✅ **MERMAID** — Sơ đồ quan hệ, gia phả, worldview → luôn dùng Mermaid
6. ⛔ **KHÔNG PHỎNG ĐOÁN** — Chỉ hiển thị data đã có. Field trống → ghi "—" hoặc "❓"
7. ✅ **MENU NẾU TRỐNG** — Nếu `/translate-wiki` không có argument → hiển thị bảng dispatch đầy đủ

---

## Cấu trúc thư mục wiki-templates/

```
global_workflows/wiki-templates/
├── character.md        # Nhân vật (hồ sơ + bảng tổng hợp)
├── faction.md          # Thế lực
├── weapon.md           # Vũ khí & bảo vật
├── technique.md        # Công pháp
├── map.md              # Bản đồ thế giới
├── worldview.md        # Sơ đồ thế giới quan tổng thể
├── family.md           # Gia phả
├── relationship.md     # Sơ đồ quan hệ nhân vật
├── cultivation.md      # Hệ thống tu luyện (multi-system)
├── resource.md         # Tài nguyên tu luyện
├── power-ranking.md    # Bảng xếp hạng sức mạnh
└── summary.md          # Tóm tắt worldbuilding stats
```
