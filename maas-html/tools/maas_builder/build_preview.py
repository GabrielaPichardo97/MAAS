#!/usr/bin/env python3
"""Construye todos los episodios MAAS disponibles con media real verificada."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run(*command: object) -> None:
    result = subprocess.run([str(value) for value in command], check=False)
    if result.returncode:
        raise RuntimeError(f"Falló el comando con exit code {result.returncode}: {' '.join(map(str, command))}")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    legacy_media = root.parent / "media"
    scripts = root / "tools" / "scripts"
    reports = root / "reports"
    catalog = root / "media-library" / "media-catalog.json"
    effect_catalog = root.parent / "habilidades" / "seleccionar-efectos-maas" / "references" / "effects-catalog.json"
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
        summaries = []
        episode_dirs = sorted(path for path in (root / "content" / "episodes").iterdir() if (path / "episode-source.json").is_file())
        with tempfile.TemporaryDirectory(prefix="maas-preview-") as temporary:
            temporary_root = Path(temporary)
            for content in episode_dirs:
                episode_id = content.name
                source = content / "episode-source.json"
                source_text = source.read_text(encoding="utf-8-sig")
                profile = "canonical-v2" if "{{fx " in source_text else "legacy-v1"
                output = root / "public" / "episodes" / episode_id / "episode.manifest.json"
                episode_reports = reports / "episodes" / episode_id
                compiled = temporary_root / f"{episode_id}.compiled.json"
                synchronized = temporary_root / f"{episode_id}.synchronized.json"
                validate = [sys.executable, scripts / "validate_episode.py", source, "--mode", "strict"]
                compile_command = [
                    sys.executable, scripts / "compile_episode.py", source,
                    "--profile", profile, "--character-map", content / "character-map.json",
                ]
                if profile == "canonical-v2":
                    validate.extend(["--profile", profile])
                    compile_command.extend(["--effect-catalog", effect_catalog])
                compile_command.extend(["--output", compiled])
                run(*validate)
                run(*compile_command)
                resolved_input = compiled
                if profile == "legacy-v1":
                    run(
                        sys.executable, scripts / "build_audio_cues.py", compiled, content / "audio-durations.json",
                        "--profile", profile, "--output", synchronized,
                    )
                    resolved_input = synchronized
                run(
                    sys.executable, scripts / "media_pipeline.py", "resolve", resolved_input, catalog,
                    content / "presentation.json", root / "media-library" / "emotion-policy.json",
                    "--mode", "publication" if profile == "canonical-v2" else "preview", "--output", output,
                    "--episode-gaps", episode_reports / "episode-gaps.json",
                )
                run(
                    sys.executable, scripts / "media_pipeline.py", "stage", catalog, output,
                    "--root", legacy_media, "--output", root / "public" / "assets",
                )
                manifest = json.loads(output.read_text(encoding="utf-8"))
                summaries.append({
                    "assets": len(manifest["assets"]), "durationMs": manifest["durationMs"],
                    "episodeId": manifest["episodeId"], "output": str(output),
                    "profile": profile, "timelineCues": len(manifest["timeline"]),
                    "warnings": len(manifest["warnings"]),
                })
        print(json.dumps({"episodes": summaries}, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
