#!/usr/bin/env python3
"""Convierte episode-gaps.json del resolver oficial en reporte Markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    lines = [f"# Huecos de media · {data.get('episodeId', 'episodio')}", "", f"Modo: `{data.get('mode', 'publication')}`", ""]
    gaps = data.get("gaps", [])
    if not gaps:
        lines.append("No hay huecos de media.")
    else:
        for gap in gaps:
            kind = gap.get("assetType") or gap.get("type", "asset")
            identifier = gap.get("characterId") or gap.get("placeId") or gap.get("suggestedPath") or "sin-id"
            required = ", ".join(gap.get("requiredFor", [])) or "sin cues"
            blocking = gap.get("blockingPublication", gap.get("blocking", True))
            suggested = gap.get("suggestedFilename") or gap.get("suggestedPath", "por definir")
            lines.extend([f"## {kind}: {identifier}", "", f"- Bloqueante: `{bool(blocking)}`", f"- Requerido por: {required}", f"- Ruta sugerida: `{suggested}`", ""])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"gaps": len(gaps), "output": str(args.output)}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
