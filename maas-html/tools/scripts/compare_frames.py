#!/usr/bin/env python3
"""Calcula MAE y SSIM global entre dos frames usando Pillow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def metrics(expected: Path, actual: Path) -> dict:
    try:
        from PIL import Image, ImageChops, ImageStat  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Pillow es requerido para comparar frames") from exc
    with Image.open(expected) as left_image, Image.open(actual) as right_image:
        left = left_image.convert("L")
        right = right_image.convert("L")
        if left.size != right.size:
            return {"sameSize": False, "expectedSize": left.size, "actualSize": right.size, "mae": None, "ssim": None}
        diff = ImageChops.difference(left, right)
        mae = ImageStat.Stat(diff).mean[0] / 255.0
        left_stat, right_stat = ImageStat.Stat(left), ImageStat.Stat(right)
        mu_x, mu_y = left_stat.mean[0], right_stat.mean[0]
        var_x, var_y = left_stat.var[0], right_stat.var[0]
        pixels_x, pixels_y = list(left.getdata()), list(right.getdata())
        covariance = sum((x - mu_x) * (y - mu_y) for x, y in zip(pixels_x, pixels_y)) / max(1, len(pixels_x) - 1)
        c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
        ssim = ((2 * mu_x * mu_y + c1) * (2 * covariance + c2)) / ((mu_x**2 + mu_y**2 + c1) * (var_x + var_y + c2))
        return {"sameSize": True, "width": left.width, "height": left.height, "mae": mae, "ssim": ssim}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expected", type=Path)
    parser.add_argument("actual", type=Path)
    parser.add_argument("--minimum-ssim", type=float, default=0.97)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = metrics(args.expected, args.actual)
    except (OSError, RuntimeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    result["minimumSsim"] = args.minimum_ssim
    result["valid"] = bool(result["sameSize"] and result["ssim"] is not None and result["ssim"] >= args.minimum_ssim)
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
