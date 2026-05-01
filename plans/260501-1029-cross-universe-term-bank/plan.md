# Plan: Converter-DrDuc Production Hardening v24

Created: 2026-05-01T10:55:00+07:00
Updated: 2026-05-01T17:40:00+07:00
Status: 🟢 Plans Complete — Ready for Execution
Branch: `converter-drduc-v24-production-hardening`

## Overview

Hoàn thiện toàn bộ repo `converter-drduc` theo hướng production-grade, deterministic / non-LLM, có trace, metadata DB, learning loop và regression gate. Bao gồm Cross-Universe Term Bank, Grammar Transfer Planner, Context Resolver, và Learning Loop.

## Tech Stack
- Language: Python 3.11+
- Database: SQLite (trie_cache.db, translation_memory.db), JSONL (term bank)
- Framework: Clean Architecture — core/pipeline/analysis/grammar/entities/context/learning/state/ui
- Test: pytest + regression gate
- UI: Tauri + React + TypeScript (Vite)

## Architecture Principles (A1-A14)

```
A1.  Không viết lại repo từ đầu
A2.  Deterministic-first / non-LLM core
A3.  Python production path là authoritative
A4.  TermBank lookup chạy trước Trie (sequential prepend)
A5.  Machine output không đi thẳng vào approved TM
A6.  Mọi segment đi qua SegmentPacket
A7.  Mọi decision phải có trace
A8.  Protected spans thắng mọi rewrite
A9.  Noise filter dùng hard whitelist trước, scoring sau
A10. Unknown grammar chỉ tạo candidate cần review
A11. Ambiguous entity không inject tag vào bản dịch — chỉ QA flag
A12. Learning loop phải có human review + regression gate
A13. Không promote entity/rule/noise/TM nếu test fail
A14. Mỗi phase phải chạy full regression
```

## Phases — Detailed Plans

| Phase | Name | Priority | Duration | Dep | Status | Detail File |
|-------|------|----------|----------|-----|--------|-------------|
| 00 | Baseline Audit & Repo Housekeeping | P0 | 3-5d | — | ⬜ | [phase-00-audit.md](phase-00-audit.md) |
| 01 | Core Governance: SegmentPacket, TraceEvent, TM Split | P0 | 1-2w | P0 | ⬜ | [phase-01-governance.md](phase-01-governance.md) |
| 02 | Segment Typing, Protected Span, Noise Filter | P0 | 2w | P1 | ⬜ | [phase-02-segment.md](phase-02-segment.md) |
| 03 | Non-LLM Grammar Pattern Scanner | P1 | 1-2w | P2 | ⬜ | [phase-03-grammar-scanner.md](phase-03-grammar-scanner.md) |
| 04 | Cross-Universe Term Bank Data Migration | P1 | 1w | P2 | ⬜ | [phase-04-migration.md](phase-04-migration.md) |
| 05 | Term Bank Schema Expansion | P1 | 1w | P4 | ⬜ | [phase-05-schema.md](phase-05-schema.md) |
| 06 | Universe Detector | P1 | 1w | P5 | ⬜ | [phase-06-detector.md](phase-06-detector.md) |
| 07 | Context-Aware Entity Resolution | P1 | 2w | P6 | ⬜ | [phase-07-resolution.md](phase-07-resolution.md) |
| 08 | Grammar Transfer Planner | P1 | 3w | P3+P7 | ⬜ | [phase-08-grammar.md](phase-08-grammar.md) |
| 09 | Entity Enrichment & User Review | P1 | 1w | P7 | ⬜ | [phase-09-enrichment.md](phase-09-enrichment.md) |
| 10 | Context Resolver, Zero-Pronoun, EAPEE | P1 | 2w | P7+P9 | ⬜ | [phase-10-context.md](phase-10-context.md) |
| 11 | Metadata DB & Learning Loop | P0/P1 | 2w | P1+P8+P9+P10 | ⬜ | [phase-11-learning.md](phase-11-learning.md) |
| 12 | Regression Gate, CI, Performance | P0 | 1w | All | ⬜ | [phase-12-regression.md](phase-12-regression.md) |
| 13 | E2E Integration & Release Candidate | P1 | 1-2w | P12 | ⬜ | [phase-13-release.md](phase-13-release.md) |

**Tổng:** 14 phases | 16-22 tuần

## Milestones

```
v23.5 — Non-LLM Grammar Pattern Mining
v23.6 — Core Governance + TM Split
v23.7 — Segment/Noise Safety
v23.8 — Cross-Universe Entity System
v23.9 — Grammar Transfer Planner
v24.0 — Production Release Candidate
```

## Dependency Graph

```
Phase 00 ──→ Phase 01 ──→ Phase 02 ──┬──→ Phase 03 ──────────────┐
                                      │                            │
                                      └──→ Phase 04 → 05 → 06 → 07 ──┬→ Phase 08
                                                                       │
                                                                       ├→ Phase 09
                                                                       │
                                                                       └→ Phase 10
                                                                              │
Phase 01 + 08 + 09 + 10 ──→ Phase 11 ──→ Phase 12 ──→ Phase 13
```

## Quick Commands
- Start Phase 0: `/code phase-00`
- Check progress: `/next`
- Save context: `/save-brain`

## Reference
- Master Plan: [CONVERTER_DRDUC_MASTER_IMPLEMENTATION_PLAN_V3_COMPLETE.md](CONVERTER_DRDUC_MASTER_IMPLEMENTATION_PLAN_V3_COMPLETE.md)
- Implementation Plan (V2): [implementation_plan.md](implementation_plan.md)
