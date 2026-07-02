#!/usr/bin/env python3
"""Consolida reportes JSON y produce evidencia JSON/HTML segura."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--html-output", type=Path, required=True)
    args = parser.parse_args()
    entries = []
    for path in args.reports:
        data = json.loads(path.read_text(encoding="utf-8"))
        entries.append({"path": path.as_posix(), "valid": bool(data.get("valid")), "data": data})
    summary = {"valid": all(entry["valid"] for entry in entries), "passed": sum(entry["valid"] for entry in entries), "total": len(entries), "reports": entries}
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    rows = "".join(f"<tr><td>{html.escape(entry['path'])}</td><td>{'PASS' if entry['valid'] else 'FAIL'}</td><td><pre>{html.escape(json.dumps(entry['data'], ensure_ascii=False, indent=2))}</pre></td></tr>" for entry in entries)
    document = f"<!doctype html><html lang='es'><meta charset='utf-8'><title>Auditoría MAAS</title><style>body{{font-family:system-ui}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #999;padding:.5rem;vertical-align:top}}pre{{white-space:pre-wrap}}</style><h1>Auditoría MAAS: {'PASS' if summary['valid'] else 'FAIL'}</h1><p>{summary['passed']}/{summary['total']} reportes válidos.</p><table><thead><tr><th>Reporte</th><th>Estado</th><th>Detalle</th></tr></thead><tbody>{rows}</tbody></table></html>"
    args.html_output.parent.mkdir(parents=True, exist_ok=True)
    args.html_output.write_text(document, encoding="utf-8", newline="\n")
    print(json.dumps({"valid": summary["valid"], "json": str(args.json_output), "html": str(args.html_output)}, ensure_ascii=False))
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
