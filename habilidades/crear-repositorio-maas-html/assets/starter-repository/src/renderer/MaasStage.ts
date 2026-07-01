import { Application, Assets, Container, Sprite, Text, TextStyle } from "pixi.js";
import type { TimelineCue } from "../types";
import { legacyCameraTransform } from "./effectMath";

export class MaasStage {
  private readonly app = new Application();
  private readonly viewport = new Container();
  private readonly camera = new Container();
  private cue?: TimelineCue;

  async init(host: HTMLElement): Promise<void> {
    await this.app.init({ background: "#f7f5ef", resizeTo: host, antialias: true });
    host.appendChild(this.app.canvas);
    this.viewport.addChild(this.camera);
    this.app.stage.addChild(this.viewport);
    this.resize(host.clientWidth, host.clientHeight);
  }

  async show(cue: TimelineCue): Promise<void> {
    this.cue = cue;
    this.camera.removeChildren().forEach((child) => child.destroy());
    if (cue.backgroundUrl) {
      const texture = await Assets.load(cue.backgroundUrl);
      const background = new Sprite(texture);
      background.width = 1920;
      background.height = 1080;
      this.camera.addChild(background);
    }
    if (cue.spriteUrl) {
      const texture = await Assets.load(cue.spriteUrl);
      const sprite = new Sprite(texture);
      sprite.width = 854;
      sprite.height = 854;
      sprite.position.set(cue.speakerPosition === "derecha" ? 968 : 300, 308);
      this.camera.addChild(sprite);
    }
    const visualText = new Text({ text: cue.text ?? "", style: new TextStyle({ fontFamily: "Nanum Gothic, sans-serif", fontSize: 80, fill: "#111", wordWrap: true, wordWrapWidth: 500 }) });
    visualText.position.set(cue.speakerPosition === "derecha" ? 348 : 1054, cue.speakerPosition === "derecha" ? 70 : 98);
    this.camera.addChild(visualText);
    this.camera.pivot.set(960, 540);
    this.camera.position.set(960, 540);
  }

  update(elapsedMs: number): void {
    if (!this.cue?.effect) return;
    const value = legacyCameraTransform(this.cue.effect.code, this.cue.effect.intensity, this.cue.speakerPosition ?? "izquierda", elapsedMs / 1000);
    this.camera.scale.set(value.scale);
    this.camera.position.set(960 + value.x * 1920, 540 + value.y * 1080);
  }

  resize(width: number, height: number): void {
    const scale = Math.min(width / 1920, height / 1080);
    this.viewport.scale.set(scale);
    this.viewport.position.set((width - 1920 * scale) / 2, (height - 1080 * scale) / 2);
  }

  destroy(): void {
    this.app.destroy(true, { children: true, texture: false, textureSource: false });
  }
}
