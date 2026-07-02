#!/usr/bin/env python3
"""Construye una adaptación MAAS conservadora desde diálogo etiquetado."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path


COLON_RE = re.compile(r"^\s*([^:\n]{1,80}):[ \t]*(.+?)\s*$")
BRACKET_RE = re.compile(r"^\s*\[([^\]]+)\][ \t]*(.*?)\s*$")
LEGACY_HEADER_RE = re.compile(r"^\s*\[([^\]]+)\]\s*\(([^|]+)\|([^|]+)\|([^)]*)\)\s*$")
PLACE_RE = re.compile(r"^\s*\*\*([^*]+)\*\*\s*$")
SCENE_RE = re.compile(r"^\s*(?:ESCENA|SCENE)\s*:\s*(.+?)\s*$", re.IGNORECASE)
TRANSITION_RE = re.compile(r"^\s*---.+?---\s*$")
CAMERA_SUFFIX_RE = re.compile(r"\s*\((?:ES|ZI|ZO|PA-I|PA-D|TI-A|TI-B|PP)(?:\*[0-9]+(?:\.[0-9]+)?)?(?:\s+[^()]*)?\)\s*$")
NUMBER_PREFIX_RE = re.compile(r"^\s*\d+(?:\.\s*|\s+)")
STANDALONE_RE = re.compile(r"^[A-ZÁÉÍÓÚÜÑ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_ -]{0,59}$")


EMOTIONS = {
    "felicidad": "felicidad", "alegría": "felicidad", "divertido": "felicidad", "sonríe": "felicidad",
    "tristeza": "tristeza", "resignado": "tristeza", "cansancio": "tristeza",
    "enojo": "enojo", "furioso": "enojo", "frustración": "enojo", "horror": "miedo",
    "seriedad": "seriedad", "serio": "seriedad", "neutral": "seriedad", "sincero": "seriedad",
    "preocupación": "preocupación", "precavido": "confusión", "dudoso": "confusión",
    "miedo": "miedo", "pánico": "miedo", "sorpresa": "sorpresa", "confusión": "confusión",
    "confundido": "confusión", "intrigado": "confusión", "curiosidad": "confusión",
}


def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().casefold()
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-") or "dialogo-maas"


def seed_for(episode_id: str) -> int:
    return int.from_bytes(hashlib.sha256(episode_id.encode()).digest()[:4], "big") & 0x7FFFFFFF


def estimate_duration(text: str) -> int:
    words = len(re.findall(r"\b\w+\b", text, re.UNICODE))
    return max(2000, int(round((words / 2.5 * 1000 + 300) / 100) * 100))


def inferred(value: object, confidence: float) -> dict:
    return {"value": value, "inferred": True, "confidence": confidence}


def speaker_at(lines: list[str], index: int) -> tuple[str, str | None, bool] | None:
    line = lines[index]
    match = COLON_RE.fullmatch(line)
    if match:
        return match.group(1).strip(), match.group(2), False
    match = BRACKET_RE.fullmatch(line)
    if match:
        return match.group(1).strip(), match.group(2) or None, False
    next_line = lines[index + 1] if index + 1 < len(lines) else ""
    candidate = line.strip()
    has_letters = any(character.isalpha() for character in candidate)
    if STANDALONE_RE.fullmatch(candidate) and has_letters and candidate == candidate.upper() and next_line.strip() and not COLON_RE.fullmatch(next_line):
        return line.strip(), None, False
    return None


def canonical_emotion(value: str | None) -> tuple[str, float]:
    if not value:
        return "seriedad", 0.25
    normalized = unicodedata.normalize("NFC", value).strip().casefold()
    for key, emotion in EMOTIONS.items():
        if key in normalized:
            return emotion, 0.8
    return "seriedad", 0.4


def declared_duration(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"([0-9]+)\s+segundos?", value, re.IGNORECASE)
    return int(match.group(1)) * 1000 if match else None


def spoken_text(raw: str) -> str:
    return NUMBER_PREFIX_RE.sub("", CAMERA_SUFFIX_RE.sub("", raw)).strip()


def make_beat(number: int, speaker: str, text: str, source: str, start: int, end: int, *,
              character_map: dict[str, str], emotion: str | None = None,
              stage_direction: str | None = None, duration_ms: int | None = None) -> dict:
    resolved_emotion, emotion_confidence = canonical_emotion(emotion)
    return {
        "id": f"beat-{number:04d}",
        "speaker": speaker,
        "characterId": character_map.get(speaker, slug(speaker)),
        "speakerInference": {"inferred": False, "confidence": 1.0},
        "verbatimText": text,
        "sourceFragment": source,
        "sourceStartLine": start,
        "sourceEndLine": end,
        "emotion": inferred(resolved_emotion, emotion_confidence),
        "stageDirection": inferred(stage_direction or "En posición neutra", 0.85 if stage_direction else 0.2),
        "durationMs": inferred(duration_ms or estimate_duration(text), 0.9 if duration_ms else 0.65),
    }


def parse(text: str, default_place: str | None, character_map: dict[str, str] | None = None) -> tuple[list[dict], list[dict]]:
    lines = text.splitlines()
    character_map = character_map or {}
    place_label = default_place
    place_inferred = default_place is None
    scenes: list[dict] = []
    beats: list[dict] = []
    unresolved: list[dict] = []
    active_speaker: str | None = None
    active_legacy = False
    active_emotion: str | None = None
    active_stage: str | None = None
    active_duration: int | None = None
    pending_lines: list[tuple[str, int]] = []
    beat_number = 0

    def flush_block() -> None:
        nonlocal beat_number, pending_lines
        if not active_speaker or not pending_lines:
            pending_lines = []
            return
        clean = [(spoken_text(raw), raw, line_number) for raw, line_number in pending_lines]
        clean = [item for item in clean if item[0]]
        per_line_duration = max(40, active_duration // len(clean)) if active_duration and clean else None
        for dialogue, raw, line_number in clean:
            beat_number += 1
            beats.append(make_beat(
                beat_number, active_speaker, dialogue, raw, line_number, line_number,
                character_map=character_map, emotion=active_emotion,
                stage_direction=active_stage, duration_ms=per_line_duration,
            ))
        pending_lines = []

    def flush_scene() -> None:
        nonlocal beats
        if not beats:
            return
        scenes.append({
            "id": f"scene-{len(scenes) + 1:03d}",
            "placeId": slug(place_label) if place_label else None,
            "placeLabel": place_label,
            "placeInference": {"inferred": place_inferred, "confidence": 0.0 if place_inferred else 1.0},
            "beats": beats,
        })
        beats = []

    index = 0
    while index < len(lines):
        raw = lines[index]
        if not raw.strip():
            index += 1
            continue
        if raw.strip().strip("–- ").casefold() == "script":
            index += 1
            continue
        marker = PLACE_RE.fullmatch(raw) or SCENE_RE.fullmatch(raw)
        if marker:
            flush_block()
            if beats:
                place_label = marker.group(1).strip()
                place_inferred = False
                flush_scene()
                place_label = default_place
                place_inferred = default_place is None
            else:
                place_label = marker.group(1).strip()
                place_inferred = False
            active_speaker = None
            active_legacy = False
            index += 1
            continue
        if TRANSITION_RE.fullmatch(raw):
            flush_block()
            active_speaker = None
            active_legacy = False
            index += 1
            continue
        legacy_header = LEGACY_HEADER_RE.fullmatch(raw)
        if legacy_header:
            flush_block()
            active_speaker = legacy_header.group(1).strip()
            active_legacy = True
            active_duration = declared_duration(legacy_header.group(2))
            active_emotion = legacy_header.group(3).strip()
            active_stage = legacy_header.group(4).strip()
            index += 1
            continue
        if active_legacy and active_speaker:
            pending_lines.append((raw, index + 1))
            index += 1
            continue
        parsed = speaker_at(lines, index)
        if parsed:
            flush_block()
            active_speaker, inline, _ = parsed
            active_legacy = False
            active_emotion = active_stage = None
            active_duration = None
            if inline:
                beat_number += 1
                beats.append(make_beat(beat_number, active_speaker, inline, raw, index + 1, index + 1, character_map=character_map))
            index += 1
            continue
        if active_speaker:
            pending_lines.append((raw, index + 1))
        else:
            unresolved.append({
                "code": "E_SPEAKER_AMBIGUOUS",
                "message": "No se puede atribuir el parlamento sin inventar un hablante.",
                "blocking": True,
                "line": index + 1,
            })
        index += 1
    flush_block()
    flush_scene()
    if not scenes and not unresolved:
        unresolved.append({"code": "E_DIALOGUE_EMPTY", "message": "No se encontraron parlamentos.", "blocking": True})
    if any(scene["placeId"] is None for scene in scenes):
        unresolved.append({"code": "E_PLACE_UNRESOLVED", "message": "Falta definir el lugar de una o más escenas.", "blocking": True})
    return scenes, unresolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--title")
    parser.add_argument("--episode-id")
    parser.add_argument("--language", default="es-MX")
    parser.add_argument("--place")
    parser.add_argument("--character-map", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw_input = args.input.read_text(encoding="utf-8-sig")
    if args.input.suffix.casefold() == ".json":
        container = json.loads(raw_input)
        raw_input = str(container.get("content", ""))
    text = raw_input.replace("\r\n", "\n").replace("\r", "\n")
    character_map = json.loads(args.character_map.read_text(encoding="utf-8-sig")) if args.character_map else {}
    title = (args.title or args.input.stem).strip()
    episode_id = slug(args.episode_id or title)
    scenes, unresolved = parse(text, args.place, character_map)
    document = {
        "schemaVersion": "1.0",
        "metadata": {"episodeId": episode_id, "title": title, "language": args.language, "status": "draft", "seed": seed_for(episode_id)},
        "sourceText": text,
        "sourceTextSha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "scenes": scenes,
        "unresolved": unresolved,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"beats": sum(len(scene["beats"]) for scene in scenes), "output": str(args.output), "unresolved": len(unresolved)}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
