export function normalizeUserPath(value: string): string {
  const trimmed = value.trim();
  const unquoted = trimmed.replace(/^"(.*)"$/, "$1");
  return unquoted.replace(/\//g, "\\");
}

export function isAbsolutePath(value: string): boolean {
  return /^[a-zA-Z]:[\\/]/.test(value) || /^\\\\/.test(value) || value.startsWith("/");
}

export function getParentPath(value: string): string {
  const normalized = normalizeUserPath(value);
  const lastSlash = Math.max(normalized.lastIndexOf("\\"), normalized.lastIndexOf("/"));
  if (lastSlash <= 0) {
    return normalized;
  }
  return normalized.slice(0, lastSlash);
}

export function downloadJson(filename: string, payload: unknown) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
