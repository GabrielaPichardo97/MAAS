#!/usr/bin/env python3
"""Aplica una puesta visual determinista y revisable a una dirección MAAS propuesta."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PUSH = "motion.push-in.emphasis.subtle.v1.0.0"
KEN_BURNS = "motion.ken-burns.exposition.documentary.v1.0.0"
RACK_FOCUS = "motion.rack-focus.attention.depth-shift.v1.0.0"
SHAKE = "motion.camera-shake.impact.decay.v1.0.0"
PUNCH = "time.punch-edit.impact.snap.v1.0.0"
VIRTUAL_DOLLY = "motion.virtual-dolly.reveal.parallax.v1.0.0"
COLOR = "stylize.color-grade.coherence.clean.v1.0.0"
LIGHT_LEAK = "stylize.light-leak.atmosphere.film.v1.0.0"
PARTICLES = "stylize.particles.atmosphere.dynamic.v1.0.0"


def effect(effect_id: str, role: str, intensity: float, target: str, params: dict | None = None) -> dict:
    return {"id": effect_id, "role": role, "intensity": intensity, "target": target, "params": params or {}}


def surreal(index: int, text: str) -> tuple[dict, list[dict]]:
    context = {
        "sceneType": "general", "arousal": min(0.82, 0.42 + index * 0.025),
        "continuity": 0.58, "focus": "face", "stylization": 0.68,
        "tempo": 112, "musicSync": False, "textNeed": False,
        "availableInputs": [], "reducedMotion": False,
    }
    if index == 0:
        return context, [
            effect(PUSH, "dominant", 0.62, "speaker", {"scaleEnd": 1.18, "easing": "ease-out"}),
            effect(COLOR, "finish", 0.38, "frame", {"contrast": 0.12, "saturation": 0.78, "tint": -0.08}),
        ]
    if "OSD" in text and any(hit in text.casefold() for hit in ("ay", "dum", "puaj")):
        return context, [effect(PUNCH, "dominant", 0.58, "frame")]
    cycle = [
        [effect(RACK_FOCUS, "dominant", 0.42, "speaker", {"blurPx": 12, "focusTo": "subject"})],
        [effect(LIGHT_LEAK, "finish", 0.38, "frame", {"intensity": 0.32, "color": "#ff8a4c"})],
        [effect(VIRTUAL_DOLLY, "dominant", 0.34, "frame", {"depth": 0.28, "travel": 0.2})],
        [effect(PARTICLES, "finish", 0.32, "frame", {"rate": 24, "lifeMs": 1200, "gravity": 0.12})],
        [effect(PUSH, "dominant", 0.48, "speaker")],
    ]
    return context, cycle[(index - 1) % len(cycle)]


def office(index: int, text: str) -> tuple[dict, list[dict]]:
    urgency = any(hit in text.casefold() for hit in ("nooo", "no lo leas", "trampa", "sistemas"))
    context = {
        "sceneType": "general" if not urgency else "suspense",
        "arousal": 0.78 if urgency else min(0.72, 0.3 + index * 0.018),
        "continuity": 0.72 if not urgency else 0.38,
        "focus": "frame" if index == 0 or urgency else "face",
        "stylization": 0.52, "tempo": 104 if not urgency else 132,
        "musicSync": False, "textNeed": False, "availableInputs": [], "reducedMotion": False,
    }
    if index == 0:
        return context, [
            effect(KEN_BURNS, "dominant", 0.52, "frame", {"endX": 0.16, "endY": 0, "scaleEnd": 1.14}),
            effect(LIGHT_LEAK, "finish", 0.34, "frame", {"intensity": 0.28, "color": "#ffd07a"}),
        ]
    if urgency:
        return context, [
            effect(SHAKE, "dominant", 0.58, "frame", {"amplitudePx": 10, "frequencyHz": 9, "decayMs": 520}),
            effect(COLOR, "finish", 0.32, "frame", {"contrast": 0.18, "saturation": 1.18, "tint": 0.08}),
        ]
    cycle = [
        [effect(PUSH, "dominant", 0.4, "speaker")],
        [effect(RACK_FOCUS, "support", 0.32, "speaker", {"blurPx": 10, "focusTo": "subject"})],
        [effect(COLOR, "finish", 0.28, "frame", {"contrast": 0.08, "saturation": 0.9, "tint": 0})],
        [effect(PUNCH, "dominant", 0.42, "frame")],
        [effect(LIGHT_LEAK, "finish", 0.3, "frame", {"intensity": 0.24, "color": "#ffb15a"})],
    ]
    return context, cycle[(index - 1) % len(cycle)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direction", type=Path)
    parser.add_argument("--preset", choices=("surreal", "office-escalation"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--context-output", type=Path)
    args = parser.parse_args()

    document = json.loads(args.direction.read_text(encoding="utf-8-sig"))
    choose = surreal if args.preset == "surreal" else office
    first_context = None
    beat_index = 0
    for scene in document.get("scenes", []):
        for beat in scene.get("beats", []):
            context, effects = choose(beat_index, beat["verbatimText"])
            beat["effectContext"] = context
            beat["effects"] = effects
            beat["direction"] = {
                "performance": "Sostener el subtexto y dejar respirar el remate",
                "blocking": beat["stageDirection"],
                "shot": "close" if context["focus"] == "face" else "medium-wide",
                "cameraMovement": "motivated" if effects else "static",
                "focus": context["focus"],
                "transition": "clean-cut",
            }
            first_context = first_context or context
            beat_index += 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    if args.context_output and first_context:
        args.context_output.write_text(json.dumps(first_context, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"beats": beat_index, "output": str(args.output), "preset": args.preset}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
