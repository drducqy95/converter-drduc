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
  grammarScanReport: Record<string, unknown> | null;
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
  onScanGrammarPatterns: () => void;
  onReviewRule: (rule: CandidateRule, status: string) => void;
  onReviewCandidate: (entry: CandidateEntry, status: string) => void;
  onInspectToken: (query: string) => void;
}) {
  const filteredRules = props.candidateRules.filter((rule) => props.ruleFilter === "all" || rule.status === props.ruleFilter);
  const grammarSummary = (props.grammarScanReport?.summary && typeof props.grammarScanReport.summary === "object"
    ? props.grammarScanReport.summary
    : {}) as Record<string, unknown>;
  const grammarUnknownCount = Number(grammarSummary.unknown_candidate_count ?? 0) || 0;
  const grammarMatchCount = Number(grammarSummary.total_matches ?? 0) || 0;
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
        <Panel title="Form feedback" subtitle="Nhập feedback, bản dịch mong muốn và phạm vi học.">
          <div className="form-grid">
            <div className="split-grid">
              <label className="field">
                <span>Phạm vi</span>
                <select className="input" value={props.feedbackScope} onChange={(event) => props.onFeedbackFieldChange("feedbackScope", event.target.value)}>
                  <option value="chapter">Chương</option>
                  <option value="project">Project</option>
                </select>
              </label>
              <label className="field">
                <span>Gợi ý rule</span>
                <select className="input" value={props.feedbackRuleHint} onChange={(event) => props.onFeedbackFieldChange("feedbackRuleHint", event.target.value)}>
                  <option value="auto">Tự động</option>
                  <option value="phrase_override">Override cụm</option>
                  <option value="style_profile">Style profile</option>
                  <option value="style_guidance">Hướng dẫn style</option>
                </select>
              </label>
            </div>
            <label className="field">
              <span>Feedback</span>
              <textarea className="textarea compact-textarea" value={props.feedbackText} onChange={(event) => props.onFeedbackFieldChange("feedbackText", event.target.value)} />
            </label>
            <label className="field">
              <span>Trích đoạn nguồn</span>
              <textarea className="textarea compact-textarea" value={props.feedbackSourceText} onChange={(event) => props.onFeedbackFieldChange("feedbackSourceText", event.target.value)} />
            </label>
            <label className="field">
              <span>Bản dịch hiện tại</span>
              <textarea className="textarea compact-textarea" value={props.feedbackCurrentTranslation} onChange={(event) => props.onFeedbackFieldChange("feedbackCurrentTranslation", event.target.value)} />
            </label>
            <label className="field">
              <span>Bản dịch mong muốn</span>
              <textarea className="textarea compact-textarea" value={props.feedbackPreferredTranslation} onChange={(event) => props.onFeedbackFieldChange("feedbackPreferredTranslation", event.target.value)} />
            </label>
            <button className="button" type="button" disabled={props.busy || !props.backendAvailable} onClick={props.onSubmitFeedback}>
              Phân tích và đề xuất
            </button>
            <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable} onClick={props.onScanGrammarPatterns}>
              Quét mẫu ngữ pháp
            </button>
          </div>
        </Panel>

        <Panel title="Timeline học" subtitle="Snapshot mới nhất và đề xuất từ vòng học tập.">
          <div className="list-stack">
            <article className="timeline-row">
              <span className="pill subtle">Now</span>
              <div>
                <strong>{props.overview?.project.active_chapter ?? "project"}</strong>
                <p>{String(props.learningReport?.current_run?.qa_total ?? "Chưa có dữ liệu QA")}</p>
              </div>
            </article>
            <article className="timeline-row">
              <span className="pill subtle">Reco</span>
              <div>
                <strong>Đề xuất</strong>
                <p>{String((props.learningReport?.recommendations ?? []).length)} item(s)</p>
              </div>
            </article>
            <article className="timeline-row">
              <span className="pill subtle">Auto</span>
              <div>
                <strong>Tự áp dụng</strong>
                <p>{String((props.learningReport?.auto_applied ?? []).length)} item(s)</p>
              </div>
            </article>
            <article className="timeline-row">
              <span className="pill subtle">Grammar</span>
              <div>
                <strong>Quét pattern</strong>
                <p>{grammarUnknownCount} candidate chưa rõ, {grammarMatchCount} match đã biết</p>
              </div>
            </article>
          </div>
          <pre className="output-block compact-block">{JSON.stringify(props.learningReport ?? {}, null, 2)}</pre>
          {props.grammarScanReport ? (
            <pre className="output-block compact-block">{JSON.stringify(props.grammarScanReport, null, 2)}</pre>
          ) : null}
        </Panel>
      </div>

      <div className="split-grid coach-grid">
        <Panel title="Đề xuất phân tích" subtitle="Danh sách suggestion sinh ra từ feedback tự nhiên.">
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
              <p className="empty-state">Gửi feedback để tạo hàng đợi suggestion.</p>
            )}
          </div>
        </Panel>

        <Panel title="Duyệt candidate entry" subtitle="Review term mơ hồ theo ngữ cảnh chương và mở thẳng Từ điển.">
          <div className="toolbar">
            <label className="field compact">
              <span>Trạng thái</span>
              <select className="input" value={props.candidateFilter} onChange={(event) => props.onCandidateFilterChange(event.target.value)}>
                <option value="all">Tất cả</option>
                <option value="candidate">Candidate</option>
                <option value="verified">Đã duyệt</option>
                <option value="rejected">Đã loại</option>
              </select>
            </label>
            <label className="field grow">
              <span>Tìm</span>
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
                      Mở trong Từ điển
                    </button>
                  </div>
                  <div className="action-row">
                    <button className="button" type="button" disabled={props.busy || !props.backendAvailable || entry.status === "verified"} onClick={() => props.onReviewCandidate(entry, "verified")}>
                      Duyệt
                    </button>
                    <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable || entry.status === "rejected"} onClick={() => props.onReviewCandidate(entry, "rejected")}>
                      Loại
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

      <Panel title="Candidate rule" subtitle="Hàng đợi rule được duyệt/loại và apply vào project config.">
        <div className="toolbar">
          <label className="field compact">
            <span>Trạng thái</span>
            <select className="input" value={props.ruleFilter} onChange={(event) => props.onRuleFilterChange(event.target.value)}>
              <option value="all">Tất cả</option>
              <option value="candidate">Candidate</option>
              <option value="verified">Đã duyệt</option>
              <option value="rejected">Đã loại</option>
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
                    Duyệt và áp dụng
                  </button>
                  <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable || rule.status === "rejected"} onClick={() => props.onReviewRule(rule, "rejected")}>
                    Loại
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
