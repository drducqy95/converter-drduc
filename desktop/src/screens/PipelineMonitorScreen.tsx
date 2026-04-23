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
    <div className="panel-stack">
      <div className="split-grid monitor-grid">
        <Panel title="Pipeline Stepper" subtitle="Theo dõi từng giai đoạn Nhập -&gt; Biên dịch -&gt; Gán POS -&gt; Dịch -&gt; QA -&gt; Xuất.">
          <PipelineStepper
            stages={props.pipeline?.stages ?? []}
            onRunStage={props.onRunStage}
            busy={props.busy}
            backendAvailable={props.backendAvailable}
          />
        </Panel>

        <Panel title="Coverage Metrics" subtitle="Số liệu dictionary và coverage metadata theo thời điểm hiện tại.">
          <pre className="output-block compact-block">{JSON.stringify(props.pipeline?.dictionary_stats ?? {}, null, 2)}</pre>
        </Panel>
      </div>

      <div className="split-grid monitor-grid">
        <Panel title="Stage Logs" subtitle="Timeline command event từ sidecar, dùng để kiểm tra run lại stage.">
          <div className="list-stack">
            {props.events.length ? (
              props.events.map((event, index) => (
                <article key={`${event.stage}-${index}`} className="timeline-row">
                  <span className={`pill tone-${event.level}`}>{event.progress}%</span>
                  <div>
                    <strong>{event.stage}</strong>
                    <p>{event.message}</p>
                  </div>
                </article>
              ))
            ) : (
              <p className="empty-state">Chưa có event nào được ghi nhận.</p>
            )}
          </div>
        </Panel>

        <Panel title="Warnings" subtitle="Cảnh báo từ sidecar và script trong quá trình run stage.">
          <div className="list-stack">
            {props.warnings.length ? (
              props.warnings.map((warning) => (
                <article key={warning} className="issue-card">
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
