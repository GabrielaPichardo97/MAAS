#!/usr/bin/env python3
"""Valida estructura, hash y fidelidad de dialogue-adaptation.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def validate(data: dict, allow_unresolved: bool = False) -> list[str]:
    errors: list[str] = []
    if data.get("schemaVersion") != "1.0":
        errors.append("E_SCHEMA: schemaVersion debe ser 1.0")
    text = data.get("sourceText")
    if not isinstance(text, str) or hashlib.sha256(text.encode("utf-8")).hexdigest() != data.get("sourceTextSha256"):
        errors.append("E_FIDELITY: sourceTextSha256 no coincide")
    lines = text.splitlines() if isinstance(text, str) else []
    beat_ids: set[str] = set()
    for scene in data.get("scenes", []):
        if not scene.get("placeId"):
            errors.append(f"E_PLACE_UNRESOLVED: {scene.get('id')}")
        for beat in scene.get("beats", []):
            beat_id = beat.get("id")
            if beat_id in beat_ids:
                errors.append(f"E_SCHEMA: beat duplicado {beat_id}")
            beat_ids.add(beat_id)
            start, end = beat.get("sourceStartLine"), beat.get("sourceEndLine")
            if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start or end > len(lines):
                errors.append(f"E_FIDELITY: rango inválido en {beat_id}")
                continue
            fragment = "\n".join(lines[start - 1:end])
            if fragment != beat.get("sourceFragment"):
                errors.append(f"E_FIDELITY: sourceFragment cambió en {beat_id}")
            if beat.get("verbatimText") not in fragment:
                errors.append(f"E_FIDELITY: verbatimText no pertenece a la fuente en {beat_id}")
    if not beat_ids:
        errors.append("E_DIALOGUE_EMPTY: no hay beats")
    if not allow_unresolved:
        errors.extend(f"{item.get('code')}: {item.get('message')}" for item in data.get("unresolved", []) if item.get("blocking"))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--allow-unresolved", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        errors = validate(data, args.allow_unresolved)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as exc:
        errors = [f"E_SCHEMA: {exc}"]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
