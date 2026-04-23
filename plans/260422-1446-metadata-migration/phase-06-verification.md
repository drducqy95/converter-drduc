# Phase 06: Verification & Regression Testing

Status: ⬜ Pending
Dependencies: Phase 05 (integration complete)

## Objective
Xác nhận rằng hệ thống metadata-enriched engine tạo ra output bằng hoặc tốt hơn legacy regex engine trên tất cả 5 chương đã dịch.

## Implementation Steps

### 1. [ ] Create regression test suite

```python
# tests/test_pos_regression.py
REGRESSION_CASES = [
    ("穿黑色风衣的男子", "nam tử mặc áo gió màu đen"),
    ("惨白腐烂的双手", "song thủ thảm bạch hủ lan"),
    ("这两个死党", "hai cái tử đảng này"),
    ("发疯似的", "như phát điên"),
    ("在课桌下面摸找着", "摸找着在课桌下面"),
    ("你妈妈才把你给抓", "mẹ ngươi mới bắt ngươi"),
    ("被一下咬断", "bị cắn đứt"),
    ("40多岁", "hơn 40 tuổi"),
    ("这时门外", "lúc này ngoài cửa"),
]
```

### 2. [ ] Batch translate Chapters 1-5 with both engines

```powershell
# Legacy engine
python run_full_pipeline.py --engine legacy --output output_legacy/

# POS engine  
python run_full_pipeline.py --engine pos --output output_pos/

# Diff comparison
python tools/diff_translations.py output_legacy/ output_pos/
```

### 3. [ ] Quality metrics comparison

| Metric | Legacy | POS Engine | Target |
|--------|--------|------------|--------|
| QA Issues (avg/chapter) | ? | ? | ≤ legacy |
| Untranslated CJK chars | ? | ? | ≤ legacy |
| AMBIG annotations | ? | ? | ≤ legacy |
| Sentence order accuracy | ? | ? | ≥ legacy |
| Translation speed (s/chapter) | ? | ? | ≤ 2x legacy |

### 4. [ ] Performance benchmark

```python
# Benchmark: translate 1000 sentences
import time
sentences = load_test_sentences()
start = time.time()
for s in sentences:
    engine.translate(s)
elapsed = time.time() - start
print(f"POS Engine: {elapsed:.2f}s for {len(sentences)} sentences")
```

### 5. [ ] Push to GitHub & update project state

```powershell
git add -A
git commit -m "feat: Phase 09 - Metadata-enriched dictionary with POS-driven grammar engine"
git push origin main
```

Update `project_progress.json`:
```json
{
    "id": "T1.9",
    "desc": "Phase 09 - Metadata Dictionary & POS Engine",
    "status": "DONE",
    "progress": 100,
    "details": "..."
}
```

## Files to Create
- `tests/test_pos_regression.py` — **[NEW]** regression tests
- `src/tools/diff_translations.py` — **[NEW]** output comparison
- `reports/pos_migration_report.md` — **[NEW]** final report

## Test Criteria
- [ ] All 9 regression cases PASS
- [ ] Chapter 1-5 QA issues ≤ legacy count
- [ ] No new untranslated CJK characters
- [ ] Performance within 2x of legacy speed
- [ ] Git push successful

---
**Migration Complete! 🎉**
