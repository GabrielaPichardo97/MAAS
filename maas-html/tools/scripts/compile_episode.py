#!/usr/bin/env python3
"""Compila un episode-source JSON a una timeline MAAS determinista."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
NORMALIZER_PATH = HERE / "normalize_legacy_input.py"
spec = importlib.util.spec_from_file_location("maas_normalizer", NORMALIZER_PATH)
normalizer = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(normalizer)

HEADER_RE = re.compile(r"^\s*\[([^\]]+)\]\s*\(([^|]+)\|([^|]+)\|([^)]*)\)\s*$")
LEGACY_HEADER_RE = re.compile(r"^\s*\[([^\]]+)\]\s*\(([^|]+)\|([^|]+)\|([^)]*)\)\)+\s*$")
PLACE_RE = re.compile(r"^\s*\*\*([^*]+)\*\*\s*$")
TRANSITION_RE = re.compile(r"^\s*---(.+?)---\s*$")
CAMERA_RE = re.compile(r"\((ES|ZI|ZO|PA-I|PA-D|TI-A|TI-B|PP)(?:\*([0-9]+(?:\.[0-9]+)?))?(?:\s+([^()]+))?\)\s*$")
CAMERA_ANY_RE = re.compile(r"\((ES|ZI|ZO|PA-I|PA-D|TI-A|TI-B|PP)(?:\*([0-9]+(?:\.[0-9]+)?))?(?:\s+([^()]+))?\)")
FX_RE = re.compile(r"\{\{fx\s+([^\s}]+)((?:\s+[A-Za-z][\w-]*=(?:\"[^\"]*\"|[^\s}]+))*)\s*\}\}")
FX_PAIR_RE = re.compile(r"([A-Za-z][\w-]*)=(\"[^\"]*\"|[^\s}]+)")
FX_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*\.v\d+\.\d+\.\d+$")
NUMBER_PREFIX_RE = re.compile(r"^\s*\d+(?:\.\s*|\s+)")

EMOTIONS = {
    "felicidad": "happy", "alegría": "happy", "entusiasmo": "happy", "curiosidad": "happy",
    "ironía": "happy", "sarcasmo": "happy", "alivio": "happy", "tristeza": "sad",
    "resignación": "sad", "enojo": "angry", "frustración": "angry", "exasperación": "angry",
    "seriedad": "serious", "serio": "serious", "preocupación": "worried", "miedo": "worried",
    "sorpresa": "surprised", "confusión": "confused", "cansancio": "sad", "pensamiento": "a",
}


def parse_duration(value: str) -> int:
    value = value.strip().lower()
    seconds = re.fullmatch(r"([0-9]+)\s+segundos?", value)
    if seconds:
        return int(seconds.group(1)) * 1000
    clock = re.fullmatch(r"([0-9]{1,2}):([0-5][0-9])", value)
    if clock:
        return (int(clock.group(1)) * 60 + int(clock.group(2))) * 1000
    raise ValueError(f"E_DURATION: {value}")


def effect_from(line: str, profile: str, warnings: list[dict[str, Any]], line_no: int) -> tuple[str, dict[str, Any]]:
    match = CAMERA_RE.search(line)
    if not match and profile == "legacy-v1":
        matches = list(CAMERA_ANY_RE.finditer(line))
        if matches:
            match = matches[-1]
            warnings.append({"code": "W_TRAILING_DIALOGUE_METADATA", "line": line_no, "value": line[match.end():].strip()})
    if not match:
        if profile == "legacy-v1":
            warnings.append({"code": "W_MISSING_CAMERA_STATIC", "line": line_no, "value": line})
            return NUMBER_PREFIX_RE.sub("", line.strip()), {"code": "ES", "intensity": 1.0, "target": None, "tremor": True}
        raise ValueError(f"E_DIALOGUE_CAMERA: {line}")
    text = (line[: match.start()] + line[match.end():]).strip()
    text = NUMBER_PREFIX_RE.sub("", text)
    code, intensity, target = match.groups()
    return text, {"code": code, "intensity": float(intensity or 1.0), "target": target.strip() if target else None, "tremor": True}


def scalar(value: str) -> str | int | float | bool:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.casefold() in {"true", "false"}:
        return value.casefold() == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+(?:\.\d+)?", value):
        return float(value)
    return value


def validate_parameter(name: str, value: Any, spec: dict[str, Any], line_no: int) -> None:
    kind = spec["type"]
    if kind == "boolean" and not isinstance(value, bool):
        raise ValueError(f"E_EFFECT_PARAM line {line_no}: {name} exige boolean")
    if kind in {"number", "integer"}:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or (kind == "integer" and not isinstance(value, int)):
            raise ValueError(f"E_EFFECT_PARAM line {line_no}: {name} exige {kind}")
        if value < spec["min"] or value > spec["max"]:
            raise ValueError(f"E_EFFECT_PARAM line {line_no}: {name} fuera de {spec['min']}..{spec['max']}")
    if kind == "enum" and value not in spec["values"]:
        raise ValueError(f"E_EFFECT_PARAM line {line_no}: {name} debe ser uno de {spec['values']}")
    if kind == "color" and (not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value)):
        raise ValueError(f"E_EFFECT_PARAM line {line_no}: {name} exige color #RRGGBB")


def effects_from(line: str, catalog: dict[str, dict[str, Any]], line_no: int) -> tuple[str, list[dict[str, Any]]]:
    effects: list[dict[str, Any]] = []
    roles: set[str] = set()
    for match in FX_RE.finditer(line):
        effect_id = match.group(1)
        if not FX_ID_RE.fullmatch(effect_id) or effect_id not in catalog:
            raise ValueError(f"E_EFFECT_ID line {line_no}: {effect_id}")
        pairs = {key: scalar(value) for key, value in FX_PAIR_RE.findall(match.group(2))}
        role = pairs.pop("role", None)
        if role not in {"dominant", "support", "finish"}:
            raise ValueError(f"E_EFFECT_STACK line {line_no}: role obligatorio dominant/support/finish")
        if role in roles:
            raise ValueError(f"E_EFFECT_STACK line {line_no}: role duplicado {role}")
        roles.add(role)
        intensity = pairs.pop("intensity", 1.0)
        if isinstance(intensity, bool) or not isinstance(intensity, (int, float)) or not 0 <= intensity <= 1:
            raise ValueError(f"E_EFFECT_PARAM line {line_no}: intensity fuera de 0..1")
        start = pairs.pop("startOffsetMs", 0)
        duration = pairs.pop("durationMs", -1)
        target = pairs.pop("target", None)
        if not isinstance(start, int) or not isinstance(duration, int):
            raise ValueError(f"E_EFFECT_PARAM line {line_no}: offsets y duración exigen enteros ms")
        entry = catalog[effect_id]
        specs = entry["parameters"]
        allowed = set(specs) | set(entry.get("requirements", []))
        unknown = sorted(set(pairs) - allowed)
        if unknown:
            raise ValueError(f"E_EFFECT_PARAM line {line_no}: parámetros desconocidos {unknown}")
        for name, value in pairs.items():
            if name in specs:
                validate_parameter(name, value, specs[name], line_no)
        missing = sorted(set(entry.get("requirements", [])) - set(pairs))
        if missing:
            fallback = entry.get("fallbackId") or "sin fallback"
            raise ValueError(f"E_EFFECT_REQUIREMENT line {line_no}: faltan {missing}; alternativa {fallback}")
        params = {name: spec["default"] for name, spec in specs.items()}
        params.update(pairs)
        effects.append({"id": effect_id, "role": role, "intensity": float(intensity), "startOffsetMs": start, "durationMs": duration, "target": target, "params": params})
    if len(effects) > 3:
        raise ValueError(f"E_EFFECT_STACK line {line_no}: máximo tres efectos")
    text = FX_RE.sub("", line).strip()
    if "{{fx" in text:
        raise ValueError(f"E_EFFECT_SYNTAX line {line_no}: token fx inválido")
    return NUMBER_PREFIX_RE.sub("", text), effects


def resolve_emotion(source: str, profile: str, warnings: list[dict[str, Any]], line: int) -> str:
    key = source.strip().split()[0].casefold()
    if key in EMOTIONS:
        return EMOTIONS[key]
    if profile == "legacy-v1":
        warnings.append({"code": "W_EMOTION_HAPPY_FALLBACK", "line": line, "value": source})
        return "happy"
    raise ValueError(f"E_EMOTION line {line}: {source}")


def compile_document(data: dict, profile: str, character_map: dict[str, str], effect_catalog: dict[str, dict[str, Any]] | None = None) -> dict:
    content = data["content"].replace("\r\n", "\n").replace("\r", "\n")
    warnings: list[dict[str, Any]] = []
    timeline: list[dict[str, Any]] = []
    characters: dict[str, str] = {}
    active: dict[str, Any] | None = None
    pending: list[dict[str, Any]] = []
    scene_number = cue_number = 0
    cursor = 0

    def next_id() -> str:
        nonlocal cue_number
        cue_number += 1
        return f"cue-{cue_number:04d}"

    def flush_scene(place: str, line: int) -> None:
        nonlocal cursor, scene_number, pending
        if not pending:
            raise ValueError(f"E_PLACE line {line}: escena vacía")
        scene_number += 1
        scene_start = cursor
        for item in pending:
            item["startMs"] = cursor
            cursor += item["durationMs"]
        scene = {"id": f"scene-{scene_number:04d}", "type": "scene", "startMs": scene_start, "durationMs": cursor - scene_start, "place": place.strip(), "cueIds": [x["id"] for x in pending]}
        timeline.append(scene)
        timeline.extend(pending)
        pending = []

    lines = content.split("\n")
    dialogue_counts: dict[int, int] = {}
    header_index = -1
    for raw in lines:
        if HEADER_RE.fullmatch(raw) or (profile == "legacy-v1" and LEGACY_HEADER_RE.fullmatch(raw)):
            header_index += 1
            dialogue_counts[header_index] = 0
        elif raw.strip() and not PLACE_RE.fullmatch(raw) and not TRANSITION_RE.fullmatch(raw):
            if header_index >= 0:
                dialogue_counts[header_index] += 1

    header_index = -1
    for line_no, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue
        header = HEADER_RE.fullmatch(raw)
        if not header and profile == "legacy-v1":
            header = LEGACY_HEADER_RE.fullmatch(raw)
            if header:
                warnings.append({"code": "W_LEGACY_HEADER_PARENTHESES", "line": line_no, "value": raw})
        if header:
            header_index += 1
            alias, duration, source_emotion, stage = (x.strip() for x in header.groups())
            character_id = character_map.get(alias, alias)
            if alias not in character_map and profile == "legacy-v1":
                warnings.append({"code": "W_CHARACTER_IDENTITY", "line": line_no, "value": alias})
            elif alias not in character_map:
                raise ValueError(f"E_CHARACTER line {line_no}: {alias}")
            characters[alias] = character_id
            active = {
                "alias": alias,
                "characterId": character_id,
                "declaredDurationMs": parse_duration(duration),
                "emotion": resolve_emotion(source_emotion, profile, warnings, line_no),
                "sourceEmotion": source_emotion,
                "stageDirection": stage,
                "line": line_no,
                "count": max(1, dialogue_counts.get(header_index, 1)),
            }
            continue
        place = PLACE_RE.fullmatch(raw)
        if place:
            flush_scene(place.group(1), line_no)
            active = None
            continue
        transition = TRANSITION_RE.fullmatch(raw)
        if transition:
            duration = 1900
            timeline.append({"id": next_id(), "type": "transition", "startMs": cursor, "durationMs": duration, "text": transition.group(1).strip()})
            cursor += duration
            continue
        if active is None:
            warnings.append({"code": "W_EDITORIAL_PREFIX", "line": line_no, "value": line})
            continue
        if profile == "canonical-v2":
            text, effects = effects_from(raw, effect_catalog or {}, line_no)
            effect = None
        else:
            text, effect = effect_from(raw, profile, warnings, line_no)
            effects = []
        cue_type = "dialogue"
        sound = None
        if text.upper().startswith("OSD"):
            sound_match = re.search(r"OSD\s*\((.*?)\)", text, re.IGNORECASE)
            if not sound_match:
                raise ValueError(f"E_DIALOGUE_CAMERA line {line_no}: OSD inválido")
            sound = sound_match.group(1).strip()
            text = sound
            cue_type = "sfx"
        divided = active["declaredDurationMs"] // active["count"]
        duration = max(2000, divided) if profile == "legacy-v1" else max(40, divided)
        cue = {
            "id": next_id(), "type": cue_type, "startMs": 0, "durationMs": duration,
            "declaredDurationMs": active["declaredDurationMs"], "resolvedDurationMs": duration,
            "speaker": active["characterId"], "speakerAlias": active["alias"], "text": text,
            "emotion": active["emotion"], "sourceEmotion": active["sourceEmotion"],
            "stageDirection": active["stageDirection"], "sourceLine": line_no,
        }
        if profile == "canonical-v2":
            for item in effects:
                if item["durationMs"] < 0:
                    item["durationMs"] = duration - item["startOffsetMs"]
                if item["durationMs"] < 0 or item["startOffsetMs"] + item["durationMs"] > duration:
                    raise ValueError(f"E_EFFECT_PARAM line {line_no}: ventana fuera del cue")
            cue["effects"] = effects
        else:
            cue["effect"] = effect
        if sound is not None:
            cue["sound"] = sound
        pending.append(cue)
    if pending:
        raise ValueError("E_PLACE: el último bloque no termina con **LUGAR**")
    timeline.sort(key=lambda cue: (cue["startMs"], cue["id"]))
    if profile == "canonical-v2":
        flashes = sorted(
            cue["startMs"] + effect["startOffsetMs"]
            for cue in timeline
            for effect in cue.get("effects", [])
            if effect["id"] == "time.flash-frame.impact.single.v1.0.0"
        )
        for index, start in enumerate(flashes):
            if sum(1 for value in flashes[index:] if value < start + 1000) > 3:
                raise ValueError("E_EFFECT_SAFETY: más de tres flashes en un segundo")
    return {
        "schemaVersion": "2.0" if profile == "canonical-v2" else "1.0", "episodeId": data["episodeId"], "title": data["title"],
        "language": data["language"], "status": data["status"], "seed": data["seed"],
        "profile": profile, "orientations": ["landscape", "portrait"], "characters": characters,
        "assets": [], "audioPolicy": {"musicGain": 0.15, "transitionGain": 0.5, "sampleRate": 44100, "muteMusicDuringSfx": True},
        "timeline": timeline, "durationMs": cursor, "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--profile", choices=("legacy-v1", "canonical-v1", "canonical-v2"), default="legacy-v1")
    parser.add_argument("--character-map", type=Path)
    parser.add_argument("--effect-catalog", type=Path)
    args = parser.parse_args()
    try:
        source = json.loads(args.input.read_text(encoding="utf-8-sig"))
        data, normalization_warnings = normalizer.normalize(source)
        character_map = json.loads(args.character_map.read_text(encoding="utf-8-sig")) if args.character_map else {}
        catalog_path = args.effect_catalog
        if args.profile == "canonical-v2" and catalog_path is None:
            candidates = [
                HERE.parents[1] / "seleccionar-efectos-maas" / "references" / "effects-catalog.json",
                HERE.parents[1] / "public" / "effects-catalog.json",
            ]
            catalog_path = next((candidate for candidate in candidates if candidate.exists()), candidates[0])
        effect_catalog = {}
        if catalog_path:
            catalog_data = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
            effect_catalog = {item["id"]: item for item in catalog_data["effects"]}
        manifest = compile_document(data, args.profile, character_map, effect_catalog)
        manifest["warnings"] = normalization_warnings + manifest["warnings"]
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    payload = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
        digest = hashlib.sha256(payload.encode()).hexdigest()
        print(json.dumps({"output": str(args.output), "sha256": digest, "warnings": len(manifest["warnings"])}, ensure_ascii=False))
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
