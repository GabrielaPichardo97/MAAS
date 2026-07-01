# Diferencias conocidas

Toda entrada debe contener: ID, perfil, fecha, comportamiento legado, comportamiento web, causa, impacto, evidencia, decisión y aprobador.

Baseline inicial:

- Rasterización de Nanum Gothic puede variar ligeramente entre PIL y navegador; no justifica diferencias de wrapping.
- Compresión JPEG/MP4 introduce ruido que reduce SSIM en bordes.
- `PA-I` y `PA-D` son idénticos en legacy y opuestos en canonical.
- `ES` conserva temblor en legacy y es estático en canonical.
- canonical conserva milisegundos; legacy trunca a segundos enteros.
- La selección aleatoria histórica sin seed no es reproducible; el baseline debe fijar el asset observado y el nuevo seed.

No añadir tolerancias globales para resolver un caso aislado.
