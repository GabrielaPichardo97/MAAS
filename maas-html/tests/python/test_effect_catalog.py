import importlib.util
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parent
CATALOG_SOURCE = WORKSPACE / "habilidades" / "seleccionar-efectos-maas" / "references" / "effects-catalog.json"
CATALOG_PUBLIC = ROOT / "public" / "effects-catalog.json"
COMPILER_PATH = ROOT / "tools" / "scripts" / "compile_episode.py"


class EffectCatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_SOURCE.read_text(encoding="utf-8"))

    def test_catalog_has_34_unique_versioned_effects(self):
        effects = self.catalog["effects"]
        ids = [item["id"] for item in effects]
        pattern = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*\.v\d+\.\d+\.\d+$")
        self.assertEqual(len(effects), 34)
        self.assertEqual(len(set(ids)), 34)
        self.assertTrue(all(pattern.fullmatch(value) for value in ids))

    def test_support_distribution_is_explicit(self):
        counts = {level: 0 for level in self.catalog["supportLevels"]}
        for effect in self.catalog["effects"]:
            counts[effect["supportLevel"]] += 1
            self.assertTrue(effect["description"])
            self.assertTrue(effect["bestMoment"])
            self.assertTrue(effect["avoidWhen"])
            self.assertTrue(effect["parameters"])
        self.assertEqual(counts, {"native": 24, "approximation": 3, "input-assisted": 3, "preprocessed": 4})

    def test_public_catalog_is_exact_mirror(self):
        self.assertEqual(CATALOG_SOURCE.read_bytes(), CATALOG_PUBLIC.read_bytes())


class CanonicalV2CompilerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("canonical_compiler", COMPILER_PATH)
        cls.compiler = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(cls.compiler)
        catalog = json.loads(CATALOG_SOURCE.read_text(encoding="utf-8"))
        cls.lookup = {item["id"]: item for item in catalog["effects"]}

    def source(self, token):
        return {
            "episodeId": "canonical-v2-test", "title": "Canonical v2", "language": "es-MX", "status": "draft", "seed": 7,
            "content": f"[Ana] (2 segundos | felicidad | calma)\nHola {token}\n**Oficina**",
        }

    def test_compiles_explicit_effect_stack(self):
        token = "{{fx motion.push-in.emphasis.subtle.v1.0.0 role=dominant intensity=0.3 target=speaker}}"
        manifest = self.compiler.compile_document(self.source(token), "canonical-v2", {"Ana": "ana"}, self.lookup)
        cue = next(item for item in manifest["timeline"] if item["type"] == "dialogue")
        self.assertEqual(manifest["schemaVersion"], "2.1")
        self.assertNotIn("effect", cue)
        self.assertEqual(cue["effects"][0]["params"]["scaleEnd"], 1.1)

    def test_fails_with_documented_fallback_when_requirement_is_missing(self):
        token = "{{fx transition.morph-cut.continuity.interview-clean.v1.0.0 role=dominant}}"
        with self.assertRaisesRegex(ValueError, "E_EFFECT_REQUIREMENT.*transition.cut.continuity.clean"):
            self.compiler.compile_document(self.source(token), "canonical-v2", {"Ana": "ana"}, self.lookup)

    def test_separates_required_inputs_from_programmable_params(self):
        token = "{{fx transition.match-cut.continuity.visual-rhyme.v1.0.0 role=dominant matchAnchors=anchors-toma-1}}"
        manifest = self.compiler.compile_document(self.source(token), "canonical-v2", {"Ana": "ana"}, self.lookup)
        cue = next(item for item in manifest["timeline"] if item["type"] == "dialogue")
        effect = cue["effects"][0]
        self.assertNotIn("matchAnchors", effect["params"])
        self.assertEqual(effect["inputs"]["matchAnchors"], {"kind": "data", "assetId": "anchors-toma-1"})


if __name__ == "__main__":
    unittest.main()
