# Política de audio en navegador

- Mostrar botón “Iniciar episodio” antes de crear/reanudar el `AudioContext`.
- Mantener controles de play, pause, seek y volumen accesibles por teclado.
- Usar `AudioBufferSourceNode` por reproducción; no reutilizar nodos terminados.
- Crear buses `master`, `voice`, `sfx`, `music` con `GainNode`.
- Programar fades mediante `linearRampToValueAtTime`.
- Suspender audio al ocultarse la página solo si la reproducción se pausa en paralelo.
- Recuperar estados `suspended` e `interrupted` sin adelantar la timeline.
- No depender de carga remota durante playback; precargar y validar assets usados.
- Mantener captions visibles aunque el audio falle.
