#!/usr/bin/env python3
"""Compara cues por ID y aplica límites de drift temporal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expected", type=Path)
    parser.add_argument("actual", type=Path)
    parser.add_argument("--visual-tolerance-ms", type=int, default=40)
    parser.add_argument("--audio-tolerance-ms", type=int, default=20)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    expected_data = json.loads(args.expected.read_text(encoding="utf-8"))
    actual_data = json.loads(args.actual.read_text(encoding="utf-8"))
    expected = {cue["id"]: cue for cue in expected_data.get("timeline", expected_data)}
    actual = {cue["id"]: cue for cue in actual_data.get("timeline", actual_data)}
    cases = []
    for cue_id in sorted(set(expected) | set(actual)):
        left, right = expected.get(cue_id), actual.get(cue_id)
        if left is None or right is None:
            cases.append({"id": cue_id, "pass": False, "reason": "cue ausente", "expected": left is not None, "actual": right is not None})
            continue
        start_drift = abs(int(left["startMs"]) - int(right["startMs"]))
        duration_drift = abs(int(left["durationMs"]) - int(right["durationMs"]))
        tolerance = args.audio_tolerance_ms if left.get("audio") else args.visual_tolerance_ms
        cases.append({"id": cue_id, "pass": max(start_drift, duration_drift) <= tolerance, "startDriftMs": start_drift, "durationDriftMs": duration_drift, "toleranceMs": tolerance})
    report = {"valid": all(case["pass"] for case in cases), "cases": cases}
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
