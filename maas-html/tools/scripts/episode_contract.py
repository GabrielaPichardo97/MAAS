#!/usr/bin/env python3
"""Helpers for MAAS HTML-first manifest fields."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

TOOLCHAIN_VERSION = "0.1.0"
SUBTITLE_TYPES = {"dialogue", "sfx", "transition", "advice"}
ACTION_TYPES = {"pause", "seek", "openPanel", "openUrl", "emit"}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def language_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "und"


def timestamp(ms: int) -> str:
    total = max(0, int(ms))
    hours, rem = divmod(total, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"


def subtitle_kind(cue_type: str) -> str:
    return {"sfx": "sound", "transition": "transition", "advice": "advice"}.get(cue_type, "dialogue")


def clean_vtt_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").replace("-->", "->").strip()


def build_subtitles(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    subtitles: list[dict[str, Any]] = []
    for cue in sorted(manifest.get("timeline", []), key=lambda item: (int(item.get("startMs", 0)), str(item.get("id", "")))):
        cue_type = str(cue.get("type", ""))
        text = clean_vtt_text(str(cue.get("text", "")))
        duration = int(cue.get("durationMs", 0))
        if cue_type not in SUBTITLE_TYPES or not text or duration <= 0:
            continue
        start = int(cue.get("startMs", 0))
        speaker = str(cue.get("speakerLabel") or cue.get("speakerAlias") or cue.get("speaker") or "")
        subtitles.append({
            "id": f"subtitle-{len(subtitles) + 1:04d}",
            "cueId": str(cue["id"]),
            "startMs": start,
            "endMs": start + duration,
            "speakerLabel": speaker,
            "text": text,
            "kind": subtitle_kind(cue_type),
        })
    return subtitles


def build_webvtt(subtitles: list[dict[str, Any]]) -> str:
    blocks = ["WEBVTT", ""]
    for subtitle in subtitles:
        speaker = str(subtitle.get("speakerLabel", "")).strip()
        text = clean_vtt_text(str(subtitle["text"]))
        payload = f"{speaker}: {text}" if speaker else text
        blocks.extend([
            str(subtitle["id"]),
            f"{timestamp(int(subtitle['startMs']))} --> {timestamp(int(subtitle['endMs']))}",
            payload,
            "",
        ])
    return "\n".join(blocks)


def validate_action(action: dict[str, Any], interaction_id: str) -> dict[str, Any]:
    action_type = str(action.get("type", ""))
    if action_type not in ACTION_TYPES:
        raise ValueError(f"E_INTERACTION: accion invalida en {interaction_id}")
    result: dict[str, Any] = {"type": action_type}
    if action_type == "seek":
        position = action.get("positionMs")
        if isinstance(position, bool) or not isinstance(position, int) or position < 0:
            raise ValueError(f"E_INTERACTION: seek exige positionMs entero en {interaction_id}")
        result["positionMs"] = position
    elif action_type == "openPanel":
        panel_id = str(action.get("panelId", ""))
        if not ID_RE.fullmatch(panel_id):
            raise ValueError(f"E_INTERACTION: panelId invalido en {interaction_id}")
        result["panelId"] = panel_id
    elif action_type == "openUrl":
        url = str(action.get("url", ""))
        if not url.startswith("/") or url.startswith("//") or ".." in url or "://" in url:
            raise ValueError(f"E_INTERACTION: openUrl debe ser same-origin absoluto en {interaction_id}")
        result["url"] = url
    elif action_type == "emit":
        event = str(action.get("event", ""))
        if not ID_RE.fullmatch(event):
            raise ValueError(f"E_INTERACTION: event invalido en {interaction_id}")
        detail = action.get("detail", {})
        if not isinstance(detail, dict):
            raise ValueError(f"E_INTERACTION: detail debe ser objeto en {interaction_id}")
        result["event"] = event
        result["detail"] = detail
    return result


def normalize_target(target: Any, interaction_id: str) -> dict[str, float] | None:
    if target is None:
        return None
    if not isinstance(target, dict):
        raise ValueError(f"E_INTERACTION: target debe ser objeto en {interaction_id}")
    out: dict[str, float] = {}
    for key in ("x", "y", "width", "height"):
        value = target.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"E_INTERACTION: target.{key} invalido en {interaction_id}")
        if value < 0 or value > 1:
            raise ValueError(f"E_INTERACTION: target.{key} fuera de 0..1 en {interaction_id}")
        out[key] = float(value)
    if out["width"] <= 0 or out["height"] <= 0 or out["x"] + out["width"] > 1 or out["y"] + out["height"] > 1:
        raise ValueError(f"E_INTERACTION: target fuera del stage en {interaction_id}")
    return out


def normalize_interactions(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    duration = int(manifest.get("durationMs", 0))
    for item in manifest.get("interactions", []):
        if not isinstance(item, dict):
            raise ValueError("E_INTERACTION: cada interaccion debe ser objeto")
        interaction_id = str(item.get("id", ""))
        if not ID_RE.fullmatch(interaction_id):
            raise ValueError(f"E_INTERACTION: id invalido {interaction_id!r}")
        kind = str(item.get("type", ""))
        if kind not in {"button", "hotspot"}:
            raise ValueError(f"E_INTERACTION: type invalido en {interaction_id}")
        start = item.get("startMs")
        item_duration = item.get("durationMs")
        if isinstance(start, bool) or not isinstance(start, int) or start < 0:
            raise ValueError(f"E_INTERACTION: startMs invalido en {interaction_id}")
        if isinstance(item_duration, bool) or not isinstance(item_duration, int) or item_duration <= 0:
            raise ValueError(f"E_INTERACTION: durationMs invalido en {interaction_id}")
        if start + item_duration > duration:
            raise ValueError(f"E_INTERACTION: ventana fuera del episodio en {interaction_id}")
        label = str(item.get("label", "")).strip()
        if not label:
            raise ValueError(f"E_INTERACTION: label requerido en {interaction_id}")
        target = normalize_target(item.get("target"), interaction_id)
        if kind == "hotspot" and target is None:
            raise ValueError(f"E_INTERACTION: hotspot exige target en {interaction_id}")
        action = item.get("action")
        if not isinstance(action, dict):
            raise ValueError(f"E_INTERACTION: action requerido en {interaction_id}")
        normalized.append({
            "id": interaction_id,
            "type": kind,
            "label": label,
            "startMs": start,
            "durationMs": item_duration,
            "target": target,
            "action": validate_action(action, interaction_id),
        })
    return sorted(normalized, key=lambda value: (value["startMs"], value["id"]))


def apply_html_contract(manifest: dict[str, Any], input_hashes: dict[str, str] | None = None) -> str:
    subtitles = build_subtitles(manifest)
    vtt = build_webvtt(subtitles)
    language = str(manifest.get("language") or "und")
    episode_id = str(manifest["episodeId"])
    track_url = f"/episodes/{episode_id}/subtitles.{language_slug(language)}.vtt"
    manifest["subtitles"] = subtitles
    manifest["subtitleTracks"] = [{
        "id": f"subtitles-{language_slug(language)}",
        "kind": "subtitles",
        "format": "webvtt",
        "language": language,
        "label": "Espanol" if language.casefold().startswith("es") else language,
        "url": track_url,
        "sha256": sha256_text(vtt),
    }]
    manifest["interactions"] = normalize_interactions(manifest)
    manifest["generation"] = {
        "schemaVersion": "1.0",
        "policy": "approved-json-bit-for-bit",
        "determinism": "bit-for-bit-after-approval",
        "aiRuntime": "forbidden-during-build",
        "htmlFirst": True,
        "seed": int(manifest.get("seed", 0)),
        "toolchain": {"maasHtmlBuilder": TOOLCHAIN_VERSION},
        "inputHashes": dict(sorted((input_hashes or {}).items())),
    }
    return vtt


def write_webvtt(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
