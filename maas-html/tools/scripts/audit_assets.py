#!/usr/bin/env python3
"""Audita integridad, duplicados, naming y permiso de publicación."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--publication", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    diagnostics = []
    by_hash: dict[str, list[str]] = defaultdict(list)
    ids: set[str] = set()
    for asset in data.get("assets", []):
        asset_id = asset.get("id", "")
        if asset_id in ids:
            diagnostics.append({"code": "E_ASSET", "severity": "error", "assetId": asset_id, "message": "ID duplicado"})
        ids.add(asset_id)
        by_hash[str(asset.get("sha256"))].append(asset_id)
        name = str(asset.get("path", "")).casefold()
        if any(token in name for token in ("angy", "condused", "correct_", " (2)")):
            diagnostics.append({"code": "W_ASSET_NAMING", "severity": "warning", "assetId": asset_id, "message": "Naming legado irregular"})
        if not asset.get("license"):
            diagnostics.append({"code": "W_LICENSE_UNKNOWN", "severity": "warning", "assetId": asset_id, "message": "Licencia sin documentar"})
        if args.publication and asset.get("allowedForPublish") is not True:
            diagnostics.append({"code": "E_LICENSE", "severity": "error", "assetId": asset_id, "message": "Asset no autorizado para publicación"})
    for sha, asset_ids in by_hash.items():
        if sha and len(asset_ids) > 1:
            diagnostics.append({"code": "W_DUPLICATE_CONTENT", "severity": "warning", "sha256": sha, "assetIds": asset_ids, "message": "Contenido binario duplicado"})
    report = {"valid": not any(d["severity"] == "error" for d in diagnostics), "assetCount": len(data.get("assets", [])), "diagnostics": diagnostics}
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
