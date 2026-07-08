#!/usr/bin/env python3
"""Verifica estructura, secretos y políticas básicas de un bundle MAAS."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SECRET_PATTERNS = {
    "OPENAI_API_KEY": re.compile(r"OPENAI_API_KEY|sk-[A-Za-z0-9_-]{20,}"),
    "ELEVENLABS": re.compile(r"ELEVEN(?:LABS)?[_-]?(?:API)?[_-]?KEY", re.IGNORECASE),
    "PRIVATE_KEY": re.compile(r"BEGIN (?:RSA |EC )?PRIVATE KEY"),
    "BEARER": re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}", re.IGNORECASE),
}

HTML_INJECTION_PATTERN = re.compile(r"\b(?:innerHTML|dangerouslySetInnerHTML)\b")
VIDEO_SUFFIXES = {".mp4", ".mov", ".webm", ".m4v"}
HTML_REMOTE_ATTR_PATTERN = re.compile(
    r"\b(?:src|href|poster|action|formaction)\s*=\s*([\"'])(https?://[^\"']+)\1",
    re.IGNORECASE,
)
CSS_REMOTE_URL_PATTERN = re.compile(r"url\(\s*([\"']?)(https?://[^)\"']+)\1\s*\)", re.IGNORECASE)
JS_REMOTE_RUNTIME_PATTERN = re.compile(
    r"\b(?:fetch|importScripts|EventSource|WebSocket|Worker|SharedWorker)\s*\(\s*([\"'])(?:https?|wss?)://[^\"']+\1"
    r"|\.open\(\s*([\"'])(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\2\s*,\s*([\"'])(?:https?|wss?)://[^\"']+\3",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def application_source_injections(path: Path, text: str) -> list[str]:
    """Devuelve fuentes propias que usan APIs HTML inseguras.

    React y Pixi contienen implementaciones internas de `innerHTML`; los source
    maps permiten revisar el código de la aplicación sin confundirlo con esas
    dependencias. Los HTML finales se inspeccionan directamente.
    """
    if path.suffix.casefold() == ".html":
        return [path.name] if HTML_INJECTION_PATTERN.search(text) else []
    if path.suffix.casefold() != ".map":
        return []
    try:
        source_map = json.loads(text)
    except json.JSONDecodeError:
        return []
    findings = []
    for source, content in zip(source_map.get("sources", []), source_map.get("sourcesContent", [])):
        normalized = str(source).replace("\\", "/")
        if "/node_modules/" in normalized or "/src/" not in normalized or not isinstance(content, str):
            continue
        if HTML_INJECTION_PATTERN.search(content):
            findings.append(normalized)
    return findings


def remote_runtime_urls(path: Path, text: str) -> list[str]:
    """Return remote URLs that would be loaded or called at runtime.

    Bundled JS and source maps can contain documentation URLs, error messages,
    or SVG namespace strings. The publication gate should fail actual remote
    runtime surfaces, not static metadata embedded in local files.
    """
    suffix = path.suffix.casefold()
    if suffix == ".map":
        return []
    if suffix == ".html":
        return [match.group(2) for match in HTML_REMOTE_ATTR_PATTERN.finditer(text)] + [
            match.group(0) for match in JS_REMOTE_RUNTIME_PATTERN.finditer(text)
        ]
    if suffix == ".css":
        return [match.group(2) for match in CSS_REMOTE_URL_PATTERN.finditer(text)]
    if suffix == ".js":
        return [match.group(0) for match in JS_REMOTE_RUNTIME_PATTERN.finditer(text)]
    if suffix == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return []
        urls: list[str] = []

        def walk(value: object) -> None:
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                urls.append(value)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
            elif isinstance(value, dict):
                for item in value.values():
                    walk(item)

        walk(payload)
        return urls
    return []


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
        for source in application_source_injections(path, text):
            diagnostics.append({"code": "E_HTML_INJECTION", "severity": "error", "path": path.relative_to(root).as_posix(), "source": source, "message": "API HTML insegura en código de aplicación"})
        if args.publication:
            urls = remote_runtime_urls(path, text)
            if urls:
                diagnostics.append({"code": "E_REMOTE_RUNTIME", "severity": "error", "path": path.relative_to(root).as_posix(), "message": "URL remota en bundle", "urls": sorted(set(urls))[:5]})
    declared_asset_paths: set[str] = set()
    for manifest_path in manifests:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("durationMs", -1) < 0 or not isinstance(manifest.get("timeline"), list):
                raise ValueError("timeline/duration inválidos")
            requested = set(manifest.get("assets", []))
            asset_urls = manifest.get("assetUrls", {})
            if requested != set(asset_urls):
                diagnostics.append({"code": "E_ASSET", "severity": "error", "path": manifest_path.relative_to(root).as_posix(), "message": "assets y assetUrls no coinciden"})
            for asset_id in sorted(requested):
                url = str(asset_urls.get(asset_id, ""))
                relative = url.removeprefix("/")
                target = (root / relative).resolve()
                if not url.startswith("/assets/") or root not in target.parents or not target.is_file():
                    diagnostics.append({"code": "E_ASSET", "severity": "error", "path": relative, "message": f"Asset ausente o inseguro: {asset_id}"})
                    continue
                declared_asset_paths.add(relative.replace("\\", "/"))
                expected = Path(relative).stem
                if len(expected) == 64 and sha256(target) != expected:
                    diagnostics.append({"code": "E_ASSET", "severity": "error", "path": relative, "message": f"Hash distinto: {asset_id}"})
            subtitles = manifest.get("subtitles", [])
            if not isinstance(subtitles, list):
                diagnostics.append({"code": "E_SUBTITLE", "severity": "error", "path": manifest_path.relative_to(root).as_posix(), "message": "subtitles debe ser array"})
            for track in manifest.get("subtitleTracks", []):
                if not isinstance(track, dict) or track.get("format") != "webvtt":
                    diagnostics.append({"code": "E_SUBTITLE", "severity": "error", "path": manifest_path.relative_to(root).as_posix(), "message": "Track de subtitulos invalido"})
                    continue
                url = str(track.get("url", ""))
                relative = url.removeprefix("/")
                target = (root / relative).resolve()
                if not url.startswith(f"/episodes/{manifest.get('episodeId')}/") or ".." in url or "://" in url or root not in target.parents or not target.is_file():
                    diagnostics.append({"code": "E_SUBTITLE", "severity": "error", "path": relative, "message": "WebVTT ausente o inseguro"})
                    continue
                expected_hash = track.get("sha256")
                if expected_hash and sha256(target) != expected_hash:
                    diagnostics.append({"code": "E_SUBTITLE", "severity": "error", "path": relative, "message": "Hash WebVTT distinto"})
            generation = manifest.get("generation", {})
            if args.publication and (not isinstance(generation, dict) or generation.get("aiRuntime") != "forbidden-during-build" or generation.get("htmlFirst") is not True):
                diagnostics.append({"code": "E_GENERATION", "severity": "error", "path": manifest_path.relative_to(root).as_posix(), "message": "Contrato HTML-first/generacion ausente"})
            report = manifest_path.with_name("build-report.json")
            if not report.is_file():
                diagnostics.append({"code": "E_ASSET", "severity": "error", "path": report.relative_to(root).as_posix(), "message": "Falta build-report"})
        except (json.JSONDecodeError, ValueError) as exc:
            diagnostics.append({"code": "E_SCHEMA", "severity": "error", "path": manifest_path.relative_to(root).as_posix(), "message": str(exc)})
    if args.publication:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.casefold() in VIDEO_SUFFIXES:
                relative = path.relative_to(root).as_posix()
                if relative not in declared_asset_paths:
                    diagnostics.append({"code": "E_HTML_FIRST_VIDEO", "severity": "error", "path": relative, "message": "Video no declarado como asset autorizado"})
    result = {"valid": not any(d["severity"] == "error" for d in diagnostics), "episodes": len(manifests), "diagnostics": diagnostics}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
