import React, {
  startTransition,
  useDeferredValue,
  useEffect,
  useState,
} from "react";
import { invoke, isTauri } from "@tauri-apps/api/core";
import type {
  CandidateEntry,
  CandidateRule,
  CommandEvent,
  CommandName,
  DictionaryEntry,
  LearningReport,
  NaturalFeedbackAnalysis,
  ProjectOverview,
  ProjectRecord,
  QAReport,
  Transport,
  TranslationArtifacts,
} from "./protocol";
import { PROTOCOL_VERSION } from "./protocol";
import { createPreferredTransport } from "./transport";

const SCREENS = [
  "Project Manager",
  "Dictionary Manager",
  "Translation Workspace",
  "Translation Coach",
  "Entity & Relationship Viewer",
  "Pre-Translation Review",
  "QA Report Viewer",
  "Settings",
] as const;

type ScreenKey = (typeof SCREENS)[number];

export function App() {
  const [screen, setScreen] = useState<ScreenKey>("Project Manager");
  const [transport, setTransport] = useState<Transport | null>(null);
  const [projects, setProjects] = useState<ProjectRecord[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [overview, setOverview] = useState<ProjectOverview | null>(null);
  const [translation, setTranslation] = useState<TranslationArtifacts | null>(null);
  const [qaReport, setQaReport] = useState<QAReport | null>(null);
  const [candidates, setCandidates] = useState<CandidateEntry[]>([]);
  const [candidateRules, setCandidateRules] = useState<CandidateRule[]>([]);
  const [learningReport, setLearningReport] = useState<LearningReport | null>(null);
  const [feedbackAnalysis, setFeedbackAnalysis] = useState<NaturalFeedbackAnalysis | null>(null);
  const [statusMessage, setStatusMessage] = useState("Load a project to inspect the workflow.");
  const [events, setEvents] = useState<CommandEvent[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [createProjectId, setCreateProjectId] = useState("project-001");
  const [workspaceBaseDir, setWorkspaceBaseDir] = useState("workspace_projects");
  const [importPath, setImportPath] = useState("");
  const [translationInput, setTranslationInput] = useState("");
  const [dictionaryQuery, setDictionaryQuery] = useState("");
  const [dictionaryResults, setDictionaryResults] = useState<DictionaryEntry[]>([]);
  const [candidateFilter, setCandidateFilter] = useState("all");
  const [candidateQuery, setCandidateQuery] = useState("");
  const [ruleFilter, setRuleFilter] = useState("all");
  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackSourceText, setFeedbackSourceText] = useState("");
  const [feedbackCurrentTranslation, setFeedbackCurrentTranslation] = useState("");
  const [feedbackPreferredTranslation, setFeedbackPreferredTranslation] = useState("");
  const [feedbackScope, setFeedbackScope] = useState("chapter");
  const [feedbackRuleHint, setFeedbackRuleHint] = useState("auto");
  const [llmEndpoint, setLlmEndpoint] = useState(() => readStoredValue("drduc.llm.endpoint", ""));
  const [llmModel, setLlmModel] = useState(() => readStoredValue("drduc.llm.model", ""));
  const [llmAuthHeader, setLlmAuthHeader] = useState(() => readStoredValue("drduc.llm.authHeader", "Authorization"));
  const [llmAuthPrefix, setLlmAuthPrefix] = useState(() => readStoredValue("drduc.llm.authPrefix", "Bearer "));
  const [llmToken, setLlmToken] = useState(() => readStoredValue("drduc.llm.token", ""));
  const deferredCandidateQuery = useDeferredValue(candidateQuery);
  const deferredRuleFilter = useDeferredValue(ruleFilter);
  const backendAvailable = transport ? transport.mode !== "browser" : false;
  const workspaceRoot = workspaceBaseDir.trim() || "workspace_projects";
  const currentProjectId = overview?.project.project_id ?? selectedProjectId;
  const selectedProject =
    projects.find((project) => project.project_id === selectedProjectId) ?? null;
  const activeChapter =
    overview?.chapters.find((chapter) => chapter.chapter_id === overview.project.active_chapter) ??
    overview?.chapters[0] ??
    null;

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const nextTransport = await createPreferredTransport();
      if (cancelled) {
        return;
      }
      setTransport(nextTransport);
      if (nextTransport.mode === "tauri") {
        setStatusMessage("Native Tauri bridge detected. Requests will be forwarded to the Python sidecar.");
        return;
      }
      if (nextTransport.mode === "http") {
        setStatusMessage("HTTP bridge detected. Browser is connected to the live Python pipeline.");
        return;
      }
      if (nextTransport.mode === "demo") {
        setStatusMessage("Demo transport is active because VITE_ENABLE_DEMO=1 was provided explicitly.");
        return;
      }
      setStatusMessage("Browser preview detected. Open the native Tauri app to work with real project data.");
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
  }, [transport]);

  useEffect(() => {
    if (!transport || transport.mode === "browser" || !selectedProjectId) {
      return;
    }
    void hydrateProject(selectedProjectId);
  }, [selectedProjectId, transport]);

  useEffect(() => {
    const nextText = activeChapter?.text ?? "";
    if (!translationInput && nextText) {
      setTranslationInput(nextText);
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
    writeStoredValue("drduc.llm.endpoint", llmEndpoint);
  }, [llmEndpoint]);

  useEffect(() => {
    writeStoredValue("drduc.llm.model", llmModel);
  }, [llmModel]);

  useEffect(() => {
    writeStoredValue("drduc.llm.authHeader", llmAuthHeader);
  }, [llmAuthHeader]);

  useEffect(() => {
    writeStoredValue("drduc.llm.authPrefix", llmAuthPrefix);
  }, [llmAuthPrefix]);

  useEffect(() => {
    writeStoredValue("drduc.llm.token", llmToken);
  }, [llmToken]);

  const lockedEntities = asRecordArray(overview?.config.locked_entities);
  const candidateStatus = overview?.counts.candidate_status ?? {};
  const filteredCandidates = candidates.filter((entry) => {
    const matchesStatus = candidateFilter === "all" || entry.status === candidateFilter;
    const query = deferredCandidateQuery.trim().toLowerCase();
    if (!query) {
      return matchesStatus;
    }
    const haystack = `${entry.source_text} ${entry.target_text} ${entry.reason}`.toLowerCase();
    return matchesStatus && haystack.includes(query);
  });
  const filteredRules = candidateRules.filter((rule) => deferredRuleFilter === "all" || rule.status === deferredRuleFilter);

  async function execute<T>(
    command: CommandName,
    payload: Record<string, unknown> = {},
  ): Promise<T | null> {
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
        setImportPath(selectedPath);
        setStatusMessage(`Selected ${kind === "file" ? "source file" : "source folder"}: ${selectedPath}`);
      }
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : String(error));
    }
  }

  async function refreshProjects(baseDir = workspaceRoot) {
    const data = await execute<{ projects: ProjectRecord[] }>("list_projects", {
      base_dir: baseDir,
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

  async function refreshCandidateRules(projectId: string) {
    const data = await execute<{ rules: CandidateRule[] }>("list_candidate_rules", {
      ...buildProjectPayload(projectId),
    });
    setCandidateRules(data?.rules ?? []);
  }

  async function refreshLearningReport(projectId: string, chapterId: string | null | undefined) {
    const data = await execute<{ report: LearningReport }>("load_learning_report", {
      ...buildProjectPayload(projectId),
      chapter_id: chapterId,
    });
    setLearningReport(data?.report ?? null);
  }

  async function hydrateProject(projectId: string) {
    const nextOverview = await execute<ProjectOverview>("get_project_overview", {
      ...buildProjectPayload(projectId),
    });
    if (!nextOverview) {
      return;
    }
    setOverview(nextOverview);

    const nextArtifacts = await execute<TranslationArtifacts>("load_translation_artifacts", {
      ...buildProjectPayload(projectId),
      chapter_id: nextOverview.project.active_chapter,
    });
    setTranslation(nextArtifacts);

    const nextReport = await execute<{ report: QAReport }>("load_qa_report", {
      ...buildProjectPayload(projectId),
      chapter_id: nextOverview.project.active_chapter,
    });
    setQaReport(nextReport?.report ?? null);

    const nextCandidates = await execute<{ entries: CandidateEntry[] }>("list_candidate_entries", {
      ...buildProjectPayload(projectId),
    });
    setCandidates(nextCandidates?.entries ?? []);

    const nextRules = await execute<{ rules: CandidateRule[] }>("list_candidate_rules", {
      ...buildProjectPayload(projectId),
    });
    setCandidateRules(nextRules?.rules ?? []);

    const nextLearning = await execute<{ report: LearningReport }>("load_learning_report", {
      ...buildProjectPayload(projectId),
      chapter_id: nextOverview.project.active_chapter,
    });
    setLearningReport(nextLearning?.report ?? null);

    const seededEntityQuery = typeof nextOverview.entities[0]?.source === "string"
      ? nextOverview.entities[0].source
      : "";
    const fallbackQuery = dictionaryQuery.trim() || seededEntityQuery || "一";
    setDictionaryQuery(fallbackQuery);
    const nextDictionary = await execute<{ entries: DictionaryEntry[] }>("search_dictionary_entries", {
      query: fallbackQuery,
      limit: 12,
    });
    setDictionaryResults(nextDictionary?.entries ?? []);
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
    await refreshLearningReport(currentProjectId, chapterId);
  }

  async function handleCreateProject(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const projectId = createProjectId.trim() || "project-001";
    const baseDir = workspaceRoot;
    const data = await execute<{ project_id: string }>("create_project", {
      project_id: projectId,
      base_dir: baseDir,
    });
    if (!data) {
      return;
    }
    await refreshProjects(baseDir);
    startTransition(() => {
      setSelectedProjectId(data.project_id);
      setScreen("Project Manager");
    });
  }

  async function handleImport() {
    if (!currentProjectId) {
      return;
    }
    const filepath = importPath.trim();
    if (!filepath) {
      setStatusMessage("Select a real source file or source directory before importing.");
      return;
    }
    const data = await execute<{
      chapters: Array<{ chapter_id: string; text: string }>;
      overview: ProjectOverview;
    }>("import_file", {
      ...buildProjectPayload(currentProjectId),
      filepath,
    });
    if (!data) {
      return;
    }
    const importedOverview = data.overview;
    const importedChapters = data.chapters.length > 0 ? data.chapters : importedOverview.chapters;
    setOverview(importedOverview);
    setTranslation(null);
    setQaReport(null);
    setCandidates([]);
    setCandidateRules([]);
    setLearningReport(null);
    setFeedbackAnalysis(null);
    setTranslationInput(importedChapters[0]?.text ?? "");
    setFeedbackSourceText(importedChapters[0]?.text ?? "");
  }

  async function handleTranslate() {
    if (!currentProjectId) {
      return;
    }
    const data = await execute<{
      translation_artifacts: TranslationArtifacts;
      overview: ProjectOverview;
    }>("translate", {
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
    const nextCandidates = await execute<{ entries: CandidateEntry[] }>("list_candidate_entries", {
      ...buildProjectPayload(currentProjectId),
    });
    setCandidates(nextCandidates?.entries ?? []);
    startTransition(() => {
      setScreen("Translation Workspace");
    });
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
    startTransition(() => {
      setScreen("QA Report Viewer");
    });
  }

  async function handleReviewCandidate(entry: CandidateEntry, status: string) {
    if (!currentProjectId) {
      return;
    }
    const data = await execute<{ overview: ProjectOverview }>("review_candidate_entry", {
      ...buildProjectPayload(currentProjectId),
      candidate_id: entry.id,
      status,
      reason: status === "verified" ? "Approved from desktop shell." : "Needs manual rewrite.",
    });
    if (!data) {
      return;
    }
    setOverview(data.overview);
    const nextCandidates = await execute<{ entries: CandidateEntry[] }>("list_candidate_entries", {
      ...buildProjectPayload(currentProjectId),
    });
    setCandidates(nextCandidates?.entries ?? []);
    const nextArtifacts = await execute<TranslationArtifacts>("load_translation_artifacts", {
      ...buildProjectPayload(currentProjectId),
      chapter_id: data.overview.project.active_chapter ?? entry.chapter_id,
    });
    setTranslation(nextArtifacts);
  }

  async function handleSubmitFeedback() {
    if (!currentProjectId) {
      return;
    }
    const llmConfigured = llmEndpoint.trim() && llmModel.trim() && llmToken.trim();
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
      llm: llmConfigured
        ? {
          endpoint: llmEndpoint.trim(),
          model: llmModel.trim(),
          token: llmToken.trim(),
          auth_header: llmAuthHeader.trim() || "Authorization",
          auth_prefix: llmAuthPrefix.trim() || "Bearer ",
        }
        : undefined,
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

  async function handleReviewRule(rule: CandidateRule, status: string) {
    if (!currentProjectId) {
      return;
    }
    const data = await execute<{
      rule: CandidateRule;
      overview: ProjectOverview;
    }>("review_candidate_rule", {
      ...buildProjectPayload(currentProjectId),
      rule_id: rule.id,
      status,
      reason: status === "verified" ? "Approved from translation coach." : "Rejected from translation coach.",
      chapter_id: overview?.project.active_chapter ?? activeChapter?.chapter_id,
    });
    if (!data) {
      return;
    }
    setOverview(data.overview);
    await refreshCandidateRules(currentProjectId);
  }

  async function handleSearchDictionary(queryOverride?: string) {
    const query = (queryOverride ?? dictionaryQuery).trim() || "一";
    setDictionaryQuery(query);
    const data = await execute<{ entries: DictionaryEntry[] }>("search_dictionary_entries", {
      query,
      limit: 12,
    });
    setDictionaryResults(data?.entries ?? []);
  }

  function renderScreen() {
    if (!overview) {
      if (screen === "Project Manager") {
        return (
          <div className="panel-stack">
            <Panel
              title="Project Control"
              subtitle="Create a workspace first, then import source material and continue through the translation workflow."
            >
              <form className="form-grid" onSubmit={handleCreateProject}>
                <label className="field">
                  <span>Project Id</span>
                  <input
                    className="input"
                    value={createProjectId}
                    onChange={(event) => setCreateProjectId(event.target.value)}
                    placeholder="project-001"
                  />
                </label>
                <label className="field">
                  <span>Workspace Project Root</span>
                  <input
                    className="input"
                    value={workspaceBaseDir}
                    onChange={(event) => setWorkspaceBaseDir(event.target.value)}
                    placeholder="workspace_projects"
                  />
                </label>
                <div className="action-row">
                  <button className="button" type="submit" disabled={busy || !backendAvailable}>
                    Create Project
                  </button>
                </div>
              </form>
              <div className="detail-grid">
                <InfoLine label="Project" value="Not selected" />
                <InfoLine label="Directory" value="Create or select a project first" />
                <InfoLine label="Languages" value="zh -> vi" />
                <InfoLine label="Active chapter" value="Not selected" />
              </div>
            </Panel>
            <Panel
              title="Existing Projects"
              subtitle="Choose an existing workspace from the current base directory once it is available."
            >
              <div className="list-stack">
                {projects.length > 0 ? (
                  projects.map((project) => (
                    <button
                      key={project.project_id}
                      className={`list-card ${project.project_id === selectedProjectId ? "active" : ""}`}
                      type="button"
                      onClick={() => {
                        startTransition(() => {
                          setSelectedProjectId(project.project_id);
                        });
                      }}
                    >
                      <strong>{project.project_id}</strong>
                      <span>
                        {project.source_language}
                        {" -> "}
                        {project.target_language}
                      </span>
                      <small>{project.project_dir}</small>
                    </button>
                  ))
                ) : (
                  <p className="empty-state">No projects found yet. Create one to unlock the workflow.</p>
                )}
              </div>
            </Panel>
          </div>
        );
      }

      if (screen === "Settings") {
        return (
          <div className="panel-stack">
            <Panel
              title="Settings and Contract"
              subtitle="This shell is wired against the expanded Phase 10 contract and prefers the native Tauri bridge for real work."
            >
              <div className="detail-grid">
                <InfoLine label="Protocol version" value={PROTOCOL_VERSION} />
                <InfoLine label="Transport mode" value={transport?.mode ?? "initializing"} />
                <InfoLine label="Supported commands" value={transport?.supportedCommands.join(", ") ?? "Loading"} />
                <InfoLine label="Native blocker" value="Create or open a project to expose artifact paths and workflow state." />
              </div>
            </Panel>
          </div>
        );
      }

      return (
        <Panel
          title="Desktop Shell"
          subtitle="Open the Project Manager screen to create or select a project before using the rest of the workflow."
        >
          <p className="empty-state">
            {transport?.mode === "browser"
              ? "Browser preview is available for layout inspection only. Open the native Tauri app to work with real files."
              : transport
                ? `The shell is ready in ${transport.mode} transport mode, aligned with the expanded Python sidecar contract.`
                : "Initializing transport and loading the desktop shell."}
          </p>
        </Panel>
      );
    }

    switch (screen) {
      case "Project Manager":
        return (
          <div className="panel-stack">
            <Panel
              title="Project Control"
              subtitle="Create a workspace, import source material, and keep the active chapter aligned with state."
            >
              <form className="form-grid" onSubmit={handleCreateProject}>
                <label className="field">
                  <span>Project Id</span>
                  <input
                    className="input"
                    value={createProjectId}
                    onChange={(event) => setCreateProjectId(event.target.value)}
                    placeholder="project-001"
                  />
                </label>
                <label className="field">
                  <span>Workspace Project Root</span>
                  <input
                    className="input"
                    value={workspaceBaseDir}
                    onChange={(event) => setWorkspaceBaseDir(event.target.value)}
                    placeholder="workspace_projects"
                  />
                </label>
                <div className="action-row">
                  <button className="button" type="submit" disabled={busy || !backendAvailable}>
                    Create Project
                  </button>
                  <button
                    className="button secondary"
                    type="button"
                    disabled={busy || !backendAvailable}
                    onClick={() => {
                      startTransition(() => {
                        setScreen("Pre-Translation Review");
                      });
                    }}
                  >
                    Review Import Stage
                  </button>
                </div>
              </form>
              <div className="detail-grid">
                <InfoLine label="Project" value={overview.project.project_id} />
                <InfoLine label="Directory" value={overview.project.project_dir} />
                <InfoLine label="Languages" value={`${overview.project.source_language} -> ${overview.project.target_language}`} />
                <InfoLine label="Active chapter" value={overview.project.active_chapter ?? "Not selected"} />
              </div>
            </Panel>
            <Panel
              title="Chapters"
              subtitle="Imported chapters are available to the translation workspace and QA stage."
            >
              <div className="list-stack">
                {overview.chapters.length > 0 ? (
                  overview.chapters.map((chapter) => (
                    <button
                      key={chapter.chapter_id}
                      className={`list-card ${chapter.chapter_id === activeChapter?.chapter_id ? "active" : ""}`}
                      type="button"
                      onClick={() => void handleSelectChapter(chapter.chapter_id, chapter.text)}
                    >
                      <strong>{chapter.title}</strong>
                      <span>{chapter.chapter_id}</span>
                      <small>{chapter.source_path ?? "Pending source path"}</small>
                    </button>
                  ))
                ) : (
                  <p className="empty-state">Import a document to populate chapter artifacts.</p>
                )}
              </div>
            </Panel>
          </div>
        );
      case "Dictionary Manager":
        return (
          <div className="panel-stack">
            <Panel
              title="Dictionary Explorer"
              subtitle="Inspect compiled dictionary metadata, explanations, readings, and provenance directly from the runtime database."
            >
              <div className="toolbar">
                <label className="field grow">
                  <span>Dictionary Query</span>
                  <input
                    className="input"
                    value={dictionaryQuery}
                    onChange={(event) => setDictionaryQuery(event.target.value)}
                    placeholder="一 or 林动"
                  />
                </label>
                <button className="button" type="button" disabled={busy || !backendAvailable} onClick={() => void handleSearchDictionary()}>
                  Search Dictionary
                </button>
              </div>
              <div className="list-stack">
                {dictionaryResults.length > 0 ? (
                  dictionaryResults.map((entry) => (
                    <article key={`${entry.source}-${entry.target_vi}-${entry.source_dict}`} className="candidate-card">
                      <div className="candidate-head">
                        <div>
                          <strong>{entry.source}</strong>
                          <p>{entry.target_vi}</p>
                        </div>
                        <span className={`pill tone-${entry.status}`}>{entry.status}</span>
                      </div>
                      <div className="tag-row">
                        <span className="pill subtle">{entry.source_dict}</span>
                        <span className="pill subtle">priority {entry.priority}</span>
                        <span className="pill subtle">hit {entry.hit_count}</span>
                      </div>
                      <p className="candidate-options">
                        Pinyin: {entry.pinyin.join(", ") || "n/a"} | Han-Viet: {entry.han_viet_readings.join(", ") || "n/a"}
                      </p>
                      {entry.alternative_meanings.length > 0 ? (
                        <p className="candidate-options">
                          Alternative meanings: {entry.alternative_meanings.join(" | ")}
                        </p>
                      ) : null}
                      <p className="dictionary-explanation">{entry.full_explanation || entry.notes || "No detailed explanation available."}</p>
                    </article>
                  ))
                ) : (
                  <p className="empty-state">No dictionary entries matched the current query.</p>
                )}
              </div>
            </Panel>
            <Panel
              title="Candidate Review"
              subtitle="Ambiguity and unresolved traces are promoted into reviewable entries."
            >
              <div className="toolbar">
                <label className="field compact">
                  <span>Status</span>
                  <select
                    className="input"
                    value={candidateFilter}
                    onChange={(event) => setCandidateFilter(event.target.value)}
                  >
                    <option value="all">All</option>
                    <option value="candidate">Candidate</option>
                    <option value="verified">Verified</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </label>
                <label className="field compact grow">
                  <span>Search</span>
                  <input
                    className="input"
                    value={candidateQuery}
                    onChange={(event) => setCandidateQuery(event.target.value)}
                    placeholder="source term or target draft"
                  />
                </label>
              </div>
              <div className="list-stack">
                {filteredCandidates.length > 0 ? (
                  filteredCandidates.map((entry) => (
                    <div key={entry.id} className="candidate-card">
                      <div className="candidate-head">
                        <div>
                          <strong>{entry.source_text}</strong>
                          <p>{entry.target_text}</p>
                        </div>
                        <span className={`pill tone-${entry.status}`}>{entry.status}</span>
                      </div>
                      <div className="tag-row">
                        <span className="pill subtle">{entry.fallback_level}</span>
                        <span className="pill subtle">{entry.segment_id}</span>
                        <span className="pill subtle">{entry.reason}</span>
                      </div>
                      <p className="candidate-options">{entry.candidates.join(" | ")}</p>
                      <div className="action-row">
                        <button className="button" type="button" disabled={!backendAvailable} onClick={() => void handleReviewCandidate(entry, "verified")}>
                          Verify
                        </button>
                        <button className="button secondary" type="button" disabled={!backendAvailable} onClick={() => void handleReviewCandidate(entry, "rejected")}>
                          Reject
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="empty-state">No candidate entries match the current filters.</p>
                )}
              </div>
            </Panel>
          </div>
        );
      case "Translation Workspace":
        return (
          <div className="panel-stack">
            <Panel
              title="Translation Workspace"
              subtitle="Run the active chapter through the sidecar contract and inspect clean output, draft markers, and trace evidence."
            >
              <div className="split-grid">
                <label className="field">
                  <span>Source Text</span>
                  <textarea
                    className="textarea"
                    value={translationInput}
                    onChange={(event) => setTranslationInput(event.target.value)}
                  />
                </label>
                <div className="action-column">
                  <button className="button" type="button" disabled={busy || !backendAvailable} onClick={() => void handleTranslate()}>
                    Translate Active Slice
                  </button>
                  <button className="button secondary" type="button" disabled={busy || !backendAvailable} onClick={() => void handleRunQa()}>
                    Run QA
                  </button>
                </div>
              </div>
            </Panel>
            <div className="split-grid">
              <Panel title="Clean Output" subtitle="Reader-facing translation without inline annotations.">
                <pre className="output-block">{translation?.clean_text || "No translation available yet."}</pre>
              </Panel>
              <Panel title="Annotated Draft" subtitle="Ambiguity and unresolved markers remain visible for review.">
                <pre className="output-block">{translation?.draft_text || "No draft annotations available yet."}</pre>
              </Panel>
            </div>
            <Panel
              title="Trace Evidence"
              subtitle="Each segment exposes the selected candidate, fallback level, and the evidence trail needed for review."
            >
              <div className="list-stack">
                {translation?.segments.length ? (
                  translation.segments.map((segment) => (
                    <article key={segment.sentence_id} className="trace-card">
                      <div className="trace-head">
                        <strong>{segment.sentence_id}</strong>
                        <span className={`pill tone-${segment.fallback_level ?? "runtime"}`}>{segment.fallback_level ?? "runtime"}</span>
                      </div>
                      <p>{segment.source_text}</p>
                      <div className="trace-row">
                        {segment.trace.map((trace) => (
                          <span key={`${segment.sentence_id}-${trace.source}-${trace.reason}`} className="pill subtle">
                            {trace.source}
                            {" -> "}
                            {trace.selected} ({trace.fallback_level})
                          </span>
                        ))}
                      </div>
                    </article>
                  ))
                ) : (
                  <p className="empty-state">Translate the active slice to inspect trace payloads.</p>
                )}
              </div>
            </Panel>
          </div>
        );
      case "Translation Coach":
        return (
          <div className="panel-stack">
            <Panel
              title="Translation Coach"
              subtitle="Convert natural-language editorial feedback into reviewable rules, style tuning, and reusable phrase fixes."
            >
              <div className="split-grid">
                <div className="form-grid">
                  <div className="toolbar">
                    <label className="field compact">
                      <span>Scope</span>
                      <select className="input" value={feedbackScope} onChange={(event) => setFeedbackScope(event.target.value)}>
                        <option value="chapter">Chapter</option>
                        <option value="project">Project</option>
                      </select>
                    </label>
                    <label className="field compact">
                      <span>Hint</span>
                      <select className="input" value={feedbackRuleHint} onChange={(event) => setFeedbackRuleHint(event.target.value)}>
                        <option value="auto">Auto</option>
                        <option value="style">Style</option>
                        <option value="phrase">Phrase</option>
                        <option value="term">Term</option>
                        <option value="entity">Entity</option>
                        <option value="naturalization">Naturalization</option>
                      </select>
                    </label>
                  </div>
                  <label className="field">
                    <span>Feedback</span>
                    <textarea
                      className="textarea"
                      value={feedbackText}
                      onChange={(event) => setFeedbackText(event.target.value)}
                      placeholder="Ví dụ: Hội thoại chương này cần tự nhiên hơn, xưng hô bớt cứng. Đổi “夏天骐” thành “Hạ Thiên Kỳ”."
                    />
                  </label>
                  <label className="field">
                    <span>Source Snippet</span>
                    <textarea
                      className="textarea compact-textarea"
                      value={feedbackSourceText}
                      onChange={(event) => setFeedbackSourceText(event.target.value)}
                      placeholder="Đoạn Hán ngữ hoặc câu nguồn liên quan"
                    />
                  </label>
                  <div className="split-grid">
                    <label className="field">
                      <span>Current Translation</span>
                      <textarea
                        className="textarea compact-textarea"
                        value={feedbackCurrentTranslation}
                        onChange={(event) => setFeedbackCurrentTranslation(event.target.value)}
                        placeholder="Bản dịch hiện tại"
                      />
                    </label>
                    <label className="field">
                      <span>Preferred Translation</span>
                      <textarea
                        className="textarea compact-textarea"
                        value={feedbackPreferredTranslation}
                        onChange={(event) => setFeedbackPreferredTranslation(event.target.value)}
                        placeholder="Bản dịch mong muốn hoặc câu sửa tay"
                      />
                    </label>
                  </div>
                  <div className="action-row">
                    <button className="button" type="button" disabled={busy || !backendAvailable || !feedbackText.trim()} onClick={() => void handleSubmitFeedback()}>
                      Analyze and Propose
                    </button>
                    <span className="pill subtle">
                      {feedbackScope === "chapter"
                        ? `Target chapter: ${overview.project.active_chapter ?? "none"}`
                        : "Target scope: project"}
                    </span>
                  </div>
                </div>
                <div className="form-grid">
                  <Panel title="LLM Assist" subtitle="Optional OpenAI-compatible endpoint. Credentials are stored locally in this desktop shell only.">
                    <div className="form-grid">
                      <label className="field">
                        <span>Endpoint</span>
                        <input className="input" value={llmEndpoint} onChange={(event) => setLlmEndpoint(event.target.value)} placeholder="https://api.example.com/v1/chat/completions" />
                      </label>
                      <label className="field">
                        <span>Model</span>
                        <input className="input" value={llmModel} onChange={(event) => setLlmModel(event.target.value)} placeholder="gpt-4.1-mini or custom model" />
                      </label>
                      <div className="split-grid">
                        <label className="field">
                          <span>Auth Header</span>
                          <input className="input" value={llmAuthHeader} onChange={(event) => setLlmAuthHeader(event.target.value)} placeholder="Authorization" />
                        </label>
                        <label className="field">
                          <span>Auth Prefix</span>
                          <input className="input" value={llmAuthPrefix} onChange={(event) => setLlmAuthPrefix(event.target.value)} placeholder="Bearer " />
                        </label>
                      </div>
                      <label className="field">
                        <span>API Key / OAuth Token</span>
                        <input className="input" type="password" value={llmToken} onChange={(event) => setLlmToken(event.target.value)} placeholder="Stored only in localStorage on this machine" />
                      </label>
                    </div>
                  </Panel>
                </div>
              </div>
            </Panel>
            <div className="split-grid">
              <Panel title="Analysis Suggestions" subtitle="Suggestions are created from your feedback and queued as reviewable rules.">
                <div className="list-stack">
                  {feedbackAnalysis?.suggestions.length ? (
                    feedbackAnalysis.suggestions.map((suggestion, index) => (
                      <article key={`${suggestion.rule_type}-${index}`} className="candidate-card">
                        <div className="candidate-head">
                          <div>
                            <strong>{suggestion.title}</strong>
                            <p>{suggestion.summary}</p>
                          </div>
                          <span className="pill subtle">{Math.round(suggestion.confidence * 100)}%</span>
                        </div>
                        <div className="tag-row">
                          <span className="pill subtle">{suggestion.rule_type}</span>
                          <span className="pill subtle">{suggestion.scope}</span>
                          <span className="pill subtle">{suggestion.origin}</span>
                        </div>
                        <pre className="output-block compact-block">{JSON.stringify(suggestion.payload, null, 2)}</pre>
                      </article>
                    ))
                  ) : (
                    <p className="empty-state">No suggestion generated yet. Submit feedback to populate this queue.</p>
                  )}
                </div>
              </Panel>
              <Panel title="Learning Snapshot" subtitle="Latest learning report for the active chapter or project.">
                {learningReport?.current_run ? (
                  <div className="detail-grid">
                    <InfoLine label="QA Total" value={stringValue(learningReport.current_run.qa_total)} />
                    <InfoLine label="Word Similarity" value={stringValue((learningReport.current_run.reference_comparison as Record<string, unknown> | undefined)?.word_similarity ?? "n/a")} />
                    <InfoLine label="Translate Seconds" value={stringValue((learningReport.current_run.runtime_metrics as Record<string, unknown> | undefined)?.translate_seconds ?? "n/a")} />
                    <InfoLine label="Auto Applied" value={stringValue((learningReport.auto_applied ?? []).length)} />
                    <pre className="output-block compact-block">{JSON.stringify(learningReport.recommendations ?? [], null, 2)}</pre>
                  </div>
                ) : (
                  <p className="empty-state">Run QA to generate a learning report for this chapter.</p>
                )}
              </Panel>
            </div>
            <Panel
              title="Candidate Rules"
              subtitle="Review and apply structured rules generated from user feedback. Verified rules update the project config or learned terms."
            >
              <div className="toolbar">
                <label className="field compact">
                  <span>Status</span>
                  <select className="input" value={ruleFilter} onChange={(event) => setRuleFilter(event.target.value)}>
                    <option value="all">All</option>
                    <option value="candidate">Candidate</option>
                    <option value="verified">Verified</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </label>
              </div>
              <div className="list-stack">
                {filteredRules.length ? (
                  filteredRules.map((rule) => (
                    <article key={rule.id} className="candidate-card">
                      <div className="candidate-head">
                        <div>
                          <strong>{ruleTitle(rule)}</strong>
                          <p>{ruleSummary(rule)}</p>
                        </div>
                        <span className={`pill tone-${rule.status}`}>{rule.status}</span>
                      </div>
                      <div className="tag-row">
                        <span className="pill subtle">{rule.rule_type}</span>
                        <span className="pill subtle">{stringValue((rule.rule_payload.chapter_id as string | undefined) ?? "project")}</span>
                      </div>
                      <pre className="output-block compact-block">{JSON.stringify(rule.rule_payload.payload ?? rule.rule_payload, null, 2)}</pre>
                      <div className="action-row">
                        <button className="button" type="button" disabled={!backendAvailable || rule.status === "verified"} onClick={() => void handleReviewRule(rule, "verified")}>
                          Verify and Apply
                        </button>
                        <button className="button secondary" type="button" disabled={!backendAvailable || rule.status === "rejected"} onClick={() => void handleReviewRule(rule, "rejected")}>
                          Reject
                        </button>
                      </div>
                    </article>
                  ))
                ) : (
                  <p className="empty-state">No candidate rules in the queue yet.</p>
                )}
              </div>
            </Panel>
          </div>
        );
      case "Entity & Relationship Viewer":
        return (
          <div className="panel-stack">
            <div className="split-grid">
              <Panel title="Entities" subtitle="Locked names and project-level terminology hints.">
                <div className="list-stack">
                  {overview.entities.length ? (
                    overview.entities.map((entity, index) => (
                      <div key={`entity-${index}`} className="list-card compact">
                        <strong>{stringValue(entity.source)}</strong>
                        <span>{stringValue(entity.target)}</span>
                        <small>{stringValue(entity.entity_type)}</small>
                      </div>
                    ))
                  ) : (
                    <p className="empty-state">Entity scan has not produced results yet.</p>
                  )}
                </div>
              </Panel>
              <Panel title="Relationships" subtitle="Config-visible relationship edges from pre-translation analysis.">
                <div className="list-stack">
                  {overview.relationships.length ? (
                    overview.relationships.map((relation, index) => (
                      <div key={`relation-${index}`} className="list-card compact">
                        <strong>{stringValue(relation.source)}</strong>
                        <span>{stringValue(relation.relation)}</span>
                        <small>{stringValue(relation.target)}</small>
                      </div>
                    ))
                  ) : (
                    <p className="empty-state">Relationship graph is empty for this slice.</p>
                  )}
                </div>
              </Panel>
            </div>
          </div>
        );
      case "Pre-Translation Review":
        return (
          <div className="panel-stack">
            <Panel
              title="Pre-Translation Review"
              subtitle="Import source material, inspect generated config, and verify terminology before translation begins."
            >
              <div className="toolbar">
                <label className="field grow">
                  <span>Source File Or Source Directory</span>
                  <input
                    className="input"
                    value={importPath}
                    onChange={(event) => setImportPath(event.target.value)}
                    placeholder="D:\\docs\\chapter-001.md or D:\\Novel\\source"
                  />
                </label>
                <button className="button secondary" type="button" disabled={busy || !backendAvailable} onClick={() => void pickImportPath("file")}>
                  Choose File
                </button>
                <button className="button secondary" type="button" disabled={busy || !backendAvailable} onClick={() => void pickImportPath("folder")}>
                  Choose Folder
                </button>
                <button className="button" type="button" disabled={busy || !backendAvailable} onClick={() => void handleImport()}>
                  Import and Prepare
                </button>
              </div>
              <div className="tag-row">
                {lockedEntities.map((entity, index) => (
                  <span key={`lock-${index}`} className="pill subtle">
                    {stringValue(entity.source)}
                    {" -> "}
                    {stringValue(entity.target)}
                  </span>
                ))}
              </div>
            </Panel>
            <div className="split-grid">
              <Panel title="Terminology Suggestions" subtitle="Terms that deserve review before runtime ranking starts.">
                <div className="list-stack">
                  {overview.terminology_suggestions.length ? (
                    overview.terminology_suggestions.map((item, index) => (
                      <div key={`term-${index}`} className="list-card compact">
                        <strong>{stringValue(item.source)}</strong>
                        <span>{stringValue(item.candidates)}</span>
                        <small>{stringValue(item.ambiguity)}</small>
                      </div>
                    ))
                  ) : (
                    <p className="empty-state">No terminology suggestions have been generated.</p>
                  )}
                </div>
              </Panel>
              <Panel title="Config Snapshot" subtitle="The translation workspace reads these hints directly from the reviewable config payload.">
                <pre className="output-block">{JSON.stringify(overview.config, null, 2)}</pre>
              </Panel>
            </div>
          </div>
        );
      case "QA Report Viewer":
        return (
          <div className="panel-stack">
            <Panel
              title="QA Report Viewer"
              subtitle="Render the latest QA payload and expose issue-level evidence for the reviewer."
            >
              <div className="action-row">
                <button className="button" type="button" disabled={busy || !backendAvailable} onClick={() => void handleRunQa()}>
                  Refresh QA
                </button>
                <span className="pill subtle">
                  Issues: {qaReport?.summary.issues ?? 0}
                </span>
              </div>
            </Panel>
            <div className="list-stack">
              {qaReport?.issues.length ? (
                qaReport.issues.map((issue) => (
                  <article key={`${issue.segment_id}-${issue.checker}`} className="issue-card">
                    <div className="trace-head">
                      <strong>{issue.checker}</strong>
                      <span className={`pill tone-${issue.severity}`}>{issue.severity}</span>
                    </div>
                    <p>{issue.message}</p>
                    <small>{issue.segment_id}</small>
                  </article>
                ))
              ) : (
                <p className="empty-state">QA has not reported any issues for the active slice.</p>
              )}
            </div>
          </div>
        );
      case "Settings":
        return (
          <div className="panel-stack">
            <Panel
              title="Settings and Contract"
              subtitle="This shell is wired against the expanded Phase 10 contract and prefers the native Tauri bridge for real work."
            >
              <div className="detail-grid">
                <InfoLine label="Protocol version" value={PROTOCOL_VERSION} />
                <InfoLine label="Transport mode" value={transport?.mode ?? "initializing"} />
                <InfoLine label="Supported commands" value={transport?.supportedCommands.join(", ") ?? "Loading"} />
                <InfoLine label="Native blocker" value="Rust/Cargo are still required to verify packaging in this environment." />
              </div>
            </Panel>
            <Panel
              title="Artifact Paths"
              subtitle="The desktop shell surfaces the same artifact model expected by the Python project manager."
            >
              <pre className="output-block">{JSON.stringify(overview.artifacts, null, 2)}</pre>
            </Panel>
          </div>
        );
      default:
        return null;
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-kicker">Phase 10</span>
          <h1>DrDuc Translator</h1>
          <p>
            Desktop workflow shell for project control, translation review, QA, learning loops, and human-in-the-loop rule tuning.
          </p>
        </div>

        <div className="transport-card">
          <span className="pill">{transport?.mode ?? "loading"} transport</span>
          <p>
            {transport?.mode === "tauri"
              ? "Native runtime detected. UI commands are forwarded to the Python sidecar through Tauri invoke."
              : transport?.mode === "demo"
                ? "Demo mode was enabled explicitly for UI-only development."
                : transport?.mode === "http"
                  ? "HTTP bridge connected. The Python backend is executing your workflow requests."
                  : "Browser preview does not execute the translation backend. Launch the native Tauri app for real project work."}
          </p>
        </div>

        <nav className="nav-stack">
          {SCREENS.map((item) => (
            <button
              key={item}
              className={`nav-button ${item === screen ? "active" : ""}`}
              type="button"
              onClick={() => {
                startTransition(() => {
                  setScreen(item);
                });
              }}
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
                onClick={() => {
                  startTransition(() => {
                    setSelectedProjectId(project.project_id);
                  });
                }}
              >
                <strong>{project.project_id}</strong>
                <span>
                  {project.source_language}
                  {" -> "}
                  {project.target_language}
                </span>
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
            <span className={`pill ${busy ? "busy" : ""}`}>{busy ? "Running command" : "Idle"}</span>
            <span className="pill subtle">
              {overview?.project.active_chapter ?? "No active chapter"}
            </span>
          </div>
        </header>

        <section className="metrics-row">
          <MetricCard label="Chapters" value={overview?.counts.chapters ?? 0} />
          <MetricCard label="Segments" value={overview?.counts.segments ?? 0} />
          <MetricCard label="Candidates" value={overview?.counts.candidates_total ?? 0} />
          <MetricCard label="QA Issues" value={overview?.counts.qa_issues ?? 0} />
        </section>

        {Object.keys(candidateStatus).length > 0 ? (
          <section className="tag-row">
            {Object.entries(candidateStatus).map(([status, total]) => (
              <span key={status} className={`pill tone-${status}`}>
                {status}: {total}
              </span>
            ))}
          </section>
        ) : null}

        {warnings.length > 0 ? (
          <section className="warning-strip">
            {warnings.map((warning) => (
              <p key={warning}>{warning}</p>
            ))}
          </section>
        ) : null}

        <section className="screen-area">{renderScreen()}</section>

        <section className="split-grid footer-grid">
          <Panel
            title="Command Timeline"
            subtitle="The shell exposes the same event payloads the sidecar uses for progress and recovery hints."
          >
            <div className="list-stack">
              {events.length > 0 ? (
                events.map((event) => (
                  <div key={`${event.stage}-${event.message}`} className="timeline-row">
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
          <Panel
            title="Runtime Snapshot"
            subtitle="Latest output paths and segment counts for the active project."
          >
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

function Panel(props: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <section className="panel">
      <header className="panel-head">
        <div>
          <h3>{props.title}</h3>
          <p>{props.subtitle}</p>
        </div>
      </header>
      {props.children}
    </section>
  );
}

function MetricCard(props: { label: string; value: number }) {
  return (
    <article className="metric-card">
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </article>
  );
}

function InfoLine(props: { label: string; value: string }) {
  return (
    <div className="info-line">
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </div>
  );
}

function asRecordArray(value: unknown): Array<Record<string, unknown>> {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object");
}

function stringValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value.map((item) => stringValue(item)).join(", ");
  }
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (value && typeof value === "object") {
    return JSON.stringify(value);
  }
  return "n/a";
}

function ruleTitle(rule: CandidateRule): string {
  const title = rule.rule_payload.title;
  return typeof title === "string" && title.trim() ? title : rule.rule_type;
}

function ruleSummary(rule: CandidateRule): string {
  const summary = rule.rule_payload.summary;
  if (typeof summary === "string" && summary.trim()) {
    return summary;
  }
  return stringValue(rule.rule_payload.payload ?? rule.rule_payload);
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
