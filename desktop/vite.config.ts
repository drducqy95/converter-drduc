import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const devHost = process.env.TAURI_DEV_HOST;

export default defineConfig({
  base: "./",
  clearScreen: false,
  plugins: [react()],
  server: {
    host: devHost || false,
    port: 5173,
    strictPort: true,
    hmr: devHost
      ? {
          protocol: "ws",
          host: devHost,
          port: 5173,
        }
      : undefined,
  },
});
