# Phase 01: Schema Design & Migration

Status: ⬜ Pending
Dependencies: None (non-breaking, additive only)

## Objective
Mở rộng schema SQLite và Markdown dictionary format để chứa metadata POS, morphology, và context — **KHÔNG** phá vỡ runtime hiện tại.

## Implementation Steps

### 1. [ ] Design enhanced `entries_v2` schema

> [!IMPORTANT]
> `md_dictionary_compiler.py` **luôn xóa và tạo lại** `trie_cache.db` mỗi lần compile (`_remove_existing_db_with_retry()`). Do đó KHÔNG cần `ALTER TABLE` — chỉ cần sửa `CREATE TABLE` DDL trong compiler.

Thêm các cột mới vào `CREATE TABLE entries` trong compiler:

```sql
CREATE TABLE entries (
    source TEXT PRIMARY KEY,
    target TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 2,
    category TEXT DEFAULT '',
    one_mean INTEGER DEFAULT 0,
    locked INTEGER DEFAULT 0,
    -- ═══ EXISTING ═══
    notes TEXT DEFAULT '',
    source_file TEXT DEFAULT '',
    source_language TEXT DEFAULT 'zh',
    target_language TEXT DEFAULT 'vi',
    entry_role TEXT DEFAULT 'translation',
    metadata_json TEXT DEFAULT '',
    -- ═══ NEW: Phase 09 Metadata ═══
    pos_tag TEXT DEFAULT NULL,           -- VERB, NOUN, ADJ, ...
    pos_sub TEXT DEFAULT NULL,           -- transitive, separable, color, ...
    entity_type TEXT DEFAULT NULL,       -- person, location, organization
    is_function_word INTEGER DEFAULT 0,  -- 的, 了, 着, 把, 被
    luat_nhan_trigger INTEGER DEFAULT 0, -- triggers grammar pattern
    reorder_role TEXT DEFAULT NULL,      -- modifier, head, complement, marker
    cultural_origin TEXT DEFAULT NULL,   -- han_viet, modern_cn
    genre_affinity TEXT DEFAULT NULL,    -- JSON: ["xianxia","wuxia"]
    register_level TEXT DEFAULT NULL     -- formal, informal, literary
);
```

**POS Tag Taxonomy (16 loại):**

| Tag | Tên Việt | Subtypes | Ví dụ |
|-----|----------|----------|-------|
| `NOUN` | Danh từ | concrete, abstract, proper | 风衣, 墓碑, 教室 |
| `VERB` | Động từ | transitive, intransitive, stative, separable | 穿, 跑, 吃, 生气 |
| `ADJ` | Tính từ | scalar, color, evaluative | 大, 白, 好 |
| `ADV` | Trạng từ | degree, time, manner, frequency | 很, 非常, 已经 |
| `PRON` | Đại từ | personal, demonstrative, interrogative | 我, 这, 谁 |
| `PREP` | Giới từ | locative, directional, passive, ba | 在, 从, 被, 把 |
| `CONJ` | Liên từ | coordinating, subordinating | 和, 但是, 除了 |
| `PART` | Trợ từ | structural, aspect, modal | 的, 了, 着, 吗 |
| `CLF` | Lượng từ | general, specific | 个, 座, 块 |
| `NUM` | Số từ | cardinal, ordinal | 一, 第一 |
| `IDIOM` | Thành ngữ | chengyu, xiehouyu | 九死一生 |
| `COMP` | Bổ ngữ | resultative, potential, directional | 出来, 起来, 下去 |
| `SUFFIX` | Hậu tố | simulative, approximative | 似的, 一样, 一般 |
| `LOC` | Phương vị từ | spatial | 上, 下, 里, 外, 前, 后 |
| `INTJ` | Thán từ | | 啊, 哦, 嗯 |
| `AUX` | Trợ động từ | modal, ability | 会, 能, 可以, 要 |

### 2. [ ] Update `md_dictionary_compiler.py`
- Parse new columns from Markdown tables: `pos_tag`, `pos_sub`, `entity_type`, etc.
- Write to enhanced SQLite schema
- Backward-compatible: missing columns → NULL defaults

### 3. [ ] Update Markdown dictionary format spec
Thêm columns vào bulk MD tables:
```markdown
| source | target | pos_tag | pos_sub | reorder_role | notes |
```

### 4. [ ] Create migration script `tools/migrate_schema.py`
- `ALTER TABLE` for existing `trie_cache.db`
- Idempotent (safe to run multiple times)
- Logs migration status

### 5. [ ] Add `reorder_role` classification logic
Define reorder_role values với concrete mapping:

| reorder_role | POS Tags áp dụng | Ý nghĩa trong đảo cấu trúc | Ví dụ |
|--------------|-------------------|----------------------------|-------|
| `"modifier"` | VERB, ADJ, ADV | Phần bổ nghĩa đứng trước 的 | 穿(modifier), 惨白(modifier) |
| `"head"` | NOUN | Danh từ trung tâm nhận modifier | 男子(head), 双手(head) |
| `"complement"` | COMP | Bổ ngữ kết quả/xu hướng/khả năng | 出来(complement), 起来(complement) |
| `"marker"` | PART | Trợ từ cấu trúc (bản lề đảo) | 的(marker), 了(marker) |
| `"connector"` | PREP, CONJ | Giới từ/liên từ liên kết cụm | 在(connector), 从(connector) |
| `"quantifier"` | NUM, CLF | Nhóm số-lượng từ | 两(quantifier), 座(quantifier) |
| `"demonstrative"` | PRON(dem) | Chỉ thị từ cần đẩy ra cuối | 这(demonstrative), 那(demonstrative) |

> Mỗi entry có thể có reorder_role = NULL nếu POS chưa được seed hoặc vai trò chưa xác định.

### 6. [ ] Verify backward compatibility
Run existing pipeline → output must be IDENTICAL to pre-migration.

## Files to Create/Modify
- `src/core/md_dictionary_compiler.py` — Extended parsing + schema
- `src/tools/migrate_schema.py` — **[NEW]** migration script
- `data/dictionaries/global/vietphrase/*.md` — Format spec update

## Test Criteria
- [ ] `ALTER TABLE` runs without errors
- [ ] Existing pipeline output identical (regression)
- [ ] New columns readable via `SELECT pos_tag FROM entries`

---
Next Phase: [phase-02-pos-seeding.md](phase-02-pos-seeding.md)
