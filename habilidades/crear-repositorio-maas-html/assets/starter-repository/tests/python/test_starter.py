import json
import unittest
from pathlib import Path


class StarterTest(unittest.TestCase):
    def test_demo_manifest_has_timeline(self):
        root = Path(__file__).resolve().parents[2]
        data = json.loads((root / "public/episodes/demo/episode.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schemaVersion"], "1.0")
        self.assertGreater(len(data["timeline"]), 0)


if __name__ == "__main__":
    unittest.main()
