import type { PipelineStageStatus } from "../protocol";

export function PipelineStepper(props: {
  stages: PipelineStageStatus[];
  activeStageId?: string;
  onRunStage?: (stageId: string) => void;
  busy?: boolean;
  backendAvailable?: boolean;
}) {
  return (
    <div className="pipeline-stepper">
      {props.stages.map((stage) => (
        <article
          key={stage.id}
          className={`step-card step-${stage.status} ${props.activeStageId === stage.id ? "active" : ""}`}
        >
          <div className="step-marker">
            <span>{stage.progress}%</span>
          </div>
          <div className="step-body">
            <div className="step-head">
              <div>
                <strong>{stage.label}</strong>
                <p>{stage.message}</p>
              </div>
              <span className={`pill tone-${stage.status}`}>{stage.status}</span>
            </div>
            <div className="tag-row">
              {Object.entries(stage.metrics).slice(0, 3).map(([key, value]) => (
                <span key={`${stage.id}-${key}`} className="pill subtle">
                  {key}: {String(value)}
                </span>
              ))}
            </div>
            {props.onRunStage ? (
              <div className="action-row">
                <button
                  className="button secondary"
                  type="button"
                  disabled={props.busy || !props.backendAvailable}
                  onClick={() => props.onRunStage?.(stage.id)}
                >
                  Run Stage
                </button>
              </div>
            ) : null}
          </div>
        </article>
      ))}
    </div>
  );
}
