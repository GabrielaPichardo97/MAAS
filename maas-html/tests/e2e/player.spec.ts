import { expect, test } from "@playwright/test";

const episodePath = "/";

for (const viewport of [
  { name: "wide", width: 1280, height: 720 },
  { name: "narrow", width: 390, height: 844 },
]) {
  test(`${viewport.name}: media real y controles`, async ({ browser }) => {
    const page = await browser.newPage({ viewport });
    const errors: string[] = [];
    const pngResponses: number[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (message) => {
      if (message.type() === "error") errors.push(message.text());
    });
    page.on("response", (response) => {
      if (response.url().endsWith(".png")) pngResponses.push(response.status());
    });

    await page.goto(episodePath, { waitUntil: "networkidle" });
    await expect(page.locator(".stage")).toHaveAttribute("data-stage-status", /^rendered:/, { timeout: 15_000 });
    await expect(page.locator(".caption")).toContainText("Pato");
    expect(await page.locator("canvas").count()).toBe(1);
    expect(await page.evaluate(() => document.body.scrollWidth <= innerWidth)).toBe(true);
    expect(pngResponses.length).toBeGreaterThanOrEqual(2);
    expect(pngResponses.every((status) => status === 200)).toBe(true);

    await page.getByRole("button", { name: "Iniciar episodio" }).click();
    await page.getByRole("button", { name: "Pausar" }).click();
    await page.getByRole("button", { name: "Adelantar 5 segundos" }).click();
    await expect(page.locator(".caption")).toContainText("Cactus");
    await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur());
    await page.keyboard.press("c");
    await expect(page.locator(".caption")).toContainText("Captions desactivados");
    await page.keyboard.press("c");
    await page.keyboard.press("ArrowRight");
    await expect(page.locator(".caption")).toContainText("Conejo");

    await page.locator(".secondary-controls button").last().click();
    await expect.poll(() => page.evaluate(() => Boolean(document.fullscreenElement))).toBe(true);
    await page.evaluate(() => document.exitFullscreen());
    expect(errors).toEqual([]);
    await page.close();
  });
}

test("HTML directo del Episodio 0", async ({ page }) => {
  await page.goto("/episodes/episodio-0-prueba-renderizar/", { waitUntil: "networkidle" });
  await expect(page.getByRole("heading", { name: /Episodio 0/ })).toBeVisible();
  await expect(page.getByRole("button", { name: "Iniciar episodio" })).toBeVisible();
});

test("interacciones HTML aparecen por ventana temporal y no viven en Pixi", async ({ page, request }) => {
  const response = await request.get("/episodes/episodio-0-prueba-renderizar/episode.manifest.json");
  const manifest = await response.json();
  manifest.interactions = [
    { id: "abrir-contexto", type: "button", label: "Ver contexto", startMs: 0, durationMs: 5000, target: null, action: { type: "openPanel", panelId: "contexto" } },
    { id: "hotspot-pato", type: "hotspot", label: "Pato", startMs: 0, durationMs: 5000, target: { x: 0.12, y: 0.22, width: 0.18, height: 0.28 }, action: { type: "emit", event: "personaje", detail: { speaker: "pato" } } },
  ];
  await page.route("**/episodes/episodio-0-prueba-renderizar/episode.manifest.json", (route) => route.fulfill({ json: manifest }));
  await page.goto("/", { waitUntil: "networkidle" });
  await expect(page.getByTestId("interaction-layer")).toHaveCount(0);
  await page.evaluate(() => {
    (window as typeof window & { __maasEvents?: unknown[] }).__maasEvents = [];
    document.addEventListener("maas-interaction", (event) => {
      (window as typeof window & { __maasEvents: unknown[] }).__maasEvents.push((event as CustomEvent).detail);
    });
  });
  await page.getByRole("button", { name: "Iniciar episodio" }).click();
  await expect(page.getByTestId("interaction-abrir-contexto")).toBeVisible();
  await expect(page.getByTestId("interaction-hotspot-pato")).toBeVisible();
  await page.getByTestId("interaction-hotspot-pato").click();
  await expect.poll(() => page.evaluate(() => (window as typeof window & { __maasEvents?: unknown[] }).__maasEvents?.length ?? 0)).toBe(1);
  await page.getByTestId("interaction-abrir-contexto").click();
  await expect(page.getByRole("dialog", { name: "Ver contexto" })).toBeVisible();
  await page.getByRole("button", { name: "Cerrar" }).click();
  await page.getByRole("button", { name: "Adelantar 5 segundos" }).click();
  await expect(page.getByTestId("interaction-layer")).toHaveCount(0);
});

