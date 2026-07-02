#!/usr/bin/env python3
"""Rank MAAS effects from a normalized editorial context."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "references" / "effects-catalog.json"


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def fit(value: float, bounds: list[float]) -> float:
    low, high = bounds
    if low <= value <= high:
        return 1.0
    return clamp(1.0 - min(abs(value - low), abs(value - high)) * 2.0)


def recommend(context: dict, catalog: dict) -> list[dict]:
    available = set(context.get("availableInputs", []))
    scene = context.get("sceneType", "general")
    focus = context.get("focus", "frame")
    arousal = clamp(float(context.get("arousal", 0.5)))
    continuity = clamp(float(context.get("continuity", 0.5)))
    music = 1.0 if context.get("musicSync") else 0.0
    results = []
    for effect in catalog["effects"]:
        missing = sorted(set(effect.get("requirements", [])) - available)
        if missing:
            continue
        narrative = effect["narrative"]
        scene_fit = 1.0 if scene in narrative["sceneTypes"] else 0.65 if "general" in narrative["sceneTypes"] else 0.25
        focus_fit = 1.0 if focus in narrative["focus"] else 0.65 if "frame" in narrative["focus"] else 0.35
        score = (
            0.30 * scene_fit
            + 0.20 * fit(continuity, narrative["continuity"])
            + 0.20 * fit(arousal, narrative["arousal"])
            + 0.15 * focus_fit
            + 0.10 * (1.0 if effect.get("musicFriendly") == bool(music) else 0.5)
            + 0.05 * (1.0 if effect["supportLevel"] == "native" else 0.85 if effect["supportLevel"] in {"input-assisted", "preprocessed"} else 0.65)
        )
        results.append({
            "id": effect["id"],
            "displayName": effect["displayName"],
            "score": round(score, 4),
            "supportLevel": effect["supportLevel"],
            "bestMoment": effect["bestMoment"],
            "avoidWhen": effect["avoidWhen"],
            "fallbackId": effect.get("fallbackId"),
        })
    return sorted(results, key=lambda item: (-item["score"], item["id"]))[:3]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("context", type=Path)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()
    context = json.loads(args.context.read_text(encoding="utf-8"))
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    print(json.dumps({"recommendations": recommend(context, catalog)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
