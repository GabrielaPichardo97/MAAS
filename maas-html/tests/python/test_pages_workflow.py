import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[3] / ".github" / "workflows" / "pages.yml"


class PagesWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WORKFLOW.read_text(encoding="utf-8")

    def test_separates_build_and_deploy_for_safe_retries(self):
        self.assertIn("  build:\n", self.source)
        self.assertIn("  deploy:\n", self.source)
        self.assertIn("    needs: build\n", self.source)
        self.assertIn("github-pages-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}", self.source)
        self.assertIn("artifact_name: ${{ needs.build.outputs.artifact_name }}", self.source)

    def test_uses_node_24_actions_without_insecure_opt_out(self):
        for action in (
            "actions/checkout@v6",
            "actions/setup-python@v6",
            "actions/setup-node@v6",
            "pnpm/action-setup@v4.4.0",
            "actions/configure-pages@v6",
            "actions/upload-pages-artifact@v5",
            "actions/deploy-pages@v5",
        ):
            self.assertIn(action, self.source)
        self.assertIn('node-version: "24"', self.source)
        self.assertNotIn("ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION", self.source)


if __name__ == "__main__":
    unittest.main()
