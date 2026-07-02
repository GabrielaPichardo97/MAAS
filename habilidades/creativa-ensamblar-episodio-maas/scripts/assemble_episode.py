#!/usr/bin/env python3
"""Ensambla artefactos MAAS desde una dirección aprobada y fiel."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path


def scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False) if re.search(r"\s|[{}]", value) else value
    return str(value)


def effect_token(effect: dict) -> str:
    pairs = [f"role={effect['role']}", f"intensity={effect['intensity']}"]
    if effect.get("startOffsetMs") is not None:
        pairs.append(f"startOffsetMs={int(effect['startOffsetMs'])}")
    if effect.get("durationMs") is not None:
        pairs.append(f"durationMs={int(effect['durationMs'])}")
    if effect.get("target"):
        pairs.append(f"target={scalar(effect['target'])}")
    pairs.extend(f"{name}={scalar(value)}" for name, value in sorted(effect.get("params", {}).items()))
    return "{{fx " + effect["id"] + " " + " ".join(pairs) + "}}"


def ensure_fidelity(direction: dict, adaptation: dict, adaptation_sha: str) -> None:
    if direction.get("adaptationSha256") != adaptation_sha:
        raise ValueError("E_FIDELITY: adaptationSha256 no coincide")
    if any(item.get("blocking") for item in adaptation.get("unresolved", [])):
        raise ValueError("E_UNRESOLVED: la adaptación conserva diagnósticos bloqueantes")
    if any(item.get("blocking") or item.get("blockingPublication") for item in direction.get("unresolvedMedia", [])):
        raise ValueError("E_ASSET: la dirección conserva huecos de media bloqueantes")
    approval = direction.get("approval", {})
    if approval.get("status") != "approved" or not approval.get("approvedBy") or not approval.get("approvedAt"):
        raise ValueError("E_APPROVAL: la dirección no tiene aprobación explícita completa")
    expected = {beat["id"]: beat for scene in adaptation.get("scenes", []) for beat in scene.get("beats", [])}
    actual = {beat.get("id"): beat for scene in direction.get("scenes", []) for beat in scene.get("beats", [])}
    if set(expected) != set(actual):
        raise ValueError("E_FIDELITY: el conjunto de beats cambió")
    for beat_id, source in expected.items():
        for field in ("speaker", "characterId", "verbatimText"):
            if actual[beat_id].get(field) != source.get(field):
                raise ValueError(f"E_FIDELITY: {field} cambió en {beat_id}")


def validate_effects(direction: dict, catalog: dict) -> None:
    by_id = {entry["id"]: entry for entry in catalog.get("effects", [])}
    for scene in direction.get("scenes", []):
        for beat in scene.get("beats", []):
            roles = set()
            if len(beat.get("effects", [])) > 3:
                raise ValueError(f"E_EFFECT_STACK: más de tres efectos en {beat.get('id')}")
            for effect in beat.get("effects", []):
                entry = by_id.get(effect.get("id"))
                if not entry:
                    raise ValueError(f"E_EFFECT_ID: {effect.get('id')}")
                role = effect.get("role")
                if role not in {"dominant", "support", "finish"} or role in roles:
                    raise ValueError(f"E_EFFECT_STACK: rol inválido o duplicado {role}")
                roles.add(role)
                intensity = effect.get("intensity")
                if isinstance(intensity, bool) or not isinstance(intensity, (int, float)) or not 0 <= intensity <= 1:
                    raise ValueError("E_EFFECT_PARAM: intensity fuera de 0..1")
                for timing in ("startOffsetMs", "durationMs"):
                    if effect.get(timing) is not None and (isinstance(effect[timing], bool) or not isinstance(effect[timing], int)):
                        raise ValueError(f"E_EFFECT_PARAM: {timing} exige integer")
                params = effect.get("params", {})
                if not isinstance(params, dict):
                    raise ValueError("E_EFFECT_PARAM: params exige object")
                unknown = set(params) - set(entry.get("parameters", {})) - set(entry.get("requirements", []))
                if unknown:
                    raise ValueError(f"E_EFFECT_PARAM: parámetros desconocidos {sorted(unknown)}")
                missing = set(entry.get("requirements", [])) - set(effect.get("params", {}))
                if missing:
                    raise ValueError(f"E_EFFECT_REQUIREMENT: faltan {sorted(missing)}")


def dump(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direction", type=Path)
    parser.add_argument("--adaptation", type=Path, required=True)
    parser.add_argument("--effect-catalog", type=Path, required=True)
    parser.add_argument("--output-source", type=Path, required=True)
    parser.add_argument("--character-map", type=Path, required=True)
    parser.add_argument("--presentation", type=Path, required=True)
    args = parser.parse_args()
    try:
        adaptation_raw = args.adaptation.read_bytes()
        adaptation = json.loads(adaptation_raw.decode("utf-8-sig"))
        direction = json.loads(args.direction.read_text(encoding="utf-8-sig"))
        catalog = json.loads(args.effect_catalog.read_text(encoding="utf-8-sig"))
        ensure_fidelity(direction, adaptation, hashlib.sha256(adaptation_raw).hexdigest())
        validate_effects(direction, catalog)
        content_lines: list[str] = []
        character_map: dict[str, str] = {}
        presentation_characters: dict[str, dict] = {}
        places: dict[str, str] = {}
        for scene_index, scene in enumerate(direction.get("scenes", [])):
            place_id, place_label = scene.get("placeId"), scene.get("placeLabel")
            if not place_id or not place_label:
                raise ValueError(f"E_PLACE_UNRESOLVED: {scene.get('id')}")
            places[str(place_label).upper()] = place_id
            for beat_index, beat in enumerate(scene.get("beats", [])):
                alias, character_id = beat["speaker"], beat["characterId"]
                character_map[alias] = character_id
                presentation_characters.setdefault(character_id, {"label": alias, "position": "izquierda" if (beat_index + scene_index) % 2 == 0 else "derecha"})
                seconds = max(1, math.ceil(int(beat["durationMs"]) / 1000))
                content_lines.append(f"[{alias}] ({seconds} segundos | {beat['emotion']} | {beat['stageDirection']})")
                tokens = " ".join(effect_token(effect) for effect in beat.get("effects", []))
                content_lines.append(beat["verbatimText"] + (" " + tokens if tokens else ""))
            content_lines.append(f"**{place_label.upper()}**")
            content_lines.append("")
        metadata = adaptation["metadata"]
        source = {
            "schemaVersion": "1.0", "episodeId": metadata["episodeId"], "title": metadata["title"],
            "language": metadata.get("language", "es-MX"), "status": "draft", "seed": metadata["seed"],
            "source": {"importedFrom": "MAAS/habilidades/creativa-*"},
            "content": "\n".join(content_lines).rstrip() + "\n",
        }
        presentation = {"schemaVersion": "2.0", "characters": presentation_characters, "places": places}
        dump(args.output_source, source)
        dump(args.character_map, character_map)
        dump(args.presentation, presentation)
        print(json.dumps({"beats": len(character_map) and sum(len(scene.get('beats', [])) for scene in direction.get('scenes', [])), "output": str(args.output_source)}, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
