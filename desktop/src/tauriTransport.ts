import { invoke, isTauri } from "@tauri-apps/api/core";
import {
  PROTOCOL_VERSION,
  type CommandName,
  type CommandResponse,
  type Transport,
} from "./protocol";

const SUPPORTED_COMMANDS: CommandName[] = [
  "create_project",
  "list_projects",
  "open_project",
  "get_project_overview",
  "set_active_chapter",
  "set_translation_style",
  "import_file",
  "translate",
  "load_translation_artifacts",
  "run_qa",
  "load_qa_report",
  "load_learning_report",
  "update_project_translation_config",
  "upsert_project_entity",
  "delete_project_entity",
  "delete_project_entities",
  "suggest_entity_targets",
  "search_dictionary_entries",
  "list_dictionary_entries",
  "update_dictionary_entry",
  "get_pipeline_status",
  "run_pipeline_stage",
  "list_candidate_entries",
  "review_candidate_entry",
  "submit_natural_feedback",
  "scan_grammar_learning_patterns",
  "list_candidate_rules",
  "review_candidate_rule",
];

export async function createTauriTransport(): Promise<Transport> {
  if (!isTauri()) {
    throw new Error("Tauri runtime is not available in this webview.");
  }

  return {
    mode: "tauri",
    supportedCommands: SUPPORTED_COMMANDS,
    async send<T>(
      command: CommandName,
      payload: Record<string, unknown> = {},
    ): Promise<CommandResponse<T>> {
      const requestJson = JSON.stringify({
        command,
        payload,
        request_id: `tauri-${Date.now()}`,
        protocol_version: PROTOCOL_VERSION,
      });
      const rawResponse = await invoke<string>("sidecar_request", { requestJson });
      return JSON.parse(rawResponse) as CommandResponse<T>;
    },
  };
}
