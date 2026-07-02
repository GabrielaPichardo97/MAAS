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
    await expect(page.getByText("Demostración conceptual; revisa requisitos")).toBeVisible();
    expect(await page.evaluate(() => document.body.scrollWidth <= innerWidth)).toBe(true);
    expect(errors).toEqual([]);
    await page.close();
  });
}
