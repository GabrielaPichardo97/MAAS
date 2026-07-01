#!/usr/bin/env python3
"""Comprueba herramientas requeridas sin instalar ni modificar el sistema."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys


def version(command: list[str]) -> str | None:
    if not shutil.which(command[0]):
        return None
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() or result.stderr.strip()
    except (subprocess.SubprocessError, OSError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    report = {
        "python": platform.python_version(),
        "pythonOk": sys.version_info >= (3, 11),
        "node": version(["node", "--version"]),
        "npm": version(["npm", "--version"]),
        "git": version(["git", "--version"]),
        "ffprobeOptional": version(["ffprobe", "-version"]),
    }
    report["valid"] = bool(report["pythonOk"] and report["node"] and report["npm"] and report["git"])
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
