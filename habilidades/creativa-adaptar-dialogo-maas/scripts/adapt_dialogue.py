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
PLACE_RE = re.compile(r"^\s*\*\*([^*]+)\*\*\s*$")
SCENE_RE = re.compile(r"^\s*(?:ESCENA|SCENE)\s*:\s*(.+?)\s*$", re.IGNORECASE)
STANDALONE_RE = re.compile(r"^[A-ZÁÉÍÓÚÜÑ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_ -]{0,59}$")


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


def make_beat(number: int, speaker: str, text: str, source: str, start: int, end: int) -> dict:
    return {
        "id": f"beat-{number:04d}",
        "speaker": speaker,
        "characterId": slug(speaker),
        "speakerInference": {"inferred": False, "confidence": 1.0},
        "verbatimText": text,
        "sourceFragment": source,
        "sourceStartLine": start,
        "sourceEndLine": end,
        "emotion": inferred("seriedad", 0.25),
        "stageDirection": inferred("En posición neutra", 0.2),
        "durationMs": inferred(estimate_duration(text), 0.65),
    }


def parse(text: str, default_place: str | None) -> tuple[list[dict], list[dict]]:
    lines = text.splitlines()
    place_label = default_place
    place_inferred = default_place is None
    scenes: list[dict] = []
    beats: list[dict] = []
    unresolved: list[dict] = []
    active_speaker: str | None = None
    beat_number = 0

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
        marker = PLACE_RE.fullmatch(raw) or SCENE_RE.fullmatch(raw)
        if marker:
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
            index += 1
            continue
        parsed = speaker_at(lines, index)
        if parsed:
            active_speaker, inline, _ = parsed
            if inline:
                beat_number += 1
                beats.append(make_beat(beat_number, active_speaker, inline, raw, index + 1, index + 1))
            index += 1
            continue
        if active_speaker:
            beat_number += 1
            beats.append(make_beat(beat_number, active_speaker, raw, raw, index + 1, index + 1))
        else:
            unresolved.append({
                "code": "E_SPEAKER_AMBIGUOUS",
                "message": "No se puede atribuir el parlamento sin inventar un hablante.",
                "blocking": True,
                "line": index + 1,
            })
        index += 1
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
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    text = args.input.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    title = (args.title or args.input.stem).strip()
    episode_id = slug(args.episode_id or title)
    scenes, unresolved = parse(text, args.place)
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
