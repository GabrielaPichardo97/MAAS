#!/usr/bin/env python3
"""Registra una aprobación explícita en una dirección MAAS propuesta."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--approved-by", required=True)
    parser.add_argument("--approved-at")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    if data.get("approval", {}).get("status") == "rejected":
        raise ValueError("E_APPROVAL: una propuesta rechazada debe revisarse antes de aprobarse")
    approved_at = args.approved_at or dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    data["approval"] = {"status": "approved", "approvedBy": args.approved_by, "approvedAt": approved_at}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"approvedAt": approved_at, "approvedBy": args.approved_by, "output": str(args.output)}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
