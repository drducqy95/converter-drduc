import type { ProjectOverview, QAReport, TranslationArtifacts } from "../protocol";
import { Panel } from "../components/Panel";
import { POSBadge } from "../components/POSBadge";

export function TranslationWorkspaceScreen(props: {
  busy: boolean;
  backendAvailable: boolean;
  importPath: string;
  translationInput: string;
  overview: ProjectOverview | null;
  translation: TranslationArtifacts | null;
  qaReport: QAReport | null;
  onImportPathChange: (value: string) => void;
  onPickImportPath: (kind: "file" | "folder") => void;
  onImport: () => void;
  onTranslationInputChange: (value: string) => void;
  onTranslate: () => void;
  onRunQa: () => void;
  onSelectChapter: (chapterId: string, chapterText: string) => void;
  onInspectToken: (query: string) => void;
}) {
  const activeChapter = props.overview?.chapters.find((item) => item.chapter_id === props.overview?.project.active_chapter)
    ?? props.overview?.chapters[0]
    ?? null;

  return (
    <div className="panel-stack">
      <Panel title="Translation Intake" subtitle="Nhập nguồn, chọn chapter và khởi động pipeline dịch cho active slice.">
        <div className="toolbar">
          <label className="field grow">
            <span>Source File / Folder</span>
            <input
              className="input"
              value={props.importPath}
              onChange={(event) => props.onImportPathChange(event.target.value)}
              placeholder="D:\\Novel\\source\\chapter-001.md"
            />
          </label>
          <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable} onClick={() => props.onPickImportPath("file")}>
            Choose File
          </button>
          <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable} onClick={() => props.onPickImportPath("folder")}>
            Choose Folder
          </button>
          <button className="button" type="button" disabled={props.busy || !props.backendAvailable} onClick={props.onImport}>
            Import
          </button>
          <button className="button" type="button" disabled={props.busy || !props.backendAvailable} onClick={props.onTranslate}>
            Translate Active Slice
          </button>
          <button className="button secondary" type="button" disabled={props.busy || !props.backendAvailable} onClick={props.onRunQa}>
            Run QA
          </button>
        </div>
      </Panel>

      <div className="translation-grid">
        <Panel title="Chapter Queue" subtitle="Chọn active chapter và chuyển nhanh sang token inspection.">
          <div className="list-stack">
            {props.overview?.chapters.length ? (
              props.overview.chapters.map((chapter) => (
                <button
                  key={chapter.chapter_id}
                  className={`list-card ${chapter.chapter_id === activeChapter?.chapter_id ? "active" : ""}`}
                  type="button"
                  onClick={() => props.onSelectChapter(chapter.chapter_id, chapter.text)}
                >
                  <strong>{chapter.chapter_id}</strong>
                  <span>{chapter.title}</span>
                  <small>{chapter.source_path ?? "No source path"}</small>
                </button>
              ))
            ) : (
              <p className="empty-state">Chưa có chapter nào trong project.</p>
            )}
          </div>
        </Panel>

        <div className="panel-stack">
          <Panel title="Parallel Compare" subtitle="So sánh song song giữa nguồn, clean output và draft trace.">
            <div className="compare-grid">
              <label className="field">
                <span>Source Text</span>
                <textarea
                  className="textarea"
                  value={props.translationInput}
                  onChange={(event) => props.onTranslationInputChange(event.target.value)}
                />
              </label>
              <label className="field">
                <span>Clean Output</span>
                <textarea className="textarea" value={props.translation?.clean_text ?? ""} readOnly />
              </label>
            </div>
            <label className="field">
              <span>Annotated Draft</span>
              <textarea className="textarea compact-textarea" value={props.translation?.draft_text ?? ""} readOnly />
            </label>
          </Panel>

          <Panel title="Source Token Overlay" subtitle="Token được trích từ translation trace, click để mở Dictionary Editor.">
            <div className="token-grid">
              {props.translation?.segments.flatMap((segment) => segment.trace).length ? (
                props.translation.segments.flatMap((segment) => segment.trace).map((trace, index) => (
                  <button
                    key={`${trace.source}-${index}`}
                    className="token-chip"
                    type="button"
                    onClick={() => props.onInspectToken(trace.source)}
                  >
                    <strong>{trace.source}</strong>
                    <POSBadge tag={undefined} />
                    <span>{trace.selected}</span>
                  </button>
                ))
              ) : (
                <p className="empty-state">Dịch xong sẽ có danh sách token trace để inspect.</p>
              )}
            </div>
          </Panel>
        </div>
      </div>

      <div className="split-grid">
        <Panel title="Trace Evidence" subtitle="Segment trace và fallback để review thứ tự pipeline">
          <div className="list-stack">
            {props.translation?.segments.length ? (
              props.translation.segments.map((segment) => (
                <article key={segment.sentence_id} className="trace-card">
                  <div className="trace-head">
                    <strong>{segment.sentence_id}</strong>
                    <span className={`pill tone-${segment.fallback_level ?? "runtime"}`}>{segment.fallback_level ?? "runtime"}</span>
                  </div>
                  <p>{segment.source_text}</p>
                  <div className="tag-row">
                    {segment.trace.map((trace) => (
                      <button key={`${segment.sentence_id}-${trace.source}`} className="pill subtle" type="button" onClick={() => props.onInspectToken(trace.source)}>
                        {trace.source} -&gt; {trace.selected}
                      </button>
                    ))}
                  </div>
                </article>
              ))
            ) : (
              <p className="empty-state">Chưa có translation trace.</p>
            )}
          </div>
        </Panel>

        <Panel title="QA Snapshot" subtitle="Issue-level summary để theo dõi trước khi sang Coach.">
          <div className="list-stack">
            {props.qaReport?.issues.length ? (
              props.qaReport.issues.map((issue) => (
                <article key={`${issue.segment_id}-${issue.checker}`} className="issue-card">
                  <div className="trace-head">
                    <strong>{issue.checker}</strong>
                    <span className={`pill tone-${issue.severity}`}>{issue.severity}</span>
                  </div>
                  <p>{issue.message}</p>
                  <small>{issue.segment_id}</small>
                </article>
              ))
            ) : (
              <p className="empty-state">QA chưa có issue nào cho active chapter.</p>
            )}
          </div>
        </Panel>
      </div>
    </div>
  );
}
