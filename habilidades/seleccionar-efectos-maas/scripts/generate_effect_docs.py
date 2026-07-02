#!/usr/bin/env python3
"""Generate the Spanish catalog reference from the canonical JSON catalog."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(catalog: dict) -> str:
    lines = [
        "# Catálogo canonical-v2 de efectos MAAS",
        "",
        "Fuente de verdad: `effects-catalog.json`. Los IDs son exactos y no resuelven versiones implícitas.",
        "",
        "## Niveles de soporte",
        "",
        "- `native`: ejecución directa en MAAS web.",
        "- `approximation`: aproximación 2.5D o visual documentada.",
        "- `input-assisted`: requiere material o metadata declarada.",
        "- `preprocessed`: consume un artefacto calculado fuera del navegador.",
    ]
    for family in catalog["families"]:
        lines.extend(["", f"## {family}", ""])
        for effect in (item for item in catalog["effects"] if item["family"] == family):
            lines.extend([
                f"### {effect['displayName']}", "",
                f"- **ID:** `{effect['id']}`",
                f"- **Qué hace:** {effect['description']}",
                f"- **Mejor momento:** {effect['bestMoment']}",
                f"- **Evitar:** {'; '.join(effect['avoidWhen'])}.",
                f"- **Soporte:** `{effect['supportLevel']}` · costo `{effect['renderCost']}` · móvil `{'sí' if effect['mobileSafe'] else 'no'}`.",
                f"- **Movimiento reducido:** `{effect['reducedMotion']}` · riesgo fotosensible `{effect['photosensitivityRisk']}`.",
                f"- **Requisitos:** {', '.join(f'`{x}`' for x in effect['requirements']) if effect['requirements'] else 'ninguno'}.",
                f"- **Fallback:** `{effect['fallbackId']}`." if effect.get("fallbackId") else "- **Fallback:** sin sustitución automática.",
                "- **Parámetros:**",
            ])
            for name, spec in effect["parameters"].items():
                domain = f"{spec['min']}..{spec['max']}" if "min" in spec else ", ".join(spec.get("values", [])) or spec["type"]
                lines.append(f"  - `{name}` ({spec['type']}, {domain}); default `{spec['default']}`.")
    return "\n".join(lines) + "\n"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=root / "references" / "effects-catalog.json")
    parser.add_argument("--output", type=Path, default=root / "references" / "effects-catalog.md")
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    args.output.write_text(render(catalog), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
