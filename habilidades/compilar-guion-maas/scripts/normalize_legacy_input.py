#!/usr/bin/env python3
"""Convierte el contenedor histórico de MAAS al contrato estricto 1.0."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path


def slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    return slug or "episodio"


def normalize_effects(content: str) -> tuple[str, list[dict[str, str]]]:
    warnings: list[dict[str, str]] = []
    pattern = re.compile(r"\((ES|ZI|ZO|PA-I|PA-D|TI-A|TI-B|PP)([0-9]+(?:\.[0-9]+)?)([^()]*)\)")

    def replace(match: re.Match[str]) -> str:
        before = match.group(0)
        after = f"({match.group(1)}*{match.group(2)}{match.group(3)})"
        warnings.append({"code": "W_LEGACY_EFFECT_SYNTAX", "before": before, "after": after})
        return after

    return pattern.sub(replace, content), warnings


def normalize(data: dict) -> tuple[dict, list[dict[str, str]]]:
    if data.get("schemaVersion") == "1.0":
        return data, []
    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    content, warnings = normalize_effects(content)
    episode_id = slugify(title)
    seed = int.from_bytes(hashlib.sha256(episode_id.encode()).digest()[:4], "big") & 0x7FFFFFFF
    source: dict[str, str] = {"importedFrom": "MAAS legacy JSON"}
    if data.get("url"):
        source["url"] = str(data["url"])
    if data.get("sendDate"):
        warnings.append({"code": "W_LEGACY_DATE_TIMEZONE", "value": str(data["sendDate"])})
    status = {"procesar": "ready", "procesado": "published"}.get(str(data.get("status", "")).lower(), "draft")
    warnings.insert(0, {"code": "W_LEGACY_INPUT", "value": "Contrato histórico convertido a 1.0"})
    return {
        "schemaVersion": "1.0",
        "episodeId": episode_id,
        "title": title or episode_id,
        "language": "es-MX",
        "status": status,
        "seed": seed,
        "source": source,
        "content": content,
    }, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        normalized, warnings = normalize(data)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as exc:
        print(f"E_JSON_INVALID: {exc}", file=sys.stderr)
        return 1
    payload = json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(payload)
    for warning in warnings:
        print(json.dumps(warning, ensure_ascii=False), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
