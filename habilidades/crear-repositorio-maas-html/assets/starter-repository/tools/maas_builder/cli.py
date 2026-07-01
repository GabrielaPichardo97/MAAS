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

    compile_command = sub.add_parser("compile")
    compile_command.add_argument("input", type=Path)
    compile_command.add_argument("--profile", choices=("legacy-v1", "canonical-v1"), default="legacy-v1")
    compile_command.add_argument("--output", type=Path, required=True)
    compile_command.add_argument("--character-map", type=Path)

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
    build.add_argument("--profile", choices=("legacy-v1", "canonical-v1"), default="legacy-v1")
    build.add_argument("--character-map", type=Path)

    verify = sub.add_parser("verify")
    verify.add_argument("target", type=Path)
    verify.add_argument("--publication", action="store_true")

    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    scripts = repo / "tools" / "scripts"
    if args.command == "validate":
        return run(scripts / "validate_episode.py", args.input, "--mode", args.mode, "--pretty")
    if args.command == "compile":
        command: list[object] = [args.input, "--profile", args.profile, "--output", args.output]
        if args.character_map:
            command += ["--character-map", args.character_map]
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
                valid = manifest.get("schemaVersion") == "1.0" and isinstance(manifest.get("durationMs"), int) and ordered
            except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError):
                valid = False
            print(json.dumps({"valid": valid, "target": str(args.target)}, ensure_ascii=False))
            return 0 if valid else 1
        command = [args.target]
        if args.publication:
            command.append("--publication")
        return run(scripts / "verify_bundle.py", *command)
    if args.command == "build":
        with tempfile.TemporaryDirectory(prefix="maas-build-") as temporary:
            manifest = Path(temporary) / "episode.manifest.json"
            compile_args: list[object] = [args.input, "--profile", args.profile, "--output", manifest]
            if args.character_map:
                compile_args += ["--character-map", args.character_map]
            code = run(scripts / "compile_episode.py", *compile_args)
            if code:
                return code
            return run(scripts / "build_episode.py", manifest, "--player-dist", args.player_dist, "--output", args.output)
    return 2
