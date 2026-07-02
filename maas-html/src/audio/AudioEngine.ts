export type AudioBus = "voice" | "sfx" | "music";

export class AudioEngine {
  private context: AudioContext | null = null;
  private master: GainNode | null = null;
  private readonly buses = new Map<AudioBus, GainNode>();
  private readonly active = new Set<AudioBufferSourceNode>();

  async unlock(): Promise<void> {
    if (!this.context) {
      this.context = new AudioContext({ sampleRate: 44_100 });
      this.master = this.context.createGain();
      this.master.connect(this.context.destination);
      for (const name of ["voice", "sfx", "music"] as const) {
        const gain = this.context.createGain();
        gain.connect(this.master);
        this.buses.set(name, gain);
      }
    }
    if (this.context.state !== "running") await this.context.resume();
  }

  async decode(bytes: ArrayBuffer): Promise<AudioBuffer> {
    if (!this.context) throw new Error("Audio bloqueado: llama unlock() desde un gesto de usuario");
    return this.context.decodeAudioData(bytes.slice(0));
  }

  schedule(buffer: AudioBuffer, bus: AudioBus, startAt: number, offset = 0, gain = 1): AudioBufferSourceNode {
    if (!this.context) throw new Error("AudioContext no inicializado");
    const source = this.context.createBufferSource();
    const cueGain = this.context.createGain();
    cueGain.gain.value = gain;
    source.buffer = buffer;
    source.connect(cueGain).connect(this.buses.get(bus)!);
    source.start(startAt, offset);
    this.active.add(source);
    source.addEventListener("ended", () => this.active.delete(source), { once: true });
    return source;
  }

  stopAll(): void {
    for (const source of this.active) {
      try { source.stop(); } catch { /* ya terminó */ }
    }
    this.active.clear();
  }

  setMasterGain(value: number): void {
    if (this.master) this.master.gain.value = Math.max(0, Math.min(1, value));
  }

  async close(): Promise<void> {
    this.stopAll();
    await this.context?.close();
    this.context = null;
    this.master = null;
    this.buses.clear();
  }
}
