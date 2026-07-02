import "pixi.js/unsafe-eval";
import { Application, Assets, BlurFilter, Container, Graphics, NoiseFilter, Sprite, Text, TextStyle, type Texture } from "pixi.js";
import type { TimelineCue } from "../types";
import { legacyCameraTransform } from "./effectMath";
import { canonicalEffectFrame, type CanonicalEffectFrame } from "./effectEngine";

const LOGICAL_WIDTH = 1920;
const LOGICAL_HEIGHT = 1080;

function textLabel(text: string, size: number, color = "#ffffff", weight: "500" | "700" | "800" = "700"): Text {
  return new Text({
    text,
    style: new TextStyle({
      fill: color,
      fontFamily: "Nanum Gothic, system-ui, sans-serif",
      fontSize: size,
      fontWeight: weight,
    }),
  });
}

export class MaasStage {
  private readonly app = new Application();
  private readonly viewport = new Container();
  private readonly camera = new Container();
  private readonly effectsLayer = new Container();
  private readonly effectGraphics = new Graphics();
  private readonly blurFilter = new BlurFilter({ strength: 0, quality: 2 });
  private readonly noiseFilter = new NoiseFilter({ noise: 0, seed: 1 });
  private readonly loadedUrls = new Set<string>();
  private cue?: TimelineCue;
  private ready = false;
  private destroyRequested = false;
  private drawToken = 0;
  private host?: HTMLElement;

  constructor(private readonly assetUrls: Record<string, string>) {}

  async init(host: HTMLElement): Promise<void> {
    this.host = host;
    host.dataset.stageStatus = "initializing";
    await this.app.init({ background: "#0d1424", resizeTo: host, antialias: true, preference: "webgl" });
    if (this.destroyRequested) {
      this.app.destroy(true);
      return;
    }
    this.ready = true;
    host.dataset.stageStatus = "ready";
    host.appendChild(this.app.canvas);
    this.effectsLayer.addChild(this.effectGraphics);
    this.viewport.addChild(this.camera, this.effectsLayer);
    this.app.stage.addChild(this.viewport);
    this.resize(host.clientWidth, host.clientHeight);
    if (this.cue) await this.drawCue(this.cue);
  }

  async show(cue: TimelineCue | undefined): Promise<void> {
    this.cue = cue;
    if (this.host) this.host.dataset.stageStatus = cue ? `queued:${cue.id}` : "idle";
    if (!this.ready || !cue) return;
    await this.drawCue(cue);
  }

  private clearCamera(): void {
    this.camera.removeChildren().forEach((child) => child.destroy({ children: true, texture: false, textureSource: false }));
  }

  private async loadTexture(assetId: string): Promise<Texture> {
    const url = this.assetUrls[assetId];
    if (!url) throw new Error(`Asset sin URL: ${assetId}`);
    const texture = await Assets.load<Texture>(url);
    this.loadedUrls.add(url);
    return texture;
  }

  private async drawCue(cue: TimelineCue): Promise<void> {
    const token = ++this.drawToken;
    if (this.host) this.host.dataset.stageStatus = `drawing:${cue.id}`;
    this.clearCamera();
    if (cue.type === "transition") {
      this.drawTransition(cue);
      this.resetCamera();
      return;
    }
    if (!cue.media) {
      this.drawMissing(`Cue sin media: ${cue.id}`);
      this.resetCamera();
      return;
    }
    try {
      const [backgroundTexture, spriteTexture] = await Promise.all([
        this.loadTexture(cue.media.backgroundAssetId),
        this.loadTexture(cue.media.spriteAssetId),
      ]);
      if (token !== this.drawToken || this.destroyRequested) return;
      const background = new Sprite(backgroundTexture);
      background.position.set(0, 0);
      background.width = LOGICAL_WIDTH;
      background.height = LOGICAL_HEIGHT;
      this.camera.addChild(background);

      const isRight = cue.speakerPosition === "derecha";
      const isCloseUp = cue.effect?.code === "PP";
      const frame = isCloseUp
        ? { left: isRight ? 620 : 92, top: -62, width: 1500, height: 1500 }
        : { left: isRight ? 968 : 300, top: 308, width: 854, height: 854 };
      const sprite = new Sprite(spriteTexture);
      sprite.anchor.set(0.5, 0);
      sprite.position.set(frame.left + frame.width / 2, frame.top);
      sprite.width = frame.width;
      sprite.height = frame.height;
      if (cue.media.mirrorX) sprite.scale.x *= -1;
      this.camera.addChild(sprite);

      const visualText = new Text({
        text: cue.text ?? "",
        style: new TextStyle({
          fill: "#111111",
          fontFamily: "Nanum Gothic, system-ui, sans-serif",
          fontSize: isRight ? 84 : 80,
          fontWeight: "800",
          lineHeight: 96,
          wordWrap: true,
          wordWrapWidth: 500,
        }),
      });
      visualText.position.set(isRight ? 348 : 1054, isRight ? 70 : 98);
      this.camera.addChild(visualText);
      if (this.host) this.host.dataset.stageStatus = `rendered:${cue.id}`;
    } catch (error: unknown) {
      if (token !== this.drawToken) return;
      this.clearCamera();
      this.drawMissing(error instanceof Error ? error.message : `No se pudo cargar media para ${cue.id}`);
      if (this.host) this.host.dataset.stageStatus = `error:${cue.id}`;
    }
    this.resetCamera();
  }

