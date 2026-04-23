import React, { startTransition, useDeferredValue, useEffect, useState } from "react";
import { invoke, isTauri } from "@tauri-apps/api/core";

import { Panel, InfoLine, MetricCard } from "./components/Panel";
import { CoachScreen } from "./screens/CoachScreen";
import { DashboardScreen } from "./screens/DashboardScreen";
import { DictionaryEditorScreen } from "./screens/DictionaryEditorScreen";
import { PipelineMonitorScreen } from "./screens/PipelineMonitorScreen";
import { SettingsScreen } from "./screens/SettingsScreen";
import { TranslationWorkspaceScreen } from "./screens/TranslationWorkspaceScreen";
import { createPreferredTransport } from "./transport";
import type {
  CandidateEntry,
  CandidateRule,
  CommandEvent,
  CommandName,
  DictionaryEntry,
  DictionaryListResponse,
  LearningReport,
  NaturalFeedbackAnalysis,
  PipelineStatus,
  ProjectOverview,
  ProjectRecord,
  QAReport,
  Transport,
  TranslationArtifacts,
} from "./protocol";
import { downloadJson, getParentPath, isAbsolutePath, normalizeUserPath } from "./pathUtils";
import { SCREENS, type ScreenKey } from "./uiConstants";

export function App() {
  const [screen, setScreen] = useState<ScreenKey>("Dashboard");
  const [transport, setTransport] = useState<Transport | null>(null);
  const [projects, setProjects] = useState<ProjectRecord[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [overview, setOverview] = useState<ProjectOverview | null>(null);
  const [translation, setTranslation] = useState<TranslationArtifacts | null>(null);
  const [qaReport, setQaReport] = useState<QAReport | null>(null);
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null);
  const [candidates, setCandidates] = useState<CandidateEntry[]>([]);
  const [candidateRules, setCandidateRules] = useState<CandidateRule[]>([]);
  const [learningReport, setLearningReport] = useState<LearningReport | null>(null);
  const [feedbackAnalysis, setFeedbackAnalysis] = useState<NaturalFeedbackAnalysis | null>(null);
  const [statusMessage, setStatusMessage] = useState("Mở project để bắt đầu pipeline.");
  const [events, setEvents] = useState<CommandEvent[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  const [createProjectId, setCreateProjectId] = useState(() => readStoredValue("drduc.projectId", "project-001"));
  const [workspaceBaseDir, setWorkspaceBaseDir] = useState(() => readStoredValue("drduc.workspaceBaseDir", "workspace_projects"));
  const [importPath, setImportPath] = useState("");
  const [translationInput, setTranslationInput] = useState("");

  const [dictionaryQuery, setDictionaryQuery] = useState("");
  const [dictionaryEntries, setDictionaryEntries] = useState<DictionaryEntry[]>([]);
  const [dictionaryQuickResults, setDictionaryQuickResults] = useState<DictionaryEntry[]>([]);
  const [dictionaryTotal, setDictionaryTotal] = useState(0);
  const [dictionaryPage, setDictionaryPage] = useState(1);
  const [dictionaryFilters, setDictionaryFilters] = useState<DictionaryListResponse["filters"] | null>(null);
  const [tableFilter, setTableFilter] = useState("");
  const [sourceDictFilter, setSourceDictFilter] = useState("");
  const [posTagFilter, setPosTagFilter] = useState("");
  const [entityTypeFilter, setEntityTypeFilter] = useState("");
  const [selectedEntryId, setSelectedEntryId] = useState("");
  const [selectedEntryIds, setSelectedEntryIds] = useState<string[]>([]);
  const [draftEntry, setDraftEntry] = useState<DictionaryEntry | null>(null);
  const [bulkPosTag, setBulkPosTag] = useState("");
  const [bulkEntityType, setBulkEntityType] = useState("");

  const [candidateFilter, setCandidateFilter] = useState("all");
  const [candidateQuery, setCandidateQuery] = useState("");
  const [ruleFilter, setRuleFilter] = useState("all");

  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackSourceText, setFeedbackSourceText] = useState("");
  const [feedbackCurrentTranslation, setFeedbackCurrentTranslation] = useState("");
  const [feedbackPreferredTranslation, setFeedbackPreferredTranslation] = useState("");
  const [feedbackScope, setFeedbackScope] = useState("chapter");
  const [feedbackRuleHint, setFeedbackRuleHint] = useState("auto");

  const backendAvailable = transport ? transport.mode !== "browser" : false;
  const workspaceRoot = normalizeUserPath(workspaceBaseDir) || "workspace_projects";
  const currentProjectId = overview?.project.project_id ?? selectedProjectId;
  const selectedProject = projects.find((project) => project.project_id === selectedProjectId) ?? null;
  const activeChapter =
    overview?.chapters.find((chapter) => chapter.chapter_id === overview.project.active_chapter) ??
    overview?.chapters[0] ??
    null;
  const deferredDictionaryQuery = useDeferredValue(dictionaryQuery);

  useEffect(() => {
    writeStoredValue("drduc.workspaceBaseDir", workspaceBaseDir);
  }, [workspaceBaseDir]);

  useEffect(() => {
    writeStoredValue("drduc.projectId", createProjectId);
  }, [createProjectId]);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const nextTransport = await createPreferredTransport();
      if (cancelled) {
        return;
      }
      setTransport(nextTransport);
      if (nextTransport.mode === "tauri") {
        setStatusMessage("Native Tauri bridge detected. Path resolution is absolute and sidecar-backed.");
      } else if (nextTransport.mode === "http") {
        setStatusMessage("HTTP bridge connected. Browser dev mode is running against the live Python pipeline.");
      } else if (nextTransport.mode === "demo") {
        setStatusMessage("Demo transport enabled for UI-only development.");
      } else {
        setStatusMessage("Browser preview detected. Real pipeline commands need HTTP bridge or native Tauri.");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!transport || transport.mode === "browser") {
      return;
    }
    void refreshProjects();
    void refreshPipelineStatus();
    void searchQuickDictionary("一");
  }, [transport]);

  useEffect(() => {
    if (!selectedProjectId || !transport || transport.mode === "browser") {
      return;
    }
    void hydrateProject(selectedProjectId);
  }, [selectedProjectId, transport]);

  useEffect(() => {
    if (!translationInput && activeChapter?.text) {
      setTranslationInput(activeChapter.text);
    }
  }, [activeChapter?.chapter_id, activeChapter?.text, translationInput]);

  useEffect(() => {
    if (!feedbackSourceText && activeChapter?.text) {
      setFeedbackSourceText(activeChapter.text);
    }
  }, [activeChapter?.chapter_id, activeChapter?.text, feedbackSourceText]);

  useEffect(() => {
    if (!feedbackCurrentTranslation && translation?.clean_text) {
      setFeedbackCurrentTranslation(translation.clean_text);
    }
  }, [translation?.clean_text, feedbackCurrentTranslation]);

  useEffect(() => {
    if (projects.length && (!isAbsolutePath(workspaceBaseDir) || workspaceBaseDir === "workspace_projects")) {
      setWorkspaceBaseDir(getParentPath(projects[0].project_dir));
    }
  }, [projects, workspaceBaseDir]);

  useEffect(() => {
    if (!dictionaryEntries.length) {
      setSelectedEntryId("");
      setDraftEntry(null);
      return;
    }
    const current = dictionaryEntries.find((entry) => entry.record_id === selectedEntryId) ?? dictionaryEntries[0];
    setSelectedEntryId(current.record_id);
    setDraftEntry(clone(current));
  }, [dictionaryEntries]);

  async function execute<T>(command: CommandName, payload: Record<string, unknown> = {}): Promise<T | null> {
    if (!transport) {
      return null;
    }
    setBusy(true);
    try {
      const response = await transport.send<T>(command, payload);
      setEvents(response.events);
      setWarnings(response.warnings);
      const lastEvent = response.events[response.events.length - 1];
      setStatusMessage(response.ok ? lastEvent?.message ?? `${command} completed.` : response.error);
      if (!response.ok) {
        return null;
      }
      return response.data;
    } catch (error) {
      setWarnings([]);
      setEvents([]);
      setStatusMessage(error instanceof Error ? error.message : String(error));
      return null;
    } finally {
      setBusy(false);
    }
  }

  function buildProjectPayload(projectId?: string): Record<string, unknown> {
    const effectiveProjectId = projectId ?? currentProjectId;
    const payload: Record<string, unknown> = {
      base_dir: workspaceRoot,
    };
    if (!effectiveProjectId) {
      return payload;
    }
    const projectDir =
      (overview?.project.project_id === effectiveProjectId ? overview.project.project_dir : null) ??
      (selectedProject?.project_id === effectiveProjectId ? selectedProject.project_dir : null) ??
      (projects.find((project) => project.project_id === effectiveProjectId)?.project_dir ?? null);
    payload.project_id = effectiveProjectId;
    if (projectDir) {
      payload.project_dir = projectDir;
    }
    return payload;
  }

  async function pickImportPath(kind: "file" | "folder") {
    if (!backendAvailable || !isTauri()) {
      setStatusMessage("Native picker is only available inside the Tauri desktop app.");
      return;
    }
    try {
      const selectedPath = await invoke<string | null>("pick_import_path", { kind });
      if (selectedPath) {
        setImportPath(normalizeUserPath(selectedPath));
      }
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : String(error));
    }
  }

  async function refreshProjects(baseDir = workspaceRoot) {
    const data = await execute<{ projects: ProjectRecord[] }>("list_projects", {
      base_dir: normalizeUserPath(baseDir),
    });
    if (!data) {
      return;
    }
    setProjects(data.projects);
    setSelectedProjectId((current) => {
      if (current && data.projects.some((project) => project.project_id === current)) {
        return current;
      }
      return data.projects[0]?.project_id ?? "";
    });
  }

  async function refreshPipelineStatus(projectId?: string) {
    const payload = projectId ? buildProjectPayload(projectId) : { base_dir: workspaceRoot };
    const data = await execute<PipelineStatus>("get_pipeline_status", payload);
    if (data) {
      setPipelineStatus(data);
    }
  }

  async function refreshDictionaryPage(page = dictionaryPage, queryOverride?: string) {
    const query = queryOverride ?? deferredDictionaryQuery;
    const data = await execute<DictionaryListResponse>("list_dictionary_entries", {
      query,
      page,
      page_size: 50,
      table_name: tableFilter,
      source_dict: sourceDictFilter,
      pos_tag: posTagFilter,
      entity_type: entityTypeFilter,
    });
    if (!data) {
      return;
    }
    setDictionaryEntries(data.entries);
    setDictionaryTotal(data.total);
    setDictionaryPage(data.page);
    setDictionaryFilters(data.filters);
    if (pipelineStatus) {
      setPipelineStatus({
        ...pipelineStatus,
        dictionary_stats: data.stats,
      });
    }
  }

  async function searchQuickDictionary(query: string) {
    const normalized = query.trim() || "一";
    const data = await execute<{ entries: DictionaryEntry[] }>("search_dictionary_entries", {
      query: normalized,
      limit: 8,
    });
    if (data) {
      setDictionaryQuickResults(data.entries);
    }
  }

  async function hydrateProject(projectId: string) {
    const nextOverview = await execute<ProjectOverview>("get_project_overview", buildProjectPayload(projectId));
    if (!nextOverview) {
      return;
    }
    setOverview(nextOverview);

    const chapterId = nextOverview.project.active_chapter ?? nextOverview.chapters[0]?.chapter_id;
    const nextArtifacts = await execute<TranslationArtifacts>("load_translation_artifacts", {
      ...buildProjectPayload(projectId),
      chapter_id: chapterId,
    });
    setTranslation(nextArtifacts);

    const nextReport = await execute<{ report: QAReport }>("load_qa_report", {
      ...buildProjectPayload(projectId),
      chapter_id: chapterId,
    });
    setQaReport(nextReport?.report ?? null);

    const nextCandidates = await execute<{ entries: CandidateEntry[] }>("list_candidate_entries", buildProjectPayload(projectId));
    setCandidates(nextCandidates?.entries ?? []);

    const nextRules = await execute<{ rules: CandidateRule[] }>("list_candidate_rules", buildProjectPayload(projectId));
    setCandidateRules(nextRules?.rules ?? []);

    const nextLearning = await execute<{ report: LearningReport }>("load_learning_report", {
      ...buildProjectPayload(projectId),
      chapter_id: chapterId,
    });
    setLearningReport(nextLearning?.report ?? null);

    const seededQuery = nextOverview.entities[0]?.source ? String(nextOverview.entities[0].source) : "一";
    setDictionaryQuery(seededQuery);
    await refreshDictionaryPage(1, seededQuery);
    await searchQuickDictionary(seededQuery);
    await refreshPipelineStatus(projectId);
  }

  async function handleCreateProject(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const projectId = createProjectId.trim() || "project-001";
    const data = await execute<{ project_id: string }>("create_project", {
      project_id: projectId,
      base_dir: workspaceRoot,
    });
    if (!data) {
      return;
    }
    await refreshProjects();
    startTransition(() => {
      setSelectedProjectId(data.project_id);
      setScreen("Dashboard");
    });
  }

  async function handleImport() {
    if (!currentProjectId) {
      setStatusMessage("Create or select a project before importing.");
      return;
    }
    const filepath = normalizeUserPath(importPath);
    if (!filepath) {
      setStatusMessage("Nhap duong dan file/folder nguon truoc khi import.");
      return;
    }
    const data = await execute<{ overview: ProjectOverview }>("import_file", {
      ...buildProjectPayload(currentProjectId),
      filepath,
    });
    if (!data) {
      return;
    }
    setOverview(data.overview);
    setTranslation(null);
    setQaReport(null);
    setFeedbackAnalysis(null);
    setFeedbackSourceText(data.overview.chapters[0]?.text ?? "");
    setTranslationInput(data.overview.chapters[0]?.text ?? "");
    await hydrateProject(currentProjectId);
    startTransition(() => {
      setScreen("Translation Workspace");
    });
  }

  async function handleSelectChapter(chapterId: string, chapterText: string) {
    if (!currentProjectId) {
      return;
    }
    setTranslationInput(chapterText);
    const nextOverview = await execute<ProjectOverview>("set_active_chapter", {
      ...buildProjectPayload(currentProjectId),
      chapter_id: chapterId,
    });
    if (!nextOverview) {
      return;
    }
    setOverview(nextOverview);
    const nextArtifacts = await execute<TranslationArtifacts>("load_translation_artifacts", {
      ...buildProjectPayload(currentProjectId),
      chapter_id: chapterId,
    });
    setTranslation(nextArtifacts);
    const nextReport = await execute<{ report: QAReport }>("load_qa_report", {
      ...buildProjectPayload(currentProjectId),
      chapter_id: chapterId,
    });
    setQaReport(nextReport?.report ?? null);
    const nextLearning = await execute<{ report: LearningReport }>("load_learning_report", {
      ...buildProjectPayload(currentProjectId),
      chapter_id: chapterId,
    });
    setLearningReport(nextLearning?.report ?? null);
    await refreshPipelineStatus(currentProjectId);
  }

  async function handleTranslate() {
    if (!currentProjectId) {
      return;
    }
    const data = await execute<{ translation_artifacts: TranslationArtifacts; overview: ProjectOverview }>("translate", {
      ...buildProjectPayload(currentProjectId),
      chapter_id: overview?.project.active_chapter ?? activeChapter?.chapter_id,
      text: translationInput.trim(),
      config: overview?.config ?? {},
    });
    if (!data) {
      return;
    }
    setTranslation(data.translation_artifacts);
    setOverview(data.overview);
    setFeedbackSourceText(translationInput.trim());
    setFeedbackCurrentTranslation(data.translation_artifacts.clean_text);
    const nextCandidates = await execute<{ entries: CandidateEntry[] }>("list_candidate_entries", buildProjectPayload(currentProjectId));
    setCandidates(nextCandidates?.entries ?? []);
    await refreshPipelineStatus(currentProjectId);
  }

  async function handleRunQa() {
    if (!currentProjectId) {
      return;
    }
    const data = await execute<{ report: QAReport; overview: ProjectOverview; learning_report?: LearningReport }>("run_qa", {
      ...buildProjectPayload(currentProjectId),
      chapter_id: overview?.project.active_chapter ?? activeChapter?.chapter_id,
    });
    if (!data) {
      return;
    }
    setQaReport(data.report);
    setOverview(data.overview);
    setLearningReport(data.learning_report ?? null);
    await refreshPipelineStatus(currentProjectId);
  }

  async function handleReviewCandidate(entry: CandidateEntry, status: string) {
    if (!currentProjectId) {
      return;
    }
    const data = await execute<{ overview: ProjectOverview }>("review_candidate_entry", {
      ...buildProjectPayload(currentProjectId),
      candidate_id: entry.id,
      status,
      reason: status === "verified" ? "Approved from coach workspace." : "Rejected from coach workspace.",
    });
    if (!data) {
      return;
    }
    setOverview(data.overview);
    const nextCandidates = await execute<{ entries: CandidateEntry[] }>("list_candidate_entries", buildProjectPayload(currentProjectId));
    setCandidates(nextCandidates?.entries ?? []);
  }

  async function handleReviewRule(rule: CandidateRule, status: string) {
    if (!currentProjectId) {
      return;
    }
    const data = await execute<{ overview: ProjectOverview }>("review_candidate_rule", {
      ...buildProjectPayload(currentProjectId),
      rule_id: rule.id,
      status,
      reason: status === "verified" ? "Applied from coach workspace." : "Rejected from coach workspace.",
      chapter_id: overview?.project.active_chapter ?? activeChapter?.chapter_id,
    });
    if (!data) {
      return;
    }
    setOverview(data.overview);
    const nextRules = await execute<{ rules: CandidateRule[] }>("list_candidate_rules", buildProjectPayload(currentProjectId));
    setCandidateRules(nextRules?.rules ?? []);
  }

  async function handleSubmitFeedback() {
    if (!currentProjectId) {
      return;
    }
    const data = await execute<{
      analysis: NaturalFeedbackAnalysis;
      rules: CandidateRule[];
      overview: ProjectOverview;
    }>("submit_natural_feedback", {
      ...buildProjectPayload(currentProjectId),
      chapter_id: feedbackScope === "chapter" ? overview?.project.active_chapter ?? activeChapter?.chapter_id : undefined,
      scope: feedbackScope,
      rule_type_hint: feedbackRuleHint,
      feedback_text: feedbackText,
      source_text: feedbackSourceText,
      current_translation: feedbackCurrentTranslation,
      preferred_translation: feedbackPreferredTranslation,
    });
    if (!data) {
      return;
    }
    setFeedbackAnalysis(data.analysis);
    setCandidateRules(data.rules);
    setOverview(data.overview);
    startTransition(() => {
      setScreen("Translation Coach");
    });
  }

  async function handleRunPipelineStage(stageId: string) {
    const payload: Record<string, unknown> = stageId === "compile" || stageId === "assign_pos"
      ? {}
      : buildProjectPayload(currentProjectId);
    if (stageId === "import") {
      payload.filepath = normalizeUserPath(importPath);
    }
    const data = await execute<{ pipeline: PipelineStatus }>("run_pipeline_stage", {
      ...payload,
      stage: stageId,
      text: stageId === "translate" ? translationInput.trim() : undefined,
      chapter_id: overview?.project.active_chapter ?? activeChapter?.chapter_id,
      config: overview?.config ?? {},
    });
    if (!data) {
      return;
    }
    if (data.pipeline) {
      setPipelineStatus(data.pipeline);
    }
    if (currentProjectId) {
      await hydrateProject(currentProjectId);
    } else {
      await refreshPipelineStatus();
    }
  }

  async function handleOpenDictionaryEntry(entry: DictionaryEntry) {
    setSelectedEntryId(entry.record_id);
    setDraftEntry(clone(entry));
    startTransition(() => {
      setScreen("Dictionary Editor");
    });
  }

  async function handleInspectToken(query: string) {
    setDictionaryQuery(query);
    await refreshDictionaryPage(1, query);
    await searchQuickDictionary(query);
    startTransition(() => {
      setScreen("Dictionary Editor");
    });
  }

  function handleSelectDictionaryEntry(entry: DictionaryEntry) {
    setSelectedEntryId(entry.record_id);
    setDraftEntry(clone(entry));
  }

  function handleToggleEntrySelection(recordId: string) {
    setSelectedEntryIds((current) =>
      current.includes(recordId) ? current.filter((item) => item !== recordId) : [...current, recordId],
    );
  }

  function handleDraftChange(field: string, value: string | boolean) {
    setDraftEntry((current) => {
      if (!current) {
        return current;
      }
      const next = clone(current);
      const metadata = { ...(next.metadata ?? {}) };
      switch (field) {
        case "priority":
          next.priority = Number(value) || next.priority;
          break;
        case "luat_nhan_trigger":
          next.luat_nhan_trigger = Boolean(value);
          metadata.luat_nhan_trigger = Boolean(value) ? 1 : 0;
          break;
        case "pinyin":
          next.pinyin = String(value).split(",").map((item) => item.trim()).filter(Boolean);
          break;
        case "full_explanation":
          next.full_explanation = String(value);
          metadata.full_explanation = String(value);
          break;
        case "pos_sub":
        case "entity_type":
        case "reorder_role":
        case "cultural_origin":
        case "genre_affinity":
        case "register_level":
          (next as Record<string, unknown>)[field] = String(value);
          if (String(value).trim()) {
            metadata[field] = String(value).trim();
          } else {
            delete metadata[field];
          }
          break;
        default:
          (next as Record<string, unknown>)[field] = value;
          break;
      }
      next.metadata = metadata;
      return next;
    });
  }

  async function handleSaveDictionaryEntry() {
    if (!draftEntry) {
      return;
    }
    const data = await execute<{ entry: DictionaryEntry; pipeline: PipelineStatus }>("update_dictionary_entry", {
      table_name: draftEntry.table_name,
      record_id: draftEntry.row_id,
      source: draftEntry.source,
      target_vi: draftEntry.target_vi,
      priority: draftEntry.priority,
      pos_tag: draftEntry.pos_tag ?? "",
      pos_sub: draftEntry.pos_sub ?? "",
      entity_type: draftEntry.entity_type ?? "",
      pinyin: Array.isArray(draftEntry.pinyin) ? draftEntry.pinyin.join(", ") : "",
      traditional: draftEntry.traditional ?? "",
      luat_nhan_trigger: Boolean(draftEntry.luat_nhan_trigger),
      reorder_role: draftEntry.reorder_role ?? "",
      notes: draftEntry.notes,
      full_explanation: draftEntry.full_explanation,
      metadata: draftEntry.metadata ?? {},
    });
    if (!data) {
      return;
    }
    setDraftEntry(clone(data.entry));
    setSelectedEntryId(data.entry.record_id);
    setPipelineStatus(data.pipeline ?? pipelineStatus);
    await refreshDictionaryPage(dictionaryPage, dictionaryQuery);
    await searchQuickDictionary(draftEntry.source);
  }

  async function handleApplyBulkUpdate() {
    if (!selectedEntryIds.length) {
      return;
    }
    const selected = dictionaryEntries.filter((entry) => selectedEntryIds.includes(entry.record_id));
    for (const entry of selected) {
      await execute("update_dictionary_entry", {
        table_name: entry.table_name,
        record_id: entry.row_id,
        pos_tag: bulkPosTag || undefined,
        entity_type: bulkEntityType || undefined,
      });
    }
    setSelectedEntryIds([]);
    await refreshDictionaryPage(dictionaryPage, dictionaryQuery);
    await refreshPipelineStatus(currentProjectId);
  }

  function handleExportFiltered() {
    downloadJson("dictionary-filtered-export.json", {
      query: dictionaryQuery,
      filters: { tableFilter, sourceDictFilter, posTagFilter, entityTypeFilter },
      total: dictionaryTotal,
      entries: dictionaryEntries,
    });
  }

  function handleFeedbackFieldChange(field: string, value: string) {
    switch (field) {
      case "feedbackText":
        setFeedbackText(value);
        break;
      case "feedbackSourceText":
        setFeedbackSourceText(value);
        break;
      case "feedbackCurrentTranslation":
        setFeedbackCurrentTranslation(value);
        break;
      case "feedbackPreferredTranslation":
        setFeedbackPreferredTranslation(value);
        break;
      case "feedbackScope":
        setFeedbackScope(value);
        break;
      case "feedbackRuleHint":
        setFeedbackRuleHint(value);
        break;
      default:
        break;
    }
  }

  function renderScreen() {
    switch (screen) {
      case "Dashboard":
        return (
          <DashboardScreen
            overview={overview}
            pipeline={pipelineStatus}
            quickQuery={dictionaryQuery}
            quickResults={dictionaryQuickResults}
            onQuickQueryChange={setDictionaryQuery}
            onQuickSearch={() => void searchQuickDictionary(dictionaryQuery)}
            onOpenDictionaryEntry={(entry) => void handleOpenDictionaryEntry(entry)}
          />
        );
      case "Dictionary Editor":
        return (
          <DictionaryEditorScreen
            busy={busy}
            backendAvailable={backendAvailable}
            query={dictionaryQuery}
            filters={dictionaryFilters}
            tableFilter={tableFilter}
            sourceDictFilter={sourceDictFilter}
            posTagFilter={posTagFilter}
            entityTypeFilter={entityTypeFilter}
            page={dictionaryPage}
            pageSize={50}
            total={dictionaryTotal}
            entries={dictionaryEntries}
            selectedEntry={dictionaryEntries.find((entry) => entry.record_id === selectedEntryId) ?? null}
            draft={draftEntry}
            selectedIds={selectedEntryIds}
            bulkPosTag={bulkPosTag}
            bulkEntityType={bulkEntityType}
            onQueryChange={setDictionaryQuery}
            onTableFilterChange={setTableFilter}
            onSourceDictFilterChange={setSourceDictFilter}
            onPosTagFilterChange={setPosTagFilter}
            onEntityTypeFilterChange={setEntityTypeFilter}
            onSearch={(page) => void refreshDictionaryPage(page ?? 1, dictionaryQuery)}
            onSelectEntry={handleSelectDictionaryEntry}
            onToggleEntrySelection={handleToggleEntrySelection}
            onDraftChange={handleDraftChange}
            onSave={() => void handleSaveDictionaryEntry()}
            onBulkPosTagChange={setBulkPosTag}
            onBulkEntityTypeChange={setBulkEntityType}
            onApplyBulkUpdate={() => void handleApplyBulkUpdate()}
            onExportFiltered={handleExportFiltered}
          />
        );
      case "Translation Workspace":
        return (
          <TranslationWorkspaceScreen
            busy={busy}
            backendAvailable={backendAvailable}
            importPath={importPath}
            translationInput={translationInput}
            overview={overview}
            translation={translation}
            qaReport={qaReport}
            onImportPathChange={setImportPath}
            onPickImportPath={(kind) => void pickImportPath(kind)}
            onImport={() => void handleImport()}
            onTranslationInputChange={setTranslationInput}
            onTranslate={() => void handleTranslate()}
            onRunQa={() => void handleRunQa()}
            onSelectChapter={(chapterId, chapterText) => void handleSelectChapter(chapterId, chapterText)}
            onInspectToken={(query) => void handleInspectToken(query)}
          />
        );
      case "Translation Coach":
        return (
          <CoachScreen
            busy={busy}
            backendAvailable={backendAvailable}
            overview={overview}
            candidates={candidates}
            candidateRules={candidateRules}
            learningReport={learningReport}
            feedbackAnalysis={feedbackAnalysis}
            feedbackText={feedbackText}
            feedbackSourceText={feedbackSourceText}
            feedbackCurrentTranslation={feedbackCurrentTranslation}
            feedbackPreferredTranslation={feedbackPreferredTranslation}
            feedbackScope={feedbackScope}
            feedbackRuleHint={feedbackRuleHint}
            ruleFilter={ruleFilter}
            candidateFilter={candidateFilter}
            candidateQuery={candidateQuery}
            onFeedbackFieldChange={handleFeedbackFieldChange}
            onRuleFilterChange={setRuleFilter}
            onCandidateFilterChange={setCandidateFilter}
            onCandidateQueryChange={setCandidateQuery}
            onSubmitFeedback={() => void handleSubmitFeedback()}
            onReviewRule={(rule, status) => void handleReviewRule(rule, status)}
            onReviewCandidate={(entry, status) => void handleReviewCandidate(entry, status)}
            onInspectToken={(query) => void handleInspectToken(query)}
          />
        );
      case "Pipeline Monitor":
        return (
          <PipelineMonitorScreen
            busy={busy}
            backendAvailable={backendAvailable}
            pipeline={pipelineStatus}
            events={events}
            warnings={warnings}
            onRunStage={(stageId) => void handleRunPipelineStage(stageId)}
          />
        );
      case "Settings":
        return (
          <SettingsScreen
            transport={transport}
            overview={overview}
            pipeline={pipelineStatus}
            workspaceBaseDir={workspaceBaseDir}
            onWorkspaceBaseDirChange={setWorkspaceBaseDir}
            onRunStage={(stageId) => void handleRunPipelineStage(stageId)}
            busy={busy}
            backendAvailable={backendAvailable}
          />
        );
      default:
        return null;
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-kicker">Pipeline UI</span>
          <h1>DrDuc Translator</h1>
          <p>Glassmorphism UI được tách module hóa thành 6 screen có dictionary CRUD và pipeline monitor.</p>
        </div>

        <div className="transport-card">
          <span className="pill">{transport?.mode ?? "loading"} transport</span>
          <p>{statusMessage}</p>
        </div>

        <form className="panel mini-panel" onSubmit={handleCreateProject}>
          <div className="panel-head">
            <div>
              <h3>Project Intake</h3>
              <p>Tao nhanh project moi tai workspace root da normalize.</p>
            </div>
          </div>
          <div className="form-grid">
            <label className="field">
              <span>Project Id</span>
              <input className="input" value={createProjectId} onChange={(event) => setCreateProjectId(event.target.value)} />
            </label>
            <label className="field">
              <span>Workspace Root</span>
              <input className="input" value={workspaceBaseDir} onChange={(event) => setWorkspaceBaseDir(event.target.value)} />
            </label>
            <button className="button" type="submit" disabled={busy || !backendAvailable}>Create Project</button>
          </div>
        </form>

        <nav className="nav-stack">
          {SCREENS.map((item) => (
            <button
              key={item}
              className={`nav-button ${item === screen ? "active" : ""}`}
              type="button"
              onClick={() => startTransition(() => setScreen(item))}
            >
              {item}
            </button>
          ))}
        </nav>

        <div className="sidebar-section">
          <h2>Projects</h2>
          <div className="list-stack">
            {projects.map((project) => (
              <button
                key={project.project_id}
                className={`list-card ${project.project_id === currentProjectId ? "active" : ""}`}
                type="button"
                onClick={() => startTransition(() => setSelectedProjectId(project.project_id))}
              >
                <strong>{project.project_id}</strong>
                <span>{project.source_language} -&gt; {project.target_language}</span>
                <small>{project.project_dir}</small>
              </button>
            ))}
          </div>
        </div>
      </aside>

      <main className="workspace">
        <header className="hero">
          <div>
            <span className="brand-kicker">Active Slice</span>
            <h2>{overview?.project.project_id ?? "No project selected"}</h2>
            <p>{statusMessage}</p>
          </div>
          <div className="hero-actions">
            <span className={`pill ${busy ? "busy" : ""}`}>{busy ? "Running" : "Idle"}</span>
            <span className="pill subtle">{overview?.project.active_chapter ?? "No active chapter"}</span>
          </div>
        </header>

        <section className="metrics-row">
          <MetricCard label="Chapters" value={overview?.counts.chapters ?? 0} />
          <MetricCard label="Segments" value={overview?.counts.segments ?? 0} />
          <MetricCard label="Candidates" value={overview?.counts.candidates_total ?? 0} />
          <MetricCard label="QA Issues" value={overview?.counts.qa_issues ?? 0} />
        </section>

        {warnings.length > 0 ? (
          <section className="warning-strip">
            {warnings.map((warning) => (
              <p key={warning}>{warning}</p>
            ))}
          </section>
        ) : null}

        <section className="screen-area">{renderScreen()}</section>

        <section className="split-grid footer-grid">
          <Panel title="Command Timeline" subtitle="Event payload tu sidecar giup debug va monitor stage transitions.">
            <div className="list-stack">
              {events.length ? (
                events.map((event, index) => (
                  <div key={`${event.stage}-${index}`} className="timeline-row">
                    <span className="pill subtle">{event.progress}%</span>
                    <div>
                      <strong>{event.stage}</strong>
                      <p>{event.message}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="empty-state">No command events recorded yet.</p>
              )}
            </div>
          </Panel>
          <Panel title="Runtime Snapshot" subtitle="Path artifact da duoc normalize, khong con truot goc thu muc nhu cac lan truoc.">
            <div className="detail-grid">
              <InfoLine label="Output" value={translation?.paths.clean || overview?.artifacts.output_path || "Unavailable"} />
              <InfoLine label="Draft" value={translation?.paths.draft || overview?.artifacts.draft_path || "Unavailable"} />
              <InfoLine label="Trace" value={translation?.paths.trace || overview?.artifacts.trace_path || "Unavailable"} />
              <InfoLine label="QA" value={overview?.artifacts.qa_report_path || "Unavailable"} />
            </div>
          </Panel>
        </section>
      </main>
    </div>
  );
}

function readStoredValue(key: string, fallback: string): string {
  if (typeof window === "undefined") {
    return fallback;
  }
  return window.localStorage.getItem(key) ?? fallback;
}

function writeStoredValue(key: string, value: string) {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(key, value);
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}
