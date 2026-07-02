#!/usr/bin/env python3
"""Construye un asset-manifest determinista desde un repositorio MAAS."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("probe_media", HERE / "probe_media.py")
probe_module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(probe_module)

SOURCE_EXTENSIONS = {".png", ".webp", ".jpg", ".jpeg", ".ttf", ".otf", ".mp3", ".m4a", ".wav", ".mp4"}
EXCLUDED_PARTS = {"Videos", "clips", "Caps", "Audios_personajes", "__pycache__", ".git"}


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-") or "asset"


def classify(relative: Path) -> str:
    lower = "/".join(part.casefold() for part in relative.parts)
    if "personajes_animales" in lower:
        return "sprite"
    if "/fondos/" in f"/{lower}/":
        return "background"
    if "transiciones" in lower:
        return "transition"
    if relative.suffix.casefold() in {".ttf", ".otf"}:
        return "font"
    if "endings" in lower:
        return "ending"
    if "background" in lower:
        return "music"
    if "efectos" in lower or "ambiente" in lower:
        return "sfx"
    if "audios_personajes" in lower:
        return "voice"
    return "other"


def sprite_fields(relative: Path) -> dict[str, Any]:
    if "personajes_animales" not in [p.casefold() for p in relative.parts]:
        return {"character": None, "emotion": None, "gaze": None}
    character = relative.parent.name
    stem = relative.stem.removeprefix("Correct_")
    parts = stem.split("_")
    gaze = parts[-1].casefold() if parts[-1].casefold() in {"left", "right", "front"} else None
    emotion = "_".join(parts[:-1]) if gaze else parts[0]
    return {"character": character, "emotion": emotion, "gaze": gaze}


def make_entry(root: Path, path: Path, used: set[str]) -> dict[str, Any]:
    relative = path.relative_to(root)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    asset_id = slug(relative.with_suffix("").as_posix())
    if asset_id in used:
        asset_id = f"{asset_id}-{sha[:8]}"
    used.add(asset_id)
    metadata = probe_module.probe(path)
    asset_type = classify(relative)
    fields = sprite_fields(relative)
    place = relative.parent.name if asset_type == "background" else None
    orientation = None
    if asset_type == "ending":
        orientation = "portrait" if "_v" in relative.stem.casefold() else "landscape"
    return {
        "id": asset_id,
        "type": asset_type,
        "path": relative.as_posix(),
        "sha256": sha,
        **metadata,
        **fields,
        "place": place,
        "orientation": orientation,
        "aliases": [path.name],
        "source": None,
        "author": None,
        "license": "OFL-1.1" if asset_type == "font" and "nanum" in lower_path(path) else None,
        "allowedForPublish": bool(asset_type == "font" and "nanum" in lower_path(path)),
    }


def lower_path(path: Path) -> str:
    return path.as_posix().casefold()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--generated-at", default="1970-01-01T00:00:00Z")
    parser.add_argument("--overrides", type=Path, help="JSON assetId -> metadata revisada")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print("E_ASSET: raíz inexistente")
        return 1
    paths = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in SOURCE_EXTENSIONS:
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        paths.append(path)
    used: set[str] = set()
    assets = [make_entry(root, path, used) for path in sorted(paths, key=lambda p: p.as_posix().casefold())]
    if args.overrides:
        try:
            overrides = json.loads(args.overrides.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            print(f"E_JSON_INVALID: {exc}")
            return 1
        by_id = {asset["id"]: asset for asset in assets}
        unknown = sorted(set(overrides) - set(by_id))
        if unknown:
            print(f"E_ASSET: overrides para IDs desconocidos: {unknown}")
            return 1
        allowed = {"source", "author", "license", "allowedForPublish", "aliases", "orientation", "place", "character", "emotion", "gaze"}
        for asset_id, values in overrides.items():
            if not isinstance(values, dict) or set(values) - allowed:
                print(f"E_SCHEMA: override inválido para {asset_id}")
                return 1
            by_id[asset_id].update(values)
    manifest = {"schemaVersion": "1.0", "generatedAt": args.generated_at, "assets": assets}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    counts: dict[str, int] = {}
    for asset in assets:
        counts[asset["type"]] = counts.get(asset["type"], 0) + 1
    print(json.dumps({"assets": len(assets), "counts": counts, "output": str(args.output)}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
