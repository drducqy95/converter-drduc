#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::Serialize;
use std::env;
use std::path::{Path, PathBuf};
use std::process::Command;

const PROTOCOL_VERSION: &str = "2026-04-16.phase10";

#[derive(Clone)]
struct PythonInvocation {
    program: String,
    pre_args: Vec<String>,
}

#[derive(Serialize)]
struct DesktopRuntimeInfo {
    repo_root: String,
    protocol_version: String,
    python_candidates: Vec<String>,
}

#[tauri::command]
async fn sidecar_request(request_json: String) -> Result<String, String> {
    tauri::async_runtime::spawn_blocking(move || execute_sidecar_request(&request_json))
        .await
        .map_err(|error| error.to_string())?
}

#[tauri::command]
fn desktop_runtime_info() -> Result<DesktopRuntimeInfo, String> {
    let repo_root = resolve_repo_root()?;
    let python_candidates = python_candidates()
        .into_iter()
        .map(|candidate| {
            if candidate.pre_args.is_empty() {
                candidate.program
            } else {
                format!("{} {}", candidate.program, candidate.pre_args.join(" "))
            }
        })
        .collect();

    Ok(DesktopRuntimeInfo {
        repo_root: repo_root.display().to_string(),
        protocol_version: PROTOCOL_VERSION.to_string(),
        python_candidates,
    })
}

#[tauri::command]
fn pick_import_path(kind: String) -> Result<Option<String>, String> {
    let selected = match kind.as_str() {
        "file" => {
            let dialog = rfd::FileDialog::new().add_filter(
                "Supported source files",
                &["txt", "md", "markdown", "html", "htm", "docx", "pdf"],
            );
            dialog.pick_file()
        }
        "folder" => {
            let dialog = rfd::FileDialog::new();
            dialog.pick_folder()
        }
        _ => return Err(format!("Unsupported picker kind: {kind}")),
    };
    Ok(selected.map(|path| path.display().to_string()))
}

fn execute_sidecar_request(request_json: &str) -> Result<String, String> {
    let repo_root = resolve_repo_root()?;
    let mut errors: Vec<String> = Vec::new();

    for candidate in python_candidates() {
        match run_sidecar(&repo_root, &candidate, request_json) {
            Ok(output) => return Ok(output),
            Err(error) => errors.push(error),
        }
    }

    Err(format!(
        "Unable to start Python sidecar. Checked {}. Errors: {}",
        repo_root.display(),
        errors.join(" | ")
    ))
}

fn run_sidecar(
    repo_root: &Path,
    candidate: &PythonInvocation,
    request_json: &str,
) -> Result<String, String> {
    let mut command = Command::new(&candidate.program);
    command.args(&candidate.pre_args);
    command.args([
        "-m",
        "src.ui.sidecar_bridge",
        "--request-json",
        request_json,
    ]);
    command.current_dir(repo_root);
    command.env("PYTHONUTF8", "1");
    command.env("PYTHONIOENCODING", "utf-8");

    let output = command.output().map_err(|error| {
        format!(
            "{} failed to launch: {}",
            render_candidate(candidate),
            error
        )
    })?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
        return Err(format!(
            "{} exited with code {:?}: {}",
            render_candidate(candidate),
            output.status.code(),
            stderr
        ));
    }

    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    if stdout.is_empty() {
        return Err(format!(
            "{} returned empty stdout from sidecar bridge",
            render_candidate(candidate)
        ));
    }
    Ok(stdout)
}

fn resolve_repo_root() -> Result<PathBuf, String> {
    if let Ok(value) = env::var("DRDUC_TRANSLATOR_REPO_ROOT") {
        let path = PathBuf::from(value);
        if path.exists() {
            return Ok(path);
        }
    }

    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    manifest_dir
        .parent()
        .and_then(|path| path.parent())
        .map(Path::to_path_buf)
        .ok_or_else(|| "Unable to resolve repository root from CARGO_MANIFEST_DIR".to_string())
}

fn python_candidates() -> Vec<PythonInvocation> {
    if let Ok(program) = env::var("DRDUC_TRANSLATOR_PYTHON") {
        if !program.trim().is_empty() {
            return vec![PythonInvocation {
                program,
                pre_args: Vec::new(),
            }];
        }
    }

    if cfg!(target_os = "windows") {
        vec![
            PythonInvocation {
                program: "python".to_string(),
                pre_args: Vec::new(),
            },
            PythonInvocation {
                program: "py".to_string(),
                pre_args: vec!["-3".to_string()],
            },
        ]
    } else {
        vec![
            PythonInvocation {
                program: "python3".to_string(),
                pre_args: Vec::new(),
            },
            PythonInvocation {
                program: "python".to_string(),
                pre_args: Vec::new(),
            },
        ]
    }
}

fn render_candidate(candidate: &PythonInvocation) -> String {
    if candidate.pre_args.is_empty() {
        candidate.program.clone()
    } else {
        format!("{} {}", candidate.program, candidate.pre_args.join(" "))
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            sidecar_request,
            desktop_runtime_info,
            pick_import_path
        ])
        .run(tauri::generate_context!())
        .expect("error while running DrDuc Translator desktop");
}
