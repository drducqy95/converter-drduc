# DrDuc Translator - Desktop Development Guide

This directory contains the Vite frontend and Tauri native bridge. There are three ways to run the project during development:

## 1. Native Tauri App (Preferred)
Runs the full native desktop shell exactly as users will see it.
```bash
npm run tauri:dev
```
- Connects directly to the Python sidecar via Tauri native transport.
- Fast, full access to local file system pickers.

## 2. HTTP Bridge + Browser (Browser Mode)
Runs the same Python translation pipeline, but exposed over HTTP so you can use standard browser dev tools (Chrome/Edge).
```bash
npm run dev:bridge
```
- Starts the `http_bridge.py` backend on port `9721`.
- Starts the `vite` dev server concurrently.
- Navigate to `http://localhost:5173`.
- **Note:** Native file pickers are polyfilled or unavailable in this mode.

### Managing the Bridge Manually
If you want to run them separately:
1. `npm run bridge` (starts Python bridge)
2. `npm run dev` (starts Vite)

## 3. Demo Mode (No Python dependency)
Runs pure frontend with mocked demo data.
```bash
npm run dev:demo
```
*(Requires setting `VITE_ENABLE_DEMO=1` in your environment or scripts)*

## Troubleshooting

- **Address in use (Port 9721)**: If `npm run dev:bridge` fails because the bridge port is taken, a previous Python process might still be running.
  - Windows: `Stop-Process -Name python` (WARNING: kills all Python processes)
- **CORS Errors**: The bridge backend is hardcoded to allow `*`. Ensure you are hitting `localhost:9721`.
- **Missing Python deps**: Ensure you have installed the root project dependencies from the main `requirements.txt`.
