import {
  PROTOCOL_VERSION,
  type CandidateEntry,
  type CandidateRule,
  type ChapterInfo,
  type CommandEvent,
  type CommandName,
  type CommandResponse,
  type DictionaryEntry,
  type LearningReport,
  type NaturalFeedbackAnalysis,
  type PipelineStatus,
  type ProjectOverview,
  type ProjectRecord,
  type QAReport,
  type Transport,
  type TranslationArtifacts,
  type TranslationSegment,
  type TranslationTrace,
} from "./protocol";

type DemoProject = {
  project: ProjectRecord;
  state: Record<string, unknown>;
  chapters: ChapterInfo[];
  entities: Array<Record<string, unknown>>;
  relationships: Array<Record<string, unknown>>;
  terminologySuggestions: Array<Record<string, unknown>>;
  config: Record<string, unknown>;
  translation: TranslationArtifacts | null;
  qaReport: QAReport | null;
  candidates: CandidateEntry[];
  nextCandidateId: number;
  candidateRules: CandidateRule[];
  nextRuleId: number;
  learningReport: LearningReport | null;
};

const SUPPORTED_COMMANDS: CommandName[] = [
  "create_project",
  "list_projects",
  "open_project",
  "get_project_overview",
  "set_active_chapter",
  "set_translation_style",
  "import_file",
  "translate",
  "load_translation_artifacts",
  "run_qa",
  "load_qa_report",
  "load_learning_report",
  "update_project_translation_config",
  "upsert_project_entity",
  "delete_project_entity",
  "delete_project_entities",
  "suggest_entity_targets",
  "search_dictionary_entries",
  "list_dictionary_entries",
  "update_dictionary_entry",
  "get_pipeline_status",
  "run_pipeline_stage",
  "list_candidate_entries",
  "review_candidate_entry",
  "submit_natural_feedback",
  "scan_grammar_learning_patterns",
  "list_candidate_rules",
  "review_candidate_rule",
];

const SAMPLE_SOURCE = "林动说道：“浪漫！”";