  private drawTransition(cue: TimelineCue): void {
    const background = new Graphics()
      .rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT).fill("#11182b")
      .circle(250, 210, 250).fill({ color: "#f28b45", alpha: 0.35 })
      .circle(1700, 870, 360).fill({ color: "#5d91f2", alpha: 0.3 });
    this.camera.addChild(background);
    const eyebrow = textLabel("MAAS · PREVIEW LOCAL", 30, "#9fb4db", "700");
    eyebrow.anchor.set(0.5);
    eyebrow.position.set(960, 385);
    this.camera.addChild(eyebrow);
    const title = new Text({
      text: cue.text ?? "CAMBIO DE ESCENA",
      style: new TextStyle({ align: "center", fill: "#ffffff", fontFamily: "system-ui, sans-serif", fontSize: 94, fontWeight: "800", wordWrap: true, wordWrapWidth: 1180 }),
    });
    title.anchor.set(0.5);
    title.position.set(960, 525);
    this.camera.addChild(title);
  }

  private drawMissing(message: string): void {
    const background = new Graphics().rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT).fill("#30151b");
    const title = textLabel("MEDIA FALTANTE", 70, "#ffb2b2", "800");
    title.anchor.set(0.5);
    title.position.set(960, 440);
    const detail = new Text({ text: message, style: new TextStyle({ align: "center", fill: "#ffe1e1", fontFamily: "system-ui, sans-serif", fontSize: 34, wordWrap: true, wordWrapWidth: 1300 }) });
    detail.anchor.set(0.5);
    detail.position.set(960, 560);
    this.camera.addChild(background, title, detail);
  }

  private resetCamera(): void {
    this.camera.pivot.set(LOGICAL_WIDTH / 2, LOGICAL_HEIGHT / 2);
    this.camera.position.set(LOGICAL_WIDTH / 2, LOGICAL_HEIGHT / 2);
    this.camera.scale.set(1);
    this.camera.rotation = 0;
    this.camera.alpha = 1;
    this.camera.tint = 0xffffff;
    this.camera.filters = null;
    this.effectGraphics.clear();
  }

  update(elapsedMs: number, reducedMotion: boolean): void {
    if (!this.ready || !this.cue) return;
    const effects = this.cue.effects ?? [];
    if (effects.length > 0) {
      const seed = this.cue.id.split("").reduce((sum, char) => sum + char.charCodeAt(0), 0);
      const value = canonicalEffectFrame(effects, elapsedMs, seed, reducedMotion);
      this.camera.scale.set(value.scale);
      this.camera.position.set(LOGICAL_WIDTH / 2 + value.x * LOGICAL_WIDTH, LOGICAL_HEIGHT / 2 + value.y * LOGICAL_HEIGHT);
      this.camera.rotation = value.rotation;
      this.camera.alpha = value.alpha;
      this.camera.tint = value.tint;
      this.blurFilter.strength = value.blur;
      this.noiseFilter.noise = value.noise;
      this.camera.filters = value.blur > 0 || value.noise > 0 ? [this.blurFilter, this.noiseFilter] : null;
      this.drawEffects(value);
      return;
    }
    const effect = this.cue.effect;
    if (!effect || reducedMotion) {
      this.camera.scale.set(1);
      this.camera.position.set(LOGICAL_WIDTH / 2, LOGICAL_HEIGHT / 2);
      return;
    }
    const value = legacyCameraTransform(effect.code, effect.intensity, this.cue.speakerPosition ?? "izquierda", elapsedMs / 1000);
    this.camera.scale.set(value.scale);
    this.camera.position.set(LOGICAL_WIDTH / 2 + value.x * LOGICAL_WIDTH, LOGICAL_HEIGHT / 2 + value.y * LOGICAL_HEIGHT);
  }

  private drawEffects(value: CanonicalEffectFrame): void {
    const graphics = this.effectGraphics;
    graphics.clear();
    if (value.flash) graphics.rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT).fill({ color: value.flash.color, alpha: value.flash.alpha });
    if (value.leak) {
      const x = value.leak.x * LOGICAL_WIDTH;
      graphics.circle(x, LOGICAL_HEIGHT * 0.35, 520).fill({ color: value.leak.color, alpha: value.leak.alpha * 0.24 });
      graphics.circle(x, LOGICAL_HEIGHT * 0.35, 270).fill({ color: value.leak.color, alpha: value.leak.alpha * 0.35 });
    }
    if (value.flare) {
      const x = value.flare.x * LOGICAL_WIDTH;
      const y = value.flare.y * LOGICAL_HEIGHT;
      graphics.circle(x, y, 120).fill({ color: 0xffffff, alpha: value.flare.alpha });
      graphics.circle(x, y, 260).stroke({ color: 0xffd68a, alpha: value.flare.alpha * 0.55, width: 14 });
    }
    if (value.particles) {
      for (let index = 0; index < value.particles.count; index += 1) {
        const x = ((index * 137.5 + value.particles.progress * 170) % 1000) / 1000 * LOGICAL_WIDTH;
        const y = ((index * 83.7 + value.particles.progress * 260) % 1000) / 1000 * LOGICAL_HEIGHT;
        graphics.circle(x, y, 3 + index % 7).fill({ color: 0xffe2b8, alpha: 0.35 + (index % 4) * 0.1 });
      }
    }
  }

  resize(width: number, height: number): void {
    if (!this.ready || width <= 0 || height <= 0) return;
    const scale = Math.min(width / LOGICAL_WIDTH, height / LOGICAL_HEIGHT);
    this.viewport.scale.set(scale);
    this.viewport.position.set((width - LOGICAL_WIDTH * scale) / 2, (height - LOGICAL_HEIGHT * scale) / 2);
  }

  destroy(): void {
    this.destroyRequested = true;
    if (this.host) this.host.dataset.stageStatus = "destroyed";
    this.drawToken += 1;
    for (const url of this.loadedUrls) void Assets.unload(url);
    this.loadedUrls.clear();
    if (this.ready) {
      this.app.destroy(true, { children: true, texture: false, textureSource: false });
      this.ready = false;
    }
  }
}
