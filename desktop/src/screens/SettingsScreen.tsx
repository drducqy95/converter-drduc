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
        <Panel title="Environment" subtitle="Protocol, transport và artifact path đang hoạt động.">
          <div className="detail-grid">
            <InfoLine label="Protocol Version" value={PROTOCOL_VERSION} />
            <InfoLine label="Transport" value={props.transport?.mode ?? "initializing"} />
            <InfoLine label="Workspace Root" value={props.workspaceBaseDir || "workspace_projects"} />
            <InfoLine label="Active Project" value={props.overview?.project.project_id ?? "None"} />
            <InfoLine label="DB Total" value={String(props.pipeline?.dictionary_stats.total ?? 0)} />
            <InfoLine label="POS Coverage" value={`${props.pipeline?.dictionary_stats.pos_coverage_pct ?? 0}%`} />
          </div>
          <label className="field">
            <span>Workspace Project Root</span>
            <input className="input" value={props.workspaceBaseDir} onChange={(event) => props.onWorkspaceBaseDirChange(event.target.value)} />
          </label>
        </Panel>

        <Panel title="Maintenance" subtitle="Điều khiển rerun compiler, seeder và kiểm tra tính sẵn sàng của pipeline.">
          <div className="action-column">
            <button className="button" type="button" disabled={props.busy || !props.backendAvailable} onClick={() => props.onRunStage("compile")}>
              Rerun Dictionary Compile
            </button>
            <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable} onClick={() => props.onRunStage("assign_pos")}>
              Rerun POS Seeder
            </button>
            <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable} onClick={() => props.onRunStage("export")}>
              Verify Export Artifacts
            </button>
          </div>
          <pre className="output-block compact-block">{JSON.stringify(props.pipeline?.dictionary_stats.metadata ?? {}, null, 2)}</pre>
        </Panel>
      </div>

      <Panel title="Artifact Paths" subtitle="Tất cả path đã được normalize về absolute path để tránh lỗi dẫn path cũ.">
        <pre className="output-block">{JSON.stringify(props.overview?.artifacts ?? {}, null, 2)}</pre>
      </Panel>
    </div>
  );
}