export function createDemoTransport(): Transport {
  const projects = new Map<string, DemoProject>();
  const seeded = createSeedProject();
  projects.set(seeded.project.project_id, seeded);

  return {
    mode: "demo",
    supportedCommands: SUPPORTED_COMMANDS,
    async send<T>(
      command: CommandName,
      payload: Record<string, unknown> = {},
    ): Promise<CommandResponse<T>> {
      await delay(110);
      const requestId = `demo-${Date.now()}`;
      const events: CommandEvent[] = [
        makeEvent("received", `Demo backend received ${command}`, 10),
      ];

      try {
        switch (command) {
          case "list_projects": {
            const data = {
              projects: Array.from(projects.values()).map((item) => clone(item.project)),
              supported_commands: SUPPORTED_COMMANDS,
            };
            events.push(makeEvent("projects_loaded", "Loaded demo projects", 100));
            return makeResponse(command, requestId, data as T, events);
          }
          case "create_project": {
            const projectId = asString(payload.project_id, "demo-project");
            const baseDir = asString(payload.base_dir, "demo://workspace");
            const project = createBlankProject(projectId, baseDir);
            projects.set(projectId, project);
            events.push(makeEvent("project_created", `Created ${projectId}`, 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              project_dir: project.project.project_dir,
              project: clone(project.project),
              overview: buildOverview(project),
            } as T, events);
          }
          case "open_project":
          case "get_project_overview": {
            const project = ensureProject(projects, payload);
            events.push(makeEvent("project_loaded", `Loaded ${project.project.project_id}`, 100));
            return makeResponse(command, requestId, buildOverview(project) as T, events);
          }
          case "set_active_chapter": {
            const project = ensureProject(projects, payload);
            const chapterId = asString(payload.chapter_id, project.project.active_chapter ?? "chapter-001");
            project.project.active_chapter = chapterId;
            project.state.active_chapter = chapterId;
            events.push(makeEvent("chapter_selected", `Selected ${chapterId}`, 100));
            return makeResponse(command, requestId, buildOverview(project) as T, events);
          }
          case "set_translation_style": {
            const project = ensureProject(projects, payload);
            if (typeof payload.style_profile === "string" && payload.style_profile) {
              project.config.style_profile = payload.style_profile;
            }
            if (payload.naturalization && typeof payload.naturalization === "object") {
              project.config.naturalization = clone(payload.naturalization as Record<string, unknown>);
            }
            if (payload.style_context && typeof payload.style_context === "object") {
              project.config.style_context = clone(payload.style_context as Record<string, unknown>);
            }
            events.push(makeEvent("style_updated", "Updated demo style preferences", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              chapter_id: project.project.active_chapter,
              config: clone(project.config),
              effective_style: {
                effective_profile: project.config.style_profile ?? "balanced_novel",
                effective_context: clone(project.config.style_context ?? {}),
                naturalization: clone(project.config.naturalization ?? {}),
              },
              overview: buildOverview(project),
            } as T, events);
          }
          case "import_file": {
            const project = ensureProject(projects, payload);
            const filepath = asString(payload.filepath, "demo://source/chapter.md");
            hydrateImportedProject(project, filepath);
            events.push(makeEvent("import_completed", "Prepared pre-translation artifacts", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              project_dir: project.project.project_dir,
              chapters: clone(project.chapters),
              entities: clone(project.entities),
              relationships: clone(project.relationships),
              config: clone(project.config),
              overview: buildOverview(project),
            } as T, events);
          }
          case "translate": {
            const project = ensureProject(projects, payload);
            if (!project.chapters.length) {
              hydrateImportedProject(project, "demo://source/chapter.md");
            }
            const chapterId = asNullableString(payload.chapter_id) ?? project.project.active_chapter ?? "chapter-001";
            project.project.active_chapter = chapterId;
            project.state.active_chapter = chapterId;
            const config = (payload.config as Record<string, unknown>) ?? project.config;
            const sourceText = asString(payload.text, getActiveChapter(project)?.text ?? SAMPLE_SOURCE);
            const translation = generateTranslationArtifacts(project, chapterId, sourceText, config);
            project.translation = translation;
            project.candidates = extractCandidates(translation, project.nextCandidateId);
            project.nextCandidateId = project.candidates.reduce((maxId, item) => Math.max(maxId, item.id + 1), project.nextCandidateId);
            project.state.last_translation = {
              chapter_id: chapterId,
              segments: translation.segments.length,
              candidate_entries_added: project.candidates.length,
            };
            events.push(makeEvent("translation_completed", "Generated translation artifacts", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              project_dir: project.project.project_dir,
              chapter_id: chapterId,
              clean_text: translation.clean_text,
              draft_text: translation.draft_text,
              segments: translation.segments.length,
              candidate_entries_added: project.candidates.length,
              translation_artifacts: clone(translation),
              overview: buildOverview(project),
            } as T, events);
          }
          case "load_translation_artifacts": {
            const project = ensureProject(projects, payload);
            events.push(makeEvent("artifacts_loaded", "Loaded translation artifacts", 100));
            return makeResponse(
              command,
              requestId,
              clone(project.translation ?? emptyTranslation(project.project.project_id, project.project.active_chapter)) as T,
              events,
            );
          }
          case "run_qa": {
            const project = ensureProject(projects, payload);
            const translation = project.translation ?? emptyTranslation(project.project.project_id, project.project.active_chapter);
            project.qaReport = generateQAReport(translation);
            project.learningReport = {
              chapter_id: project.project.active_chapter,
              current_run: {
                qa_total: project.qaReport.summary.issues,
                runtime_metrics: {
                  translate_seconds: 1.9,
                },
              },
              recommendations: project.qaReport.summary.issues > 0
                ? [{ type: "demo", message: "Review ambiguity and style suggestions." }]
                : [],
              auto_applied: [],
            };
            project.state.last_qa = {
              chapter_id: project.project.active_chapter,
              issues: project.qaReport.summary.issues,
            };
            events.push(makeEvent("qa_completed", "Generated QA report", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              chapter_id: project.project.active_chapter,
              report: clone(project.qaReport),
              qa_report_path: `${project.project.project_dir}/reports/qa_report.json`,
              overview: buildOverview(project),
            } as T, events);
          }
          case "load_qa_report": {
            const project = ensureProject(projects, payload);
            events.push(makeEvent("qa_loaded", "Loaded QA report", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              chapter_id: project.project.active_chapter,
              report: clone(project.qaReport ?? emptyReport()),
            } as T, events);
          }
          case "load_learning_report": {
            const project = ensureProject(projects, payload);
            events.push(makeEvent("learning_loaded", "Loaded learning report", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              chapter_id: project.project.active_chapter,
              report: clone(project.learningReport ?? emptyLearningReport(project.project.active_chapter)),
            } as T, events);
          }
          case "update_project_translation_config": {
            const project = ensureProject(projects, payload);
            if (!payload.config || typeof payload.config !== "object" || Array.isArray(payload.config)) {
              throw new Error("config must be an object");
            }
            project.config = clone(payload.config as Record<string, unknown>);
            events.push(makeEvent("config_updated", "Saved demo project translation config", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              config: clone(project.config),
              overview: buildOverview(project),
            } as T, events);
          }
          case "upsert_project_entity": {
            const project = ensureProject(projects, payload);
            if (!payload.entity || typeof payload.entity !== "object" || Array.isArray(payload.entity)) {
              throw new Error("entity must be an object");
            }
            const entity = normalizeDemoEntity(payload.entity as Record<string, unknown>);
            project.entities = upsertBySource(project.entities, entity);
            if (entity.entity_type === "junk_phrase") {
              project.config.ignored_phrases = upsertJunkPhrase(project.config.ignored_phrases, entity);
            } else if (payload.sync_locked !== false) {
              const locked = Array.isArray(project.config.locked_entities)
                ? [...(project.config.locked_entities as Array<Record<string, unknown>>)]
                : [];
              project.config.locked_entities = upsertBySource(locked, {
                source: entity.source,
                target: entity.target,
                entity_type: entity.entity_type,
                origin: "user_review",
              });
            }
            events.push(makeEvent("entity_updated", "Saved demo project entity", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              entity: clone(entity),
              overview: buildOverview(project),
            } as T, events);
          }
          case "delete_project_entity": {
            const project = ensureProject(projects, payload);
            const source = asString(payload.source, "").trim();
            if (!source) {
              throw new Error("source is required");
            }
            const beforeCount = project.entities.length;
            project.entities = project.entities.filter((entity) => asString(entity.source, "").trim() !== source);
            project.config = removeJunkPhrases(project.config, new Set([source]));
            if (payload.sync_locked !== false && Array.isArray(project.config.locked_entities)) {
              project.config.locked_entities = (project.config.locked_entities as Array<Record<string, unknown>>)
                .filter((entity) => asString(entity.source, "").trim() !== source);
            }
            events.push(makeEvent("entity_deleted", "Deleted demo project entity", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              source,
              deleted: project.entities.length !== beforeCount,
              overview: buildOverview(project),
            } as T, events);
          }
          case "delete_project_entities": {
            const project = ensureProject(projects, payload);
            const sources = Array.isArray(payload.sources)
              ? payload.sources.map((source) => asString(source, "").trim()).filter(Boolean)
              : [];
            if (!sources.length) {
              throw new Error("sources must contain at least one entity source");
            }
            const sourceSet = new Set(sources);
            const beforeCount = project.entities.length;
            project.entities = project.entities.filter((entity) => !sourceSet.has(asString(entity.source, "").trim()));
            project.config = removeJunkPhrases(project.config, sourceSet);
            if (payload.sync_locked !== false && Array.isArray(project.config.locked_entities)) {
              project.config.locked_entities = (project.config.locked_entities as Array<Record<string, unknown>>)
                .filter((entity) => !sourceSet.has(asString(entity.source, "").trim()));
            }
            events.push(makeEvent("entities_deleted", "Deleted demo project entities", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              sources,
              deleted_count: beforeCount - project.entities.length,
              overview: buildOverview(project),
            } as T, events);
          }
          case "suggest_entity_targets": {
            const source = asString(payload.source, "").trim();
            if (!source) {
              throw new Error("source is required");
            }
            events.push(makeEvent("entity_targets_suggested", "Generated demo entity target suggestions", 100));
            return makeResponse(command, requestId, {
              source,
              suggestions: buildDemoEntityTargetSuggestions(source),
            } as T, events);
          }
          case "search_dictionary_entries": {
            const query = asString(payload.query, "一");
            const entries = buildDemoDictionaryResults(query);
            events.push(makeEvent("dictionary_loaded", "Loaded dictionary entries", 100));
            return makeResponse(command, requestId, {
              query,
              entries,
            } as T, events);
          }
          case "list_dictionary_entries": {
            const query = asString(payload.query, "");
            const tableName = asString(payload.table_name, "");
            const sourceDict = asString(payload.source_dict, "");
            const posTag = asString(payload.pos_tag, "");
            const entityType = asString(payload.entity_type, "");
            const page = Number(payload.page ?? 1) || 1;
            const pageSize = Number(payload.page_size ?? 50) || 50;
            let entries = buildDemoDictionaryResults(query);
            if (tableName) {
              entries = entries.filter((entry) => entry.table_name === tableName);
            }
            if (sourceDict) {
              entries = entries.filter((entry) => entry.source_dict === sourceDict);
            }
            if (posTag) {
              entries = entries.filter((entry) => entry.pos_tag === posTag);
            }
            if (entityType) {
              entries = entries.filter((entry) => entry.entity_type === entityType);
            }
            const total = entries.length;
            const pageEntries = entries.slice((page - 1) * pageSize, page * pageSize);
            events.push(makeEvent("dictionary_list_loaded", "Loaded paginated dictionary entries", 100));
            return makeResponse(command, requestId, {
              entries: clone(pageEntries),
              total,
              page,
              page_size: pageSize,
              filters: {
                categories: Array.from(new Set(buildDemoDictionaryResults("").map((entry) => entry.source_dict))),
                pos_tags: Array.from(new Set(buildDemoDictionaryResults("").map((entry) => entry.pos_tag ?? "").filter(Boolean))),
                entity_types: Array.from(new Set(buildDemoDictionaryResults("").map((entry) => entry.entity_type ?? "").filter(Boolean))),
                tables: Array.from(new Set(buildDemoDictionaryResults("").map((entry) => entry.table_name))),
              },
              stats: buildDemoPipelineStatus(projects.get("phase10-demo") ?? seeded).dictionary_stats,
            } as T, events);
          }
          case "update_dictionary_entry": {
            const recordId = asString(payload.record_id, "");
            const entry = buildDemoDictionaryResults("").find((item) => item.record_id === recordId);
            if (!entry) {
              throw new Error(`Dictionary entry ${recordId} not found`);
            }
            if (typeof payload.target_vi === "string") {
              entry.target_vi = payload.target_vi;
            }
            if (typeof payload.pos_tag === "string") {
              entry.pos_tag = payload.pos_tag || null;
            }
            if (typeof payload.pos_sub === "string") {
              entry.pos_sub = payload.pos_sub || null;
            }
            if (typeof payload.entity_type === "string") {
              entry.entity_type = payload.entity_type || null;
            }
            if (typeof payload.full_explanation === "string") {
              entry.full_explanation = payload.full_explanation;
            }
            if (typeof payload.traditional === "string") {
              entry.traditional = payload.traditional;
            }
            if (typeof payload.notes === "string") {
              entry.notes = payload.notes;
            }
            if (typeof payload.pinyin === "string") {
              entry.pinyin = payload.pinyin.split(",").map((item) => item.trim()).filter(Boolean);
            }
            events.push(makeEvent("dictionary_updated", "Updated demo dictionary entry", 100));
            return makeResponse(command, requestId, {
              entry: clone(entry),
              pipeline: buildDemoPipelineStatus(projects.get("phase10-demo") ?? seeded),
            } as T, events);
          }
          case "get_pipeline_status": {
            const project = ensureProject(projects, payload);
            events.push(makeEvent("pipeline_loaded", "Loaded demo pipeline status", 100));
            return makeResponse(command, requestId, buildDemoPipelineStatus(project) as T, events);
          }
          case "run_pipeline_stage": {
            const project = ensureProject(projects, payload);
            events.push(makeEvent("pipeline_stage", `Executed demo stage ${String(payload.stage ?? "unknown")}`, 100));
            return makeResponse(command, requestId, {
              stage: payload.stage,
              pipeline: buildDemoPipelineStatus(project),
            } as T, events);
          }
          case "list_candidate_entries": {
            const project = ensureProject(projects, payload);
            const status = asNullableString(payload.status);
            const entries = status
              ? project.candidates.filter((entry) => entry.status === status)
              : project.candidates;
            events.push(makeEvent("candidates_loaded", "Loaded candidate entries", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              entries: clone(entries),
            } as T, events);
          }
          case "list_candidate_rules": {
            const project = ensureProject(projects, payload);
            const status = asNullableString(payload.status);
            const rules = status
              ? project.candidateRules.filter((rule) => rule.status === status)
              : project.candidateRules;
            events.push(makeEvent("rules_loaded", "Loaded candidate rules", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              rules: clone(rules),
            } as T, events);
          }
          case "review_candidate_entry": {
            const project = ensureProject(projects, payload);
            const candidateId = Number(payload.candidate_id);
            const nextStatus = asString(payload.status, "verified");
            const reason = asString(payload.reason, "");
            const entry = project.candidates.find((item) => item.id === candidateId);
            if (!entry) {
              throw new Error(`Candidate ${candidateId} not found`);
            }
            entry.status = nextStatus;
            entry.reviewer_reason = reason;
            applyCandidateReview(project, entry);
            events.push(makeEvent("candidate_reviewed", "Updated candidate review", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              entry: clone(entry),
              overview: buildOverview(project),
            } as T, events);
          }
          case "submit_natural_feedback": {
            const project = ensureProject(projects, payload);
            const analysis = buildDemoFeedbackAnalysis(payload, project.project.active_chapter);
            const createdRuleIds: number[] = [];
            for (const suggestion of analysis.suggestions) {
              const ruleId = project.nextRuleId;
              project.candidateRules.push({
                id: ruleId,
                rule_type: suggestion.rule_type,
                rule_payload: clone(suggestion) as Record<string, unknown>,
                status: "candidate",
                reviewer_reason: "",
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
              });
              createdRuleIds.push(ruleId);
              project.nextRuleId += 1;
            }
            events.push(makeEvent("feedback_analyzed", "Generated candidate rules from natural-language feedback", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              analysis,
              created_rule_ids: createdRuleIds,
              rules: clone(project.candidateRules),
              overview: buildOverview(project),
            } as T, events);
          }
          case "scan_grammar_learning_patterns": {
            const project = ensureProject(projects, payload);
            const report = buildDemoGrammarLearningReport();
            const createdRuleIds: number[] = [];
            if (payload.enqueue_candidates !== false) {
              for (const candidate of report.unknown_candidates.slice(0, Number(payload.max_candidate_rules ?? 5))) {
                const ruleId = project.nextRuleId;
                project.candidateRules.push({
                  id: ruleId,
                  rule_type: "grammar_pattern_candidate",
                  rule_payload: {
                    title: `Grammar candidate: ${candidate.pattern_text}`,
                    summary: `${candidate.pattern_type} repeated ${candidate.frequency} time(s); review only.`,
                    payload: clone(candidate) as Record<string, unknown>,
                    confidence: candidate.confidence,
                    scope: "project",
                    chapter_id: null,
                    origin: "grammar_pattern_scanner",
                  },
                  status: "candidate",
                  reviewer_reason: "",
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                });
                createdRuleIds.push(ruleId);
                project.nextRuleId += 1;
              }
            }
            events.push(makeEvent("grammar_scan_completed", "Generated demo grammar learning report", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              report,
              report_paths: {},
              created_rule_ids: createdRuleIds,
              rules: clone(project.candidateRules),
              overview: buildOverview(project),
            } as T, events);
          }
          case "review_candidate_rule": {
            const project = ensureProject(projects, payload);
            const ruleId = Number(payload.rule_id);
            const nextStatus = asString(payload.status, "verified");
            const reason = asString(payload.reason, "");
            const rule = project.candidateRules.find((item) => item.id === ruleId);
            if (!rule) {
              throw new Error(`Rule ${ruleId} not found`);
            }
            rule.status = nextStatus;
            rule.reviewer_reason = reason;
            rule.updated_at = new Date().toISOString();
            const applied = nextStatus === "verified" ? applyDemoRule(project, rule) : null;
            events.push(makeEvent("rule_reviewed", "Updated candidate rule", 100));
            return makeResponse(command, requestId, {
              project_id: project.project.project_id,
              rule: clone(rule),
              applied,
              overview: buildOverview(project),
            } as T, events);
          }
          default:
            throw new Error(`Unsupported demo command: ${command}`);
        }
      } catch (error) {
        return makeErrorResponse(command, requestId, error instanceof Error ? error.message : String(error), events);
      }
    },
  };
}

