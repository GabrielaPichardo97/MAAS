#!/usr/bin/env python3
"""Construye el Episodio 0 con personajes y fondos reales del catálogo MAAS."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


EPISODE_ID = "episodio-0-prueba-renderizar"


def run(*command: object) -> None:
    result = subprocess.run([str(value) for value in command], check=False)
    if result.returncode:
        raise RuntimeError(f"Falló el comando con exit code {result.returncode}: {' '.join(map(str, command))}")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    legacy_media = root.parent / "media"
    content = root / "content" / "episodes" / EPISODE_ID
    scripts = root / "tools" / "scripts"
    reports = root / "reports"
    catalog = root / "media-library" / "media-catalog.json"
    output = root / "public" / "episodes" / EPISODE_ID / "episode.manifest.json"
    try:
        run(sys.executable, scripts / "build_asset_manifest.py", legacy_media, "--output", reports / "asset-manifest.json")
        run(sys.executable, scripts / "media_pipeline.py", "catalog", reports / "asset-manifest.json", "--root", legacy_media, "--output", catalog)
        run(sys.executable, scripts / "media_pipeline.py", "validate", catalog, "--root", legacy_media)
        run(
            sys.executable, scripts / "media_pipeline.py", "report-gaps", catalog,
            "--output-json", reports / "media-gaps.json",
            "--output-md", reports / "media-gaps.md",
            "--requests-dir", reports / "media-requests",
        )
        run(sys.executable, scripts / "validate_episode.py", content / "episode-source.json", "--mode", "strict")
        with tempfile.TemporaryDirectory(prefix="maas-preview-") as temporary:
            temporary_root = Path(temporary)
            compiled = temporary_root / "compiled.json"
            synchronized = temporary_root / "synchronized.json"
            run(
                sys.executable, scripts / "compile_episode.py", content / "episode-source.json",
                "--profile", "legacy-v1", "--character-map", content / "character-map.json", "--output", compiled,
            )
            run(
                sys.executable, scripts / "build_audio_cues.py", compiled, content / "audio-durations.json",
                "--profile", "legacy-v1", "--output", synchronized,
            )
            run(
                sys.executable, scripts / "media_pipeline.py", "resolve", synchronized, catalog,
                content / "presentation.json", root / "media-library" / "emotion-policy.json",
                "--mode", "preview", "--output", output,
                "--episode-gaps", reports / "episode-0-media-gaps.json",
            )
        run(
            sys.executable, scripts / "media_pipeline.py", "stage", catalog, output,
            "--root", legacy_media, "--output", root / "public" / "assets",
        )
        manifest = json.loads(output.read_text(encoding="utf-8"))
        summary = {
            "assets": len(manifest["assets"]),
            "durationMs": manifest["durationMs"],
            "episodeId": manifest["episodeId"],
            "output": str(output),
            "timelineCues": len(manifest["timeline"]),
            "warnings": len(manifest["warnings"]),
        }
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
