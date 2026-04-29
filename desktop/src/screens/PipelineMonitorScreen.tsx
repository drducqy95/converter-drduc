import type { CommandEvent, PipelineStatus } from "../protocol";
import { Panel } from "../components/Panel";
import { PipelineStepper } from "../components/PipelineStepper";

export function PipelineMonitorScreen(props: {
  busy: boolean;
  backendAvailable: boolean;
  pipeline: PipelineStatus | null;
  events: CommandEvent[];
  warnings: string[];
  onRunStage: (stageId: string) => void;
}) {
  return (
    <div className="panel-stack monitor-compact">
      <Panel title="Stepper pipeline" subtitle="View rút gọn: đủ các stage chính trong một khung.">
        <PipelineStepper
          stages={props.pipeline?.stages ?? []}
          onRunStage={props.onRunStage}
          busy={props.busy}
          backendAvailable={props.backendAvailable}
        />
      </Panel>

      <div className="monitor-compact-grid">
        <Panel title="Chỉ số coverage" subtitle="Dictionary coverage hiện tại.">
          <pre className="output-block compact-block">{JSON.stringify(props.pipeline?.dictionary_stats ?? {}, null, 2)}</pre>
        </Panel>

        <Panel title="Log stage" subtitle="Các event mới nhất.">
          <div className="list-stack compact-list">
            {props.events.length ? (
              props.events.slice(0, 6).map((event, index) => (
                <article key={`${event.stage}-${index}`} className="timeline-row compact-row">
                  <span className={`pill tone-${event.level}`}>{event.progress}%</span>
                  <div>
                    <strong>{event.stage}</strong>
                    <p>{event.message}</p>
                  </div>
                </article>
              ))
            ) : (
              <p className="empty-state">Chưa có event nào.</p>
            )}
          </div>
        </Panel>

        <Panel title="Cảnh báo" subtitle="Cảnh báo gần nhất.">
          <div className="list-stack compact-list">
            {props.warnings.length ? (
              props.warnings.slice(0, 5).map((warning) => (
                <article key={warning} className="issue-card compact-row">
                  <strong>warning</strong>
                  <p>{warning}</p>
                </article>
              ))
            ) : (
              <p className="empty-state">Không có warning nào.</p>
            )}
          </div>
        </Panel>
      </div>
    </div>
  );
}