function createSeedProject(): DemoProject {
  const project = createBlankProject("phase10-demo", "demo://workspace");
  hydrateImportedProject(project, "demo://samples/chapter-001.md");
  project.translation = generateTranslationArtifacts(project, "chapter-001", SAMPLE_SOURCE, project.config);
  project.candidates = extractCandidates(project.translation, 1);
  project.nextCandidateId = project.candidates.length + 1;
  project.qaReport = generateQAReport(project.translation);
  project.learningReport = emptyLearningReport(project.project.active_chapter);
  return project;
}

function createBlankProject(projectId: string, baseDir: string): DemoProject {
  return {
    project: {
      project_id: projectId,
      project_dir: `${baseDir}/${projectId}`,
      source_language: "zh",
      target_language: "vi",
      active_chapter: null,
    },
    state: {
      project_id: projectId,
      source_language: "zh",
      target_language: "vi",
      active_chapter: null,
    },
    chapters: [],
    entities: [],
    relationships: [],
    terminologySuggestions: [],
    config: {},
    translation: null,
    qaReport: null,
    candidates: [],
    nextCandidateId: 1,
    candidateRules: [],
    nextRuleId: 1,
    learningReport: null,
  };
}

function hydrateImportedProject(project: DemoProject, filepath: string) {
  project.chapters = [
    {
      chapter_id: "chapter-001",
      title: "第1章 Khoi dau",
      text: SAMPLE_SOURCE,
      start: 0,
      end: SAMPLE_SOURCE.length,
      source_path: `${project.project.project_dir}/source/chapters/chapter-001.txt`,
    },
  ];
  project.entities = [
    {
      source: "林动",
      target: "Lâm Động",
      entity_type: "person",
      confidence: 0.98,
      source_dict: "cultivation_names",
      ambiguity_flag: false,
      count: 1,
      positions: [0],
    },
  ];
  project.relationships = [
    {
      source: "林动",
      target: "statement",
      relation: "speaker_of",
      confidence: 0.73,
    },
  ];
  project.terminologySuggestions = [
    {
      source: "浪漫",
      candidates: ["lãng mạn", "lãng mạn hóa"],
      ambiguity: true,
    },
  ];
  project.config = {
    genre_hints: ["general"],
    cultural_origin_hint: "han_viet",
    high_ambiguity_terms: ["浪漫"],
    locked_entities: [
      {
        source: "林动",
        target: "Lâm Động",
        entity_type: "person",
      },
    ],
    terminology_review: clone(project.terminologySuggestions),
    relationships: clone(project.relationships),
  };
  project.project.active_chapter = "chapter-001";
  project.state.active_chapter = "chapter-001";
  project.state.last_import = {
    filepath,
    chapters: project.chapters.length,
    entities: project.entities.length,
  };
}

