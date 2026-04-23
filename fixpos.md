# POS Migration Debugging & POSRewriteEngine Fix Plan

> Khắc phục các lỗi sai lệch giữa migration plan và thực thi, sửa [POSRewriteEngine](file:///d:/Converter%20by%20DrDuc/src/core/pos_rewrite_engine.py#15-151) để xử lý đúng modifier chain.

## Phân Tích Nguyên Nhân Gốc (Root Cause Analysis)

Kết quả diagnostic ([pos_diagnostic_results.json](file:///d:/Converter%20by%20DrDuc/pos_diagnostic_results.json)) cho thấy **7 vấn đề**:

### 🔴 Critical Issues (Gây hỏng rewrite trực tiếp)

| # | Vấn đề | Impact | Ví dụ |
|---|--------|--------|-------|
| 1 | **POS Tag Naming Mismatch** | Engine dùng `ADJECTIVE`, `PARTICLE` nhưng plan/docs dùng `ADJ`, `PART` | [_rewrite_de_constructions](file:///d:/Converter%20by%20DrDuc/src/core/pos_rewrite_engine.py#42-85) check `== "PARTICLE"` thay vì `== "PART"` |
| 2 | **`男子` chưa có POS tag** | Head noun detection fail → không đảo `穿黑色风衣的男子` | `pos_tag=None` → `head.pos_tag == "NOUN"` = False |
| 3 | **`美丽` tagged NOUN** | Possessive detection sai, output `cô gái của xinh đẹp` thay vì `cô gái xinh đẹp` | CEDICT "beautiful" → heuristic gán NOUN |
| 4 | **`把`/`被` mất function word** | CEDICT overwrite Tier 1 seeds | `把`: pos_tag=NOUN, is_function_word=0 |

### 🟡 Secondary Issues (Gây thiếu coverage)

| # | Vấn đề | Impact |
|---|--------|--------|
| 5 | `似的` không trong entries | Simulative rewrite không kích hoạt |
| 6 | `座` tagged NOUN/classifier | Không phải CLF → classifier rules bỏ qua |
| 7 | `腐烂` tagged VERB | Trong ngữ cảnh modifier thì nên là ADJ |

---

## Proposed Changes

### Component 1: POS Seeder — Fix Tier Priority

> [!IMPORTANT]
> **Root cause**: CEDICT Tier 3 ghi đè Tier 1 seeds vì seeder chạy Tier 1 trước, Tier 3 sau — và Tier 3 UPDATE tất cả entries kể cả đã có tag.

#### [MODIFY] [pos_seeder.py](file:///d:/Converter%20by%20DrDuc/src/tools/pos_seeder.py)

1. **Tier 3 chỉ UPDATE entries chưa có `pos_tag`** — thêm `WHERE pos_tag IS NULL` vào query CEDICT update
2. **Thêm Tier 1 seeds cho `把`/`被`** với `is_function_word=1`
3. **Fix CEDICT heuristic**: entries có meaning bắt đầu "to " → VERB ok, nhưng `beautiful/pretty` cũng bị gán NOUN vì fallback; cần thêm ADJ detection cho English adjectives
4. **Thêm `似的` vào Tier 1** với tag SUFFIX

---

### Component 2: POSRewriteEngine — Fix Head Noun Detection & Modifier Chain

#### [MODIFY] [pos_rewrite_engine.py](file:///d:/Converter%20by%20DrDuc/src/core/pos_rewrite_engine.py)

**Issue 1: Head noun detection quá strict**
```python
# HIỆN TẠI (line 53): chỉ match NOUN
if head.pos_tag == "NOUN":
```
**Fix**: Chấp nhận head noun khi `pos_tag in {"NOUN", None}` (NULL tag = untagged entry, phần lớn là noun). Thêm negative guard cho VERB/ADJ/PARTICLE.

**Issue 2: Possessive detection sai cho ADJ modifiers**
```python
# HIỆN TẠI (line 64-66): single NOUN/PRONOUN → possessive → "của"
is_possessive = (modifier_chain[0].pos_tag in ["PRONOUN", "NOUN"]
               and modifier_chain[0].pos_sub != "abstract"
               and len(modifier_chain) == 1)
```
**Fix**: Single ADJECTIVE modifier → KHÔNG phải possessive. Chỉ possessive khi modifier là PRONOUN hoặc NOUN (person/name).

**Issue 3: [_find_modifier_start](file:///d:/Converter%20by%20DrDuc/src/core/pos_rewrite_engine.py#86-106) tag validation**
- Thêm tag `"PREPOSITION"` vào valid_tags (hiện thiếu)
- Thêm guard: token không có POS tag (`None`) → coi là valid modifier nếu source ngắn (≤2 chars) — vì nhiều modifier chưa được tag

**Issue 4: Locative rewrite thiếu guard cho NUM+CLF+NOUN chain**
- `两座墓碑面前` → locative swap chỉ swap `面前` với `墓碑`, bỏ qua `两座`
- Fix: Khi swap locative, scan ngược để lấy toàn bộ NUM+CLF+NOUN chain

---

### Component 3: POS Seeder — Expand Coverage

#### [MODIFY] [pos_seeder.py](file:///d:/Converter%20by%20DrDuc/src/tools/pos_seeder.py)

1. **Fix CEDICT heuristic gán ADJ**: Detect English adjective patterns (`"(adj)"`), common adjective suffixes
2. **Thêm Tier 2 rules**: `trichdan_idioms` category → tag `IDIOM`
3. **Fix `座` classifier**: Thêm vào Tier 1 seeds `"座": {"pos_tag": "CLF", "pos_sub": "buildings"}`

---

## Verification Plan

### Automated Tests

```powershell
# 1. Re-run seeder to rebuild POS tags
cd "d:\Converter by DrDuc"
python src/tools/pos_seeder.py

# 2. Run diagnostic script to verify fixes
python /tmp/pos_diagnostic.py

# 3. Run existing regression suite (must still pass)
python -m pytest tests/test_translation_regressions.py -v
```

#### Expected diagnostic results after fix:

| Input | Expected Output | Rule |
|-------|----------------|------|
| `穿黑色风衣的男子` | `nam tử mặc màu đen áo gió` | Head+Modifier swap |
| `老太的身躯` | `thân thể của lão thái` | Possessive với "của" |
| `惨白腐烂的双手` | `hai tay trắng ởn hư thối` | Head+Modifier swap (no "của") |
| `美丽的女孩` | `cô gái xinh đẹp` | ADJ modifier (no "của") |
| `两座墓碑面前` | `trước mặt hai tòa bia mộ` | Locative + full chain swap |

### Manual Verification
- Chạy `python run_full_pipeline.py --skip-pretranslation` để dịch chapter thực tế và so sánh diff
