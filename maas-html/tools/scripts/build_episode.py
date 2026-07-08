#!/usr/bin/env python3
"""Construye una carpeta estática de episodio sin llamadas de red."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import time
from pathlib import Path

from episode_contract import build_webvtt

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_join(root: Path, relative: str) -> Path:
    if "://" in relative or Path(relative).is_absolute():
        raise ValueError(f"E_ASSET: ruta no local {relative}")
    target = (root / relative).resolve()
    if root.resolve() not in target.parents and target != root.resolve():
        raise ValueError(f"E_ASSET: ruta fuera de raíz {relative}")
    return target


def copy_new(source: Path, target: Path) -> None:
    if target.exists():
        if source.is_file() and sha256(source) == sha256(target):
            return
        raise FileExistsError(f"No se sobrescribe {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--player-dist", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--asset-manifest", type=Path)
    parser.add_argument("--asset-root", type=Path)
    parser.add_argument("--media-catalog", type=Path, help="Catálogo canónico para verificar assets ya incluidos por Vite")
    args = parser.parse_args()
    started = time.perf_counter()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        episode_id = str(manifest["episodeId"])
        if not ID_RE.fullmatch(episode_id):
            raise ValueError("E_SCHEMA: episodeId no es seguro para ruta")
        player_dist = args.player_dist.resolve()
        output = args.output.resolve()
        if not (player_dist / "index.html").is_file():
            raise ValueError("E_ASSET: player-dist no contiene index.html")
        for source in sorted(player_dist.rglob("*")):
            if source.is_file():
                copy_new(source, output / source.relative_to(player_dist))
        episode_dir = output / "episodes" / episode_id
        copy_new(player_dist / "index.html", episode_dir / "index.html")
        episode_dir.mkdir(parents=True, exist_ok=True)
        manifest_target = episode_dir / "episode.manifest.json"
        payload = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if manifest_target.exists():
            if manifest_target.read_text(encoding="utf-8") != payload:
                raise FileExistsError(f"No se sobrescribe {manifest_target}")
        else:
            manifest_target.write_text(payload, encoding="utf-8", newline="\n")
        for track in manifest.get("subtitleTracks", []):
            if track.get("format") != "webvtt":
                continue
            url = str(track.get("url", ""))
            if not url.startswith(f"/episodes/{episode_id}/") or "://" in url or ".." in url:
                raise ValueError(f"E_SUBTITLE: URL insegura {url}")
            track_target = safe_join(output, url.removeprefix("/"))
            track_payload = build_webvtt(manifest.get("subtitles", []))
            if track.get("sha256") and hashlib.sha256(track_payload.encode("utf-8")).hexdigest() != track.get("sha256"):
                raise ValueError(f"E_SUBTITLE: hash distinto para {url}")
            if track_target.exists():
                if track_target.read_text(encoding="utf-8") != track_payload:
                    raise FileExistsError(f"No se sobrescribe {track_target}")
            else:
                track_target.parent.mkdir(parents=True, exist_ok=True)
                track_target.write_text(track_payload, encoding="utf-8", newline="\n")
        copied_assets = 0
        requested = set(manifest.get("assets", []))
        asset_urls = manifest.get("assetUrls", {})
        if requested or asset_urls:
            if requested != set(asset_urls):
                raise ValueError("E_ASSET: assets y assetUrls no coinciden")
            catalog_by_id = {}
            if args.media_catalog:
                catalog_by_id = {asset["id"]: asset for asset in json.loads(args.media_catalog.read_text(encoding="utf-8"))["assets"]}
            for asset_id in sorted(requested):
                url = str(asset_urls[asset_id])
                if not url.startswith("/assets/") or "://" in url or ".." in url:
                    raise ValueError(f"E_ASSET: URL insegura para {asset_id}")
                packaged = safe_join(output, url.removeprefix("/"))
                if not packaged.is_file():
                    raise ValueError(f"E_ASSET: falta asset empaquetado {asset_id}")
                if catalog_by_id:
                    catalog_asset = catalog_by_id.get(asset_id)
                    if not catalog_asset:
                        raise ValueError(f"E_ASSET: {asset_id} ausente del catálogo")
                    if catalog_asset.get("allowedForPublish") is not True:
                        raise ValueError(f"E_LICENSE: {asset_id}")
                    if sha256(packaged) != catalog_asset.get("sha256"):
                        raise ValueError(f"E_ASSET: hash distinto para {asset_id}")
                copied_assets += 1
        if args.asset_manifest or args.asset_root:
            if not (args.asset_manifest and args.asset_root):
                raise ValueError("E_ASSET: proporciona asset-manifest y asset-root juntos")
            assets = json.loads(args.asset_manifest.read_text(encoding="utf-8"))["assets"]
            requested = set(manifest.get("assets", []))
            by_id = {asset["id"]: asset for asset in assets}
            for asset_id in sorted(requested):
                asset = by_id.get(asset_id)
                if not asset:
                    raise ValueError(f"E_ASSET: {asset_id} ausente")
                if asset.get("allowedForPublish") is not True:
                    raise ValueError(f"E_LICENSE: {asset_id}")
                source = safe_join(args.asset_root.resolve(), asset["path"])
                if sha256(source) != asset["sha256"]:
                    raise ValueError(f"E_ASSET: hash distinto para {asset_id}")
                target = output / "assets" / f"{asset['sha256']}{source.suffix.casefold()}"
                copy_new(source, target)
                if not asset_urls:
                    copied_assets += 1
        report = {
            "schemaVersion": "1.0", "episodeId": episode_id, "profile": manifest.get("profile"),
            "inputSha256": sha256(args.manifest), "manifestSha256": hashlib.sha256(payload.encode()).hexdigest(),
            "assetCount": copied_assets, "warningCount": len(manifest.get("warnings", [])),
            "timingsMs": {"total": round((time.perf_counter() - started) * 1000)},
        }
        report_path = episode_dir / "build-report.json"
        if report_path.exists():
            raise FileExistsError(f"No se sobrescribe {report_path}")
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
