import { createBrowserTransport } from "./browserTransport";
import type { Transport } from "./protocol";
import { createDemoTransport } from "./demoBackend";
import { createTauriTransport } from "./tauriTransport";
import { createHttpTransport } from "./httpTransport";

export async function createPreferredTransport(): Promise<Transport> {
  try {
    return await createTauriTransport();
  } catch {
    try {
      return await createHttpTransport();
    } catch {
      // HTTP bridge not running
    }
    if (import.meta.env.VITE_ENABLE_DEMO === "1") {
      return createDemoTransport();
    }
    return createBrowserTransport();
  }
}
