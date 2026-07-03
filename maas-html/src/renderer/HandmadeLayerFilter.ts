import { defaultFilterVert, Filter } from "pixi.js";
import type { LayerEffectFrame } from "./effectEngine";

const fragment = `
in vec2 vTextureCoord;
out vec4 finalColor;

uniform sampler2D uTexture;
uniform vec2 uTexelSize;
uniform float uLineAmplitude;
uniform float uLineWavelength;
uniform float uLineStep;
uniform float uLineSeed;
uniform float uGrainAmount;
uniform float uGrainSize;
uniform float uGrainFiber;
uniform float uGrainStep;
uniform float uGrainSeed;

float hash21(vec2 point) {
  point = fract(point * vec2(123.34, 456.21));
  point += dot(point, point + 45.32);
  return fract(point.x * point.y);
}

float valueNoise(vec2 point) {
  vec2 cell = floor(point);
  vec2 local = fract(point);
  local = local * local * (3.0 - 2.0 * local);
  float a = hash21(cell);
  float b = hash21(cell + vec2(1.0, 0.0));
  float c = hash21(cell + vec2(0.0, 1.0));
  float d = hash21(cell + vec2(1.0, 1.0));
  return mix(mix(a, b, local.x), mix(c, d, local.x), local.y);
}

float luma(vec4 color) {
  if (color.a <= 0.0001) return 0.0;
  return dot(color.rgb / color.a, vec3(0.299, 0.587, 0.114));
}

void main() {
  vec2 uv = vTextureCoord;
  vec4 base = texture(uTexture, uv);
  vec4 color = base;

  if (uLineAmplitude > 0.001) {
    vec4 leftSample = texture(uTexture, clamp(uv - vec2(uTexelSize.x, 0.0), vec2(0.0), vec2(1.0)));
    vec4 rightSample = texture(uTexture, clamp(uv + vec2(uTexelSize.x, 0.0), vec2(0.0), vec2(1.0)));
    vec4 upSample = texture(uTexture, clamp(uv - vec2(0.0, uTexelSize.y), vec2(0.0), vec2(1.0)));
    vec4 downSample = texture(uTexture, clamp(uv + vec2(0.0, uTexelSize.y), vec2(0.0), vec2(1.0)));
    float alphaEdge = abs(leftSample.a - rightSample.a) + abs(upSample.a - downSample.a);
    float colorEdge = abs(luma(leftSample) - luma(rightSample)) + abs(luma(upSample) - luma(downSample));
    float edgeMask = smoothstep(0.025, 0.24, alphaEdge * 1.4 + colorEdge);
    vec2 pixel = uv / max(uTexelSize, vec2(0.000001));
    vec2 field = pixel / max(8.0, uLineWavelength);
    vec2 phase = vec2(uLineSeed * 0.017 + uLineStep * 2.31, uLineSeed * 0.029 - uLineStep * 1.73);
    vec2 displacement = vec2(valueNoise(field + phase), valueNoise(field.yx + phase.yx + 31.7)) * 2.0 - 1.0;
    vec2 warpedUv = clamp(uv + displacement * uTexelSize * uLineAmplitude, vec2(0.0), vec2(1.0));
    vec4 warped = texture(uTexture, warpedUv);
    color = mix(base, warped, edgeMask);
  }

  if (uGrainAmount > 0.0001 && color.a > 0.0001) {
    vec2 pixel = uv / max(uTexelSize, vec2(0.000001));
    vec2 grainCell = floor(pixel / max(1.0, uGrainSize));
    float grain = hash21(grainCell + vec2(uGrainSeed * 0.13, uGrainStep * 17.0)) * 2.0 - 1.0;
    float fiberNoise = valueNoise(vec2(pixel.x * 0.012, pixel.y * 0.085 + uGrainStep * 0.9 + uGrainSeed));
    float fibers = (fiberNoise * 2.0 - 1.0) * uGrainFiber;
    float delta = (grain * (1.0 - uGrainFiber * 0.45) + fibers) * uGrainAmount;
    color.rgb /= color.a;
    color.rgb = clamp(color.rgb + vec3(delta), vec3(0.0), vec3(1.0));
    color.rgb *= color.a;
  }

  finalColor = color;
}
`;

interface HandmadeUniforms {
  uTexelSize: Float32Array;
  uLineAmplitude: number;
  uLineWavelength: number;
  uLineStep: number;
  uLineSeed: number;
  uGrainAmount: number;
  uGrainSize: number;
  uGrainFiber: number;
  uGrainStep: number;
  uGrainSeed: number;
}

export class HandmadeLayerFilter {
  readonly filter: Filter;

  constructor() {
    this.filter = Filter.from({
      gl: { vertex: defaultFilterVert, fragment },
      padding: 6,
      antialias: "inherit",
      resources: {
        handmadeUniforms: {
          uTexelSize: { value: new Float32Array([1, 1]), type: "vec2<f32>" },
          uLineAmplitude: { value: 0, type: "f32" },
          uLineWavelength: { value: 36, type: "f32" },
          uLineStep: { value: 0, type: "f32" },
          uLineSeed: { value: 0, type: "f32" },
          uGrainAmount: { value: 0, type: "f32" },
          uGrainSize: { value: 3, type: "f32" },
          uGrainFiber: { value: 0.35, type: "f32" },
          uGrainStep: { value: 0, type: "f32" },
          uGrainSeed: { value: 0, type: "f32" },
        },
      },
    });
    this.filter.enabled = false;
  }

  update(state: LayerEffectFrame, width: number, height: number): void {
    const uniforms = this.filter.resources.handmadeUniforms.uniforms as HandmadeUniforms;
    uniforms.uTexelSize[0] = 1 / Math.max(1, width);
    uniforms.uTexelSize[1] = 1 / Math.max(1, height);
    uniforms.uLineAmplitude = state.lineBoil?.amplitudePx ?? 0;
    uniforms.uLineWavelength = state.lineBoil?.wavelengthPx ?? 36;
    uniforms.uLineStep = state.lineBoil?.step ?? 0;
    uniforms.uLineSeed = state.lineBoil?.seed ?? 0;
    uniforms.uGrainAmount = state.paperGrain?.amount ?? 0;
    uniforms.uGrainSize = state.paperGrain?.grainPx ?? 3;
    uniforms.uGrainFiber = state.paperGrain?.fiber ?? 0.35;
    uniforms.uGrainStep = state.paperGrain?.step ?? 0;
    uniforms.uGrainSeed = state.paperGrain?.seed ?? 0;
    this.filter.padding = Math.ceil(uniforms.uLineAmplitude) + 2;
    this.filter.enabled = uniforms.uLineAmplitude > 0.001 || uniforms.uGrainAmount > 0.0001;
  }

  destroy(): void {
    this.filter.destroy(true);
  }
}
