# Desktop Shell

`desktop/` now contains a Phase 08 workflow shell with a validated native Tauri bridge for real work and a browser preview mode that no longer hides backend failures behind forced demo data.

Implemented in the current slice:

- A typed desktop command contract with protocol versioning, progress events, warnings, and structured errors
- Python sidecar commands for project overview, chapter selection, import, translate, QA, translation artifact loading, dictionary search, candidate listing, and candidate review
- A React/Vite shell with the seven planned screens, auto transport selection, real workspace base-dir input, and browser preview messaging that points users to native Tauri for real data
- A Tauri Rust bridge that forwards frontend requests to `python -m src.ui.sidecar_bridge` from the repository root
- Dictionary Manager metadata inspection for `target_vi`, alternative meanings, full explanations, pinyin, Han-Viet readings, source dictionary, priority, status, and hit count
- Generated bundle icons under `src-tauri/icons/`, sourced from `src-tauri/app-icon.svg`, so native Windows packaging has the required resource assets

Notes:

- Browser mode is for layout inspection only unless `VITE_ENABLE_DEMO=1` is supplied explicitly.
- Native Tauri mode is the supported path for importing real files, selecting active chapters, translating, and running QA.

Available scripts:

- `npm run build`
- `npm run tauri:dev`
- `npm run tauri:build`

Verification completed in this environment:

- `python -m pytest` -> `99 passed`
- `npm run build` -> web shell build succeeds
- `npm exec tauri info` -> native prerequisites are detected successfully
- `npm run tauri:build` -> native release build succeeds and produces `src-tauri/target/release/drduc-translator-desktop.exe`
- Native smoke test -> the release executable launches successfully on Windows

Windows toolchain layout used on this machine:

- Rust toolchain: `D:\App\Rust`
- Visual Studio Build Tools 2022: `D:\App\BuildTools\VS2022`
- Windows SDK: `C:\Program Files (x86)\Windows Kits\10`
