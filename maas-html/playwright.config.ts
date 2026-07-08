import { defineConfig } from "@playwright/test";

const port = Number(process.env.MAAS_E2E_PORT ?? 4175);
const baseURL = `http://127.0.0.1:${port}`;

export default defineConfig({
  testDir: "tests/e2e",
  workers: 1,
  use: {
    baseURL,
    channel: "chrome",
  },
  webServer: {
    command: `python -m http.server ${port} --directory dist/player --bind 127.0.0.1`,
    url: baseURL,
    reuseExistingServer: false,
    timeout: 15_000,
  },
});
