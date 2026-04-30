import type { FormEvent } from "react";
import { Panel, InfoLine } from "../components/Panel";
import type { ChapterInfo, ProjectOverview, ProjectRecord } from "../protocol";

function formatCount(value: number | undefined): string {
  return String(value ?? 0);
}

function chapterLabel(chapter: ChapterInfo): string {
  return chapter.title || chapter.chapter_id;
}

export function ProjectImportScreen(props: {
  busy: boolean;
  backendAvailable: boolean;
  projects: ProjectRecord[];
  selectedProjectId: string;
  createProjectId: string;
  workspaceBaseDir: string;
  importPath: string;
  overview: ProjectOverview | null;
  onCreateProjectIdChange: (value: string) => void;
  onWorkspaceBaseDirChange: (value: string) => void;
  onSelectProject: (projectId: string) => void;
  onCreateProject: (event: FormEvent<HTMLFormElement>) => void;
  onImportPathChange: (value: string) => void;
  onPickImportPath: (kind: "file" | "folder") => void;
  onImport: () => void;
  onSelectChapter: (chapterId: string, chapterText: string) => void;
  onRunStage: (stageId: string) => void;
}) {
  const activeChapterId = props.overview?.project.active_chapter ?? props.overview?.chapters[0]?.chapter_id ?? "";

  return (
    <div className="project-import-grid">
      <Panel
        title="Project Registry"
        subtitle="Tạo, chọn và kiểm tra workspace trước khi import nguồn."
        actions={<span className="pill subtle">{props.projects.length} project</span>}
      >
        <form className="project-create-bar" onSubmit={props.onCreateProject}>
          <label className="field">
            <span>Project id</span>
            <input
              className="input"
              value={props.createProjectId}
              onChange={(event) => props.onCreateProjectIdChange(event.target.value)}
              placeholder="project-001"
            />
          </label>
          <label className="field">
            <span>Workspace root</span>
            <input
              className="input"
              value={props.workspaceBaseDir}
              onChange={(event) => props.onWorkspaceBaseDirChange(event.target.value)}
              placeholder="workspace_projects"
            />
          </label>
          <button className="button primary" type="submit" disabled={props.busy || !props.backendAvailable}>
            Tạo project
          </button>
        </form>

        <div className="project-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Project</th>
                <th>Ngôn ngữ</th>
                <th>Chapter</th>
                <th>Workspace</th>
              </tr>
            </thead>
            <tbody>
              {props.projects.map((project) => (
                <tr
                  key={project.project_id}
                  className={project.project_id === props.selectedProjectId ? "selected" : ""}
                  onClick={() => props.onSelectProject(project.project_id)}
                >
                  <td>
                    <button className="table-link" type="button">
                      {project.project_id}
                    </button>
                  </td>
                  <td>
                    {project.source_language} -&gt; {project.target_language}
                  </td>
                  <td>{project.active_chapter ?? "Chưa chọn"}</td>
                  <td className="mono-cell">{project.project_dir}</td>
                </tr>
              ))}
              {!props.projects.length ? (
                <tr>
                  <td colSpan={4} className="empty-cell">
                    Chưa có project trong workspace hiện tại.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel
        title="Import Intake"
        subtitle="Nạp file hoặc thư mục nguồn, sau đó để pipeline sinh chapter, entity và cấu hình."
        actions={<span className={`pill ${props.backendAvailable ? "success" : "danger"}`}>{props.backendAvailable ? "bridge online" : "bridge offline"}</span>}
      >
        <div className="import-stack">
          <label className="field">
            <span>Đường dẫn nguồn</span>
            <div className="inline-input-row">
              <input
                className="input"
                value={props.importPath}
                onChange={(event) => props.onImportPathChange(event.target.value)}
                placeholder="D:\\novel\\chapter-001.md hoặc thư mục nguồn"
              />
              <button className="button ghost" type="button" onClick={() => props.onPickImportPath("file")} disabled={props.busy || !props.backendAvailable}>
                File
              </button>
              <button className="button ghost" type="button" onClick={() => props.onPickImportPath("folder")} disabled={props.busy || !props.backendAvailable}>
                Folder
              </button>
            </div>
          </label>
          <div className="stage-command-row">
            <button className="button primary" type="button" onClick={props.onImport} disabled={props.busy || !props.backendAvailable || !props.selectedProjectId}>
              Import nguồn
            </button>
            <button className="button" type="button" onClick={() => props.onRunStage("scan")} disabled={props.busy || !props.backendAvailable || !props.selectedProjectId}>
              Scan
            </button>
            <button className="button" type="button" onClick={() => props.onRunStage("compile")} disabled={props.busy || !props.backendAvailable}>
              Compile DB
            </button>
          </div>
        </div>
      </Panel>

      <Panel
        title="Chapter Queue"
        subtitle="Danh sách chapter đã import và active chapter sẽ được đưa vào workspace dịch."
        actions={<span className="pill subtle">{formatCount(props.overview?.chapters.length)} chapter</span>}
      >
        <div className="chapter-queue">
          {props.overview?.chapters.map((chapter) => (
            <button
              key={chapter.chapter_id}
              className={`chapter-row ${chapter.chapter_id === activeChapterId ? "active" : ""}`}
              type="button"
              onClick={() => props.onSelectChapter(chapter.chapter_id, chapter.text)}
            >
              <span className="chapter-marker" aria-hidden="true" />
              <span>
                <strong>{chapterLabel(chapter)}</strong>
                <small>{chapter.chapter_id}</small>
              </span>
              <span>{chapter.text.length.toLocaleString("vi-VN")} ký tự</span>
            </button>
          )) ?? <p className="empty-state">Import nguồn để tạo chapter queue.</p>}
        </div>
      </Panel>

      <Panel
        title="Project Snapshot"
        subtitle="Các chỉ số vận hành cần thấy trước khi chuyển sang workspace."
      >
        <div className="snapshot-grid">
          <InfoLine label="Segments" value={formatCount(props.overview?.counts.segments)} />
          <InfoLine label="Entities" value={formatCount(props.overview?.entities.length)} />
          <InfoLine label="Candidates" value={formatCount(props.overview?.counts.candidates_total)} />
          <InfoLine label="QA issues" value={formatCount(props.overview?.counts.qa_issues)} />
        </div>
        <div className="artifact-list">
          <InfoLine label="Output" value={props.overview?.artifacts.output_path ?? "Unavailable"} />
          <InfoLine label="Draft" value={props.overview?.artifacts.draft_path ?? "Unavailable"} />
          <InfoLine label="Trace" value={props.overview?.artifacts.trace_path ?? "Unavailable"} />
          <InfoLine label="QA report" value={props.overview?.artifacts.qa_report_path ?? "Unavailable"} />
        </div>
      </Panel>
    </div>
  );
}
