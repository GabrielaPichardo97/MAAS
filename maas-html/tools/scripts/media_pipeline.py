#!/usr/bin/env python3
"""Catálogo, resolución, staging y reportes de media para MAAS HTML."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from typing import Any


STANDARD_EMOTIONS = ("happy", "sad", "angry", "serious", "worried", "surprised", "dizzy", "confused", "scared", "cute", "a")
EMOTION_ALIASES = {"angy": "angry", "condused": "confused"}
BACKGROUND_VARIANTS = {
    None: ("landscape", "center", "legacy-v1"),
    1: ("landscape", "character-left", "legacy-v1"),
    2: ("landscape", "character-right", "legacy-v1"),
    3: ("portrait", "center", "legacy-v1"),
    4: ("portrait", "character-left", "legacy-v1"),
    5: ("portrait", "character-right", "legacy-v1"),
}


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-") or "asset"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"E_SCHEMA: {path} debe contener un objeto")
    return value


def dump_json(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sprite_metadata(asset: dict[str, Any], source: Path) -> dict[str, Any]:
    character = str(asset.get("character") or source.parent.name)
    stem = re.sub(r" \(\d+\)$", "", source.stem).removeprefix("Correct_")
    parts = stem.split("_")
    gaze = parts[-1].casefold() if parts[-1].casefold() in {"left", "right", "front"} else None
    emotion = "_".join(parts[:-1]) if gaze else parts[0]
    emotion = EMOTION_ALIASES.get(emotion.casefold(), emotion.casefold())
    quality_rank = 20 if source.stem.startswith("Correct_") else 10
    if " (" in source.stem:
        quality_rank -= 1
    canonical = f"character-{slug(character)}-{slug(emotion)}-{gaze or 'unspecified'}"
    return {
        "canonicalId": canonical,
        "characterId": slug(character),
        "characterLabel": character,
        "emotion": emotion,
        "gaze": gaze,
        "qualityRank": quality_rank,
    }


def background_metadata(asset: dict[str, Any], source: Path) -> dict[str, Any]:
    place = str(asset.get("place") or source.parent.name)
    match = re.search(r"\((\d+)\)$", source.stem)
    variant = int(match.group(1)) if match else None
    orientation, layout, profile = BACKGROUND_VARIANTS.get(variant, ("unknown", "unknown", "legacy-v1"))
    orientation_id = "portrait-legacy" if orientation == "portrait" else orientation
    return {
        "canonicalId": f"background-{slug(place)}-{orientation_id}-{layout}",
        "placeId": slug(place),
        "placeLabel": place,
        "orientation": orientation,
        "layout": layout,
        "profile": profile,
        "qualityRank": 10,
    }


def command_catalog(args: argparse.Namespace) -> int:
    raw = load_json(args.raw_manifest)
    root = args.root.resolve()
    result_assets = []
    used: dict[str, int] = {}
    for asset in raw.get("assets", []):
        source_path = str(asset["path"])
        source = (root / source_path).resolve()
        if root not in source.parents or not source.is_file():
            raise ValueError(f"E_ASSET: fuente inválida {source_path}")
        asset_type = str(asset["type"])
        metadata: dict[str, Any] = {}
        if asset_type == "sprite":
            metadata = sprite_metadata(asset, source)
        elif asset_type == "background":
            metadata = background_metadata(asset, source)
        canonical = metadata.pop("canonicalId", f"raw-{slug(str(asset['id']))}")
        count = used.get(canonical, 0)
        used[canonical] = count + 1
        canonical_id = canonical if count == 0 else f"{canonical}-{str(asset['sha256'])[:8]}"
        visual = asset_type in {"sprite", "background"}
        result_assets.append({
            "id": canonical_id,
            "type": asset_type,
            "sourceAssetId": asset["id"],
            "sourcePath": source_path.replace("\\", "/"),
            "sha256": asset["sha256"],
            "mimeType": asset.get("mimeType") or mimetypes.guess_type(source.name)[0] or "application/octet-stream",
            "width": asset.get("width"),
            "height": asset.get("height"),
            "durationMs": asset.get("durationMs"),
            "licenseId": "maas-proprietary" if visual else asset.get("license"),
            "allowedForPublish": True if visual else bool(asset.get("allowedForPublish")),
            **metadata,
        })
    catalog = {
        "schemaVersion": "1.0",
        "generatedAt": raw.get("generatedAt", "1970-01-01T00:00:00Z"),
        "rightsProfiles": {
            "maas-proprietary": {
                "owner": "MAAS",
                "license": "MAAS-Proprietary",
                "evidence": "Declaración del propietario, 2026-07-01",
                "allowedTypes": ["background", "sprite"],
            }
        },
        "assets": sorted(result_assets, key=lambda item: item["id"]),
    }
    dump_json(catalog, args.output)
    counts: dict[str, int] = {}
    for asset in result_assets:
        counts[asset["type"]] = counts.get(asset["type"], 0) + 1
    print(json.dumps({"assets": len(result_assets), "counts": counts, "output": str(args.output)}, ensure_ascii=False, sort_keys=True))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    root = args.root.resolve()
    diagnostics = []
    ids: set[str] = set()
    for asset in catalog.get("assets", []):
        asset_id = str(asset.get("id", ""))
        if asset_id in ids:
            diagnostics.append({"code": "E_ASSET", "assetId": asset_id, "message": "ID duplicado"})
        ids.add(asset_id)
        source = (root / str(asset.get("sourcePath", ""))).resolve()
        if root not in source.parents or not source.is_file():
            diagnostics.append({"code": "E_ASSET", "assetId": asset_id, "message": "Fuente ausente"})
        elif file_sha(source) != asset.get("sha256"):
            diagnostics.append({"code": "E_ASSET", "assetId": asset_id, "message": "SHA-256 distinto"})
    result = {"valid": not diagnostics, "assetCount": len(catalog.get("assets", [])), "diagnostics": diagnostics}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


def make_request(kind: str, character: str | None = None, emotion: str | None = None, place: str | None = None, layout: str | None = None, orientation: str | None = None, required_for: list[str] | None = None, blocking: bool = False) -> dict[str, Any]:
    request_id = slug("-".join(value for value in (kind, character, emotion, place, orientation, layout) if value))
    if kind == "sprite":
        suggested = f"characters/{character}/{emotion}.left.png"
        dimensions = {"preferred": "1024x1024", "acceptedExisting": "500x500"}
    else:
        suggested = f"backgrounds/{place}/{orientation}.{layout}.png"
        dimensions = {"preferred": "1080x1920" if orientation == "portrait" else "1920x1080", "acceptedExisting": "960x540"}
    return {
        "requestId": request_id,
        "severity": "episode-required" if blocking else "catalog-gap",
        "assetType": kind,
        "characterId": character,
        "emotion": emotion,
        "gaze": "left" if kind == "sprite" else None,
        "placeId": place,
        "orientation": orientation,
        "layout": layout,
        "dimensions": dimensions,
        "transparent": kind == "sprite",
        "anchor": {"x": 0.5, "y": 1.0} if kind == "sprite" else None,
        "styleReferenceIds": [f"character-{character}-happy-left"] if character else [f"background-{place}-landscape-center"],
        "suggestedFilename": suggested,
        "requiredFor": required_for or [],
        "blockingPublication": blocking,
    }


def catalog_gaps(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    assets = catalog.get("assets", [])
    characters = sorted({asset.get("characterId") for asset in assets if asset.get("type") == "sprite" and asset.get("characterId")})
    available = {(asset.get("characterId"), asset.get("emotion")) for asset in assets if asset.get("type") == "sprite" and asset.get("gaze") == "left"}
    gaps = [make_request("sprite", character=character, emotion=emotion) for character in characters for emotion in STANDARD_EMOTIONS if (character, emotion) not in available]
    places = sorted({asset.get("placeId") for asset in assets if asset.get("type") == "background" and asset.get("placeId")})
    for place in places:
        for layout in ("center", "character-left", "character-right"):
            native = any(asset.get("type") == "background" and asset.get("placeId") == place and asset.get("orientation") == "portrait" and asset.get("profile") == "canonical-v1" and asset.get("layout") == layout for asset in assets)
            if not native:
                gaps.append(make_request("background", place=place, orientation="portrait", layout=layout))
    return gaps


def write_gap_reports(gaps: list[dict[str, Any]], output_json: Path, output_md: Path, requests_dir: Path, catalog_sha: str) -> None:
    result = {
        "schemaVersion": "1.0",
        "catalogSha256": catalog_sha,
        "summary": {
            "total": len(gaps),
            "episodeRequired": sum(gap["severity"] == "episode-required" for gap in gaps),
            "catalogGaps": sum(gap["severity"] == "catalog-gap" for gap in gaps),
        },
        "gaps": gaps,
    }
    dump_json(result, output_json)
    request_root = requests_dir / catalog_sha[:12]
    for gap in gaps:
        dump_json(gap, request_root / f"{gap['requestId']}.json")
    lines = ["# Media faltante MAAS", "", f"Catálogo: `{catalog_sha}`", "", f"Total: {len(gaps)}", "", "| Prioridad | ID | Archivo sugerido | Bloquea publicación |", "|---|---|---|---|"]
    for gap in gaps:
        lines.append(f"| {gap['severity']} | `{gap['requestId']}` | `{gap['suggestedFilename']}` | {'sí' if gap['blockingPublication'] else 'no'} |")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def command_report_gaps(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    gaps = catalog_gaps(catalog)
    sha = file_sha(args.catalog)
    write_gap_reports(gaps, args.output_json, args.output_md, args.requests_dir, sha)
    print(json.dumps({"gaps": len(gaps), "output": str(args.output_json)}, ensure_ascii=False, sort_keys=True))
    return 0


def choose_asset(candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    return sorted(candidates, key=lambda item: (-int(item.get("qualityRank", 0)), item["id"]))[0] if candidates else None


def command_resolve(args: argparse.Namespace) -> int:
    manifest = load_json(args.manifest)
    catalog = load_json(args.catalog)
    presentation = load_json(args.presentation)
    emotion_policy = load_json(args.emotions)
    assets = catalog.get("assets", [])
    by_id = {asset["id"]: asset for asset in assets}
    selected: set[str] = set()
    episode_gaps: list[dict[str, Any]] = []
    source_aliases = {str(key).casefold(): value for key, value in emotion_policy.get("sourceAliases", {}).items()}
    fallbacks = emotion_policy.get("fallbacks", {})
    cue_places: dict[str, str] = {}
    for scene in manifest.get("timeline", []):
        if scene.get("type") == "scene":
            for cue_id in scene.get("cueIds", []):
                cue_places[str(cue_id)] = str(scene.get("place", ""))
    publication_errors: list[str] = []

    for cue in manifest.get("timeline", []):
        for effect in cue.get("effects", []):
            for input_name, reference in effect.get("inputs", {}).items():
                asset_id = str(reference.get("assetId", ""))
                asset = by_id.get(asset_id)
                if not asset:
                    raise ValueError(f"E_EFFECT_INPUT_ASSET: {cue.get('id')} {input_name} referencia {asset_id} ausente")
                if asset.get("allowedForPublish") is not True and args.mode == "publication":
                    raise ValueError(f"E_LICENSE: input {asset_id} no autorizado para publicar")
                selected.add(asset_id)
        if cue.get("type") in {"scene", "transition", "ending", "advice"}:
            continue
        speaker = str(cue.get("speaker", ""))
        character = presentation.get("characters", {}).get(speaker)
        if not character:
            raise ValueError(f"E_CHARACTER: sin presentación para {speaker}")
        position = character["position"]
        place = str(cue.get("place") or cue_places.get(str(cue.get("id", "")), ""))
        place_id = slug(place)
        source_emotion = str(cue.get("sourceEmotion", "")).strip().casefold()
        emotion = str(source_aliases.get(source_emotion, cue.get("emotion", "happy"))).casefold()
        sprite = choose_asset([asset for asset in assets if asset.get("type") == "sprite" and asset.get("characterId") == speaker and asset.get("emotion") == emotion and asset.get("gaze") == "left"])
        fallback_applied = None
        if sprite is None and args.mode == "preview":
            for fallback in fallbacks.get(emotion, ["happy"]):
                sprite = choose_asset([asset for asset in assets if asset.get("type") == "sprite" and asset.get("characterId") == speaker and asset.get("emotion") == fallback and asset.get("gaze") == "left"])
                if sprite:
                    fallback_applied = {"requested": emotion, "resolved": fallback}
                    break
        layout = "character-left" if position == "izquierda" else "character-right"
        background = choose_asset([asset for asset in assets if asset.get("type") == "background" and asset.get("placeId") == place_id and asset.get("orientation") == "landscape" and asset.get("layout") == layout])
        missing = []
        if sprite is None:
            missing.append(make_request("sprite", character=speaker, emotion=emotion, required_for=[str(cue.get("id"))], blocking=True))
        if background is None:
            missing.append(make_request("background", place=place_id, orientation="landscape", layout=layout, required_for=[str(cue.get("id"))], blocking=True))
        episode_gaps.extend(missing)
        if missing or (fallback_applied and args.mode == "publication"):
            publication_errors.append(str(cue.get("id")))
            continue
        if sprite and background:
            selected.update((sprite["id"], background["id"]))
            cue["speakerPosition"] = position
            cue["speakerLabel"] = character["label"]
            cue["media"] = {
                "spriteAssetId": sprite["id"],
                "backgroundAssetId": background["id"],
                "mirrorX": position == "izquierda",
                "layout": f"landscape-{layout}",
                "fallbackApplied": fallback_applied,
            }
    manifest["assets"] = sorted(selected)
    manifest["assetUrls"] = {asset_id: f"/assets/{by_id[asset_id]['sha256']}{Path(by_id[asset_id]['sourcePath']).suffix.casefold()}" for asset_id in sorted(selected)}
    dump_json(manifest, args.output)
    gap_result = {"schemaVersion": "1.0", "episodeId": manifest.get("episodeId"), "mode": args.mode, "gaps": episode_gaps}
    dump_json(gap_result, args.episode_gaps)
    if publication_errors:
        raise ValueError(f"E_ASSET: media exacta ausente para {', '.join(publication_errors)}; consulta {args.episode_gaps}")
    print(json.dumps({"assets": len(selected), "episodeGaps": len(episode_gaps), "output": str(args.output)}, ensure_ascii=False, sort_keys=True))
    return 0


def command_stage(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    manifest = load_json(args.manifest)
    root = args.root.resolve()
    output = args.output.resolve()
    by_id = {asset["id"]: asset for asset in catalog.get("assets", [])}
    staged = 0
    for asset_id in manifest.get("assets", []):
        asset = by_id.get(asset_id)
        if not asset:
            raise ValueError(f"E_ASSET: {asset_id} no está en catálogo")
        if asset.get("allowedForPublish") is not True:
            raise ValueError(f"E_LICENSE: {asset_id}")
        source = (root / asset["sourcePath"]).resolve()
        if root not in source.parents or file_sha(source) != asset["sha256"]:
            raise ValueError(f"E_ASSET: fuente o hash inválido para {asset_id}")
        target = output / f"{asset['sha256']}{source.suffix.casefold()}"
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if file_sha(target) != asset["sha256"]:
                raise ValueError(f"E_ASSET: no se sobrescribe {target}")
        else:
            shutil.copy2(source, target)
        staged += 1
    print(json.dumps({"output": str(output), "staged": staged}, ensure_ascii=False, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    catalog = sub.add_parser("catalog")
    catalog.add_argument("raw_manifest", type=Path)
    catalog.add_argument("--root", type=Path, required=True)
    catalog.add_argument("--output", type=Path, required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("catalog", type=Path)
    validate.add_argument("--root", type=Path, required=True)
    gaps = sub.add_parser("report-gaps")
    gaps.add_argument("catalog", type=Path)
    gaps.add_argument("--output-json", type=Path, required=True)
    gaps.add_argument("--output-md", type=Path, required=True)
    gaps.add_argument("--requests-dir", type=Path, required=True)
    resolve = sub.add_parser("resolve")
    resolve.add_argument("manifest", type=Path)
    resolve.add_argument("catalog", type=Path)
    resolve.add_argument("presentation", type=Path)
    resolve.add_argument("emotions", type=Path)
    resolve.add_argument("--mode", choices=("preview", "publication"), default="preview")
    resolve.add_argument("--output", type=Path, required=True)
    resolve.add_argument("--episode-gaps", type=Path, required=True)
    stage = sub.add_parser("stage")
    stage.add_argument("catalog", type=Path)
    stage.add_argument("manifest", type=Path)
    stage.add_argument("--root", type=Path, required=True)
    stage.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return {
            "catalog": command_catalog,
            "validate": command_validate,
            "report-gaps": command_report_gaps,
            "resolve": command_resolve,
            "stage": command_stage,
        }[args.command](args)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
