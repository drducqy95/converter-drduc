import {
    PROTOCOL_VERSION,
    type CommandName,
    type CommandResponse,
    type Transport,
} from "./protocol";

const DEFAULT_BRIDGE_URL = "http://localhost:9721";

const SUPPORTED_COMMANDS: CommandName[] = [
    "create_project", "list_projects", "open_project",
    "get_project_overview", "set_active_chapter", "set_translation_style",
    "import_file", "translate", "load_translation_artifacts",
    "run_qa", "load_qa_report", "load_learning_report",
    "update_project_translation_config", "upsert_project_entity", "delete_project_entity", "delete_project_entities", "suggest_entity_targets",
    "search_dictionary_entries", "list_dictionary_entries",
    "update_dictionary_entry", "get_pipeline_status", "run_pipeline_stage",
    "list_candidate_entries",
    "review_candidate_entry", "submit_natural_feedback",
    "scan_grammar_learning_patterns", "list_candidate_rules", "review_candidate_rule",
];

export async function createHttpTransport(): Promise<Transport> {
    const baseUrl = import.meta.env.VITE_BRIDGE_URL || DEFAULT_BRIDGE_URL;
    // Probe health endpoint
    const health = await fetch(`${baseUrl}/api/health`, { signal: AbortSignal.timeout(2000) });
    if (!health.ok) throw new Error("HTTP bridge health check failed");

    return {
        mode: "http",
        supportedCommands: SUPPORTED_COMMANDS,
        async send<T>(command: CommandName, payload: Record<string, unknown> = {}): Promise<CommandResponse<T>> {
            const requestJson = JSON.stringify({
                command, payload,
                request_id: `http-${Date.now()}`,
                protocol_version: PROTOCOL_VERSION,
            });
            const response = await fetch(`${baseUrl}/api/sidecar`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: requestJson,
            });
            return await response.json() as CommandResponse<T>;
        },
    };
}
