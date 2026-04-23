# Phase 05: Integration & Legacy Migration

Status: ⬜ Pending
Dependencies: Phase 04 (POS rewrite engine working)

## Objective
Tích hợp `POSRewriteEngine` vào `RBMTTranslator._translate_sentence`, migrate `PronounResolver` và `CulturalOriginDetector` sang metadata-driven, và dần loại bỏ `zh_structure_rewriter.py`.

## Implementation Steps

### 1. [ ] Integrate POS tokenization into `_translate_sentence`

**Hiện tại**: `rewrite_chinese_structure(sentence)` → regex trên raw text
**Mới**: Pre-tokenize sentence via Trie → get POS tokens → `POSRewriteEngine.rewrite(tokens)` → translate reordered tokens

```python
def _translate_sentence(self, sentence, config, ...):
    # Step 1: Pre-tokenize (Trie longest-match to get POS tokens)
    tokens = self._pre_tokenize(sentence)
    
    # Step 2: POS-driven rewriting (if sufficient POS coverage)
    pos_coverage = sum(1 for t in tokens if t.pos_tag) / max(len(tokens), 1)
    if pos_coverage >= 0.6:  # ≥ 60% tokens have POS
        tokens = self.pos_rewrite_engine.rewrite(tokens)
    else:
        # Fallback to legacy regex
        sentence = rewrite_chinese_structure(sentence)
        tokens = self._pre_tokenize(sentence)  # re-tokenize
    
    # Step 3: Translate tokens
    for token in tokens:
        result_parts.append(token.target)
    
    # Step 4: Vietnamese post-processing (keep existing)
    text = rewrite_vietnamese_grammar(text)
```

#### `_pre_tokenize()` Method Design

```python
def _pre_tokenize(self, text: str) -> list[TrieMatch]:
    """Tokenize Chinese text into TrieMatch sequence via longest-prefix.
    
    This is NOT translation — it's structural analysis.
    Each token carries POS metadata from the Trie.
    Unmatched CJK chars become single-char tokens with pos_tag=None.
    """
    tokens = []
    i = 0
    while i < len(text):
        match = self.trie.lookup(text, i)
        if match:
            tokens.append(match)
            i += match.length
        else:
            ch = text[i]
            tokens.append(TrieMatch(
                source=ch, target=ch,
                priority=0, length=1, one_mean=False,
                pos_tag=None, is_function_word=False,
                reorder_role=None, entity_type=None,
            ))
            i += 1
    return tokens
```

> [!WARNING]
> `_pre_tokenize()` dùng cùng Trie lookup nhưng KHÔNG translate. Nó chỉ tạo token sequence để POS engine phân tích cấu trúc.

### 2. [ ] Migrate `PronounResolver` to use metadata
Instead of hardcoded pronoun matrix, use `genre_affinity` and `register_level` from entries:

```python
# Before: separate hardcoded dict
# After: query entry metadata
entry = trie.lookup_exact("我")
if entry and entry.pos_tag == "PRON":
    genre = config.get("genre_hints", ["general"])[0]
    # Use genre_affinity from metadata to select translation
```

### 3. [ ] Migrate `CulturalOriginDetector` to metadata
Replace keyword heuristics with `cultural_origin` field from entries:

```python
# Before: scan text for fixed markers
# After: aggregate cultural_origin from matched tokens
origins = [t.cultural_origin for t in tokens if t.cultural_origin]
dominant = Counter(origins).most_common(1)[0][0]
```

### 4. [ ] Establish fallback strategy
Run both engines in parallel during migration:

```python
def _translate_sentence(self, sentence, config, ...):
    pos_tokens = self._pre_tokenize(sentence)
    
    if all(t.pos_tag for t in pos_tokens):
        # POS coverage sufficient → use new engine
        tokens = self.pos_rewrite_engine.rewrite(pos_tokens)
    else:
        # Fallback → legacy regex rewriter
        sentence = rewrite_chinese_structure(sentence)
```

### 5. [ ] Deprecate `zh_structure_rewriter.py`
Gradual deprecation timeline:

| Stage | Condition | Action |
|-------|-----------|--------|
| **Coexist** | POS coverage < 60% | Legacy regex runs, POS engine disabled |
| **Shadow** | POS coverage ≥ 60% | POS engine runs, output compared (not used) |
| **Primary** | POS parity verified | POS engine produces output, legacy = fallback |
| **Sole** | Phase 06 PASS | Legacy moved to `_legacy/`, warning logged |

File operations:
- Move to `src/engine/_legacy/zh_structure_rewriter.py`
- Log warning when fallback is triggered
- Target removal after Phase 06 verification PASS

## Files to Modify
- `src/engine/rbmt_translator.py` — Integration point
- `src/eapee/pronoun_resolver.py` — Metadata migration
- `src/engine/cultural_origin_detector.py` — Metadata migration
- `src/engine/zh_structure_rewriter.py` — Deprecation path

## Test Criteria
- [ ] Both engines produce equivalent output on Chapter 1-5
- [ ] Fallback triggers ≤ 10% of sentences (target: 0%)
- [ ] No regression from existing translations
- [ ] PronounResolver uses metadata when available
- [ ] CulturalOriginDetector uses metadata when available

---
Next Phase: [phase-06-verification.md](phase-06-verification.md)
