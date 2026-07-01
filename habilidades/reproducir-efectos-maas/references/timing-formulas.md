# Fórmulas de tiempo

## Reproducción

| Elemento | `legacy-v1` | `canonical-v1` |
|---|---|---|
| Diálogo con audio | `max(2000,floor((audioMs+200)/1000)*1000)` | `max(declaredMs,audioMs+200)` |
| Diálogo sin audio | reparto declarado, mínimo 2000 ms | reparto declarado, mínimo 40 ms |
| Transición | 1900 ms | configurable, default 1900 ms |
| Fade de transición | 500 ms | configurable |
| Consejo | 40 ms | desactivado por defecto |
| Frame de temblor | `floor(t*25)` | igual si está activo |
| Velocidad final | 1.0 | 1.0 |

`startMs` se acumula con enteros. Web Audio programa cues contra un único `AudioContext.currentTime`; no encadenar `setTimeout`.

## Procesamiento histórico

Las pausas de 6 s por TTS, 2 s por escena y 1 s por imagen no afectan el video y no se migran. El reporte nuevo mide validación, inventario, TTS, compilación, fixtures, bundle y total mediante reloj monotónico.