function buildOverview(project: DemoProject): ProjectOverview {
  const candidateStatus = project.candidates.reduce<Record<string, number>>((acc, entry) => {
    acc[entry.status] = (acc[entry.status] ?? 0) + 1;
    return acc;
  }, {});
  const candidateRuleStatus = project.candidateRules.reduce<Record<string, number>>((acc, rule) => {
    acc[rule.status] = (acc[rule.status] ?? 0) + 1;
    return acc;
  }, {});
  return {
    project: clone(project.project),
    state: clone(project.state),
    chapters: clone(project.chapters),
    config: clone(project.config),
    entities: clone(project.entities),
    relationships: clone(project.relationships),
    terminology_suggestions: clone(project.terminologySuggestions),
    counts: {
      chapters: project.chapters.length,
      segments: project.translation?.segments.length ?? 0,
      candidates_total: project.candidates.length,
      candidate_status: candidateStatus,
      candidate_rules_total: project.candidateRules.length,
      candidate_rule_status: candidateRuleStatus,
      qa_issues: project.qaReport?.summary.issues ?? 0,
    },
    artifacts: {
      config_path: `${project.project.project_dir}/working/config/translation_config.json`,
      output_path: `${project.project.project_dir}/output/translated.txt`,
      draft_path: `${project.project.project_dir}/drafts/translated_draft.txt`,
      trace_path: `${project.project.project_dir}/drafts/translation_trace.json`,
      qa_report_path: `${project.project.project_dir}/reports/qa_report.json`,
    },
  };
}

