import {
  PROTOCOL_VERSION,
  type CommandName,
  type CommandResponse,
  type Transport,
} from "./protocol";

export function createBrowserTransport(): Transport {
  return {
    mode: "browser",
    supportedCommands: [],
    async send<T>(command: CommandName): Promise<CommandResponse<T>> {
      const message =
        "Browser preview does not have access to the Python sidecar. Start the native Tauri app to work with real project data.";
      return {
        ok: false,
        command,
        request_id: `browser-${Date.now()}`,
        protocol_version: PROTOCOL_VERSION,
        data: {} as T,
        error: message,
        warnings: [],
        events: [
          {
            stage: "unavailable",
            message,
            progress: 100,
            level: "warning",
          },
        ],
        generated_at: new Date().toISOString(),
      };
    },
  };
}
