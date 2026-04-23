import type { DictionaryEntry, PipelineStatus, ProjectOverview } from "../protocol";
import { MetricRing } from "../components/MetricRing";
import { Panel, MetricCard } from "../components/Panel";
import { PipelineStepper } from "../components/PipelineStepper";
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

  return (
    <div className="panel-stack">
      <div className="dashboard-grid">
        <Panel title="KPI Dictionary" subtitle="Tổng quan độ phủ metadata và quy mô runtime dictionary">
          <div className="metrics-row dashboard-metrics">
            <MetricCard label="Tổng Mục" value={stats?.total ?? 0} />
            <MetricCard label="Runtime" value={stats?.runtime_total ?? 0} />
            <MetricCard label="Reference" value={stats?.reference_total ?? 0} />
            <MetricCard label="Entity" value={stats?.entity_total ?? 0} />
          </div>
          <div className="ring-row">
            <MetricRing label="POS Coverage" value={stats?.pos_coverage_pct ?? 0} />
            <MetricRing label="Pinyin Coverage" value={stats?.pinyin_coverage_pct ?? 0} tone="warm" />
          </div>
        </Panel>

        <Panel title="Pipeline Snapshot" subtitle="Trạng thái hiện tại của toàn bộ pipeline thao tác">
          <PipelineStepper stages={props.pipeline?.stages ?? []} />
        </Panel>
      </div>

      <div className="dashboard-grid">
        <Panel title="Recent Workflow" subtitle="Trạng thái import, dịch và QA mới nhất của project đang chọn.">
          <div className="detail-grid">
            <MetricCard label="Chapters" value={props.overview?.counts.chapters ?? 0} />
            <MetricCard label="Segments" value={props.overview?.counts.segments ?? 0} />
            <MetricCard label="Candidates" value={props.overview?.counts.candidates_total ?? 0} />
            <MetricCard label="QA Issues" value={props.overview?.counts.qa_issues ?? 0} />
          </div>
          <pre className="output-block compact-block">{JSON.stringify(lastState, null, 2)}</pre>
        </Panel>

        <Panel title="Quick Dictionary Lookup" subtitle="Tra nhanh term, nhảy sang Dictionary Editor khi cần chỉnh sửa.">
          <div className="toolbar">
            <label className="field grow">
              <span>Quick Query</span>
              <input
                className="input"
                value={props.quickQuery}
                onChange={(event) => props.onQuickQueryChange(event.target.value)}
                placeholder="Nhập Hán tự, pinyin hoặc nghĩa"
              />
            </label>
            <button className="button" type="button" onClick={props.onQuickSearch}>
              Search
            </button>
          </div>
          <div className="list-stack">
            {props.quickResults.length ? (
              props.quickResults.slice(0, 6).map((entry) => (
                <button
                  key={entry.record_id || `${entry.source}-${entry.table_name}`}
                  className="list-card"
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
              <p className="empty-state">Chưa có kết quả tra cứu nhanh</p>
            )}
          </div>
        </Panel>
      </div>
    </div>
  );
}
