import { Application, Assets, Container, Sprite, Text, TextStyle } from "pixi.js";
import { legacyCameraTransform, type EffectCode } from "./effectMath";

export interface VisualCue {
  id: string;
  text: string;
  backgroundUrl?: string;
  spriteUrl?: string;
  speakerPosition?: "izquierda" | "derecha";
  effect: { code: EffectCode; intensity: number };
}

export class MaasStage {
  private app = new Application();
  private viewport = new Container();
  private camera = new Container();
  private currentCue?: VisualCue;

  async init(host: HTMLElement): Promise<void> {
    await this.app.init({ background: "#000", resizeTo: host, antialias: true });
    host.appendChild(this.app.canvas);
    this.viewport.addChild(this.camera);
    this.app.stage.addChild(this.viewport);
    this.resize(host.clientWidth, host.clientHeight);
  }

  async show(cue: VisualCue): Promise<void> {
    this.currentCue = cue;
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
      sprite.setSize(854, 854);
      sprite.position.set(cue.speakerPosition === "derecha" ? 968 : 300, 308);
      this.camera.addChild(sprite);
    }
    const text = new Text({ text: cue.text, style: new TextStyle({ fontFamily: "Nanum Gothic", fontSize: 80, fill: "#000" }) });
    text.position.set(cue.speakerPosition === "derecha" ? 348 : 1054, cue.speakerPosition === "derecha" ? 70 : 98);
    this.camera.addChild(text);
    this.camera.pivot.set(960, 540);
    this.camera.position.set(960, 540);
  }

  update(elapsedMs: number): void {
    if (!this.currentCue) return;
    const value = legacyCameraTransform(
      this.currentCue.effect.code,
      this.currentCue.effect.intensity,
      this.currentCue.speakerPosition ?? "izquierda",
      elapsedMs / 1000,
    );
    this.camera.scale.set(value.scale);
    this.camera.position.set(960 + value.xFraction * 1920, 540 + value.yFraction * 1080);
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
