# Cross-Universe Term Bank & Context-Aware Entity Scanner

## Mục tiêu

Xây dựng hệ thống term bank toàn diện và thuật toán entity scanning nhận biết ngữ cảnh (universe-aware) để dịch chính xác các thể loại truyện **Chư Thiên (诸天)**, **Vô Hạn (无限流)**, **Xuyên Việt Đồng Nhân (穿越同人)** — nơi nhân vật, địa danh, và thuật ngữ từ nhiều tác phẩm khác nhau xuất hiện chồng chéo trong cùng một văn bản.

---

## Quyết định đã xác nhận

| # | Quyết định | Chi tiết |
|---|-----------|----------|
| Q1 | Entity types chi tiết tối đa | Giữ tất cả: `person`, `location`, `organization`, `realm`, `technique`, `weapon`, `item`, `title`, `creature`, `faction`, `term`. Nền tảng tích lũy database |
| Q2 | User-controlled term bank enrichment | Entity scan → điền đầy đủ info → gắn tag → trình user duyệt → user chọn lưu vào term bank. Không tự động |
| Q3 | Same-name cross-universe disambiguation | Thuật toán phân biệt 2+ entity cùng `source` khác `universe` trong cùng context bằng co-occurrence + fingerprint |
| Q4 | Import toàn bộ real-world names | Toàn bộ Name_Doithuc.md (~220 entries) → `global/real_world.jsonl` |

---

## 1. Phân tích Thế giới quan

### 1.1 Mô hình 4 Layers Entity

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: SHARED TERMS (Dùng chung mọi truyện)         │
│  ├── Tu luyện cấp bậc: 元婴期, 结丹期, 化神期...        │
│  ├── Chức vụ: 宗主, 长老, 掌门...                       │
│  ├── Thuật ngữ: 灵气, 灵根, 飞升, 渡劫...              │
│  └── Vũ khí cấp: 法器, 灵器, 法宝, 仙器...             │
│                                                         │
│  Layer 2: FRANCHISE-SPECIFIC (Riêng theo tác phẩm)      │
│  ├── Đấu Phá: 斗气, 斗者→斗帝, 异火榜                  │
│  ├── Đấu La: 魂环, 魂力, 封号斗罗                       │
│  ├── Tiên Nghịch: 天逆珠, 禁制, 碎涅期                  │
│  └── Quỷ Bí: Sequence系统, 非凡特性, 扮演法             │
│                                                         │
│  Layer 3: CHARACTER NAMES (Nhân vật)                     │
│  ├── Canon characters: 萧炎, 唐三, 韩立...              │
│  ├── Historical figures: 李世民, 诸葛亮...               │
│  ├── Mythological: 雷神, 太白金星...                     │
│  └── Western transliterations: 克莱恩, 汤姆...          │
│                                                         │
│  Layer 4: CROSS-UNIVERSE OVERLAP (Chồng chéo)           │
│  ├── 长老 = Trưởng Lão (mọi truyện)                    │
│  ├── 雷神 = Lôi Thần (mythology) vs Thor (Marvel)       │
│  └── Same-name characters across works                  │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Universe Mapping

| Universe ID | Tác phẩm | Fingerprint Terms |
|-------------|----------|-------------------|
| `tu_tien` | Phàm Nhân Tu Tiên, Tiên Nghịch, Tru Tiên | 灵根, 筑基, 结丹, 元婴, 化神, 飞升 |
| `dau_khi` | Đấu Phá Thương Khung, Vũ Động Càn Khôn | 斗气, 异火, 斗尊, 斗帝, 萧炎 |
| `dau_la` | Đấu La Đại Lục, Thần Ấn Vương Tọa | 魂环, 魂力, 魂兽, 斗罗, 武魂 |
| `than_dong` | Già Thiên, Hoàn Mỹ Thế Giới | 大帝, 圣人, 荒古, 至尊骨 |
| `kiem_lai` | Kiếm Lai, Tuyết Trung Hãn Đao Hành | 剑仙, 浩然天下, 纯粹武夫 |
| `quy_bi` | Quỷ Bí Chi Chủ | 序列, 魔药, 非凡特性, 扮演法 |

---

## 2. Proposed Changes

### Phase 1: JSONL Data Migration

#### [NEW] [md_to_jsonl_converter.py](file:///d:/Converter%20by%20DrDuc/scripts/md_to_jsonl_converter.py)

Script parse format `* 中文 = Hán Việt` từ 12 file markdown → JSONL records:

