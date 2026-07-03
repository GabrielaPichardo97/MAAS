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
    await expect(page.getByText("34 resultados", { exact: true })).toBeVisible();
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
    expect(await page.evaluate(() => document.body.scrollWidth <= innerWidth)).toBe(true);
    expect(errors).toEqual([]);
    await page.close();
  });
}

test("los 34 efectos tienen salida observable y control temporal", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  await page.goto("/effects/", { waitUntil: "networkidle" });
  const buttons = page.locator(".effect-list button");
  await expect(buttons).toHaveCount(34);
  const preview = page.getByTestId("effect-preview");
  const timeline = page.getByRole("slider", { name: "Tiempo de la demostración" });
  const observable = (value: string | null, elapsed: number) => {
    if (!value) return false;
    const state = JSON.parse(value) as Record<string, number | boolean | string[]>;
    return Math.abs(Number(state.x)) > 0.0001 || Math.abs(Number(state.y)) > 0.0001 || Math.abs(Number(state.scale) - 1) > 0.0001
      || Number(state.blur) > 0 || Number(state.noise) > 0 || Number(state.incoming) !== 1 || Number(state.outgoing) !== 0
      || Number(state.blackout) > 0 || Number(state.panes) > 1 || Number(state.morph) > 0 || Number(state.jump) > 0
      || Boolean(state.overlay) || Math.abs(Number(state.source) - elapsed) > 1 || (state.diagnostics as string[]).length > 0;
  };
  for (let index = 0; index < 34; index += 1) {
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
