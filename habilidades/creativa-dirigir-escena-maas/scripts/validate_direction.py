#!/usr/bin/env python3
"""Valida fidelidad, aprobación y stacks canonical-v2 de una dirección."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROLES = {"dominant", "support", "finish"}


def parameter_errors(name: str, value: object, spec: dict) -> list[str]:
    kind = spec.get("type")
    errors = []
    if kind == "integer" and (isinstance(value, bool) or not isinstance(value, int)):
        errors.append(f"{name} exige integer")
    elif kind == "number" and (isinstance(value, bool) or not isinstance(value, (int, float))):
        errors.append(f"{name} exige number")
    elif kind == "boolean" and not isinstance(value, bool):
        errors.append(f"{name} exige boolean")
    elif kind == "enum" and value not in spec.get("values", []):
        errors.append(f"{name} fuera de enum")
    elif kind == "color" and (not isinstance(value, str) or len(value) != 7 or not value.startswith("#")):
        errors.append(f"{name} exige #RRGGBB")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "min" in spec and value < spec["min"]:
            errors.append(f"{name} menor que {spec['min']}")
        if "max" in spec and value > spec["max"]:
            errors.append(f"{name} mayor que {spec['max']}")
    return errors


def validate(direction: dict, adaptation: dict, adaptation_sha: str, catalog: dict) -> list[str]:
    errors: list[str] = []
    if direction.get("schemaVersion") != "1.0":
        errors.append("E_SCHEMA: schemaVersion debe ser 1.0")
    if direction.get("adaptationSha256") != adaptation_sha:
        errors.append("E_FIDELITY: adaptationSha256 no coincide")
    expected = {beat["id"]: beat for scene in adaptation.get("scenes", []) for beat in scene.get("beats", [])}
    actual = {beat.get("id"): beat for scene in direction.get("scenes", []) for beat in scene.get("beats", [])}
    if set(expected) != set(actual):
        errors.append("E_FIDELITY: el conjunto de beats cambió")
    effects_by_id = {item["id"]: item for item in catalog.get("effects", [])}
    for beat_id, source in expected.items():
        beat = actual.get(beat_id, {})
        for field in ("speaker", "characterId", "verbatimText"):
            if beat.get(field) != source.get(field):
                errors.append(f"E_FIDELITY: {field} cambió en {beat_id}")
        roles: set[str] = set()
        if len(beat.get("effects", [])) > 3:
            errors.append(f"E_EFFECT_STACK: más de tres efectos en {beat_id}")
        available = set(beat.get("effectContext", {}).get("availableInputs", []))
        reduced = bool(beat.get("effectContext", {}).get("reducedMotion"))
        for effect in beat.get("effects", []):
            effect_id, role = effect.get("id"), effect.get("role")
            entry = effects_by_id.get(effect_id)
            if not entry:
                errors.append(f"E_EFFECT_ID: {effect_id} en {beat_id}")
                continue
            if role not in ROLES or role in roles:
                errors.append(f"E_EFFECT_STACK: rol inválido o duplicado {role} en {beat_id}")
            roles.add(role)
            intensity = effect.get("intensity")
            if isinstance(intensity, bool) or not isinstance(intensity, (int, float)) or not 0 <= intensity <= 1:
                errors.append(f"E_EFFECT_PARAM: intensity en {beat_id}")
            params = effect.get("params", {})
            allowed = set(entry.get("parameters", {})) | set(entry.get("requirements", []))
            if set(params) - allowed:
                errors.append(f"E_EFFECT_PARAM: parámetros desconocidos en {beat_id}")
            requirements = set(entry.get("requirements", []))
            missing_inputs = requirements - available
            missing_values = requirements - set(params)
            if missing_inputs:
                errors.append(f"E_EFFECT_REQUIREMENT: inputs no disponibles {sorted(missing_inputs)} en {beat_id}")
            if missing_values:
                errors.append(f"E_EFFECT_REQUIREMENT: faltan valores {sorted(missing_values)} en {beat_id}")
            for name, value in params.items():
                if name in entry.get("parameters", {}):
                    errors.extend(f"E_EFFECT_PARAM: {message} en {beat_id}" for message in parameter_errors(name, value, entry["parameters"][name]))
            if reduced and entry.get("reducedMotion") == "disable":
                errors.append(f"E_EFFECT_SAFETY: {effect_id} se desactiva con movimiento reducido")
    approval = direction.get("approval", {})
    if approval.get("status") not in {"proposed", "approved", "rejected"}:
        errors.append("E_APPROVAL: status inválido")
    if approval.get("status") == "approved" and (not approval.get("approvedBy") or not approval.get("approvedAt")):
        errors.append("E_APPROVAL: faltan approvedBy/approvedAt")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direction", type=Path)
    parser.add_argument("--adaptation", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    args = parser.parse_args()
    try:
        adaptation_raw = args.adaptation.read_bytes()
        direction = json.loads(args.direction.read_text(encoding="utf-8-sig"))
        adaptation = json.loads(adaptation_raw.decode("utf-8-sig"))
        catalog = json.loads(args.catalog.read_text(encoding="utf-8-sig"))
        errors = validate(direction, adaptation, hashlib.sha256(adaptation_raw).hexdigest(), catalog)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, KeyError) as exc:
        errors = [f"E_SCHEMA: {exc}"]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