- Auto-detect entity_type từ section header (### Nhân vật → person, ### Bản đồ → location, etc.)
- Auto-fill `universe`, `work`, `franchise` từ file metadata
- Auto-tag từ section context

**Output structure:**

```
data/term_bank/
├── global/
│   ├── proper_names.jsonl          (existing — giữ nguyên)
│   ├── shared_cultivation.jsonl    (NEW — thuật ngữ tu tiên chung: 灵气, 结丹, 元婴...)
│   ├── shared_titles.jsonl         (NEW — chức vụ chung: 宗主, 长老, 掌门...)
│   └── real_world.jsonl            (NEW — toàn bộ Name_Doithuc.md, ~220 entries)
├── universes/                      (NEW — 6 universe folders)
│   ├── tu_tien/
│   │   ├── characters.jsonl        (Hàn Lập, Vương Lâm, Trương Tiểu Phàm...)
│   │   ├── locations.jsonl         (Hoàng Phong Cốc, Triệu Quốc...)
│   │   ├── organizations.jsonl     (Thất Huyền Môn, Lạc Vân Tông...)
│   │   ├── realms.jsonl            (Luyện Khí, Trúc Cơ, Kết Đan...)
│   │   ├── techniques.jsonl        (Trường Xuân Công, Thanh Nguyên Kiếm Quyết...)
│   │   ├── weapons.jsonl           (Thanh Trúc Phong Vân Kiếm...)
│   │   ├── items.jsonl             (Linh Thạch, Trúc Cơ Đan...)
│   │   └── creatures.jsonl         (Phệ Kim Trùng, Đề Hồn Thú...)
│   ├── dau_khi/...
│   ├── dau_la/...
│   ├── than_dong/...
│   ├── kiem_lai/...
│   └── quy_bi/...
└── projects/
    └── project-001/
        └── private_terms.jsonl     (existing)
```

---

### Phase 2: Term Bank Schema Expansion

#### [MODIFY] [term_bank.py](file:///d:/Converter%20by%20DrDuc/src/pipeline/term_bank.py)

**TermBankRecord** — thêm fields mới:

```python
@dataclass(slots=True)
class TermBankRecord:
    # ... existing fields ...
    
    # NEW: Disambiguation fields
    context_markers: list[str]          # Fingerprint terms: ["斗气", "异火"]
    co_occurring_entities: list[str]    # Entities thường đi cùng: ["药尘", "萧薰儿"]
```

**TermBank** — thêm methods mới:

```python
def lookup_with_context(self, source, *, context_window, entity_type) -> list[TermBankRecord]:
    """Disambiguate: nếu có 2+ records cùng source, dùng context_window để rank."""
    
def detect_universe(self, text) -> list[tuple[str, float]]:
    """Detect universe(s) từ text fragment bằng fingerprint + co-occurrence."""
    
def get_universe_glossary(self, universe) -> list[TermBankRecord]:
    """Get all terms for a universe."""

def suggest_enrichment(self, entity: EntitySuggestion, *, context: str) -> TermBankRecord:
    """Pre-fill TermBankRecord template từ scanned entity, ready for user review."""
```

**Universe loader** — mở rộng `_iter_record_files()`:

```python
# Load thêm: data/term_bank/universes/{universe_id}/*.jsonl
```

---

### Phase 3: Universe Detection Algorithm

#### [MODIFY] [entity_scanner.py](file:///d:/Converter%20by%20DrDuc/src/pipeline/entity_scanner.py)

**Thuật toán `detect_universe()`:**

```
Input:  text window (1000-3000 chars)
Output: [(universe_id, confidence_score), ...]

1. FINGERPRINT SCAN
   - Quét text tìm fingerprint terms của mỗi universe
   - Mỗi match = +1 score cho universe đó
   
2. CHARACTER CO-OCCURRENCE
   - Nếu 萧炎 + 药尘 → dau_khi (0.99)
   - Nếu 唐三 + 小舞 → dau_la (0.99)
   - Nếu 韩立 + 南宫婉 → tu_tien (0.99)
   
3. MULTI-UNIVERSE DETECTION (cho Chư Thiên)
   - Nếu detect >= 2 universes với confidence > 0.5
   → CẢ HAI đều active, không merge
   → Entity resolution dùng nearest-context-window

4. FALLBACK
   - Không detect được → tất cả universes inactive
   → Dùng global term bank + Hán Việt mặc định
```

---

### Phase 4: Context-Aware Entity Resolution

#### [MODIFY] [entity_scanner.py](file:///d:/Converter%20by%20DrDuc/src/pipeline/entity_scanner.py)

**Same-Name Cross-Universe Disambiguation:**

```
Scenario: Text chứa cả 萧炎 (Đấu Phá) và nhân vật khác cùng tên khác universe

Algorithm:
1. Pre-scan: detect_universe(full_text) → active_universes
2. For each entity occurrence:
   a. context_window = text[pos-200 : pos+200]
   b. local_universe = detect_universe(context_window)
   c. candidates = term_bank.lookup(source)
   d. IF len(candidates) == 1: use it
   e. IF len(candidates) > 1:
      - Score each candidate by:
        * universe match with local_universe (+3)
        * co_occurring_entities found in context_window (+2 each)
        * context_markers found in context_window (+1 each)
      - Pick highest score
      - IF tie: append [universe_tag] to translation
```

**Resolution Priority Chain:**

```
1. Project-private term bank     (scope=private, highest)
2. Universe-specific term bank   (universe matches detected)
3. Global term bank              (scope=global)
4. Trie dictionary (compiled)
5. Heuristic name mining         (lowest)
```

**Entity types expansion:**

```python
ENTITY_TYPES = {
    "person",       "location",     "organization",
    "realm",        "technique",    "weapon",
    "item",         "title",        "creature",
    "faction",      "term",
}
```

---

### Phase 5: User-Facing Entity Review & Term Bank Enrichment

#### [MODIFY] [entity_scanner.py](file:///d:/Converter%20by%20DrDuc/src/pipeline/entity_scanner.py)

**EntitySuggestion** — thêm fields cho user review:

```python
@dataclass(slots=True)
class EntitySuggestion:
    # ... existing fields ...
    
    # NEW: Review metadata
    universe: str = ""                    # Detected universe
    work: str = ""                        # Detected work
    review_status: str = "pending"        # pending|approved|rejected|saved
    enrichment_ready: bool = False        # True = đủ info để save vào term bank
    suggested_tags: list[str] = field(default_factory=list)
    suggested_context_markers: list[str] = field(default_factory=list)
```

#### [NEW] [entity_enrichment.py](file:///d:/Converter%20by%20DrDuc/src/pipeline/entity_enrichment.py)

Module xử lý workflow enrichment:

```python
class EntityEnrichmentManager:
    """Manages the user-confirmed flow: scan → review → approve → save to term bank."""
    
    def prepare_for_review(self, entities: list[EntitySuggestion], *, detected_universes) -> list[EntitySuggestion]:
        """Điền đầy đủ info, gắn tag, chuẩn bị cho user duyệt."""
    
    def approve_entity(self, entity: EntitySuggestion) -> EntitySuggestion:
        """User duyệt entity → đánh dấu approved."""
    
    def save_to_term_bank(self, entities: list[EntitySuggestion], *, target_scope: str) -> int:
        """User chọn lưu → append vào JSONL file tương ứng. Returns count saved."""
    
    def export_review_report(self, entities: list[EntitySuggestion]) -> str:
        """Export report dạng Markdown cho user review."""
```

#### [MODIFY] [sidecar_bridge.py](file:///d:/Converter%20by%20DrDuc/src/ui/sidecar_bridge.py)

Thêm commands cho UI:

```python
# Entity review commands
"entity_scan_review"         # Scan + trình user duyệt
"entity_approve"             # User approve entity
"entity_reject"              # User reject entity
"entity_save_to_term_bank"   # User chọn lưu vào term bank
"entity_export_report"       # Export report
```

---

## 3. Verification Plan

### Automated Tests

```bash
# Phase 1: Migration
pytest tests/test_md_to_jsonl.py           # Parse 12 MD files → validate JSONL output

# Phase 2-3: Term bank + Universe detection
pytest tests/test_term_bank_universe.py    # detect_universe(), lookup_with_context()

# Phase 4: Context-aware scanning
pytest tests/test_entity_context.py        # Same-name disambiguation

# Phase 5: Enrichment workflow
pytest tests/test_entity_enrichment.py     # Review → approve → save flow

# Regression
pytest tests/test_translation_regressions.py  # Existing tests still pass
```

### Manual Verification

- Lấy sample chương truyện Chư Thiên (có nhân vật multi-universe) → chạy entity scanner → verify
- Kiểm tra canon names: 萧炎→Tiêu Viêm, 唐三→Đường Tam, 韩立→Hàn Lập
- Test enrichment flow: scan → review → approve → save → re-scan confirms persistence

---

## 4. Execution Phases

| Phase | Nội dung | Ước tính |
|-------|----------|----------|
| **Phase 1** | `md_to_jsonl_converter.py` + chạy migration 12 MD + Name_Doithuc | 1 session |
| **Phase 2** | Mở rộng `TermBankRecord` + `TermBank` loader + universe support | 1 session |
| **Phase 3** | `detect_universe()` algorithm + fingerprint data | 1 session |
| **Phase 4** | Context-aware `EntityScanner.scan()` + disambiguation | 1 session |
| **Phase 5** | `EntityEnrichmentManager` + sidecar commands + tests | 1 session |

**Tổng:** 5 phases | ~5 sessions
