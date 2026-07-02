import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEGACY_MEDIA = ROOT.parent / "media"
EPISODE_ID = "episodio-0-prueba-renderizar"
CONTENT = ROOT / "content" / "episodes" / EPISODE_ID
MANIFEST_PATH = ROOT / "public" / "episodes" / EPISODE_ID / "episode.manifest.json"
CATALOG_PATH = ROOT / "media-library" / "media-catalog.json"
PIPELINE = ROOT / "tools" / "scripts" / "media_pipeline.py"
sys.path.insert(0, str(ROOT / "tools" / "scripts"))

from verify_bundle import application_source_injections  # noqa: E402


class RealMediaManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_episode_zero_has_expected_timeline(self):
        self.assertEqual(self.manifest["episodeId"], EPISODE_ID)
        self.assertEqual(self.manifest["profile"], "legacy-v1")
        self.assertEqual(self.manifest["durationMs"], 33_900)
        self.assertEqual(len(self.manifest["timeline"]), 19)

    def test_character_mapping_uses_real_cast(self):
        self.assertEqual(
            self.manifest["characters"],
            {"Persona_1": "pato", "Persona_2": "cactus", "Persona_3": "conejo", "Persona_4": "pata"},
        )

    def test_every_character_cue_has_real_png_media(self):
        cues = [cue for cue in self.manifest["timeline"] if cue["type"] in {"dialogue", "sfx"}]
        self.assertEqual(len(cues), 16)
        self.assertTrue(all("media" in cue for cue in cues))
        self.assertTrue(all(cue["media"]["fallbackApplied"] is None for cue in cues))
        self.assertTrue(all("characterTheme" not in json.dumps(cue) for cue in cues))
        self.assertEqual(set(self.manifest["characters"].values()), {"pato", "cactus", "conejo", "pata"})

    def test_manifest_references_only_staged_hashed_pngs(self):
        self.assertEqual(len(self.manifest["assets"]), 11)
        self.assertEqual(set(self.manifest["assets"]), set(self.manifest["assetUrls"]))
        for url in self.manifest["assetUrls"].values():
            self.assertRegex(url, r"^/assets/[a-f0-9]{64}\.png$")
            self.assertTrue((ROOT / "public" / url.removeprefix("/")).is_file())

    def test_episode_has_no_media_gaps(self):
        report = json.loads((ROOT / "reports" / "episode-0-media-gaps.json").read_text(encoding="utf-8"))
        self.assertEqual(report["gaps"], [])


class CatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    def test_catalog_preserves_all_assets_and_authorizes_visuals(self):
        self.assertEqual(len(self.catalog["assets"]), 365)
        visuals = [asset for asset in self.catalog["assets"] if asset["type"] in {"sprite", "background"}]
        self.assertEqual(len(visuals), 209)
        self.assertTrue(all(asset["allowedForPublish"] and asset["licenseId"] == "maas-proprietary" for asset in visuals))

    def test_aliases_are_normalized_in_metadata(self):
        ids = {asset["id"] for asset in self.catalog["assets"]}
        self.assertTrue(any("character-gata-angry-left" in asset_id for asset_id in ids))
        self.assertTrue(any("character-pato-confused-right" in asset_id for asset_id in ids))
        self.assertFalse(any("angy" in asset_id or "condused" in asset_id or "correct" in asset_id for asset_id in ids))

    def test_general_gaps_are_documented_but_non_blocking(self):
        report = json.loads((ROOT / "reports" / "media-gaps.json").read_text(encoding="utf-8"))
        self.assertEqual(report["summary"]["total"], 78)
        self.assertEqual(report["summary"]["episodeRequired"], 0)
        self.assertTrue(all(not gap["blockingPublication"] for gap in report["gaps"]))

    def test_publication_missing_asset_writes_actionable_request(self):
        with tempfile.TemporaryDirectory(prefix="maas-media-test-") as temporary:
            temp = Path(temporary)
            catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
            catalog["assets"] = [asset for asset in catalog["assets"] if asset["id"] != "character-pata-worried-left"]
            catalog_path = temp / "catalog.json"
            output = temp / "manifest.json"
            gaps = temp / "gaps.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable, str(PIPELINE), "resolve", str(MANIFEST_PATH), str(catalog_path),
                    str(CONTENT / "presentation.json"), str(ROOT / "media-library" / "emotion-policy.json"),
                    "--mode", "publication", "--output", str(output), "--episode-gaps", str(gaps),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            report = json.loads(gaps.read_text(encoding="utf-8"))
            request = report["gaps"][0]
            self.assertEqual(request["characterId"], "pata")
            self.assertEqual(request["emotion"], "worried")
            self.assertEqual(request["suggestedFilename"], "characters/pata/worried.left.png")
            self.assertTrue(request["blockingPublication"])


class BundleSecurityTest(unittest.TestCase):
    def test_html_injection_scanner_distinguishes_app_from_dependencies(self):
        source_map = json.dumps({"sources": ["../../../node_modules/react/index.js", "../../../src/App.tsx"], "sourcesContent": ["node.innerHTML = value", "export const safe = 'texto'"]})
        self.assertEqual(application_source_injections(Path("index.js.map"), source_map), [])
        unsafe_map = source_map.replace("export const safe = 'texto'", "node.innerHTML = value")
        self.assertEqual(application_source_injections(Path("index.js.map"), unsafe_map), ["../../../src/App.tsx"])


if __name__ == "__main__":
    unittest.main()
