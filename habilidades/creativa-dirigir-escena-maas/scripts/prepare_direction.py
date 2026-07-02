#!/usr/bin/env python3
"""Crea un plan cinematográfico propuesto sin alterar la adaptación."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("adaptation", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.adaptation.read_bytes()
    adaptation = json.loads(raw.decode("utf-8-sig"))
    scenes = []
    for scene_index, scene in enumerate(adaptation.get("scenes", [])):
        beats = []
        for beat in scene.get("beats", []):
            beats.append({
                "id": beat["id"],
                "speaker": beat["speaker"],
                "characterId": beat["characterId"],
                "verbatimText": beat["verbatimText"],
                "emotion": beat["emotion"]["value"],
                "stageDirection": beat["stageDirection"]["value"],
                "durationMs": beat["durationMs"]["value"],
                "direction": {
                    "performance": "Mantener la intención del parlamento",
                    "blocking": beat["stageDirection"]["value"],
                    "shot": "medium",
                    "cameraMovement": "static",
                    "focus": "speaker",
                    "transition": "clean-cut",
                },
                "effectContext": {
                    "sceneType": "general", "arousal": 0.3, "continuity": 0.8,
                    "focus": "face", "stylization": 0.2, "tempo": 90,
                    "musicSync": False, "textNeed": False, "availableInputs": [],
                    "reducedMotion": False,
                },
                "effects": [],
            })
        scenes.append({
            "id": scene["id"], "placeId": scene.get("placeId"), "placeLabel": scene.get("placeLabel"),
            "orientation": "landscape", "beats": beats,
        })
    direction = {
        "schemaVersion": "1.0",
        "adaptationSha256": hashlib.sha256(raw).hexdigest(),
        "metadata": adaptation["metadata"],
        "approval": {"status": "proposed", "approvedBy": None, "approvedAt": None},
        "scenes": scenes,
        "unresolvedMedia": [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(direction, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"beats": sum(len(scene["beats"]) for scene in scenes), "output": str(args.output), "status": "proposed"}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
