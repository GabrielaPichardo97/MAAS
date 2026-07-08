import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "tools" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from episode_contract import apply_html_contract, build_webvtt  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_build_hashes() -> dict[str, str]:
    paths = [
        ROOT / "media-library" / "media-catalog.json",
        ROOT / "reports" / "media-gaps.json",
        ROOT / "reports" / "media-gaps.md",
    ]
    paths.extend(sorted((ROOT / "public" / "episodes").glob("*/episode.manifest.json")))
    paths.extend(sorted((ROOT / "public" / "episodes").glob("*/build-report.json")))
    paths.extend(sorted((ROOT / "public" / "episodes").glob("*/subtitles.*.vtt")))
    return {path.relative_to(ROOT).as_posix(): sha(path) for path in paths}


class HtmlFirstContractTest(unittest.TestCase):
    def test_manifest_subtitle_track_matches_webvtt(self) -> None:
        manifest_path = ROOT / "public" / "episodes" / "episodio-0-prueba-renderizar" / "episode.manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        track = manifest["subtitleTracks"][0]
        self.assertEqual(track["format"], "webvtt")
        vtt_path = ROOT / "public" / track["url"].removeprefix("/")
        self.assertTrue(vtt_path.is_file())
        self.assertEqual(sha(vtt_path), track["sha256"])
        self.assertTrue(vtt_path.read_text(encoding="utf-8").startswith("WEBVTT\n\nsubtitle-0001"))
        self.assertEqual(manifest["subtitles"][0]["speakerLabel"], "Pato")

    def test_content_build_is_deterministic_for_public_artifacts(self) -> None:
        subprocess.run([sys.executable, str(ROOT / "tools" / "maas_builder" / "build_preview.py")], cwd=ROOT, check=True)
        before = tracked_build_hashes()
        subprocess.run([sys.executable, str(ROOT / "tools" / "maas_builder" / "build_preview.py")], cwd=ROOT, check=True)
        self.assertEqual(tracked_build_hashes(), before)

    def test_interaction_contract_rejects_external_urls(self) -> None:
        manifest = {
            "episodeId": "demo",
            "language": "es-MX",
            "seed": 1,
            "durationMs": 1000,
            "timeline": [],
            "interactions": [
                {"id": "bad-url", "type": "button", "label": "Mal", "startMs": 0, "durationMs": 500, "target": None, "action": {"type": "openUrl", "url": "https://example.test"}}
            ],
        }
        with self.assertRaisesRegex(ValueError, "openUrl"):
            apply_html_contract(manifest)

    def test_publication_gate_rejects_undeclared_video(self) -> None:
        with tempfile.TemporaryDirectory(prefix="maas-html-first-") as temporary:
            root = Path(temporary)
            episode = root / "episodes" / "demo"
            episode.mkdir(parents=True)
            subtitles = [{"id": "subtitle-0001", "cueId": "cue-0001", "startMs": 0, "endMs": 1000, "speakerLabel": "", "text": "Hola", "kind": "dialogue"}]
            vtt = build_webvtt(subtitles)
            (root / "index.html").write_text("<!doctype html><title>Demo</title>\n", encoding="utf-8")
            (episode / "subtitles.es-mx.vtt").write_text(vtt, encoding="utf-8", newline="\n")
            (episode / "build-report.json").write_text("{}\n", encoding="utf-8")
            (root / "clip.mp4").write_bytes(b"not a real video")
            manifest = {
                "episodeId": "demo",
                "durationMs": 1000,
                "timeline": [],
                "assets": [],
                "assetUrls": {},
                "subtitleTracks": [{"id": "subtitles-es-mx", "kind": "subtitles", "format": "webvtt", "language": "es-MX", "label": "Espanol", "url": "/episodes/demo/subtitles.es-mx.vtt", "sha256": hashlib.sha256(vtt.encode("utf-8")).hexdigest()}],
                "subtitles": subtitles,
                "generation": {"schemaVersion": "1.0", "aiRuntime": "forbidden-during-build", "htmlFirst": True},
            }
            (episode / "episode.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPTS / "verify_bundle.py"), str(root), "--publication"], capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("E_HTML_FIRST_VIDEO", result.stdout)


if __name__ == "__main__":
    unittest.main()
