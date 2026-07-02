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