test("stack artesanal renderiza en WebGL y conserva capas aisladas", async ({ page, request }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  const response = await request.get("/episodes/episodio-0-prueba-renderizar/episode.manifest.json");
  const manifest = await response.json();
  const firstDialogue = manifest.timeline.find((cue: { type: string; media?: unknown }) => cue.type === "dialogue" && cue.media);
  firstDialogue.effects = [
    { id: "stylize.line-boil.handmade.edge-jitter.v1.0.0", role: "dominant", intensity: 0.65, startOffsetMs: 0, durationMs: firstDialogue.durationMs, target: "speaker", params: { amplitudePx: 1.25, rateFps: 8, wavelengthPx: 36 } },
    { id: "motion.cutout-wobble.presence.puppet-idle.v1.0.0", role: "support", intensity: 0.65, startOffsetMs: 0, durationMs: firstDialogue.durationMs, target: "speaker", params: { travelPx: 4, rotationDeg: 0.45, rateFps: 6 } },
    { id: "stylize.paper-grain.texture.living-fiber.v1.0.0", role: "finish", intensity: 0.65, startOffsetMs: 0, durationMs: firstDialogue.durationMs, target: "background", params: { amount: 0.06, grainPx: 3, fiber: 0.35, rateFps: 6 } },
  ];
  await page.route("**/episodes/episodio-0-prueba-renderizar/episode.manifest.json", (route) => route.fulfill({ json: manifest }));
  await page.goto("/", { waitUntil: "networkidle" });
  await expect(page.locator(".stage")).toHaveAttribute("data-stage-status", /^rendered:/, { timeout: 15_000 });
  await page.getByRole("button", { name: "Iniciar episodio" }).click();
  await expect(page.locator(".stage")).toHaveAttribute("data-effect-ids", /line-boil.*cutout-wobble.*paper-grain/);
  await expect(page.locator(".stage")).toHaveAttribute("data-effect-layers", "background:paper-grain,speaker:line-boil+wobble");
  await expect(page.locator(".stage")).toHaveAttribute("data-effect-diagnostics", "");
  expect(errors).toEqual([]);
});

for (const episode of [
  {
    id: "episodio-0-prueba-efectos",
    title: /Prueba de efectos/,
    firstEffect: "motion.push-in.emphasis.subtle.v1.0.0",
  },
  {
    id: "episodio-17-el-correo-infinito",
    title: /El correo infinito/,
    firstEffect: "motion.ken-burns.exposition.documentary.v1.0.0",
  },
]) {
  test(`HTML creativo ${episode.id} renderiza y empieza con efectos`, async ({ page, request }) => {
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
    const response = await request.get(`/episodes/${episode.id}/episode.manifest.json`);
    expect(response.ok()).toBe(true);
    const manifest = await response.json();
    const firstDialogue = manifest.timeline.find((cue: { type: string }) => cue.type === "dialogue");
    expect(firstDialogue.effects[0].id).toBe(episode.firstEffect);

    await page.goto(`/episodes/${episode.id}/`, { waitUntil: "networkidle" });
    await expect(page.getByRole("heading", { name: episode.title })).toBeVisible();
    await expect(page.locator(".stage")).toHaveAttribute("data-stage-status", /^rendered:/, { timeout: 15_000 });
    await page.getByRole("button", { name: "Iniciar episodio" }).click();
    await expect(page.getByRole("button", { name: "Pausar" })).toBeVisible();
    expect(await page.locator("canvas").count()).toBe(1);
    expect(errors).toEqual([]);
  });
}
