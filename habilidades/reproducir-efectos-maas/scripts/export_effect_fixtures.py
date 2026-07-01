#!/usr/bin/env python3
"""Genera fixtures exhaustivos de efectos legacy-v1."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("legacy_effect_math", HERE / "legacy_effect_math.py")
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def build() -> dict:
    fixtures = []
    for code in ("ES", "ZI", "ZO", "PA-I", "PA-D", "TI-A", "TI-B", "PP"):
        for intensity in (1.0, 1.2, 1.5, 2.5):
            for position in ("izquierda", "derecha"):
                for duration in (2.0, 5.0, 10.0):
                    samples = []
                    invalid = None
                    for time_seconds in (0.0, duration / 2.0, duration):
                        try:
                            value = module.transform(code, intensity, position, time_seconds)
                            samples.append({"timeSeconds": time_seconds, **module.asdict(value)})
                        except ValueError as exc:
                            invalid = str(exc)
                            break
                    fixtures.append({"code": code, "intensity": intensity, "position": position, "durationSeconds": duration, "samples": samples, "invalid": invalid})
    return {"schemaVersion": "1.0", "profile": "legacy-v1", "fps": 25, "fixtures": fixtures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
