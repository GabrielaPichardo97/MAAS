#!/usr/bin/env python3
"""Oráculo numérico de transformaciones de cámara legacy-v1."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Transform:
    scale: float
    x_fraction: float
    y_fraction: float


def transform(code: str, intensity: float, position: str, time_seconds: float) -> Transform:
    if intensity <= 0:
        intensity = 1.0
    if time_seconds < 0:
        raise ValueError("time_seconds no puede ser negativo")
    code = code.upper()
    base = 0.05
    sign_x = -1.0 if position.casefold() == "izquierda" else 1.0
    if code == "ES":
        result = Transform(1.0, 0.0, 0.0)
    elif code in {"ZI", "ZO"}:
        zoom = base * intensity * time_seconds
        result = Transform(1.0 + zoom if code == "ZI" else 1.0 - zoom, sign_x * base * intensity * time_seconds / 2.0, 0.0)
    elif code in {"PA-I", "PA-D"}:
        result = Transform(1.0 + base * intensity * time_seconds / 2.0, sign_x * base * intensity * time_seconds / 4.0, 0.0)
    elif code == "TI-A":
        result = Transform(1.0, 0.0, base * intensity * time_seconds)
    elif code == "TI-B":
        result = Transform(1.0, 0.0, -base * intensity * time_seconds)
    elif code.startswith("PP"):
        result = Transform(1.0 + base * intensity * time_seconds, 0.0, 0.0)
    else:
        result = Transform(1.0, 0.0, 0.0)
    if result.scale <= 0:
        raise ValueError(f"E_EFFECT: escala no positiva ({result.scale})")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("code")
    parser.add_argument("--intensity", type=float, default=1.0)
    parser.add_argument("--position", choices=("izquierda", "derecha"), default="izquierda")
    parser.add_argument("--time", type=float, default=0.0)
    args = parser.parse_args()
    print(json.dumps(asdict(transform(args.code, args.intensity, args.position, args.time)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
