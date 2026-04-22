export const PROTOCOL_VERSION = "2026-04-16.phase10";

export type TransportMode = "browser" | "demo" | "http" | "tauri";

export type CommandName =
  | "create_project"
  | "list_projects"
  | "open_project"
  | "get_project_overview"
  | "set_active_chapter"
  | "set_translation_style"
  | "import_file"
  | "translate"
  | "load_translation_artifacts"
  | "run_qa"
  | "load_qa_report"
  | "load_learning_report"
  | "search_dictionary_entries"
  | "list_candidate_entries"
  | "review_candidate_entry"
  | "submit_natural_feedback"
  | "list_candidate_rules"
  | "review_candidate_rule";

export type CommandEvent = {
  stage: string;
  message: string;
  progress: number;
  level: string;
  payload?: Record<string, unknown>;
};

export type CommandResponse<T> = {
  ok: boolean;
  command: string;
  request_id: string;
  protocol_version: string;
  data: T;
  error: string;
  warnings: string[];
  events: CommandEvent[];
  generated_at: string;
};

export type ProjectRecord = {
  project_id: string;
  project_dir: string;
  source_language: string;
  target_language: string;
  active_chapter: string | null;
};

export type ChapterInfo = {
  chapter_id: string;
  title: string;
  text: string;
  start: number;
  end: number;
  source_path?: string;
};

export type CandidateEntry = {
  id: number;
  source_text: string;
  target_text: string;
  status: string;
  reviewer_reason: string;
  chapter_id: string;
  segment_id: string;
  fallback_level: string;
  candidates: string[];
  reason: string;
  created_at: string;
};

export type CandidateRule = {
  id: number;
  rule_type: string;
  rule_payload: Record<string, unknown>;
  status: string;
  reviewer_reason: string;
  created_at: string;
  updated_at: string;
};

export type FeedbackSuggestion = {
  rule_type: string;
  title: string;
  summary: string;
  payload: Record<string, unknown>;
  confidence: number;
  scope: string;
  chapter_id: string | null;
  origin: string;
};

export type NaturalFeedbackAnalysis = {
  feedback_text: string;
  scope: string;
  chapter_id: string | null;
  rule_type_hint: string;
  llm_used: boolean;
  warnings: string[];
  suggestions: FeedbackSuggestion[];
};

export type TranslationTrace = {
  source: string;
  selected: string;
  candidates: string[];
  priority?: number;
  fallback_level: string;
  reason: string;
};

export type TranslationSegment = {
  sentence_id: string;
  source_text: string;
  clean_text: string;
  draft_text: string;
  emotion: string | null;
  trace: TranslationTrace[];
  fallback_level?: string;
};

export type TranslationArtifacts = {
  project_id: string;
  chapter_id: string | null;
  clean_text: string;
  draft_text: string;
  segments: TranslationSegment[];
  paths: Record<string, string>;
};

export type QAIssue = {
  severity: string;
  checker: string;
  segment_id: string;
  message: string;
};

export type QAReport = {
  summary: {
    issues: number;
    segments: number;
  };
  issues: QAIssue[];
};

export type ProjectOverview = {
  project: ProjectRecord;
  state: Record<string, unknown>;
  chapters: ChapterInfo[];
  config: Record<string, unknown>;
  entities: Array<Record<string, unknown>>;
  relationships: Array<Record<string, unknown>>;
  terminology_suggestions: Array<Record<string, unknown>>;
  counts: {
    chapters: number;
    segments: number;
    candidates_total: number;
    candidate_status: Record<string, number>;
    candidate_rules_total: number;
    candidate_rule_status: Record<string, number>;
    qa_issues: number;
  };
  artifacts: Record<string, string>;
};

export type LearningReport = {
  project_id?: string;
  chapter_id?: string | null;
  generated_at?: string;
  current_run?: Record<string, unknown>;
  previous_run?: Record<string, unknown> | null;
  delta?: Record<string, unknown>;
  recommendations?: Array<Record<string, unknown>>;
  auto_applied?: Array<Record<string, unknown>>;
  learned_terms?: Record<string, unknown>;
  updated_config?: Record<string, unknown>;
  history_path?: string;
};

export type DictionaryEntry = {
  source: string;
  target_vi: string;
  alternative_meanings: string[];
  full_explanation: string;
  source_dict: string;
  priority: number;
  status: string;
  hit_count: number;
  pinyin: string[];
  han_viet_readings: string[];
  entry_role: string;
  source_language: string;
  target_language: string;
  one_mean: boolean;
  locked: boolean;
  notes: string;
};

export type Transport = {
  mode: TransportMode;
  supportedCommands: CommandName[];
  send<T>(
    command: CommandName,
    payload?: Record<string, unknown>,
  ): Promise<CommandResponse<T>>;
};
