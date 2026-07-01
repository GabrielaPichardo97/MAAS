#!/usr/bin/env python3
"""Valida el contenedor JSON y la gramática esencial de un episodio MAAS."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

STRICT_KEYS = {"schemaVersion", "episodeId", "title", "language", "status", "seed", "source", "content"}
REQUIRED_KEYS = {"schemaVersion", "episodeId", "title", "language", "status", "content"}
LEGACY_KEYS = {"title", "content", "url", "status", "sendDate"}
HEADER_RE = re.compile(r"^\s*\[([^\]]+)\]\s*\(([^|]+)\|([^|]+)\|([^)]*)\)\s*$")
PLACE_RE = re.compile(r"^\s*\*\*([^*]+)\*\*\s*$")
TRANSITION_RE = re.compile(r"^\s*---(.+?)---\s*$")
CAMERA_RE = re.compile(r"\((ES|ZI|ZO|PA-I|PA-D|TI-A|TI-B|PP)(?:\*([0-9]+(?:\.[0-9]+)?))?(?:\s+([^()]+))?\)\s*$")
LEGACY_CAMERA_RE = re.compile(r"\((ES|ZI|ZO|PA-I|PA-D|TI-A|TI-B|PP)([0-9]+(?:\.[0-9]+)?)(?:\s+([^()]+))?\)\s*$")
DURATION_RE = re.compile(r"^(?:([0-9]+)\s+segundos?|([0-9]{1,2}):([0-5][0-9]))$", re.IGNORECASE)
EPISODE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LANGUAGE_RE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")


def diagnostic(code: str, severity: str, message: str, line: int = 0, column: int = 0, suggestion: str = "") -> dict[str, Any]:
    return {"code": code, "severity": severity, "line": line, "column": column, "message": message, "suggestion": suggestion}


def validate_container(data: Any, mode: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(data, dict):
        return [diagnostic("E_SCHEMA", "error", "La raíz debe ser un objeto JSON.")]
    keys = set(data)
    if mode == "legacy" and {"title", "content"}.issubset(keys) and "schemaVersion" not in keys:
        out.append(diagnostic("W_LEGACY_INPUT", "warning", "Se detectó el contrato legado.", suggestion="Normaliza el archivo antes de publicarlo."))
        unknown = keys - LEGACY_KEYS
        if unknown:
            out.append(diagnostic("E_SCHEMA", "error", f"Campos legados no permitidos: {sorted(unknown)}."))
        if str(data.get("status", "")).lower() not in {"procesar", "procesado"}:
            out.append(diagnostic("E_SCHEMA", "error", "status legado debe ser procesar o procesado."))
        return out
    missing = REQUIRED_KEYS - keys
    unknown = keys - STRICT_KEYS
    if missing:
        out.append(diagnostic("E_SCHEMA", "error", f"Faltan campos: {sorted(missing)}."))
    if unknown:
        out.append(diagnostic("E_SCHEMA", "error", f"Campos no permitidos: {sorted(unknown)}."))
    if data.get("schemaVersion") != "1.0":
        out.append(diagnostic("E_SCHEMA", "error", "schemaVersion debe ser 1.0."))
    if not EPISODE_ID_RE.fullmatch(str(data.get("episodeId", ""))):
        out.append(diagnostic("E_SCHEMA", "error", "episodeId no es un slug válido."))
    if not LANGUAGE_RE.fullmatch(str(data.get("language", ""))):
        out.append(diagnostic("E_SCHEMA", "error", "language no parece una etiqueta BCP 47."))
    if data.get("status") not in {"draft", "ready", "published"}:
        out.append(diagnostic("E_SCHEMA", "error", "status debe ser draft, ready o published."))
    seed = data.get("seed")
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed <= 2_147_483_647):
        out.append(diagnostic("E_SCHEMA", "error", "seed debe ser entero entre 0 y 2147483647."))
    return out


def validate_script(content: str, mode: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    normalized = content.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    seen_header = False
    block_has_header = False
    block_has_place = False
    for number, raw in enumerate(normalized.split("\n"), 1):
        line = raw.strip()
        if not line:
            continue
        header = HEADER_RE.fullmatch(raw)
        if header:
            if block_has_header and block_has_place:
                block_has_header = False
                block_has_place = False
            seen_header = True
            block_has_header = True
            character, duration, emotion, stage = (x.strip() for x in header.groups())
            if not all((character, emotion, stage)):
                out.append(diagnostic("E_SCRIPT_HEADER", "error", "El header contiene un campo vacío.", number, 1))
            if not DURATION_RE.fullmatch(duration):
                out.append(diagnostic("E_DURATION", "error", f"Duración no válida: {duration}.", number, raw.find(duration) + 1, "Usa '4 segundos' o '00:04'."))
            continue
        if PLACE_RE.fullmatch(raw):
            if not block_has_header:
                out.append(diagnostic("E_PLACE", "error", "El lugar no cierra ningún bloque de intervención.", number, 1))
            block_has_place = True
            continue
        if TRANSITION_RE.fullmatch(raw):
            continue
        if not seen_header:
            out.append(diagnostic("W_EDITORIAL_PREFIX", "warning", "Texto editorial anterior al primer header.", number, 1))
            continue
        match = CAMERA_RE.search(raw)
        legacy = LEGACY_CAMERA_RE.search(raw) if mode == "legacy" else None
        if not match and legacy:
            out.append(diagnostic("W_LEGACY_EFFECT_SYNTAX", "warning", f"Sintaxis histórica: {legacy.group(0)}.", number, legacy.start() + 1, "Inserta '*' antes de la intensidad."))
            match = legacy
        if not match:
            out.append(diagnostic("E_DIALOGUE_CAMERA", "error", "La línea requiere un camera token válido al final.", number, max(1, len(raw)), "Ejemplo: (ZI*1.2)."))
            continue
        effect = match.group(1)
        intensity = match.group(2)
        target = match.group(3)
        if intensity is not None and float(intensity) <= 0:
            out.append(diagnostic("E_EFFECT", "error", "La intensidad debe ser mayor que cero.", number, match.start() + 1))
        if effect != "PP" and target:
            out.append(diagnostic("E_EFFECT", "error", f"{effect} no admite objetivo.", number, match.start() + 1))
    if not seen_header:
        out.append(diagnostic("E_SCRIPT_HEADER", "error", "No se encontró ninguna intervención."))
    if block_has_header and not block_has_place:
        out.append(diagnostic("E_PLACE", "error", "El último bloque no termina con **LUGAR**."))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--mode", choices=("strict", "legacy"), default="strict")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        text = args.input.read_text(encoding="utf-8-sig")
        data = json.loads(text)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result = {"valid": False, "diagnostics": [diagnostic("E_JSON_INVALID", "error", str(exc))]}
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
        return 1
    diagnostics = validate_container(data, args.mode)
    content = data.get("content") if isinstance(data, dict) else None
    if isinstance(content, str) and content.strip():
        diagnostics.extend(validate_script(content, args.mode))
    else:
        diagnostics.append(diagnostic("E_SCHEMA", "error", "content debe ser un string no vacío."))
    diagnostics.sort(key=lambda item: (item["line"], item["column"], item["code"]))
    valid = not any(item["severity"] == "error" for item in diagnostics)
    print(json.dumps({"valid": valid, "diagnostics": diagnostics}, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
