import type { PipelineStatus, ProjectOverview, Transport } from "../protocol";
import { Panel, InfoLine } from "../components/Panel";
import { PROTOCOL_VERSION } from "../protocol";

export function SettingsScreen(props: {
  transport: Transport | null;
  overview: ProjectOverview | null;
  pipeline: PipelineStatus | null;
  workspaceBaseDir: string;
  onWorkspaceBaseDirChange: (value: string) => void;
  onRunStage: (stageId: string) => void;
  busy: boolean;
  backendAvailable: boolean;
}) {
  return (
    <div className="panel-stack">
      <div className="split-grid">
        <Panel title="Môi trường" subtitle="Protocol, transport và artifact path đang hoạt động.">
          <div className="detail-grid">
            <InfoLine label="Phiên bản protocol" value={PROTOCOL_VERSION} />
            <InfoLine label="Transport" value={props.transport?.mode ?? "initializing"} />
            <InfoLine label="Workspace root" value={props.workspaceBaseDir || "workspace_projects"} />
            <InfoLine label="Project đang mở" value={props.overview?.project.project_id ?? "Chưa có"} />
            <InfoLine label="Tổng DB" value={String(props.pipeline?.dictionary_stats.total ?? 0)} />
            <InfoLine label="Phủ POS" value={`${props.pipeline?.dictionary_stats.pos_coverage_pct ?? 0}%`} />
          </div>
          <label className="field">
            <span>Workspace project root</span>
            <input className="input" value={props.workspaceBaseDir} onChange={(event) => props.onWorkspaceBaseDirChange(event.target.value)} />
          </label>
        </Panel>

        <Panel title="Bảo trì" subtitle="Chạy lại compiler, seeder và kiểm tra tính sẵn sàng của pipeline.">
          <div className="action-column">
            <button className="button" type="button" disabled={props.busy || !props.backendAvailable} onClick={() => props.onRunStage("compile")}>
              Chạy lại compile từ điển
            </button>
            <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable} onClick={() => props.onRunStage("assign_pos")}>
              Chạy lại POS seeder
            </button>
            <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable} onClick={() => props.onRunStage("export")}>
              Kiểm tra artifact xuất
            </button>
          </div>
          <pre className="output-block compact-block">{JSON.stringify(props.pipeline?.dictionary_stats.metadata ?? {}, null, 2)}</pre>
        </Panel>
      </div>

      <Panel title="Đường dẫn artifact" subtitle="Tất cả path đã được normalize về absolute path để tránh lỗi dẫn path cũ.">
        <pre className="output-block">{JSON.stringify(props.overview?.artifacts ?? {}, null, 2)}</pre>
      </Panel>
    </div>
  );
}
