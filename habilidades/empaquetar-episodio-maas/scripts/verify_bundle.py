#!/usr/bin/env python3
"""Verifica estructura, secretos y políticas básicas de un bundle MAAS."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SECRET_PATTERNS = {
    "OPENAI_API_KEY": re.compile(r"OPENAI_API_KEY|sk-[A-Za-z0-9_-]{20,}"),
    "ELEVENLABS": re.compile(r"ELEVEN(?:LABS)?[_-]?(?:API)?[_-]?KEY", re.IGNORECASE),
    "PRIVATE_KEY": re.compile(r"BEGIN (?:RSA |EC )?PRIVATE KEY"),
    "BEARER": re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}", re.IGNORECASE),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--publication", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    diagnostics = []
    if not (root / "index.html").is_file():
        diagnostics.append({"code": "E_ASSET", "severity": "error", "message": "Falta index.html raíz"})
    manifests = sorted(root.glob("episodes/*/episode.manifest.json"))
    if not manifests:
        diagnostics.append({"code": "E_ASSET", "severity": "error", "message": "No hay episodios"})
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in {".html", ".js", ".json", ".css", ".map"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                diagnostics.append({"code": "E_SECRET", "severity": "error", "path": path.relative_to(root).as_posix(), "message": name})
        if re.search(r"\b(?:innerHTML|dangerouslySetInnerHTML)\b", text):
            diagnostics.append({"code": "E_HTML_INJECTION", "severity": "error", "path": path.relative_to(root).as_posix(), "message": "API HTML insegura"})
        if args.publication and re.search(r"https?://", text) and "json-schema.org" not in text:
            diagnostics.append({"code": "E_REMOTE_RUNTIME", "severity": "error", "path": path.relative_to(root).as_posix(), "message": "URL remota en bundle"})
    for manifest_path in manifests:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("durationMs", -1) < 0 or not isinstance(manifest.get("timeline"), list):
                raise ValueError("timeline/duration inválidos")
            report = manifest_path.with_name("build-report.json")
            if not report.is_file():
                diagnostics.append({"code": "E_ASSET", "severity": "error", "path": report.relative_to(root).as_posix(), "message": "Falta build-report"})
        except (json.JSONDecodeError, ValueError) as exc:
            diagnostics.append({"code": "E_SCHEMA", "severity": "error", "path": manifest_path.relative_to(root).as_posix(), "message": str(exc)})
    result = {"valid": not any(d["severity"] == "error" for d in diagnostics), "episodes": len(manifests), "diagnostics": diagnostics}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
