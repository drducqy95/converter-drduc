import { useEffect, useMemo, useState, type SyntheticEvent } from "react";
import type { EntityTargetSuggestion, ProjectOverview, QAReport, TranslationArtifacts, TranslationSegment, TranslationTrace } from "../protocol";
import { Panel } from "../components/Panel";

type EntityDraft = {
  source: string;
  target: string;
  entity_type: string;
  source_dict: string;
  confidence: number;
  count: number;
  ambiguity_flag: boolean;
  positions: number[];
};

type CompareSelectionKind = "source" | "clean" | "draft";
type WorkspaceView = "compare" | "entities" | "config" | "trace";

const ENTITY_TYPES = ["person", "location", "organization", "project_term", "junk_phrase", "term", "realm", "technique", "weapon"];
const WORKSPACE_VIEWS: Array<{ id: WorkspaceView; label: string }> = [
  { id: "compare", label: "So sánh" },
  { id: "entities", label: "Entity" },
  { id: "config", label: "Cấu hình" },
  { id: "trace", label: "Trace / QA" },
];

function normalizeCompareText(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

function compareKey(value: string): string {
  return normalizeCompareText(value).toLowerCase();
}

function compareTextScore(selection: string, candidate: string): number {
  const selected = compareKey(selection);
  const text = compareKey(candidate);
  if (!selected || !text) {
    return 0;
  }
  if (text === selected) {
    return 10000 + text.length;
  }
  if (text.includes(selected)) {
    return 5000 + selected.length - Math.abs(text.length - selected.length);
  }
  if (selected.includes(text)) {
    return 3000 + text.length - Math.abs(text.length - selected.length);
  }
  return 0;
}

function pickTraceByField(selection: string, traces: TranslationTrace[], field: "source" | "selected"): TranslationTrace | null {
  let bestTrace: TranslationTrace | null = null;
  let bestScore = 0;
  for (const trace of traces) {
    const score = compareTextScore(selection, trace[field]);
    if (score > bestScore) {
      bestScore = score;
      bestTrace = trace;
    }
  }
  return bestTrace;
}

function joinTraceField(traces: TranslationTrace[], field: "source" | "selected"): string {
  const parts = traces
    .map((trace) => normalizeCompareText(trace[field]))
    .filter(Boolean);
  if (field === "source") {
    return parts.join("");
  }
  return normalizeCompareText(parts.join(" "));
}

function pickTraceWindow(selection: string, traces: TranslationTrace[], field: "source" | "selected"): TranslationTrace[] {
  const selectedKey = compareKey(selection);
  if (!selectedKey) {
    return [];
  }
  const candidates = traces.filter((trace) => compareKey(trace[field]));
  let bestWindow: TranslationTrace[] = [];
  let bestScore = 0;
  for (let start = 0; start < candidates.length; start += 1) {
    const window: TranslationTrace[] = [];
    for (let end = start; end < candidates.length && end < start + 24; end += 1) {
      window.push(candidates[end]);
      const joined = joinTraceField(window, field);
      const joinedKey = compareKey(joined);
      const baseScore = compareTextScore(selection, joined);
      if (!baseScore) {
        continue;
      }
      const lengthPenalty = Math.abs(selectedKey.length - joinedKey.length);
      const exactBonus = selectedKey === joinedKey ? 100000 : 0;
      const score = exactBonus + baseScore * 10 - lengthPenalty * 4 + Math.min(window.length, 20);
      if (score > bestScore) {
        bestScore = score;
        bestWindow = [...window];
      }
    }
  }
  return bestWindow;
}

function segmentTextForKind(segment: TranslationSegment, kind: CompareSelectionKind): string {
  if (kind === "source") {
    return segment.source_text;
  }
  if (kind === "draft") {
    return segment.draft_text;
  }
  return segment.clean_text;
}

function pickSegmentBySelection(kind: CompareSelectionKind, selection: string, segments: TranslationSegment[]): TranslationSegment | null {
  let bestSegment: TranslationSegment | null = null;
  let bestScore = 0;
  for (const segment of segments) {
    const score = compareTextScore(selection, segmentTextForKind(segment, kind));
    if (score > bestScore) {
      bestScore = score;
      bestSegment = segment;
    }
  }
  return bestSegment;
}

function emptyEntityDraft(): EntityDraft {
  return {
    source: "",
    target: "",
    entity_type: "project_term",
    source_dict: "user_review",
    confidence: 1,
    count: 1,
    ambiguity_flag: false,
    positions: [],
  };
}

function draftFromEntity(entity: Record<string, unknown>): EntityDraft {
  return {
    source: String(entity.source ?? ""),
    target: String(entity.target ?? ""),
    entity_type: String(entity.entity_type ?? "project_term"),
    source_dict: String(entity.source_dict ?? "user_review"),
    confidence: Number(entity.confidence ?? 1) || 1,
    count: Number(entity.count ?? 1) || 1,
    ambiguity_flag: Boolean(entity.ambiguity_flag),
    positions: Array.isArray(entity.positions) ? entity.positions.filter((item): item is number => typeof item === "number") : [],
  };
}

export function TranslationWorkspaceScreen(props: {
  busy: boolean;
  backendAvailable: boolean;
  importPath: string;
  translationInput: string;
  overview: ProjectOverview | null;
  translation: TranslationArtifacts | null;
  qaReport: QAReport | null;
  onImportPathChange: (value: string) => void;
  onPickImportPath: (kind: "file" | "folder") => void;
  onImport: () => void;
  onTranslationInputChange: (value: string) => void;
  onTranslate: () => void;
  onRunQa: () => void;
  onSelectChapter: (chapterId: string, chapterText: string) => void;
  onInspectToken: (query: string) => void;
  onSaveTranslationConfig: (config: Record<string, unknown>) => void;
  onSaveProjectEntity: (entity: Record<string, unknown>, syncLocked: boolean) => void;
  onDeleteProjectEntity: (source: string, syncLocked: boolean) => void;
  onDeleteProjectEntities: (sources: string[], syncLocked: boolean) => void;
  onSuggestEntityTargets: (source: string) => Promise<EntityTargetSuggestion[]>;
}) {
  const activeChapter = props.overview?.chapters.find((item) => item.chapter_id === props.overview?.project.active_chapter)
    ?? props.overview?.chapters[0]
    ?? null;
  const [configDraft, setConfigDraft] = useState("{}");
  const [configError, setConfigError] = useState("");
  const [entityQuery, setEntityQuery] = useState("");
  const [entityDraft, setEntityDraft] = useState<EntityDraft>(() => emptyEntityDraft());
  const [syncLocked, setSyncLocked] = useState(true);
  const [targetSuggestions, setTargetSuggestions] = useState<EntityTargetSuggestion[]>([]);
  const [suggestingTargets, setSuggestingTargets] = useState(false);
  const [workspaceView, setWorkspaceView] = useState<WorkspaceView>("compare");
  const [selectedEntitySources, setSelectedEntitySources] = useState<Set<string>>(() => new Set());

  useEffect(() => {
    setConfigDraft(JSON.stringify(props.overview?.config ?? {}, null, 2));
    setConfigError("");
  }, [props.overview?.project.project_id, props.overview?.config]);

  useEffect(() => {
    const source = entityDraft.source.trim();
    if (!source) {
      setTargetSuggestions([]);
      setSuggestingTargets(false);
      return;
    }
    let cancelled = false;
    setSuggestingTargets(true);
    const timer = window.setTimeout(() => {
      props.onSuggestEntityTargets(source)
        .then((suggestions) => {
          if (!cancelled) {
            setTargetSuggestions(suggestions);
          }
        })
        .catch(() => {
          if (!cancelled) {
            setTargetSuggestions([]);
          }
        })
        .finally(() => {
          if (!cancelled) {
            setSuggestingTargets(false);
          }
        });
    }, 250);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [entityDraft.source]);

  useEffect(() => {
    const existingSources = new Set((props.overview?.entities ?? []).map((entity) => String(entity.source ?? "")).filter(Boolean));
    setSelectedEntitySources((current) => {
      const next = new Set([...current].filter((source) => existingSources.has(source)));
      return next.size === current.size ? current : next;
    });
  }, [props.overview?.entities]);

  const traceItems = useMemo(
    () => props.translation?.segments.flatMap((segment) => segment.trace) ?? [],
    [props.translation],
  );
  const lockedSources = useMemo(() => {
    const locked = Array.isArray(props.overview?.config.locked_entities) ? props.overview?.config.locked_entities : [];
    return new Set(
      locked
        .map((item) => (item && typeof item === "object" ? String((item as Record<string, unknown>).source ?? "") : ""))
        .filter(Boolean),
    );
  }, [props.overview?.config]);
  const filteredEntities = useMemo(() => {
    const query = entityQuery.trim().toLowerCase();
    const entities = props.overview?.entities ?? [];
    if (!query) {
      return entities.slice(0, 120);
    }
    return entities
      .filter((entity) => `${String(entity.source ?? "")} ${String(entity.target ?? "")} ${String(entity.entity_type ?? "")}`.toLowerCase().includes(query))
      .slice(0, 120);
  }, [entityQuery, props.overview?.entities]);

  function selectTraceForEntity(trace: TranslationTrace) {
    setEntityDraft({
      ...emptyEntityDraft(),
      source: trace.source,
      target: trace.selected,
      source_dict: "trace_review",
      entity_type: "project_term",
    });
    setSyncLocked(true);
    setWorkspaceView("entities");
  }

  function applyCompareSelection(kind: CompareSelectionKind, selectedText: string, position: number) {
    const segments = props.translation?.segments ?? [];
    const segment = pickSegmentBySelection(kind, selectedText, segments);
    const scopedTraces = segment?.trace.length ? segment.trace : traceItems;

    setEntityDraft((current) => {
      if (kind === "source") {
        const traceWindow = pickTraceWindow(selectedText, scopedTraces, "source");
        const fallbackWindow = traceWindow.length ? traceWindow : pickTraceWindow(selectedText, traceItems, "source");
        const trace = pickTraceByField(selectedText, scopedTraces, "source") ?? pickTraceByField(selectedText, traceItems, "source");
        return {
          ...current,
          source: selectedText,
          target: fallbackWindow.length ? joinTraceField(fallbackWindow, "selected") : trace?.selected || current.target || segment?.clean_text || "",
          entity_type: current.entity_type || "project_term",
          source_dict: "parallel_compare_selection",
          positions: position >= 0 ? [position] : current.positions,
        };
      }

      const traceWindow = pickTraceWindow(selectedText, scopedTraces, "selected");
      const fallbackWindow = traceWindow.length ? traceWindow : pickTraceWindow(selectedText, traceItems, "selected");
      const trace = pickTraceByField(selectedText, scopedTraces, "selected") ?? pickTraceByField(selectedText, traceItems, "selected");
      return {
        ...current,
        source: fallbackWindow.length ? joinTraceField(fallbackWindow, "source") : trace?.source || current.source || segment?.source_text || "",
        target: selectedText,
        entity_type: current.entity_type || "project_term",
        source_dict: "parallel_compare_selection",
        positions: position >= 0 ? [position] : current.positions,
      };
    });
    setSyncLocked(true);
  }

  function handleCompareSelection(kind: CompareSelectionKind, event: SyntheticEvent<HTMLTextAreaElement>) {
    const control = event.currentTarget;
    const start = control.selectionStart;
    const end = control.selectionEnd;
    if (start === end) {
      return;
    }
    const selectedText = normalizeCompareText(control.value.slice(start, end));
    if (!selectedText) {
      return;
    }
    applyCompareSelection(kind, selectedText, start);
  }

  function handleChapterSelect(chapterId: string) {
    const chapter = props.overview?.chapters.find((item) => item.chapter_id === chapterId);
    if (chapter) {
      props.onSelectChapter(chapter.chapter_id, chapter.text);
    }
  }

  function saveConfigDraft() {
    try {
      const parsed = JSON.parse(configDraft) as unknown;
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      throw new Error("Config phải là JSON object.");
      }
      setConfigError("");
      props.onSaveTranslationConfig(parsed as Record<string, unknown>);
    } catch (error) {
      setConfigError(error instanceof Error ? error.message : String(error));
    }
  }

  function saveEntityDraft() {
    if (!entityDraft.source.trim() || !entityDraft.target.trim()) {
      return;
    }
    props.onSaveProjectEntity(
      {
        ...entityDraft,
        source: entityDraft.source.trim(),
        target: entityDraft.target.trim(),
        entity_type: entityDraft.entity_type || "project_term",
        source_dict: entityDraft.source_dict || "user_review",
      },
      syncLocked,
    );
  }

  function deleteEntityDraft() {
    const source = entityDraft.source.trim();
    if (!source) {
      return;
    }
    if (!window.confirm(`Xóa entity "${source}"?`)) {
      return;
    }
    props.onDeleteProjectEntity(source, syncLocked);
    setEntityDraft(emptyEntityDraft());
    setTargetSuggestions([]);
  }

  function toggleEntitySelection(source: string, checked: boolean) {
    setSelectedEntitySources((current) => {
      const next = new Set(current);
      if (checked) {
        next.add(source);
      } else {
        next.delete(source);
      }
      return next;
    });
  }

  function selectVisibleEntities() {
    setSelectedEntitySources((current) => {
      const next = new Set(current);
      for (const entity of filteredEntities) {
        const source = String(entity.source ?? "").trim();
        if (source) {
          next.add(source);
        }
      }
      return next;
    });
  }

  function clearEntitySelection() {
    setSelectedEntitySources(new Set());
  }

  function deleteSelectedEntities() {
    const sources = [...selectedEntitySources].filter(Boolean);
    if (!sources.length) {
      return;
    }
    if (!window.confirm(`Xóa ${sources.length} entity đã chọn?`)) {
      return;
    }
    props.onDeleteProjectEntities(sources, syncLocked);
    setSelectedEntitySources(new Set());
    if (sources.includes(entityDraft.source.trim())) {
      setEntityDraft(emptyEntityDraft());
      setTargetSuggestions([]);
    }
  }

  function renderTargetSuggestions() {
    if (!entityDraft.source.trim()) {
      return null;
    }
    return (
      <div className="target-suggestions">
        <span>Đề xuất target</span>
        <div className="target-suggestion-list">
          {suggestingTargets ? (
            <small>Đang tạo gợi ý...</small>
          ) : targetSuggestions.length ? (
            targetSuggestions.map((suggestion) => (
              <button
                key={`${suggestion.kind}-${suggestion.value}`}
                className="target-suggestion-chip"
                type="button"
                title={suggestion.detail}
                onClick={() => setEntityDraft({ ...entityDraft, target: suggestion.value })}
              >
                <strong>{suggestion.label}</strong>
                <span>{suggestion.value}</span>
              </button>
            ))
          ) : (
            <small>Chưa có gợi ý Hán Việt hoặc Latinh phù hợp.</small>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="panel-stack workspace-screen">
      <Panel title="Nạp bản dịch" subtitle="Chọn nguồn, chọn chương và chạy thao tác chính cho slice đang mở.">
        <div className="workspace-control-row">
          <label className="field grow">
            <span>Tệp / thư mục nguồn</span>
            <input
              className="input"
              value={props.importPath}
              onChange={(event) => props.onImportPathChange(event.target.value)}
              placeholder="D:\\Novel\\source\\chapter-001.md"
            />
          </label>
          <label className="field chapter-select-field">
            <span>Chương ({props.overview?.counts.chapters ?? 0})</span>
            <select className="input" value={activeChapter?.chapter_id ?? ""} onChange={(event) => handleChapterSelect(event.target.value)}>
              {props.overview?.chapters.length ? (
                props.overview.chapters.map((chapter) => (
                  <option key={chapter.chapter_id} value={chapter.chapter_id}>
                    {chapter.chapter_id} - {chapter.title}
                  </option>
                ))
              ) : (
                <option value="">Chưa có chương</option>
              )}
            </select>
          </label>
          <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable} onClick={() => props.onPickImportPath("file")}>
            Chọn tệp
          </button>
          <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable} onClick={() => props.onPickImportPath("folder")}>
            Chọn thư mục
          </button>
          <button className="button" type="button" disabled={props.busy || !props.backendAvailable} onClick={props.onImport}>
            Nhập
          </button>
          <button className="button" type="button" disabled={props.busy || !props.backendAvailable} onClick={props.onTranslate}>
            Dịch
          </button>
          <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable} onClick={props.onRunQa}>
            QA
          </button>
        </div>
      </Panel>

      <nav className="workspace-tabs" aria-label="Translation workspace">
        {WORKSPACE_VIEWS.map((view) => (
          <button
            key={view.id}
            className={`workspace-tab ${workspaceView === view.id ? "active" : ""}`}
            type="button"
            onClick={() => setWorkspaceView(view.id)}
          >
            {view.label}
          </button>
        ))}
      </nav>

      {workspaceView === "compare" ? (
        <div className="compare-workspace">
          <Panel title="So sánh song song" subtitle="Bôi đen trong nguồn, bản sạch hoặc bản nháp để tạo entity; mở tab Entity để chỉnh chi tiết.">
            <div className="compare-grid expanded-compare-grid">
              <label className="field">
                <span>Nguồn</span>
                <textarea
                  className="textarea compare-textarea"
                  value={props.translationInput}
                  onChange={(event) => props.onTranslationInputChange(event.target.value)}
                  onSelect={(event) => handleCompareSelection("source", event)}
                />
              </label>
              <label className="field">
                <span>Bản sạch</span>
                <textarea className="textarea compare-textarea" value={props.translation?.clean_text ?? ""} readOnly onSelect={(event) => handleCompareSelection("clean", event)} />
              </label>
            </div>
            <label className="field">
              <span>Bản nháp chú giải</span>
              <textarea className="textarea draft-compare-textarea" value={props.translation?.draft_text ?? ""} readOnly onSelect={(event) => handleCompareSelection("draft", event)} />
            </label>
            <div className="compare-selection-strip">
              <div>
                <span>Entity nháp</span>
                <strong>{entityDraft.source || "Chưa chọn nguồn"} -&gt; {entityDraft.target || "Chưa chọn target"}</strong>
              </div>
              <div className="action-row">
                <button className="button secondary" type="button" onClick={() => setWorkspaceView("entities")}>
                  Mở Entity
                </button>
                <button className="button" type="button" disabled={props.busy || !props.backendAvailable || !entityDraft.source.trim() || (entityDraft.entity_type !== "junk_phrase" && !entityDraft.target.trim())} onClick={saveEntityDraft}>
                  Lưu Entity
                </button>
              </div>
            </div>
          </Panel>

          <Panel title="Lớp token nguồn" subtitle="Token trace hỗ trợ tra từ điển hoặc nạp nhanh vào tab Entity.">
            <div className="token-grid compact-token-grid">
              {traceItems.length ? (
                traceItems.slice(0, 80).map((trace, index) => (
                  <article key={`${trace.source}-${index}`} className="token-chip compact-token-chip">
                    <strong>{trace.source}</strong>
                    <span>{trace.selected}</span>
                    <div className="token-actions">
                      <button className="pill subtle" type="button" onClick={() => props.onInspectToken(trace.source)}>
                        Từ điển
                      </button>
                      <button className="pill subtle" type="button" onClick={() => selectTraceForEntity(trace)}>
                        Entity
                      </button>
                    </div>
                  </article>
                ))
              ) : (
                <p className="empty-state">Dịch xong sẽ có danh sách token trace để kiểm tra.</p>
              )}
            </div>
          </Panel>
        </div>
      ) : null}

      {workspaceView === "entities" ? (
        <Panel title="Duyệt Entity Project" subtitle="Thêm hoặc sửa entity khi kiểm bản dịch; sync vào locked_entities nếu cần ưu tiên lần dịch lại.">
          <div className="toolbar">
            <label className="field grow">
              <span>Tìm entity đã quét</span>
              <input className="input" value={entityQuery} onChange={(event) => setEntityQuery(event.target.value)} placeholder="source / target / type" />
            </label>
            <button className="button secondary" type="button" onClick={() => setEntityDraft(emptyEntityDraft())}>
              Entity mới
            </button>
            <button className="button secondary" type="button" disabled={!filteredEntities.length} onClick={selectVisibleEntities}>
              Chọn đang hiện
            </button>
            <button className="button secondary" type="button" disabled={!selectedEntitySources.size} onClick={clearEntitySelection}>
              Bỏ chọn
            </button>
            <button className="button secondary danger-button" type="button" disabled={props.busy || !props.backendAvailable || !selectedEntitySources.size} onClick={deleteSelectedEntities}>
              Xóa đã chọn ({selectedEntitySources.size})
            </button>
          </div>
          <div className="entity-workbench">
            <div className="entity-list">
              {filteredEntities.length ? (
                filteredEntities.map((entity) => {
                  const source = String(entity.source ?? "");
                  const selected = selectedEntitySources.has(source);
                  return (
                    <article
                      key={`${source}-${String(entity.target ?? "")}`}
                      className={`list-card compact entity-list-row ${lockedSources.has(source) ? "active" : ""} ${selected ? "selected" : ""}`}
                    >
                      <input
                        type="checkbox"
                        aria-label={`Select ${source}`}
                        checked={selected}
                        onChange={(event) => toggleEntitySelection(source, event.target.checked)}
                      />
                      <button className="entity-row-button" type="button" onClick={() => setEntityDraft(draftFromEntity(entity))}>
                        <strong>{source} -&gt; {String(entity.target ?? "")}</strong>
                        <span>{String(entity.entity_type ?? "project_term")} | count {String(entity.count ?? 1)}</span>
                        <small>{String(entity.source_dict ?? "unknown")}{lockedSources.has(source) ? " | locked" : ""}</small>
                      </button>
                    </article>
                  );
                })
              ) : (
                <p className="empty-state">Không có entity nào khớp bộ lọc.</p>
              )}
            </div>
            <div className="form-grid">
              <div className="split-grid compact-split">
                <label className="field">
                  <span>Nguồn</span>
                  <input className="input" value={entityDraft.source} onChange={(event) => setEntityDraft({ ...entityDraft, source: event.target.value })} />
                </label>
                <label className="field">
                  <span>Target VI</span>
                  <input className="input" value={entityDraft.target} onChange={(event) => setEntityDraft({ ...entityDraft, target: event.target.value })} />
                  {renderTargetSuggestions()}
                </label>
              </div>
              <div className="split-grid compact-split">
                <label className="field">
                  <span>Loại entity</span>
                  <select className="input" value={entityDraft.entity_type} onChange={(event) => setEntityDraft({ ...entityDraft, entity_type: event.target.value })}>
                    {ENTITY_TYPES.map((type) => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </label>
                <label className="field">
                  <span>Nguồn dữ liệu</span>
                  <input className="input" value={entityDraft.source_dict} onChange={(event) => setEntityDraft({ ...entityDraft, source_dict: event.target.value })} />
                </label>
              </div>
              <div className="split-grid compact-split">
                <label className="field">
                  <span>Confidence</span>
                  <input className="input" type="number" min="0" max="1" step="0.01" value={entityDraft.confidence} onChange={(event) => setEntityDraft({ ...entityDraft, confidence: Number(event.target.value) || 0 })} />
                </label>
                <label className="field">
                  <span>Count</span>
                  <input className="input" type="number" min="1" value={entityDraft.count} onChange={(event) => setEntityDraft({ ...entityDraft, count: Number(event.target.value) || 1 })} />
                </label>
              </div>
              <label className="check-line">
                <input type="checkbox" checked={syncLocked} onChange={(event) => setSyncLocked(event.target.checked)} />
                <span>Sync vào translation_config.locked_entities</span>
              </label>
              <div className="action-row">
                <button className="button" type="button" disabled={props.busy || !props.backendAvailable || !entityDraft.source.trim() || (entityDraft.entity_type !== "junk_phrase" && !entityDraft.target.trim())} onClick={saveEntityDraft}>
                  Cập nhật Entity
                </button>
                <button className="button secondary danger-button" type="button" disabled={props.busy || !props.backendAvailable || !entityDraft.source.trim()} onClick={deleteEntityDraft}>
                  Xóa Entity
                </button>
              </div>
            </div>
          </div>
        </Panel>
      ) : null}

      {workspaceView === "config" ? (
        <Panel title="Cấu hình dịch" subtitle="Chỉnh trực tiếp translation_config.json của project hiện tại.">
          <label className="field">
            <span>Config JSON</span>
            <textarea className="textarea config-textarea" value={configDraft} onChange={(event) => setConfigDraft(event.target.value)} />
          </label>
          {configError ? <p className="empty-state error-text">{configError}</p> : null}
          <div className="action-row">
            <button className="button" type="button" disabled={props.busy || !props.backendAvailable} onClick={saveConfigDraft}>
              Lưu cấu hình
            </button>
            <button className="button secondary" type="button" onClick={() => setConfigDraft(JSON.stringify(props.overview?.config ?? {}, null, 2))}>
              Khôi phục nháp
            </button>
          </div>
        </Panel>
      ) : null}

      {workspaceView === "trace" ? (
        <div className="split-grid">
          <Panel title="Bằng chứng trace" subtitle="Segment trace và fallback để review thứ tự pipeline.">
            <div className="list-stack">
              {props.translation?.segments.length ? (
                props.translation.segments.map((segment) => (
                  <article key={segment.sentence_id} className="trace-card">
                    <div className="trace-head">
                      <strong>{segment.sentence_id}</strong>
                      <span className={`pill tone-${segment.fallback_level ?? "runtime"}`}>{segment.fallback_level ?? "runtime"}</span>
                    </div>
                    <p>{segment.source_text}</p>
                    <div className="tag-row">
                      {segment.trace.map((trace) => (
                        <button key={`${segment.sentence_id}-${trace.source}`} className="pill subtle" type="button" onClick={() => props.onInspectToken(trace.source)}>
                          {trace.source} -&gt; {trace.selected}
                        </button>
                      ))}
                    </div>
                  </article>
                ))
              ) : (
                <p className="empty-state">Chưa có trace bản dịch.</p>
              )}
            </div>
          </Panel>

          <Panel title="Tóm tắt QA" subtitle="Tổng hợp issue để theo dõi trước khi sang Coach.">
            <div className="list-stack">
              {props.qaReport?.issues.length ? (
                props.qaReport.issues.map((issue) => (
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
                <p className="empty-state">QA chưa có issue nào cho active chapter.</p>
              )}
            </div>
          </Panel>
        </div>
      ) : null}
    </div>
  );
}
