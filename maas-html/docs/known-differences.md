# Diferencias conocidas del primer preview

Perfil: `legacy-v1`. Fecha de baseline: 2026-07-01.

| ID | Comportamiento legado | Comportamiento web | Causa e impacto | Decisión |
|---|---|---|---|---|
| PREVIEW-001 | Usa sprites y fondos rasterizados históricos. | Usa los PNG reales de Pato, Cactus, Conejo, Pata, Oficina y Pasillo, seleccionados por catálogo y hash. | Los masters actuales son 500×500 y 960×540; puede variar la nitidez al escalar. | Aceptar los PNG actuales y registrar mayor resolución como mejora, no como bloqueo. |
| PREVIEW-002 | Reproduce voz, SFX y música. | Conserva captions y tiempos, pero reproduce silencio. | No se incluyen assets sonoros ni TTS; no existe gate de drift de audio. | Habilitar audio sólo después de contar con assets autorizados. |
| PREVIEW-003 | Aplica temblor basado en bordes a 25 FPS. | Aplica únicamente cámara, paneo, tilt, zoom y PP. | El shader y edge maps todavía no están implementados. | No declarar paridad visual; respetar `prefers-reduced-motion`. |
| PREVIEW-004 | Produce composiciones horizontal y vertical independientes. | Usa un stage horizontal 1920×1080 con `contain` responsivo. | Existen variantes portrait laterales legadas, pero no fondos portrait nativos 1080×1920. | Validar landscape; las 27 fichas portrait quedan documentadas como huecos generales. |

`canonical-v1` no está aprobado. El único gate automático de esta entrega es la timeline determinista y la verificación funcional del bundle local.