function buildDemoPipelineStatus(project: DemoProject): PipelineStatus {
  return {
    stages: [
      { id: "import", label: "Nhap", status: project.chapters.length ? "completed" : "pending", progress: project.chapters.length ? 100 : 0, message: "Demo import stage", metrics: { chapters: project.chapters.length } },
      { id: "compile", label: "Bien dich", status: "completed", progress: 100, message: "Demo dictionary DB ready", metrics: { total: 2 } },
      { id: "assign_pos", label: "Gan POS", status: "completed", progress: 97, message: "Demo POS coverage", metrics: { pos_coverage_pct: 97, pinyin_coverage_pct: 99 } },
      { id: "translate", label: "Dich", status: project.translation ? "completed" : "pending", progress: project.translation ? 100 : 0, message: "Demo translation stage", metrics: { chapter: project.project.active_chapter } },
      { id: "qa", label: "QA", status: project.qaReport ? "completed" : "pending", progress: project.qaReport ? 100 : 0, message: "Demo QA stage", metrics: { issues: project.qaReport?.summary.issues ?? 0 } },
      { id: "export", label: "Xuat", status: project.translation ? "completed" : "pending", progress: project.translation ? 100 : 0, message: "Demo export artifacts", metrics: { output: `${project.project.project_dir}/output/translated.txt` } },
    ],
    dictionary_stats: {
      runtime_total: 2,
      reference_total: 0,
      total: 2,
      pos_total: 2,
      pinyin_total: 2,
      entity_total: 1,
      pos_coverage_pct: 97,
      pinyin_coverage_pct: 99,
      compiled_at: new Date().toISOString(),
      entry_readings_total: 2,
      metadata: { mode: "demo" },
    },
    project: clone(project.project),
    artifacts: buildOverview(project).artifacts,
    last_state: clone(project.state),
  };
}

function buildDemoDictionaryResults(query: string): DictionaryEntry[] {
  const catalog: DictionaryEntry[] = [
    {
      record_id: "entries:1",
      row_id: 1,
      table_name: "entries",
      source: "一",
      target_vi: "nhất",
      alternative_meanings: ["một", "toàn bộ"],
      full_explanation: "nhất [yi1] 1. Một. 2. Cùng. 3. Bao quát hết thảy. 4. Chuyên chú vào một mặt.",
      source_dict: "thieuchuu_reference",
      priority: 1,
      status: "reference",
      hit_count: 0,
      pinyin: ["yi1"],
      han_viet_readings: ["nhất"],
      entry_role: "reference",
      source_language: "zh",
      target_language: "vi",
      one_mean: false,
      locked: false,
      notes: "",
      source_file: "_bulk_thieuchuu.md",
      source_path: "demo://dict/_bulk_thieuchuu.md",
      pos_tag: "NUMBER",
      pos_sub: "cardinal",
      entity_type: null,
      traditional: "一",
      is_function_word: false,
      luat_nhan_trigger: false,
      reorder_role: null,
      metadata: {
        full_explanation: "nhất [yi1] 1. Một. 2. Cùng. 3. Bao quát hết thảy. 4. Chuyên chú vào một mặt.",
      },
    },
    {
      record_id: "entries:2",
      row_id: 2,
      table_name: "entries",
      source: "林动",
      target_vi: "Lâm Động",
      alternative_meanings: [],
      full_explanation: "Project entity override for the protagonist.",
      source_dict: "cultivation_names",
      priority: 4,
      status: "locked",
      hit_count: 3,
      pinyin: ["lin2 dong4"],
      han_viet_readings: ["Lâm Động"],
      entry_role: "runtime",
      source_language: "zh",
      target_language: "vi",
      one_mean: true,
      locked: true,
      notes: "Seeded demo entity",
      source_file: "_names_person_east.md",
      source_path: "demo://dict/_names_person_east.md",
      pos_tag: "NOUN",
      pos_sub: "name",
      entity_type: "person",
      traditional: "林動",
      is_function_word: false,
      luat_nhan_trigger: true,
      reorder_role: "head",
      metadata: {
        pos_sub: "name",
        entity_type: "person",
        luat_nhan_trigger: 1,
        reorder_role: "head",
      },
    },
  ];
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    return catalog;
  }
  return catalog.filter((entry) => {
    const haystack = [
      entry.source,
      entry.target_vi,
      entry.source_dict,
      entry.full_explanation,
      ...entry.alternative_meanings,
      ...entry.pinyin,
      ...entry.han_viet_readings,
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(normalized);
  });
}

