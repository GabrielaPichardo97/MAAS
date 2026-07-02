from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[3]
PLAYER = WORKSPACE / "maas-html"
ADAPT = WORKSPACE / "habilidades" / "creativa-adaptar-dialogo-maas" / "scripts"
DIRECT = WORKSPACE / "habilidades" / "creativa-dirigir-escena-maas" / "scripts"
ASSEMBLE = WORKSPACE / "habilidades" / "creativa-ensamblar-episodio-maas" / "scripts"
CATALOG = WORKSPACE / "habilidades" / "seleccionar-efectos-maas" / "references" / "effects-catalog.json"
TOOLS = PLAYER / "tools" / "scripts"
PUSH_IN = "motion.push-in.emphasis.subtle.v1.0.0"
MATCH_CUT = "transition.match-cut.continuity.visual-rhyme.v1.0.0"


def run(*args: object, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([sys.executable, *(str(arg) for arg in args)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != expected:
        raise AssertionError(f"exit={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


class CreativeSkillsTest(unittest.TestCase):
    def adapt(self, root: Path, text: str, place: str = "Oficina") -> Path:
        raw = root / "dialogue.txt"
        output = root / "dialogue-adaptation.json"
        raw.write_text(text, encoding="utf-8", newline="\n")
        run(ADAPT / "adapt_dialogue.py", raw, "--title", "Prueba creativa", "--place", place, "--output", output)
        return output

    def direct(self, root: Path, adaptation: Path, approve: bool = False, with_effect: bool = False) -> Path:
        output = root / "cinematic-direction.json"
        run(DIRECT / "prepare_direction.py", adaptation, "--output", output)
        data = json.loads(output.read_text(encoding="utf-8"))
        if with_effect:
            data["scenes"][0]["beats"][0]["effects"] = [{
                "id": PUSH_IN, "role": "dominant", "intensity": 0.3, "target": "speaker",
                "params": {"scaleEnd": 1.1, "easing": "ease-in-out"},
            }]
        output.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        if approve:
            run(DIRECT / "approve_direction.py", output, "--approved-by", "pruebas", "--approved-at", "2026-07-02T12:00:00Z", "--output", output)
        return output

    def assemble(self, root: Path, adaptation: Path, direction: Path, expected: int = 0) -> tuple[Path, Path, Path]:
        source = root / "episode-source.json"
        character_map = root / "character-map.json"
        presentation = root / "presentation.json"
        run(
            ASSEMBLE / "assemble_episode.py", direction, "--adaptation", adaptation,
            "--effect-catalog", CATALOG, "--output-source", source,
            "--character-map", character_map, "--presentation", presentation,
            expected=expected,
        )
        return source, character_map, presentation

    def test_labeled_theatrical_and_multiline_dialogue_remain_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adaptation = self.adapt(root, "Pato: ¿Ya llegaste?\nTodavía no.\nCactus: Apenas.\n")
            run(ADAPT / "validate_adaptation.py", adaptation)
            data = json.loads(adaptation.read_text(encoding="utf-8"))
            self.assertEqual([beat["verbatimText"] for beat in data["scenes"][0]["beats"]], ["¿Ya llegaste?", "Todavía no.", "Apenas."])

            theatrical = self.adapt(root, "PATO\nNo me mires así.\nCACTUS\nEstá bien.\n")
            data = json.loads(theatrical.read_text(encoding="utf-8"))
            self.assertEqual([beat["speaker"] for beat in data["scenes"][0]["beats"]], ["PATO", "CACTUS"])

    def test_unlabeled_dialogue_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adaptation = self.adapt(root, "Hola.\n¿Qué tal?\n")
            data = json.loads(adaptation.read_text(encoding="utf-8"))
            self.assertTrue(any(item["code"] == "E_SPEAKER_AMBIGUOUS" and item["blocking"] for item in data["unresolved"]))
            run(ADAPT / "validate_adaptation.py", adaptation, expected=1)

    def test_direction_rejects_duplicate_roles_and_assembly_requires_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adaptation = self.adapt(root, "Pato: Una idea.\n")
            direction = self.direct(root, adaptation)
            self.assemble(root, adaptation, direction, expected=1)
            data = json.loads(direction.read_text(encoding="utf-8"))
            effect = {"id": PUSH_IN, "role": "dominant", "intensity": 0.3, "params": {}}
            data["scenes"][0]["beats"][0]["effects"] = [effect, dict(effect)]
            direction.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            run(DIRECT / "validate_direction.py", direction, "--adaptation", adaptation, "--catalog", CATALOG, expected=1)
            data["scenes"][0]["beats"][0]["effects"] = [{"id": MATCH_CUT, "role": "dominant", "intensity": 0.3, "params": {}}]
            direction.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            run(DIRECT / "validate_direction.py", direction, "--adaptation", adaptation, "--catalog", CATALOG, expected=1)

    def test_canonical_episode_resolves_media_and_builds_html(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adaptation = self.adapt(root, "Pato: ¿Ya llegaste?\nCactus: Apenas.\n")
            run(ADAPT / "validate_adaptation.py", adaptation)
            direction = self.direct(root, adaptation, approve=True, with_effect=True)
            run(DIRECT / "validate_direction.py", direction, "--adaptation", adaptation, "--catalog", CATALOG)
            source, character_map, presentation = self.assemble(root, adaptation, direction)
            run(TOOLS / "validate_episode.py", source, "--mode", "strict", "--profile", "canonical-v2")
            compiled = root / "compiled.json"
            run(TOOLS / "compile_episode.py", source, "--profile", "canonical-v2", "--character-map", character_map, "--effect-catalog", CATALOG, "--output", compiled)
            manifest = root / "manifest.json"
            gaps = root / "episode-gaps.json"
            run(
                TOOLS / "media_pipeline.py", "resolve", compiled, PLAYER / "media-library" / "media-catalog.json",
                presentation, PLAYER / "media-library" / "emotion-policy.json", "--mode", "publication",
                "--output", manifest, "--episode-gaps", gaps,
            )
            resolved = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(resolved["profile"], "canonical-v2")
            self.assertTrue(any(cue.get("type") == "scene" for cue in resolved["timeline"]))
            self.assertTrue(any(cue.get("effects") for cue in resolved["timeline"] if cue.get("type") == "dialogue"))

            site = root / "site"
            player_dist = root / "player"
            shutil.copytree(PLAYER / "dist" / "player", player_dist, ignore=shutil.ignore_patterns("episodes"))
            run(TOOLS / "media_pipeline.py", "stage", PLAYER / "media-library" / "media-catalog.json", manifest, "--root", WORKSPACE / "media", "--output", site / "assets")
            run(TOOLS / "build_episode.py", manifest, "--player-dist", player_dist, "--output", site, "--media-catalog", PLAYER / "media-library" / "media-catalog.json")
            run(TOOLS / "verify_bundle.py", site)
            self.assertTrue((site / "episodes" / "prueba-creativa" / "index.html").is_file())

    def test_missing_media_generates_blocking_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adaptation = self.adapt(root, "UNICORNIO: Aquí estamos.\n", place="Luna")
            direction = self.direct(root, adaptation, approve=True)
            source, character_map, presentation = self.assemble(root, adaptation, direction)
            compiled = root / "compiled.json"
            run(TOOLS / "compile_episode.py", source, "--profile", "canonical-v2", "--character-map", character_map, "--effect-catalog", CATALOG, "--output", compiled)
            manifest = root / "manifest.json"
            gaps = root / "episode-gaps.json"
            run(
                TOOLS / "media_pipeline.py", "resolve", compiled, PLAYER / "media-library" / "media-catalog.json",
                presentation, PLAYER / "media-library" / "emotion-policy.json", "--mode", "publication",
                "--output", manifest, "--episode-gaps", gaps, expected=1,
            )
            report = root / "episode-gaps.md"
            run(ASSEMBLE / "render_media_gaps.py", gaps, "--output", report)
            self.assertTrue(json.loads(gaps.read_text(encoding="utf-8"))["gaps"])
            self.assertIn("Bloqueante", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
