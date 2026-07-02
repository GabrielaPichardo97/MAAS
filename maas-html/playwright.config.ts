import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "tests/e2e",
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:4174",
    channel: "chrome",
  },
  webServer: {
    command: "py -3.11 -m http.server 4174 --directory dist/player --bind 127.0.0.1",
    url: "http://127.0.0.1:4174",
    reuseExistingServer: false,
    timeout: 15_000,
  },
});
