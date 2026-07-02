#!/usr/bin/env python3
"""Obtiene metadata multimedia sin convertir ni modificar el archivo."""

from __future__ import annotations

import argparse
import json
import mimetypes
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any


def probe(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "mimeType": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        "width": None,
        "height": None,
        "durationMs": None,
    }
    try:
        from PIL import Image  # type: ignore
        if result["mimeType"].startswith("image/"):
            with Image.open(path) as image:
                result["width"], result["height"] = image.size
    except (ImportError, OSError):
        pass
    if path.suffix.casefold() == ".wav":
        try:
            with wave.open(str(path), "rb") as audio:
                result["durationMs"] = round(audio.getnframes() / audio.getframerate() * 1000)
        except (OSError, wave.Error, ZeroDivisionError):
            pass
    try:
        from mutagen import File as MutagenFile  # type: ignore
        if result["durationMs"] is None and result["mimeType"].startswith(("audio/", "video/")):
            media = MutagenFile(path)
            length = getattr(getattr(media, "info", None), "length", None)
            if length is not None:
                result["durationMs"] = round(float(length) * 1000)
    except (ImportError, OSError, ValueError):
        pass
    if result["mimeType"].startswith(("audio/", "video/")) and shutil.which("ffprobe"):
        try:
            completed = subprocess.run(
                ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            payload = json.loads(completed.stdout)
            for stream in payload.get("streams", []):
                if stream.get("codec_type") == "video":
                    result["width"] = int(stream["width"]) if stream.get("width") else result["width"]
                    result["height"] = int(stream["height"]) if stream.get("height") else result["height"]
                    break
            raw_duration = payload.get("format", {}).get("duration")
            if raw_duration is not None:
                result["durationMs"] = round(float(raw_duration) * 1000)
        except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.SubprocessError):
            pass
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    if not args.path.is_file():
        print(json.dumps({"error": "E_ASSET", "message": "Archivo inexistente"}, ensure_ascii=False))
        return 1
    print(json.dumps({"path": args.path.as_posix(), **probe(args.path)}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