function generateTranslationArtifacts(
  project: DemoProject,
  chapterId: string,
  sourceText: string,
  config: Record<string, unknown>,
): TranslationArtifacts {
  const entityTarget = getLockedEntityTarget(config, "林动") ?? "Lâm Động";
  const highAmbiguityTerms = Array.isArray(config.high_ambiguity_terms)
    ? config.high_ambiguity_terms.map(String)
    : [];
  const isAmbiguous = highAmbiguityTerms.includes("浪漫");
  const traces: TranslationTrace[] = [
    {
      source: "林动",
      selected: entityTarget,
      candidates: [entityTarget],
      priority: 95,
      fallback_level: "project_entity",
      reason: "locked_entity_override",
    },
    {
      source: "说道",
      selected: "nói",
      candidates: ["nói"],
      priority: 60,
      fallback_level: "function_map",
      reason: "builtin_function_map",
    },
    {
      source: "浪漫",
      selected: "lãng mạn",
      candidates: ["lãng mạn", "lãng mạn hóa"],
      priority: 4,
      fallback_level: isAmbiguous ? "ambiguous" : "runtime",
      reason: "terminology_runtime",
    },
  ];

  const draftSuffix = isAmbiguous
    ? "lãng mạn[[AMBIG:浪漫=>lãng mạn|lãng mạn hóa]]"
    : "lãng mạn";
  const segment: TranslationSegment = {
    sentence_id: `${chapterId}:sentence-001`,
    source_text: sourceText,
    clean_text: `${entityTarget} nói: "lãng mạn!"`,
    draft_text: `${entityTarget} nói: "${draftSuffix}!"`,
    emotion: "joy",
    trace: traces,
    fallback_level: isAmbiguous ? "ambiguous" : "runtime",
  };

  return {
    project_id: project.project.project_id,
    chapter_id: chapterId,
    clean_text: segment.clean_text,
    draft_text: segment.draft_text,
    segments: [segment],
    paths: {
      clean: `${project.project.project_dir}/output/translated.txt`,
      draft: `${project.project.project_dir}/drafts/translated_draft.txt`,
      trace: `${project.project.project_dir}/drafts/translation_trace.json`,
    },
  };
}

function generateQAReport(translation: TranslationArtifacts): QAReport {
  const issues = translation.segments.flatMap((segment) => {
    const findings = [];
    if (segment.draft_text.includes("[[AMBIG:")) {
      findings.push({
        severity: "medium",
        checker: "ambiguity",
        segment_id: segment.sentence_id,
        message: "Annotated draft still contains unresolved ambiguity",
      });
    }
    if (segment.draft_text.includes("[[UNRESOLVED]]")) {
      findings.push({
        severity: "high",
        checker: "untranslated",
        segment_id: segment.sentence_id,
        message: "Unresolved source fragment remains in draft",
      });
    }
    return findings;
  });
  return {
    summary: {
      issues: issues.length,
      segments: translation.segments.length,
    },
    issues,
  };
}

function extractCandidates(translation: TranslationArtifacts, startId: number): CandidateEntry[] {
  const candidates: CandidateEntry[] = [];
  let nextId = startId;
  for (const segment of translation.segments) {
    for (const trace of segment.trace) {
      if (trace.fallback_level !== "ambiguous" && trace.fallback_level !== "unresolved") {
        continue;
      }
      candidates.push({
        id: nextId,
        source_text: trace.source,
        target_text: trace.selected,
        status: "candidate",
        reviewer_reason: "",
        chapter_id: translation.chapter_id ?? "",
        segment_id: segment.sentence_id,
        fallback_level: trace.fallback_level,
        candidates: trace.candidates,
        reason: trace.reason,
        created_at: new Date().toISOString(),
      });
      nextId += 1;
    }
  }
  return candidates;
}

function applyCandidateReview(project: DemoProject, entry: CandidateEntry) {
  if (entry.status !== "verified" || !project.translation) {
    return;
  }
  project.translation.segments = project.translation.segments.map((segment) => {
    if (segment.sentence_id !== entry.segment_id) {
      return segment;
    }
    const nextDraft = segment.draft_text.replace(/\[\[AMBIG:[^\]]+\]\]/g, "");
    const nextTrace = segment.trace.map((trace) =>
      trace.source === entry.source_text
        ? {
            ...trace,
            selected: entry.target_text,
            candidates: [entry.target_text],
            fallback_level: "runtime",
            reason: "candidate_verified",
          }
        : trace,
    );
    return {
      ...segment,
      clean_text: segment.clean_text.replace("lãng mạn", entry.target_text),
      draft_text: nextDraft.replace("lãng mạn", entry.target_text),
      trace: nextTrace,
      fallback_level: "runtime",
    };
  });
  project.translation.clean_text = project.translation.segments.map((segment) => segment.clean_text).join("\n");
  project.translation.draft_text = project.translation.segments.map((segment) => segment.draft_text).join("\n");
}

function emptyTranslation(projectId: string, chapterId: string | null): TranslationArtifacts {
  return {
    project_id: projectId,
    chapter_id: chapterId,
    clean_text: "",
    draft_text: "",
    segments: [],
    paths: {
      clean: "",
      draft: "",
      trace: "",
    },
  };
}

