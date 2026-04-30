# Stitch Prompt: Rebuild UI/UX for Converter by DrDuc

Use this prompt in Stitch to generate a complete UI/UX redesign for the desktop app. The target app is a production translation workspace, not a marketing website.

```text
Design a production-grade desktop UI/UX for "Converter by DrDuc", a non-LLM translation workstation for Chinese web novels to Vietnamese, with a secondary EN -> VI path. The app runs as a Tauri 2 + React desktop shell and talks to a Python sidecar through a versioned JSON command protocol. The design should feel like a serious translator/editor tool: dense, organized, fast to scan, and built for repeated daily work.

Product context:
- Primary users: Vietnamese translators/editors who process long Chinese novel chapters, maintain project-specific terminology, review machine RBMT output, and run QA before publishing.
- Core backend capabilities already exist: project management, document import, chapter split, entity scan, relationship graph, translation config, RBMT translation, annotated draft output, QA reports, dictionary search/edit, candidate entry/rule review, natural feedback learning, grammar scan, pipeline status, and settings/maintenance.
- The desktop app has these command surfaces: create/list/open project, import file/folder, set active chapter, translate, load translation artifacts, run QA, load QA/learning reports, update project config, upsert/delete project entities, suggest entity targets, search/list/update dictionary entries, get pipeline status, run pipeline stage, list/review candidate entries, submit natural feedback, scan grammar learning patterns, list/review candidate rules.
- Protocol response model includes ok/error/warnings/events/generated_at. Every long action should show progress events, warnings, and structured failure states.

Overall UX direction:
- Do not create a landing page, hero page, marketing layout, decorative illustration, or tutorial-heavy interface.
- First screen must be the usable project command center.
- Make the app feel like a professional IDE/editor for translation operations: calm, data-rich, compact, precise.
- Prioritize operational density over decorative cards. Use full-width panels, tables, split panes, drawers, tabs, toolbars, status bars, and inspectors.
- Avoid glassmorphism, gradient orbs, bokeh blobs, oversized hero headings, and one-note beige/teal styling.
- Use a restrained neutral palette with distinct semantic accents: graphite/ink for text, porcelain/off-white surfaces, slate borders, blue for active navigation, green for verified/success, amber for warning/candidate, red for errors/rejected, violet only sparingly for learning/grammar.
- Border radius should be 6-8px for controls and panels. No nested card-on-card composition.
- UI language should be Vietnamese with correct accents. Use concise labels, not long explanatory paragraphs.
- Use icons for actions where standard: import, translate, QA/check, search, filter, save, edit, trash, refresh, settings, warning, success, lock, unlock, terminal/log, database, book/open chapter.
- Text must never overflow controls. Long paths, Chinese text, and Vietnamese translations must wrap or truncate with tooltip behavior.
- Design for desktop first at 1440x900 and 1366x768. Include responsive behavior for 1024px tablet/laptop and narrow 390px mobile preview, but desktop workflow is primary.

Global app shell:
- Left navigation rail, 240px expanded and 64px collapsed. Sections:
  1. Tổng quan
  2. Project & Import
  3. Workspace dịch
  4. Từ điển
  5. Coach & Review
  6. QA & Pipeline
  7. Cài đặt
- Top command bar:
  - Project selector
  - Active chapter selector
  - Workspace root/path indicator
  - Transport badge: Tauri, HTTP, Demo, Browser blocked
  - Protocol version badge
  - Global command status: Ready, Running, Failed
  - Primary quick actions: Import, Dịch, QA, Compile DB
- Bottom status/log strip:
  - last command
  - progress percentage
  - warnings count
  - generated artifact links: clean output, draft, trace, QA
- Provide a right-side collapsible "Command Timeline" drawer with event rows: stage, message, progress, level, payload preview.

Screen 1: Tổng quan / Command Center
- Purpose: see readiness and jump into the next task.
- Layout:
  - Top compact KPI strip: Chapters, Segments, Candidate entries, Candidate rules, QA issues, Dictionary total.
  - Pipeline readiness row with 5 stage chips: Compile dictionary, Import, Translate, QA, Export.
  - Dictionary health section: runtime_total, reference_total, POS coverage ring/bar, Pinyin coverage ring/bar, entity_total, compiled_at.
  - Active project summary: project_id, project_dir, source_language -> target_language, active_chapter.
  - Quick dictionary lookup: search input, 4-6 result rows with source, target_vi, POS badge, entity badge, priority, source_dict.
  - Recent state table: last prepare_seconds, translate_seconds, qa_seconds, source_chars, output_chars, candidate_entries_added.
- Empty state: if no project, show a compact create/open project form, not a marketing hero.

Screen 2: Project & Import
- Purpose: create/open project, import source file/folder, choose active chapter.
- Layout:
  - Project list table on the left: project_id, language pair, active chapter, updated status, path.
  - Project detail inspector on the right: directory, artifact paths, counts, runtime stats.
  - Import panel: file/folder path input, native picker buttons, supported formats (.txt, .md, .html, .docx, .pdf), import/prepare button.
  - Chapter table below: chapter_id, title, char count, source_path, translated status, QA issue count. Selecting a row sets active chapter.
  - Import result summary: raw path, chapters created, entities found, relationships found, config path, warnings.
- States: import running, import failed with recoverable bad files, no chapters yet, selected chapter loaded.

Screen 3: Workspace dịch
- Purpose: translate and review a chapter with evidence.
- Layout must use split panes:
  - Left pane: chapter/segment list with status markers, segment_id, source preview, fallback level, QA marker.
  - Center pane: synchronized editor with Source Chinese text and Clean Vietnamese output side by side. Both need fixed-height scrollable text panes.
  - Bottom/secondary pane: Annotated draft output with ambiguity markers.
  - Right inspector drawer: selected segment details, trace evidence, entity override editor, target suggestions, QA issues for selected segment.
- Toolbar:
  - Dịch active chapter
  - Chạy QA
  - Save project config
  - Add locked entity
  - Inspect token in dictionary
- Trace evidence component:
  - Show source token, selected target, candidates, fallback_level, priority, reason, confidence when available.
  - Fallback levels should have distinct badges: grammar_transfer, project_entity, runtime, tm_approved_exact, tm_approved_fuzzy, tm_machine_suggestion, number, pinyin, han_viet, unresolved.
- Entity workflow:
  - User can select text in source or output to prefill entity draft.
  - Entity draft fields: source, target, entity_type, source_dict, confidence, count, ambiguity_flag, sync to locked_entities.
  - Suggested targets chips: Hán Việt, Latin dictionary, existing dictionary, project entity.
- QA inline behavior:
  - QA issues should be visible as row markers and in inspector, not hidden on a separate page only.

Screen 4: Từ điển / Dictionary Studio
- Purpose: search, filter, edit, and bulk update the dictionary.
- Layout:
  - Top filter toolbar: query, table scope, source_dict, POS tag, entity_type, status, priority range, only locked, only LuatNhan trigger.
  - Main table: checkbox, source, target_vi, POS badge, POS sub, entity_type, priority, source_dict, status, hit_count, pinyin availability, Hán Việt availability.
  - Right detail inspector for selected entry:
    - source, target_vi, alternative_meanings, full_explanation, pinyin, han_viet_readings, traditional, source_file, source_path, notes, metadata JSON.
    - editable metadata: priority, pos_tag, pos_sub, entity_type, reorder_role, cultural_origin, genre_affinity, register_level, luat_nhan_trigger.
  - Bulk action bar: set POS, set entity type, export filtered, compile dictionary DB.
  - Pagination or virtualized list behavior with clear total count.
- Visual requirements:
  - This screen is table-first, not card-first.
  - Chinese and Vietnamese text must be readable at row density.
  - Use colored POS/entity badges but keep table quiet.

Screen 5: Coach & Review
- Purpose: human-in-the-loop learning, candidate review, natural feedback, grammar scan.
- Layout:
  - Left column: natural feedback form with scope (chapter/project), rule type hint, feedback text, source snippet, current translation, preferred translation.
  - Middle column: generated suggestions from feedback with confidence, rule_type, summary, payload preview.
  - Right column: learning timeline and grammar scan summary: qa_total, recommendations, auto_applied, unknown_candidate_count, total_matches.
  - Bottom tabs:
    1. Candidate entries
    2. Candidate rules
    3. Grammar pattern candidates
  - Candidate entry rows show source_text, target_text, status, fallback_level, reason, chapter_id, segment_id, candidates list.
  - Candidate rule rows show title, summary, rule_type, status, payload preview, created_at/updated_at.
  - Actions: Verify, Reject, Apply, Open in dictionary, Inspect segment.
- States:
  - Candidate, verified, rejected badges.
  - Clear disabled states when backend unavailable or busy.

Screen 6: QA & Pipeline
- Purpose: quality control and operational monitoring.
- Layout:
  - Pipeline stepper at top with stage cards: compile, import, translate, qa, export, assign_pos, scan_grammar.
  - QA report table: severity, checker, segment_id, message, linked source/target preview, action to jump to workspace.
  - Warnings panel: warning text, command, time.
  - Event log panel: progress events from sidecar, newest first, filter by level/stage.
  - Artifacts panel: clean path, draft path, trace path, QA JSON/Markdown paths, learning report path.
  - Dictionary compile status panel: compiled_at, source manifest stale/fresh, total entries.
- Make this screen good for diagnosing failed pipeline runs.

Screen 7: Cài đặt
- Purpose: environment, transport, maintenance, and paths.
- Layout:
  - Environment panel: protocol version, transport mode, workspace root, active project, Python sidecar status, Tauri/HTTP/Demo mode.
  - Path settings: workspace project root, dictionary root, compiled DB path, artifact base.
  - Maintenance actions: Compile dictionary DB, Run POS seeder, Export artifacts, Refresh pipeline status, Open logs.
  - Danger zone: clear local UI cache, reset selected project, rebuild ignored compiled cache. Use confirmation states.
  - Show structured error detail when commands fail: error string, command, request_id, protocol_version, warnings, events.

Important interaction patterns:
- Every command button should have loading and disabled states.
- Long-running commands show progress in the bottom status strip and command timeline.
- If backend transport is Browser only, disable real commands and show "Cần Tauri hoặc HTTP bridge" as an operational status, not a modal.
- Prefer drawers/inspectors over pop-up modals.
- Use tabs for subviews inside large workflows, not separate pages for every detail.
- Use segmented controls for mode switches.
- Use checkboxes/toggles for binary config such as sync_locked.
- Use compact badges for status, fallback level, POS, entity type, severity.
- Use destructive styling only for delete/reject actions.

Content rules:
- Use Vietnamese UI copy with correct accents.
- Avoid long instructional paragraphs in the app. Tooltips are allowed for unfamiliar icons.
- Do not display fake marketing text.
- Use sample data that reflects the app:
  - Project: "hong-hoang-lich"
  - Language: zh -> vi
  - Chapter: "chapter-001 - Hắc Dạ Chi Tâm"
  - Source sample: "林动走进房间。看到桌上有一封信。"
  - Clean output sample: "Lâm Động bước vào phòng. Hắn thấy trên bàn có một phong thư."
  - Dictionary entry sample: source "林动", target_vi "Lâm Động", pinyin "lin dong", entity_type "person", priority 95.
  - Candidate sample: source_text "小白", target_text "Tiểu Bạch", fallback_level "han_viet", status "candidate".
  - QA issue sample: severity "warning", checker "pronoun", message "Đại từ có thể chưa nhất quán với relationship graph."

Deliverables from Stitch:
- High-fidelity visual design for all seven screens.
- Component inventory: nav rail, top command bar, status strip, panel, data table, split editor, inspector drawer, command timeline, pipeline stepper, badge, toast/error state, empty state.
- At least one desktop full-screen mockup for each screen.
- Include responsive notes for 1024px and 390px widths.
- Keep implementation realistic for React/Tauri: CSS grid/flex layouts, no heavy 3D, no decorative canvases, no external backend assumptions.
```
