import type { DictionaryEntry, PipelineStatus, ProjectOverview } from "../protocol";
import { MetricRing } from "../components/MetricRing";
import { POSBadge } from "../components/POSBadge";
import { EntityBadge } from "../components/EntityBadge";

export function DashboardScreen(props: {
  overview: ProjectOverview | null;
  pipeline: PipelineStatus | null;
  quickQuery: string;
  quickResults: DictionaryEntry[];
  onQuickQueryChange: (value: string) => void;
  onQuickSearch: () => void;
  onOpenDictionaryEntry: (entry: DictionaryEntry) => void;
}) {
  const stats = props.pipeline?.dictionary_stats;
  const lastState = props.pipeline?.last_state ?? {};
  const stages = props.pipeline?.stages ?? [];
  const lastStateItems = Object.entries(lastState).slice(0, 6);

  const summaryItems = [
    ["Chương", props.overview?.counts.chapters ?? 0],
    ["Đoạn", props.overview?.counts.segments ?? 0],
    ["Candidate", props.overview?.counts.candidates_total ?? 0],
    ["QA", props.overview?.counts.qa_issues ?? 0],
  ];

  const dictionaryItems = [
    ["Tổng", stats?.total ?? 0],
    ["Runtime", stats?.runtime_total ?? 0],
    ["Tham chiếu", stats?.reference_total ?? 0],
    ["Entity", stats?.entity_total ?? 0],
  ];

  return (
    <div className="dashboard-compact">
      <section className="panel dashboard-summary-card">
        <div className="dashboard-card-head">
          <div>
            <span className="brand-kicker">Tổng quan</span>
            <h3>{props.overview?.project.project_id ?? "Chưa có project"}</h3>
          </div>
          <span className="pill subtle">{props.overview?.project.active_chapter ?? "Chưa chọn chương"}</span>
        </div>

        <div className="dashboard-stat-strip">
          {summaryItems.map(([label, value]) => (
            <div key={label} className="dashboard-mini-metric">
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </div>

        <div className="dashboard-stat-strip dictionary-strip">
          {dictionaryItems.map(([label, value]) => (
            <div key={label} className="dashboard-mini-metric">
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </div>

        <div className="dashboard-ring-row">
          <MetricRing label="POS" value={stats?.pos_coverage_pct ?? 0} />
          <MetricRing label="Pinyin" value={stats?.pinyin_coverage_pct ?? 0} tone="warm" />
        </div>
      </section>

      <section className="panel dashboard-pipeline-card">
        <div className="dashboard-card-head">
          <div>
            <h3>Pipeline</h3>
            <p>Stage runtime rút gọn</p>
          </div>
        </div>
        <div className="dashboard-stage-list">
          {stages.length ? (
            stages.map((stage) => (
              <article key={stage.id} className={`dashboard-stage-row step-${stage.status}`}>
                <span className="step-marker">{stage.progress}%</span>
                <div>
                  <strong>{stage.label}</strong>
                  <p>{stage.message}</p>
                </div>
                <span className={`pill tone-${stage.status}`}>{stage.status}</span>
              </article>
            ))
          ) : (
            <p className="empty-state">Chưa có trạng thái pipeline.</p>
          )}
        </div>
      </section>

      <section className="panel dashboard-state-card">
        <div className="dashboard-card-head">
          <div>
            <h3>Trạng thái gần nhất</h3>
            <p>Giá trị workflow mới nhất</p>
          </div>
        </div>
        <div className="dashboard-state-strip">
          {lastStateItems.length ? (
            lastStateItems.map(([key, value]) => (
              <div key={key} className="dashboard-state-chip">
                <span>{key}</span>
                <strong>{String(value)}</strong>
              </div>
            ))
          ) : (
            <p className="empty-state">Chưa có trạng thái workflow.</p>
          )}
        </div>
      </section>

      <section className="panel dashboard-lookup-card">
        <div className="dashboard-card-head">
          <div>
            <h3>Tra nhanh</h3>
            <p>Mở nhanh mục từ điển</p>
          </div>
        </div>
        <div className="toolbar dashboard-toolbar">
          <label className="field grow">
            <span>Từ khóa</span>
            <input
              className="input"
              value={props.quickQuery}
              onChange={(event) => props.onQuickQueryChange(event.target.value)}
              placeholder="Nguồn, pinyin hoặc target"
            />
          </label>
          <button className="button" type="button" onClick={props.onQuickSearch}>
            Tìm
          </button>
        </div>
        <div className="dashboard-lookup-list">
          {props.quickResults.length ? (
            props.quickResults.slice(0, 4).map((entry) => (
              <button
                key={entry.record_id || `${entry.source}-${entry.table_name}`}
                className="list-card dashboard-lookup-row"
                type="button"
                onClick={() => props.onOpenDictionaryEntry(entry)}
              >
                <div className="candidate-head">
                  <strong>{entry.source}</strong>
                  <POSBadge tag={entry.pos_tag} sub={entry.pos_sub} />
                </div>
                <span>{entry.target_vi}</span>
                <div className="tag-row">
                  <span className="pill subtle">{entry.source_dict}</span>
                  <EntityBadge entityType={entry.entity_type} />
                </div>
              </button>
            ))
          ) : (
            <p className="empty-state">Chưa có kết quả tra nhanh.</p>
          )}
        </div>
      </section>
    </div>
  );
}
