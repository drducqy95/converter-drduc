import type {
  CandidateEntry,
  CandidateRule,
  LearningReport,
  NaturalFeedbackAnalysis,
  ProjectOverview,
} from "../protocol";
import { EntityBadge } from "../components/EntityBadge";
import { Panel } from "../components/Panel";
import { POSBadge } from "../components/POSBadge";

export function CoachScreen(props: {
  busy: boolean;
  backendAvailable: boolean;
  overview: ProjectOverview | null;
  candidates: CandidateEntry[];
  candidateRules: CandidateRule[];
  learningReport: LearningReport | null;
  feedbackAnalysis: NaturalFeedbackAnalysis | null;
  feedbackText: string;
  feedbackSourceText: string;
  feedbackCurrentTranslation: string;
  feedbackPreferredTranslation: string;
  feedbackScope: string;
  feedbackRuleHint: string;
  ruleFilter: string;
  candidateFilter: string;
  candidateQuery: string;
  onFeedbackFieldChange: (field: string, value: string) => void;
  onRuleFilterChange: (value: string) => void;
  onCandidateFilterChange: (value: string) => void;
  onCandidateQueryChange: (value: string) => void;
  onSubmitFeedback: () => void;
  onReviewRule: (rule: CandidateRule, status: string) => void;
  onReviewCandidate: (entry: CandidateEntry, status: string) => void;
  onInspectToken: (query: string) => void;
}) {
  const filteredRules = props.candidateRules.filter((rule) => props.ruleFilter === "all" || rule.status === props.ruleFilter);
  const filteredCandidates = props.candidates.filter((entry) => {
    const matchesStatus = props.candidateFilter === "all" || entry.status === props.candidateFilter;
    const query = props.candidateQuery.trim().toLowerCase();
    if (!query) {
      return matchesStatus;
    }
    const haystack = `${entry.source_text} ${entry.target_text} ${entry.reason}`.toLowerCase();
    return matchesStatus && haystack.includes(query);
  });

  return (
    <div className="panel-stack">
      <div className="split-grid coach-grid">
        <Panel title="Feedback Form" subtitle="Đóng vào feedback, preferred translation và scope học tập.">
          <div className="form-grid">
            <div className="split-grid">
              <label className="field">
                <span>Scope</span>
                <select className="input" value={props.feedbackScope} onChange={(event) => props.onFeedbackFieldChange("feedbackScope", event.target.value)}>
                  <option value="chapter">Chapter</option>
                  <option value="project">Project</option>
                </select>
              </label>
              <label className="field">
                <span>Rule Hint</span>
                <select className="input" value={props.feedbackRuleHint} onChange={(event) => props.onFeedbackFieldChange("feedbackRuleHint", event.target.value)}>
                  <option value="auto">Auto</option>
                  <option value="phrase_override">Phrase Override</option>
                  <option value="style_profile">Style Profile</option>
                  <option value="style_guidance">Style Guidance</option>
                </select>
              </label>
            </div>
            <label className="field">
              <span>Feedback</span>
              <textarea className="textarea compact-textarea" value={props.feedbackText} onChange={(event) => props.onFeedbackFieldChange("feedbackText", event.target.value)} />
            </label>
            <label className="field">
              <span>Source Snippet</span>
              <textarea className="textarea compact-textarea" value={props.feedbackSourceText} onChange={(event) => props.onFeedbackFieldChange("feedbackSourceText", event.target.value)} />
            </label>
            <label className="field">
              <span>Current Translation</span>
              <textarea className="textarea compact-textarea" value={props.feedbackCurrentTranslation} onChange={(event) => props.onFeedbackFieldChange("feedbackCurrentTranslation", event.target.value)} />
            </label>
            <label className="field">
              <span>Preferred Translation</span>
              <textarea className="textarea compact-textarea" value={props.feedbackPreferredTranslation} onChange={(event) => props.onFeedbackFieldChange("feedbackPreferredTranslation", event.target.value)} />
            </label>
            <button className="button" type="button" disabled={props.busy || !props.backendAvailable} onClick={props.onSubmitFeedback}>
              Analyze and Propose
            </button>
          </div>
        </Panel>

        <Panel title="Learning Timeline" subtitle="Snapshot mới nhất và đề xuất từ vòng học tập.">
          <div className="list-stack">
            <article className="timeline-row">
              <span className="pill subtle">Now</span>
              <div>
                <strong>{props.overview?.project.active_chapter ?? "project"}</strong>
                <p>{String(props.learningReport?.current_run?.qa_total ?? "No QA data yet")}</p>
              </div>
            </article>
            <article className="timeline-row">
              <span className="pill subtle">Reco</span>
              <div>
                <strong>Recommendations</strong>
                <p>{String((props.learningReport?.recommendations ?? []).length)} item(s)</p>
              </div>
            </article>
            <article className="timeline-row">
              <span className="pill subtle">Auto</span>
              <div>
                <strong>Auto Applied</strong>
                <p>{String((props.learningReport?.auto_applied ?? []).length)} item(s)</p>
              </div>
            </article>
          </div>
          <pre className="output-block compact-block">{JSON.stringify(props.learningReport ?? {}, null, 2)}</pre>
        </Panel>
      </div>

      <div className="split-grid coach-grid">
        <Panel title="Analysis Suggestions" subtitle="Danh sách suggestion sinh ra từ feedback tự nhiên.">
          <div className="list-stack">
            {props.feedbackAnalysis?.suggestions.length ? (
              props.feedbackAnalysis.suggestions.map((suggestion, index) => (
                <article key={`${suggestion.rule_type}-${index}`} className="candidate-card">
                  <div className="candidate-head">
                    <strong>{suggestion.title}</strong>
                    <span className="pill subtle">{Math.round(suggestion.confidence * 100)}%</span>
                  </div>
                  <p>{suggestion.summary}</p>
                  <div className="tag-row">
                    <span className="pill subtle">{suggestion.scope}</span>
                    <span className="pill subtle">{suggestion.origin}</span>
                  </div>
                  <pre className="output-block compact-block">{JSON.stringify(suggestion.payload, null, 2)}</pre>
                </article>
              ))
            ) : (
              <p className="empty-state">Submit feedback để populate suggestion queue.</p>
            )}
          </div>
        </Panel>

        <Panel title="Candidate Entry Review" subtitle="Review ambiguity term với ngữ cảnh chapter và mở thẳng Dictionary Editor.">
          <div className="toolbar">
            <label className="field compact">
              <span>Status</span>
              <select className="input" value={props.candidateFilter} onChange={(event) => props.onCandidateFilterChange(event.target.value)}>
                <option value="all">All</option>
                <option value="candidate">Candidate</option>
                <option value="verified">Verified</option>
                <option value="rejected">Rejected</option>
              </select>
            </label>
            <label className="field grow">
              <span>Search</span>
              <input className="input" value={props.candidateQuery} onChange={(event) => props.onCandidateQueryChange(event.target.value)} />
            </label>
          </div>
          <div className="list-stack">
            {filteredCandidates.length ? (
              filteredCandidates.map((entry) => (
                <article key={entry.id} className="candidate-card">
                  <div className="candidate-head">
                    <div>
                      <strong>{entry.source_text} -&gt; {entry.target_text}</strong>
                      <p>{entry.reason}</p>
                    </div>
                    <span className={`pill tone-${entry.status}`}>{entry.status}</span>
                  </div>
                  <div className="tag-row">
                    <span className="pill subtle">{entry.chapter_id || "project"}</span>
                    <span className="pill subtle">{entry.fallback_level}</span>
                    <button className="pill subtle" type="button" onClick={() => props.onInspectToken(entry.source_text)}>
                      Open In Dictionary
                    </button>
                  </div>
                  <div className="action-row">
                    <button className="button" type="button" disabled={props.busy || !props.backendAvailable || entry.status === "verified"} onClick={() => props.onReviewCandidate(entry, "verified")}>
                      Verify
                    </button>
                    <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable || entry.status === "rejected"} onClick={() => props.onReviewCandidate(entry, "rejected")}>
                      Reject
                    </button>
                  </div>
                </article>
              ))
            ) : (
              <p className="empty-state">Không có candidate entry nào cho filter hiện tại.</p>
            )}
          </div>
        </Panel>
      </div>

      <Panel title="Candidate Rules" subtitle="Rule queue được verify/reject và apply thẳng vào project config.">
        <div className="toolbar">
          <label className="field compact">
            <span>Status</span>
            <select className="input" value={props.ruleFilter} onChange={(event) => props.onRuleFilterChange(event.target.value)}>
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
                    <strong>{String(rule.rule_payload.title ?? rule.rule_type)}</strong>
                    <p>{String(rule.rule_payload.summary ?? rule.rule_type)}</p>
                  </div>
                  <span className={`pill tone-${rule.status}`}>{rule.status}</span>
                </div>
                <div className="tag-row">
                  <span className="pill subtle">{rule.rule_type}</span>
                  <EntityBadge entityType={String(rule.rule_payload.payload && typeof rule.rule_payload.payload === "object" ? (rule.rule_payload.payload as Record<string, unknown>).entity_type ?? "" : "")} />
                  <POSBadge tag={String(rule.rule_payload.payload && typeof rule.rule_payload.payload === "object" ? (rule.rule_payload.payload as Record<string, unknown>).pos_tag ?? "" : "")} />
                </div>
                <pre className="output-block compact-block">{JSON.stringify(rule.rule_payload, null, 2)}</pre>
                <div className="action-row">
                  <button className="button" type="button" disabled={props.busy || !props.backendAvailable || rule.status === "verified"} onClick={() => props.onReviewRule(rule, "verified")}>
                    Verify and Apply
                  </button>
                  <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable || rule.status === "rejected"} onClick={() => props.onReviewRule(rule, "rejected")}>
                    Reject
                  </button>
                </div>
              </article>
            ))
          ) : (
            <p className="empty-state">Chưa có candidate rule.</p>
          )}
        </div>
      </Panel>
    </div>
  );
}