function emptyReport(): QAReport {
  return {
    summary: {
      issues: 0,
      segments: 0,
    },
    issues: [],
  };
}

function emptyLearningReport(chapterId: string | null): LearningReport {
  return {
    chapter_id: chapterId,
    current_run: {
      qa_total: 0,
      runtime_metrics: {
        translate_seconds: 0,
      },
    },
    recommendations: [],
    auto_applied: [],
  };
}

function buildDemoFeedbackAnalysis(
  payload: Record<string, unknown>,
  activeChapter: string | null,
): NaturalFeedbackAnalysis {
  const feedbackText = asString(payload.feedback_text, "");
  const scope = asString(payload.scope, "project");
  const chapterId = scope === "chapter"
    ? asNullableString(payload.chapter_id) ?? activeChapter
    : null;
  const suggestions: NaturalFeedbackAnalysis["suggestions"] = [];
  const directRewrite = feedbackText.match(/"(.+?)"\s*(?:->|=>|→)\s*"(.+?)"/);
  if (directRewrite) {
    suggestions.push({
      rule_type: "phrase_override",
      title: "Phrase override",
      summary: `Áp ${directRewrite[1]} -> ${directRewrite[2]}`,
      payload: { source: directRewrite[1], target: directRewrite[2] },
      confidence: 0.9,
      scope,
      chapter_id: chapterId,
      origin: "demo",
    });
  }
  if (/hội thoại|xưng hô|khẩu ngữ/i.test(feedbackText)) {
    suggestions.push({
      rule_type: "style_profile",
      title: "Đổi profile hội thoại",
      summary: "Feedback thiên về hội thoại tự nhiên.",
      payload: { style_profile: "dialogue_natural" },
      confidence: 0.78,
      scope,
      chapter_id: chapterId,
      origin: "demo",
    });
  }
  if (/gọn|ngắn|đỡ dài/i.test(feedbackText)) {
    suggestions.push({
      rule_type: "naturalization",
      title: "Rút gọn câu",
      summary: "Bật compact sentences.",
      payload: { naturalization: { enabled: true, compact_sentences: true } },
      confidence: 0.74,
      scope,
      chapter_id: chapterId,
      origin: "demo",
    });
  }
  if (!suggestions.length) {
    suggestions.push({
      rule_type: "style_guidance",
      title: "Lưu ghi chú",
      summary: feedbackText || "Feedback demo",
      payload: { guidance: feedbackText },
      confidence: 0.5,
      scope,
      chapter_id: chapterId,
      origin: "demo",
    });
  }
  return {
    feedback_text: feedbackText,
    scope,
    chapter_id: chapterId,
    rule_type_hint: asString(payload.rule_type_hint, "auto"),
    llm_used: false,
    warnings: [],
    suggestions,
  };
}

function buildDemoGrammarLearningReport(): Record<string, unknown> & {
  unknown_candidates: Array<Record<string, unknown> & {
    pattern_text: string;
    pattern_type: string;
    frequency: number;
    confidence: number;
  }>;
} {
  const unknownCandidates = [
    {
      candidate_id: "unknown_demo_yuqi_buru",
      pattern_text: "与其...不如",
      pattern_type: "paired_marker",
      frequency: 12,
      chapter_count: 4,
      confidence: 0.83,
      guessed_category: "preference",
      suggested_regex: "与其(?P<a>.+?)不如(?P<b>.+)",
      status: "review",
      examples: ["与其坐以待毙，不如主动出击。"],
    },
  ];
  return {
    summary: {
      total_sources: 1,
      total_chapters: 1,
      total_sentences: 24,
      total_matches: 8,
      total_rules_matched: 3,
      unknown_candidate_count: unknownCandidates.length,
    },
    sources: [],
    warnings: [],
    known_rules: [],
    unknown_candidates: unknownCandidates,
    rule_backlog: [],
    metadata: {
      engine: "GrammarLearningPatternScanner",
      pipeline_scope: "translator_learning_coach_only",
      non_llm: true,
    },
  };
}

function applyDemoRule(project: DemoProject, rule: CandidateRule): Record<string, unknown> | null {
  const payload = (rule.rule_payload.payload ?? {}) as Record<string, unknown>;
  switch (rule.rule_type) {
    case "phrase_override": {
      const source = asString(payload.source, "");
      const target = asString(payload.target, "");
      const overrides = {
        ...((project.config.project_phrase_overrides as Record<string, string> | undefined) ?? {}),
      };
      overrides[source] = target;
      project.config.project_phrase_overrides = overrides;
      return { updated: "project_phrase_overrides", source, target };
    }
    case "style_profile": {
      project.config.style_profile = asString(payload.style_profile, "balanced_novel");
      return { updated: "style_profile", style_profile: project.config.style_profile };
    }
    case "naturalization": {
      project.config.naturalization = clone((payload.naturalization as Record<string, unknown>) ?? {});
      return { updated: "naturalization" };
    }
    case "style_guidance": {
      const guidance = Array.isArray(project.config.style_guidance)
        ? [...(project.config.style_guidance as Array<Record<string, unknown>>)]
        : [];
      guidance.push(clone(payload));
      project.config.style_guidance = guidance;
      return { updated: "style_guidance" };
    }
    case "grammar_pattern_candidate": {
      const backlog = Array.isArray(project.config.grammar_learning_backlog)
        ? [...(project.config.grammar_learning_backlog as Array<Record<string, unknown>>)]
        : [];
      backlog.push(clone(payload));
      project.config.grammar_learning_backlog = backlog;
      return { updated: "grammar_learning_backlog" };
    }
    default:
      return null;
  }
}

function ensureProject(
  projects: Map<string, DemoProject>,
  payload: Record<string, unknown>,
): DemoProject {
  const projectId = asNullableString(payload.project_id)
    ?? asNullableString(payload.project_dir)?.split("/").pop()
    ?? "phase10-demo";
  const project = projects.get(projectId);
  if (!project) {
    throw new Error(`Project ${projectId} not found in demo transport`);
  }
  return project;
}

