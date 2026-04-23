import type { ChangeEvent } from "react";

import type { DictionaryEntry, DictionaryListResponse } from "../protocol";
import { EntityBadge } from "../components/EntityBadge";
import { Panel } from "../components/Panel";
import { POSBadge } from "../components/POSBadge";
import { ENTITY_OPTIONS, POS_SUB_OPTIONS, POS_TAG_OPTIONS, REORDER_ROLE_OPTIONS } from "../uiConstants";

type DraftField = keyof DictionaryEntry | "han_viet_joined";

export function DictionaryEditorScreen(props: {
  busy: boolean;
  backendAvailable: boolean;
  query: string;
  filters: DictionaryListResponse["filters"] | null;
  tableFilter: string;
  sourceDictFilter: string;
  posTagFilter: string;
  entityTypeFilter: string;
  page: number;
  pageSize: number;
  total: number;
  entries: DictionaryEntry[];
  selectedEntry: DictionaryEntry | null;
  draft: DictionaryEntry | null;
  selectedIds: string[];
  bulkPosTag: string;
  bulkEntityType: string;
  onQueryChange: (value: string) => void;
  onTableFilterChange: (value: string) => void;
  onSourceDictFilterChange: (value: string) => void;
  onPosTagFilterChange: (value: string) => void;
  onEntityTypeFilterChange: (value: string) => void;
  onSearch: (page?: number) => void;
  onSelectEntry: (entry: DictionaryEntry) => void;
  onToggleEntrySelection: (recordId: string) => void;
  onDraftChange: (field: DraftField, value: string | boolean) => void;
  onSave: () => void;
  onBulkPosTagChange: (value: string) => void;
  onBulkEntityTypeChange: (value: string) => void;
  onApplyBulkUpdate: () => void;
  onExportFiltered: () => void;
}) {
  const effectiveDraft = props.draft;
  const posSubOptions = effectiveDraft?.pos_tag ? POS_SUB_OPTIONS[effectiveDraft.pos_tag] ?? [] : [];
  const totalPages = Math.max(1, Math.ceil(props.total / props.pageSize));

  return (
    <div className="panel-stack">
      <Panel title="Dictionary Browser" subtitle="Tìm kiếm, lọc và phân trang để thao tác trên runtime/reference dictionary.">
        <div className="toolbar">
          <label className="field grow">
            <span>Query</span>
            <input
              className="input"
              value={props.query}
              onChange={(event) => props.onQueryChange(event.target.value)}
              placeholder="source, target, pinyin, explanation"
            />
          </label>
          <label className="field compact">
            <span>Scope</span>
            <select className="input" value={props.tableFilter} onChange={(event) => props.onTableFilterChange(event.target.value)}>
              <option value="">All</option>
              {(props.filters?.tables ?? []).map((value) => (
                <option key={value} value={value}>{value}</option>
              ))}
            </select>
          </label>
          <label className="field compact">
            <span>Category</span>
            <select className="input" value={props.sourceDictFilter} onChange={(event) => props.onSourceDictFilterChange(event.target.value)}>
              <option value="">All</option>
              {(props.filters?.categories ?? []).map((value) => (
                <option key={value} value={value}>{value}</option>
              ))}
            </select>
          </label>
          <label className="field compact">
            <span>POS</span>
            <select className="input" value={props.posTagFilter} onChange={(event) => props.onPosTagFilterChange(event.target.value)}>
              <option value="">All</option>
              {(props.filters?.pos_tags ?? []).map((value) => (
                <option key={value} value={value}>{value}</option>
              ))}
            </select>
          </label>
          <label className="field compact">
            <span>Entity</span>
            <select className="input" value={props.entityTypeFilter} onChange={(event) => props.onEntityTypeFilterChange(event.target.value)}>
              <option value="">All</option>
              {(props.filters?.entity_types ?? []).map((value) => (
                <option key={value} value={value}>{value}</option>
              ))}
            </select>
          </label>
          <button className="button" type="button" disabled={props.busy} onClick={() => props.onSearch(1)}>
            Apply
          </button>
        </div>

        <div className="dictionary-editor-grid">
          <div className="list-stack">
            {props.entries.map((entry) => (
              <button
                key={entry.record_id}
                className={`list-card ${props.selectedEntry?.record_id === entry.record_id ? "active" : ""}`}
                type="button"
                onClick={() => props.onSelectEntry(entry)}
              >
                <div className="candidate-head">
                  <label className="check-line" onClick={(event) => event.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={props.selectedIds.includes(entry.record_id)}
                      onChange={() => props.onToggleEntrySelection(entry.record_id)}
                    />
                    <strong>{entry.source}</strong>
                  </label>
                  <POSBadge tag={entry.pos_tag} sub={entry.pos_sub} />
                </div>
                <span>{entry.target_vi}</span>
                <div className="tag-row">
                  <span className="pill subtle">{entry.source_dict}</span>
                  <span className="pill subtle">P{entry.priority}</span>
                  <EntityBadge entityType={entry.entity_type} />
                </div>
              </button>
            ))}
          </div>

          <div className="panel-stack">
            <Panel title="Entry Detail" subtitle="Chỉnh sửa đầy đủ metadata POS 8 cột và thông tin runtime.">
              {effectiveDraft ? (
                <div className="form-grid">
                  <div className="split-grid">
                    <label className="field">
                      <span>Source</span>
                      <input className="input" value={effectiveDraft.source} onChange={handleChange(props.onDraftChange, "source")} />
                    </label>
                    <label className="field">
                      <span>Target</span>
                      <input className="input" value={effectiveDraft.target_vi} onChange={handleChange(props.onDraftChange, "target_vi")} />
                    </label>
                  </div>

                  <div className="split-grid">
                    <label className="field">
                      <span>Priority</span>
                      <input className="input" value={String(effectiveDraft.priority)} onChange={handleChange(props.onDraftChange, "priority")} />
                    </label>
                    <label className="field">
                      <span>POS Tag</span>
                      <select className="input" value={effectiveDraft.pos_tag ?? ""} onChange={handleChange(props.onDraftChange, "pos_tag")}>
                        <option value="">None</option>
                        {POS_TAG_OPTIONS.map((option) => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    </label>
                  </div>

                  <div className="split-grid">
                    <label className="field">
                      <span>POS Sub</span>
                      <select className="input" value={effectiveDraft.pos_sub ?? ""} onChange={handleChange(props.onDraftChange, "pos_sub")}>
                        <option value="">None</option>
                        {posSubOptions.map((option) => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    </label>
                    <label className="field">
                      <span>Entity Type</span>
                      <select className="input" value={effectiveDraft.entity_type ?? ""} onChange={handleChange(props.onDraftChange, "entity_type")}>
                        <option value="">None</option>
                        {ENTITY_OPTIONS.map((option) => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    </label>
                  </div>

                  <div className="split-grid">
                    <label className="field">
                      <span>Pinyin</span>
                      <input className="input" value={(effectiveDraft.pinyin ?? []).join(", ")} onChange={handleChange(props.onDraftChange, "pinyin")} />
                    </label>
                    <label className="field">
                      <span>Traditional</span>
                      <input className="input" value={effectiveDraft.traditional ?? ""} onChange={handleChange(props.onDraftChange, "traditional")} />
                    </label>
                  </div>

                  <div className="split-grid">
                    <label className="field">
                      <span>Reorder Role</span>
                      <select className="input" value={effectiveDraft.reorder_role ?? ""} onChange={handleChange(props.onDraftChange, "reorder_role")}>
                        <option value="">None</option>
                        {REORDER_ROLE_OPTIONS.map((option) => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    </label>
                    <label className="field toggle-field">
                      <span>Luat Nhan Trigger</span>
                      <input
                        type="checkbox"
                        checked={Boolean(effectiveDraft.luat_nhan_trigger)}
                        onChange={(event) => props.onDraftChange("luat_nhan_trigger", event.target.checked)}
                      />
                    </label>
                  </div>

                  <label className="field">
                    <span>Notes</span>
                    <textarea className="textarea compact-textarea" value={effectiveDraft.notes} onChange={handleChange(props.onDraftChange, "notes")} />
                  </label>
                  <label className="field">
                    <span>Full Explanation</span>
                    <textarea className="textarea compact-textarea" value={effectiveDraft.full_explanation} onChange={handleChange(props.onDraftChange, "full_explanation")} />
                  </label>

                  <div className="tag-row">
                    <span className="pill subtle">{effectiveDraft.table_name}</span>
                    <span className="pill subtle">{effectiveDraft.source_file}</span>
                    {effectiveDraft.source_path ? <span className="pill subtle">{effectiveDraft.source_path}</span> : null}
                  </div>

                  <div className="action-row">
                    <button className="button" type="button" disabled={props.busy || !props.backendAvailable} onClick={props.onSave}>
                      Save Entry
                    </button>
                  </div>
                </div>
              ) : (
                <p className="empty-state">Chọn một entry để mở trình chỉnh sửa chi tiết.</p>
              )}
            </Panel>

            <Panel title="Metadata Preview" subtitle="JSON được backend đồng bộ vào SQLite và Markdown nguồn.">
              <pre className="output-block compact-block">
                {JSON.stringify(effectiveDraft?.metadata ?? {}, null, 2)}
              </pre>
            </Panel>
          </div>
        </div>

        <div className="toolbar">
          <div className="action-row">
            <button className="button secondary" type="button" disabled={props.page <= 1 || props.busy} onClick={() => props.onSearch(props.page - 1)}>
              Prev
            </button>
            <span className="pill subtle">Page {props.page}/{totalPages}</span>
            <button className="button secondary" type="button" disabled={props.page >= totalPages || props.busy} onClick={() => props.onSearch(props.page + 1)}>
              Next
            </button>
          </div>
          <div className="action-row">
            <label className="field compact">
              <span>Bulk POS</span>
              <select className="input" value={props.bulkPosTag} onChange={(event) => props.onBulkPosTagChange(event.target.value)}>
                <option value="">None</option>
                {POS_TAG_OPTIONS.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <label className="field compact">
              <span>Bulk Entity</span>
              <select className="input" value={props.bulkEntityType} onChange={(event) => props.onBulkEntityTypeChange(event.target.value)}>
                <option value="">None</option>
                {ENTITY_OPTIONS.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <button className="button secondary" type="button" disabled={!props.selectedIds.length || props.busy || !props.backendAvailable} onClick={props.onApplyBulkUpdate}>
              Apply To Selected
            </button>
            <button className="button secondary" type="button" onClick={props.onExportFiltered}>
              Export Filtered
            </button>
          </div>
        </div>
      </Panel>
    </div>
  );
}

function handleChange(
  onChange: (field: DraftField, value: string | boolean) => void,
  field: DraftField,
) {
  return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    onChange(field, event.target.value);
  };
}
