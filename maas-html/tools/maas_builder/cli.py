from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run(script: Path, *args: object) -> int:
    return subprocess.call([sys.executable, str(script), *(str(value) for value in args)])


def main() -> int:
    parser = argparse.ArgumentParser(prog="maas")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate")
    validate.add_argument("input", type=Path)
    validate.add_argument("--mode", choices=("strict", "legacy"), default="strict")
    validate.add_argument("--profile", choices=("legacy-v1", "canonical-v1", "canonical-v2"), default="canonical-v1")

    compile_command = sub.add_parser("compile")
    compile_command.add_argument("input", type=Path)
    compile_command.add_argument("--profile", choices=("legacy-v1", "canonical-v1", "canonical-v2"), default="legacy-v1")
    compile_command.add_argument("--output", type=Path, required=True)
    compile_command.add_argument("--character-map", type=Path)
    compile_command.add_argument("--effect-catalog", type=Path)

    assets = sub.add_parser("assets")
    assets_sub = assets.add_subparsers(dest="assets_command", required=True)
    scan = assets_sub.add_parser("scan")
    scan.add_argument("root", type=Path)
    scan.add_argument("--output", type=Path, required=True)
    scan.add_argument("--overrides", type=Path)

    build = sub.add_parser("build")
    build.add_argument("input", type=Path)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--player-dist", type=Path, default=Path("web-dist"))
    build.add_argument("--profile", choices=("legacy-v1", "canonical-v1", "canonical-v2"), default="legacy-v1")
    build.add_argument("--character-map", type=Path)
    build.add_argument("--effect-catalog", type=Path)

    verify = sub.add_parser("verify")
    verify.add_argument("target", type=Path)
    verify.add_argument("--publication", action="store_true")

    media = sub.add_parser("media")
    media_sub = media.add_subparsers(dest="media_command", required=True)
    media_catalog = media_sub.add_parser("catalog")
    media_catalog.add_argument("raw_manifest", type=Path)
    media_catalog.add_argument("--root", type=Path, required=True)
    media_catalog.add_argument("--output", type=Path, required=True)
    media_validate = media_sub.add_parser("validate")
    media_validate.add_argument("catalog", type=Path)
    media_validate.add_argument("--root", type=Path, required=True)
    media_gaps = media_sub.add_parser("report-gaps")
    media_gaps.add_argument("catalog", type=Path)
    media_gaps.add_argument("--output-json", type=Path, required=True)
    media_gaps.add_argument("--output-md", type=Path, required=True)
    media_gaps.add_argument("--requests-dir", type=Path, required=True)
    media_resolve = media_sub.add_parser("resolve")
    media_resolve.add_argument("manifest", type=Path)
    media_resolve.add_argument("catalog", type=Path)
    media_resolve.add_argument("presentation", type=Path)
    media_resolve.add_argument("emotions", type=Path)
    media_resolve.add_argument("--mode", choices=("preview", "publication"), default="preview")
    media_resolve.add_argument("--output", type=Path, required=True)
    media_resolve.add_argument("--episode-gaps", type=Path, required=True)
    media_stage = media_sub.add_parser("stage")
    media_stage.add_argument("catalog", type=Path)
    media_stage.add_argument("manifest", type=Path)
    media_stage.add_argument("--root", type=Path, required=True)
    media_stage.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    scripts = repo / "tools" / "scripts"
    if args.command == "validate":
        return run(scripts / "validate_episode.py", args.input, "--mode", args.mode, "--profile", args.profile, "--pretty")
    if args.command == "compile":
        command: list[object] = [args.input, "--profile", args.profile, "--output", args.output]
        if args.character_map:
            command += ["--character-map", args.character_map]
        if args.effect_catalog:
            command += ["--effect-catalog", args.effect_catalog]
        return run(scripts / "compile_episode.py", *command)
    if args.command == "assets":
        command = [args.root, "--output", args.output]
        if args.overrides:
            command += ["--overrides", args.overrides]
        return run(scripts / "build_asset_manifest.py", *command)
    if args.command == "verify":
        if args.target.is_file():
            try:
                manifest = json.loads(args.target.read_text(encoding="utf-8-sig"))
                timeline = manifest["timeline"]
                ordered = timeline == sorted(timeline, key=lambda cue: (cue["startMs"], cue["id"]))
                version = manifest.get("schemaVersion")
                profile = manifest.get("profile")
                valid = version in {"1.0", "2.0"} and (version != "2.0" or profile == "canonical-v2") and isinstance(manifest.get("durationMs"), int) and ordered
            except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError):
                valid = False
            print(json.dumps({"valid": valid, "target": str(args.target)}, ensure_ascii=False))
            return 0 if valid else 1
        command = [args.target]
        if args.publication:
            command.append("--publication")
        return run(scripts / "verify_bundle.py", *command)
    if args.command == "media":
        if args.media_command == "catalog":
            return run(scripts / "media_pipeline.py", "catalog", args.raw_manifest, "--root", args.root, "--output", args.output)
        if args.media_command == "validate":
            return run(scripts / "media_pipeline.py", "validate", args.catalog, "--root", args.root)
        if args.media_command == "report-gaps":
            return run(scripts / "media_pipeline.py", "report-gaps", args.catalog, "--output-json", args.output_json, "--output-md", args.output_md, "--requests-dir", args.requests_dir)
        if args.media_command == "resolve":
            return run(scripts / "media_pipeline.py", "resolve", args.manifest, args.catalog, args.presentation, args.emotions, "--mode", args.mode, "--output", args.output, "--episode-gaps", args.episode_gaps)
        if args.media_command == "stage":
            return run(scripts / "media_pipeline.py", "stage", args.catalog, args.manifest, "--root", args.root, "--output", args.output)
    if args.command == "build":
        with tempfile.TemporaryDirectory(prefix="maas-build-") as temporary:
            manifest = Path(temporary) / "episode.manifest.json"
            compile_args: list[object] = [args.input, "--profile", args.profile, "--output", manifest]
            if args.character_map:
                compile_args += ["--character-map", args.character_map]
            if args.effect_catalog:
                compile_args += ["--effect-catalog", args.effect_catalog]
            code = run(scripts / "compile_episode.py", *compile_args)
            if code:
                return code
            return run(scripts / "build_episode.py", manifest, "--player-dist", args.player_dist, "--output", args.output)
    return 2
