# Phase 03: Non-LLM Grammar Pattern Scanner

Status: ⬜ Pending
Priority: P1
Duration: 1-2 tuần
Dependencies: Phase 02

## Objective
Quét file txt nguồn thống kê dạng ngữ pháp đã biết và phát hiện candidate chưa biết — hoàn toàn non-LLM.

## Tasks

### P3-T1 — Tạo analysis package
```
src/analysis/
  __init__.py
  txt_corpus_reader.py
  grammar_pattern_registry.py
  grammar_pattern_scanner.py
  unknown_pattern_miner.py
  grammar_stats.py
  grammar_reporter.py
  backlog_generator.py
```

### P3-T2 — Known GrammarPatternScanner
Config: `data/grammar/grammar_patterns.yml`
Nhóm rules:
```
condition: 如果...就, 只要...就, 一旦...就, 除非...否则
concession: 虽然...但是, 即便...也, 哪怕...也, 就算...也
passive: 被, 为...所, 被...所
disposal: 把
viewpoint: 作为, 对X而言
parallel: 一边...一边, 边...边
definition: 所谓, 也就是说, 换言之
minimizing: 罢了, 而已
evidential: 据说, 据X称
comparison: 相比之下, 与X相比
precaution: 以防, 以防万一
emphatic: 就连...也, 连...都
enumeration: 一来...二来, 其一...其二
necessity: 非...不可, 非...莫属
```

### P3-T3 — UnknownGrammarPatternMiner
Phương pháp phát hiện:
1. Marker mining
2. Paired-marker mining
3. N-gram mining
4. Frame-template mining
5. Clause anomaly mining
6. Residual-unmatched analysis

Output format:
```json
{
  "candidate_id": "unknown_xxx",
  "pattern_text": "与其...不如",
  "pattern_type": "paired_marker",
  "frequency": 37,
  "confidence": 0.86,
  "guessed_category": "preference",
  "status": "review"
}
```

### P3-T4 — CLI script
```bash
python scripts/scan_grammar_patterns.py \
  --input data/corpus/source.txt \
  --patterns data/grammar/grammar_patterns.yml \
  --out-dir reports/grammar_scan/ \
  --unknown-min-count 5
```

### P3-T5 — Export reports
- [ ] grammar_stats.json / .csv
- [ ] grammar_report.md
- [ ] rule_backlog.json

## Files to Create/Modify
- `src/analysis/*.py` — [NEW] 7 modules
- `data/grammar/grammar_patterns.yml` — [NEW]
- `data/grammar/unknown_marker_seed.yml` — [NEW]
- `scripts/scan_grammar_patterns.py` — [NEW]

## Definition of Done
```
[ ] Scanner không dùng LLM
[ ] Known patterns được thống kê
[ ] Unknown candidates xuất review (không tự promote — A10)
[ ] Không scan trong protected spans (A8)
[ ] Có JSON/CSV/Markdown report
```

---
Next Phase: Phase 04 — Term Bank Data Migration
