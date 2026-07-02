#!/usr/bin/env python3
"""Recalcula duraciones y startMs usando un mapa cueId->audioMs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def resolved_duration(cue: dict, audio_ms: int | None, profile: str) -> int:
    declared = int(cue.get("declaredDurationMs", cue.get("durationMs", 0)))
    if audio_ms is None:
        return int(cue.get("durationMs", declared))
    if cue.get("type") == "dialogue":
        if profile == "legacy-v1":
            return max(2000, ((audio_ms + 200) // 1000) * 1000)
        return max(declared, audio_ms + 200)
    if cue.get("type") == "sfx":
        return int(cue.get("durationMs", audio_ms)) if profile == "legacy-v1" else max(40, audio_ms)
    return int(cue.get("durationMs", audio_ms))


def rebuild(manifest: dict, durations: dict[str, int], profile: str) -> dict:
    narrative = [cue for cue in manifest["timeline"] if cue["type"] != "scene"]
    scenes = [cue for cue in manifest["timeline"] if cue["type"] == "scene"]
    cursor = 0
    cue_by_id = {}
    for cue in narrative:
        audio_ms = durations.get(cue["id"])
        if cue["type"] in {"dialogue", "sfx"}:
            cue["durationMs"] = resolved_duration(cue, audio_ms, profile)
            cue["resolvedDurationMs"] = cue["durationMs"]
            if audio_ms is not None:
                cue.setdefault("audio", {})["durationMs"] = audio_ms
        cue["startMs"] = cursor
        cursor += int(cue["durationMs"])
        cue_by_id[cue["id"]] = cue
    for scene in scenes:
        members = [cue_by_id[cue_id] for cue_id in scene.get("cueIds", []) if cue_id in cue_by_id]
        if members:
            scene["startMs"] = members[0]["startMs"]
            scene["durationMs"] = members[-1]["startMs"] + members[-1]["durationMs"] - scene["startMs"]
    manifest["profile"] = profile
    manifest["durationMs"] = cursor
    manifest["timeline"] = sorted(scenes + narrative, key=lambda cue: (cue["startMs"], cue["id"]))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("durations", type=Path, help="JSON object cueId -> duración en ms")
    parser.add_argument("--profile", choices=("legacy-v1", "canonical-v1", "canonical-v2"), default="legacy-v1")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
        durations = json.loads(args.durations.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"E_JSON_INVALID: {exc}")
        return 1
    if not isinstance(durations, dict) or any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in durations.values()):
        print("E_TIMELINE: durations debe ser objeto cueId -> entero no negativo")
        return 1
    result = rebuild(manifest, durations, args.profile)
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