function getActiveChapter(project: DemoProject): ChapterInfo | undefined {
  return project.chapters.find((chapter) => chapter.chapter_id === project.project.active_chapter)
    ?? project.chapters[0];
}

function getLockedEntityTarget(config: Record<string, unknown>, source: string): string | null {
  const locked = Array.isArray(config.locked_entities) ? config.locked_entities : [];
  for (const entry of locked) {
    if (entry && typeof entry === "object" && "source" in entry && "target" in entry) {
      if (String(entry.source) === source) {
        return String(entry.target);
      }
    }
  }
  return null;
}

function normalizeDemoEntity(payload: Record<string, unknown>): Record<string, unknown> {
  return {
    source: asString(payload.source, "").trim(),
    target: asString(payload.target, "").trim(),
    entity_type: asString(payload.entity_type, "project_term"),
    confidence: Number(payload.confidence ?? 1) || 1,
    source_dict: asString(payload.source_dict, "user_review"),
    ambiguity_flag: Boolean(payload.ambiguity_flag),
    count: Math.max(1, Number(payload.count ?? 1) || 1),
    positions: Array.isArray(payload.positions) ? payload.positions : [],
  };
}

function normalizeJunkPhrase(item: unknown): Record<string, unknown> | null {
  if (typeof item === "string") {
    const source = item.trim();
    return source ? { source, target: "", clean_text: "", origin: "user_review", enabled: true } : null;
  }
  if (!item || typeof item !== "object" || Array.isArray(item)) {
    return null;
  }
  const payload = item as Record<string, unknown>;
  const source = asString(payload.source ?? payload.raw_pattern ?? payload.phrase ?? payload.text, "").trim();
  const target = asString(payload.target ?? payload.target_vi, "").trim();
  if (!source && !target) {
    return null;
  }
  return {
    source,
    target,
    clean_text: asString(payload.clean_text ?? payload.replacement, "").trim(),
    origin: asString(payload.origin ?? payload.source_dict, "user_review").trim() || "user_review",
    enabled: payload.enabled !== false,
  };
}

function upsertJunkPhrase(current: unknown, entity: Record<string, unknown>): Array<Record<string, unknown>> {
  const entries = Array.isArray(current)
    ? current.map(normalizeJunkPhrase).filter(Boolean) as Array<Record<string, unknown>>
    : [];
  return upsertBySource(entries, {
    source: asString(entity.source, "").trim(),
    target: asString(entity.target, "").trim(),
    clean_text: "",
    origin: "user_review",
    enabled: true,
  });
}

function removeJunkPhrases(config: Record<string, unknown>, sources: Set<string>): Record<string, unknown> {
  for (const key of ["ignored_phrases", "junk_phrases", "user_noise_phrases"]) {
    const entries = Array.isArray(config[key])
      ? (config[key] as unknown[]).map(normalizeJunkPhrase).filter(Boolean) as Array<Record<string, unknown>>
      : null;
    if (!entries) {
      continue;
    }
    config[key] = entries.filter((item) => {
      const source = asString(item.source, "").trim();
      const target = asString(item.target, "").trim();
      return !sources.has(source) && !sources.has(target);
    });
  }
  return config;
}

function buildDemoEntityTargetSuggestions(source: string): Array<Record<string, unknown>> {
  if (source === "九岭十三坡") {
    return [
      {
        kind: "han_viet_word",
        label: "Hán Việt word by word",
        value: "Cửu Lĩnh Thập Tam Pha",
        detail: "Ghép từng Hán tự theo thứ tự source.",
        confidence: 0.9,
      },
    ];
  }
  const latinMatch = source.match(/[A-Za-z][A-Za-z0-9'._-]*(?:\s+[A-Za-z][A-Za-z0-9'._-]*)*/);
  return [
    {
      kind: "han_viet_word",
      label: "Hán Việt word by word",
      value: source,
      detail: "Demo fallback.",
      confidence: 0.5,
    },
    ...(latinMatch ? [{
      kind: "latin_source",
      label: "Latinh source",
      value: latinMatch[0],
      detail: "Giữ phần chữ Latin có sẵn trong source.",
      confidence: 0.86,
    }] : []),
  ];
}

function upsertBySource(
  items: Array<Record<string, unknown>>,
  incoming: Record<string, unknown>,
): Array<Record<string, unknown>> {
  const source = asString(incoming.source, "").trim();
  if (!source) {
    return items;
  }
  let replaced = false;
  const next = items.map((item) => {
    if (asString(item.source, "").trim() !== source) {
      return item;
    }
    replaced = true;
    return { ...item, ...incoming };
  });
  if (!replaced) {
    next.push(incoming);
  }
  return next;
}

function makeEvent(stage: string, message: string, progress: number): CommandEvent {
  return {
    stage,
    message,
    progress,
    level: "info",
  };
}

function makeResponse<T>(
  command: string,
  requestId: string,
  data: T,
  events: CommandEvent[],
): CommandResponse<T> {
  return {
    ok: true,
    command,
    request_id: requestId,
    protocol_version: PROTOCOL_VERSION,
    data,
    error: "",
    warnings: [],
    events,
    generated_at: new Date().toISOString(),
  };
}

function makeErrorResponse<T>(
  command: string,
  requestId: string,
  error: string,
  events: CommandEvent[],
): CommandResponse<T> {
  return {
    ok: false,
    command,
    request_id: requestId,
    protocol_version: PROTOCOL_VERSION,
    data: {} as T,
    error,
    warnings: [],
    events: [...events, { stage: "failed", message: error, progress: 100, level: "error" }],
    generated_at: new Date().toISOString(),
  };
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function asString(value: unknown, fallback: string): string {
  return typeof value === "string" && value.length > 0 ? value : fallback;
}

function asNullableString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function delay(ms: number) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}
