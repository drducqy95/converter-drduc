# Phase 03: TrieNode/TrieMatch Enhancement

Status: ⬜ Pending
Dependencies: Phase 01 (schema), Phase 02 (POS data seeded)

## Objective
Mở rộng `TrieNode` và `TrieMatch` để mang POS metadata từ SQLite lên runtime, cho phép engine ra quyết định ngữ pháp dựa trên từ loại.

## Implementation Steps

### 1. [ ] Extend `TrieNode.__slots__`

```python
class TrieNode:
    __slots__ = [
        'children', 'target', 'priority', 'one_mean', 'is_end',
        # Phase 09 metadata
        'pos_tag',           # str | None — "VERB", "NOUN", "ADJ", ...
        'is_function_word',  # bool — 的, 了, 着, 把, 被
        'reorder_role',      # str | None — "modifier", "head", "complement"
        'entity_type',       # str | None — "person", "location", "org"
    ]
```

**Memory impact**: +4 pointers per **leaf node** (only `is_end=True` nodes store data). Với 724K leaf entries (not all Trie nodes):
- Hiện tại: 5 slots × 8 bytes = 40 bytes/leaf + dict overhead
- Sau: 9 slots × 8 bytes = 72 bytes/leaf
- Tăng thêm: ~724K × 32 bytes = **~23 MB** thêm
- Non-leaf nodes: không bị ảnh hưởng (`__init__` gán None cho các slots mới)

> [!NOTE]
> Các non-leaf nodes vẫn có `__slots__` mới nhưng giá trị là `None` (8 bytes/pointer), chấp nhận được.

### 2. [ ] Extend `TrieMatch` dataclass

```python
@dataclass
class TrieMatch:
    source: str
    target: str
    priority: int
    length: int
    one_mean: bool
    # NEW — Phase 09
    pos_tag: str | None = None
    is_function_word: bool = False
    reorder_role: str | None = None
    entity_type: str | None = None
```

### 3. [ ] Update `load_from_sqlite` to read POS columns

```python
c.execute("""
    SELECT source, target, priority, one_mean, category,
           pos_tag, is_function_word, reorder_role, entity_type
    FROM entries ORDER BY priority ASC
""")
```

### 4. [ ] Update `insert()` to accept and store POS data

```python
def insert(self, source, target, priority=2, one_mean=False,
           pos_tag=None, is_function_word=False, 
           reorder_role=None, entity_type=None):
    ...
    node.pos_tag = pos_tag
    node.is_function_word = is_function_word
    node.reorder_role = reorder_role
    node.entity_type = entity_type
```

### 5. [ ] Update `lookup()` and `lookup_exact()` to return POS in TrieMatch

```python
best_match = TrieMatch(
    source=text[pos:i+1],
    target=target,
    priority=node.priority,
    length=i - pos + 1,
    one_mean=node.one_mean,
    pos_tag=node.pos_tag,
    is_function_word=node.is_function_word,
    reorder_role=node.reorder_role,
    entity_type=node.entity_type,
)
```

## Files to Modify
- `src/core/trie_engine.py` — TrieNode, TrieMatch, insert, load_from_sqlite, lookup

## Test Criteria
- [ ] `TrieMatch.pos_tag` returns correct value for seeded entries
- [ ] Performance benchmark: lookup speed ≤ 5% regression
- [ ] Memory usage: ≤ 20% increase from current baseline
- [ ] `trie.lookup_exact("穿").pos_tag == "VERB"`
- [ ] `trie.lookup_exact("的").is_function_word == True`
- [ ] `trie.lookup_exact("大").reorder_role == "modifier"`
- [ ] `trie.lookup_exact("男子").reorder_role == "head"`
- [ ] Entries without POS return `pos_tag=None` (not crash)

## Benchmark Script

```python
# tools/benchmark_trie_pos.py
import time, tracemalloc
from src.core.trie_engine import TrieEngine

# Memory measurement
tracemalloc.start()
trie = TrieEngine()
stats = trie.load_from_sqlite('data/dictionaries/_compiled/trie_cache.db')
mem_current, mem_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"Memory: current={mem_current/1024/1024:.1f}MB, peak={mem_peak/1024/1024:.1f}MB")

# Speed benchmark
test_words = ["修为", "突破", "境界", "灵气", "丹田", "练丹", "一个人", "天地", "大道", "太阳"]
start = time.perf_counter()
for _ in range(10_000):
    for w in test_words:
        trie.lookup_exact(w)
elapsed = time.perf_counter() - start
print(f"100K lookups: {elapsed:.3f}s ({elapsed/100_000*1e6:.1f} µs/lookup)")
```

---
Next Phase: [phase-04-pos-rewrite-engine.md](phase-04-pos-rewrite-engine.md)
