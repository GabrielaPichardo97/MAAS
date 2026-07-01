#!/usr/bin/env python3
"""Copia el starter y herramientas hermanas a un directorio nuevo."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_tree_without_overwrite(source: Path, destination: Path) -> None:
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif target.exists():
            raise FileExistsError(f"No se sobrescribe: {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--force", action="store_true", help="Permite un directorio existente, sin sobrescribir archivos")
    args = parser.parse_args()
    skill = Path(__file__).resolve().parents[1]
    skills_root = skill.parent
    destination = args.destination.resolve()
    if destination.exists() and any(destination.iterdir()) and not args.force:
        print(f"Destino no vacío: {destination}")
        return 1
    destination.mkdir(parents=True, exist_ok=True)
    try:
        copy_tree_without_overwrite(skill / "assets" / "starter-repository", destination)
        schemas = skills_root / "definir-contratos-maas" / "assets" / "schemas"
        copy_tree_without_overwrite(schemas, destination / "schemas")
        scripts = {
            "validate_episode.py": skills_root / "definir-contratos-maas" / "scripts" / "validate_episode.py",
            "normalize_legacy_input.py": skills_root / "compilar-guion-maas" / "scripts" / "normalize_legacy_input.py",
            "compile_episode.py": skills_root / "compilar-guion-maas" / "scripts" / "compile_episode.py",
            "build_asset_manifest.py": skills_root / "migrar-insumos-maas" / "scripts" / "build_asset_manifest.py",
            "probe_media.py": skills_root / "migrar-insumos-maas" / "scripts" / "probe_media.py",
            "audit_assets.py": skills_root / "migrar-insumos-maas" / "scripts" / "audit_assets.py",
            "legacy_effect_math.py": skills_root / "reproducir-efectos-maas" / "scripts" / "legacy_effect_math.py",
            "build_audio_cues.py": skills_root / "sincronizar-audio-maas" / "scripts" / "build_audio_cues.py",
            "build_episode.py": skills_root / "empaquetar-episodio-maas" / "scripts" / "build_episode.py",
            "verify_bundle.py": skills_root / "empaquetar-episodio-maas" / "scripts" / "verify_bundle.py",
            "compare_frames.py": skills_root / "auditar-paridad-maas" / "scripts" / "compare_frames.py",
            "compare_timelines.py": skills_root / "auditar-paridad-maas" / "scripts" / "compare_timelines.py",
            "generate_audit_report.py": skills_root / "auditar-paridad-maas" / "scripts" / "generate_audit_report.py",
        }
        target_scripts = destination / "tools" / "scripts"
        target_scripts.mkdir(parents=True, exist_ok=True)
        for name, source in scripts.items():
            target = target_scripts / name
            if target.exists():
                raise FileExistsError(f"No se sobrescribe: {target}")
            shutil.copy2(source, target)
    except (OSError, FileExistsError) as exc:
        print(str(exc))
        return 1
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
