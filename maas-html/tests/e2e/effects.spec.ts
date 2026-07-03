import { expect, test } from "@playwright/test";

for (const viewport of [
  { name: "wide", width: 1280, height: 800 },
  { name: "narrow", width: 390, height: 844 },
]) {
  test(`${viewport.name}: catálogo interactivo`, async ({ browser }) => {
    const page = await browser.newPage({ viewport });
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
    await page.goto("/effects/", { waitUntil: "networkidle" });
    await expect(page.getByRole("heading", { name: "Biblioteca de efectos" })).toBeVisible();
    await expect(page.getByText("37 resultados", { exact: true })).toBeVisible();
    await page.getByRole("searchbox").fill("morph");
    await expect(page.getByText("1 resultados", { exact: true })).toBeVisible();
    await page.getByRole("button", { name: /Morph cut/ }).click();
    await expect(page.getByText("transition.morph-cut.continuity.interview-clean.v1.0.0", { exact: true })).toBeVisible();
    await expect(page.getByTestId("effect-scene")).toContainText("La pausa imposible");
    await expect(page.getByTestId("effect-scene")).toContainText("Nunca dudé");
    await expect(page.getByText(/Demo con input simulado/)).toBeVisible();
    await expect(page.getByRole("button", { name: "Pausar demostración" })).toBeVisible();
    const preview = page.getByTestId("effect-preview");
    await expect(preview).toHaveAttribute("data-effect-id", "transition.morph-cut.continuity.interview-clean.v1.0.0");
    await expect(preview).not.toHaveAttribute("data-effect-signature", "");
    await page.getByRole("searchbox").fill("line boil");
    await page.getByRole("button", { name: /Line boil/ }).click();
    await expect(page.getByTestId("layer-example")).toContainText("Fondo y personaje móviles");
    await expect(page.getByRole("combobox", { name: "Capas del ejemplo" })).toHaveValue("both");
    const bothState = JSON.parse((await preview.getAttribute("data-effect-signature"))!);
    expect(bothState.layers.background.lineBoil).toBeTruthy();
    expect(bothState.layers.speaker.lineBoil).toBeTruthy();
    await page.getByRole("combobox", { name: "Capas del ejemplo" }).selectOption("background");
    await expect(page.locator("pre")).toContainText("target=background");
    const layerState = await preview.getAttribute("data-effect-signature");
    expect(JSON.parse(layerState!).layers.background.lineBoil).toBeTruthy();
    expect(JSON.parse(layerState!).layers.speaker.lineBoil).toBeFalsy();
    expect(await page.evaluate(() => document.body.scrollWidth <= innerWidth)).toBe(true);
    expect(errors).toEqual([]);
    await page.close();
  });
}

test("los 37 efectos tienen salida observable y control temporal", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  await page.goto("/effects/", { waitUntil: "networkidle" });
  const buttons = page.locator(".effect-list button");
  await expect(buttons).toHaveCount(37);
  const preview = page.getByTestId("effect-preview");
  const timeline = page.getByRole("slider", { name: "Tiempo de la demostración" });
  const observable = (value: string | null, elapsed: number) => {
    if (!value) return false;
    const state = JSON.parse(value) as Record<string, number | boolean | string[] | Record<string, unknown>>;
    const layers = state.layers as Record<string, { xPx: number; yPx: number; rotation: number; lineBoil?: unknown; paperGrain?: unknown }>;
    return Math.abs(Number(state.x)) > 0.0001 || Math.abs(Number(state.y)) > 0.0001 || Math.abs(Number(state.scale) - 1) > 0.0001
      || Number(state.blur) > 0 || Number(state.noise) > 0 || Number(state.incoming) !== 1 || Number(state.outgoing) !== 0
      || Number(state.blackout) > 0 || Number(state.panes) > 1 || Number(state.morph) > 0 || Number(state.jump) > 0
      || Boolean(state.overlay) || Math.abs(Number(state.source) - elapsed) > 1 || (state.diagnostics as string[]).length > 0
      || Object.values(layers).some((layer) => Math.abs(layer.xPx) > 0.001 || Math.abs(layer.yPx) > 0.001 || Math.abs(layer.rotation) > 0.0001 || Boolean(layer.lineBoil) || Boolean(layer.paperGrain));
  };
  for (let index = 0; index < 37; index += 1) {
    await buttons.nth(index).click();
    await page.getByRole("button", { name: "Pausar demostración" }).click();
    await timeline.fill("10");
    const early = await preview.getAttribute("data-effect-signature");
    const max = Number(await timeline.getAttribute("max"));
    const middleTime = Math.round(max / 2);
    await timeline.fill(String(middleTime));
    const middle = await preview.getAttribute("data-effect-signature");
    expect(observable(early, 10) || observable(middle, middleTime), `efecto ${index + 1} sin salida observable`).toBe(true);
  }
  expect(errors).toEqual([]);
});

test("los tres ejemplos artesanales distinguen sus capas móviles", async ({ page }) => {
  await page.goto("/effects/", { waitUntil: "networkidle" });
  const search = page.getByRole("searchbox");
  const preview = page.getByTestId("effect-preview");
  const cases = [
    { query: "paper-grain", mode: "background", label: "Fondo móvil · personaje quieto", background: "paperGrain", speaker: null },
    { query: "cutout-wobble", mode: "speaker", label: "Personaje móvil · fondo quieto", background: null, speaker: "wobble" },
    { query: "line boil", mode: "both", label: "Fondo y personaje móviles", background: "lineBoil", speaker: "lineBoil" },
  ] as const;
  for (const example of cases) {
    await search.fill(example.query);
    const button = page.locator(".effect-list button");
    await expect(button).toHaveCount(1);
    await button.click();
    await expect(preview).toHaveAttribute("data-example-mode", example.mode);
    await expect(page.getByTestId("layer-example")).toContainText(example.label);
    await expect(page.getByRole("combobox", { name: "Capas del ejemplo" })).toHaveValue(example.mode);
    await expect.poll(async () => {
      const current = JSON.parse((await preview.getAttribute("data-effect-signature"))!);
      if (example.background && !current.layers.background[example.background]) return false;
      if (example.speaker === "lineBoil" && !current.layers.speaker.lineBoil) return false;
      if (example.speaker === "wobble" && Math.abs(current.layers.speaker.xPx) + Math.abs(current.layers.speaker.yPx) + Math.abs(current.layers.speaker.rotation) === 0) return false;
      return true;
    }).toBe(true);
    const state = JSON.parse((await preview.getAttribute("data-effect-signature"))!);
    expect(Boolean(example.background && state.layers.background[example.background])).toBe(Boolean(example.background));
    if (example.speaker === "wobble") {
      expect(Math.abs(state.layers.speaker.xPx) + Math.abs(state.layers.speaker.yPx) + Math.abs(state.layers.speaker.rotation)).toBeGreaterThan(0);
    } else {
      expect(Boolean(example.speaker && state.layers.speaker[example.speaker!])).toBe(Boolean(example.speaker));
    }
    if (!example.background) expect(state.layers.background).toMatchObject({ xPx: 0, yPx: 0, rotation: 0 });
    if (!example.speaker) expect(state.layers.speaker).toMatchObject({ xPx: 0, yPx: 0, rotation: 0 });
  }
});
