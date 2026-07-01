# Gate de publicación

Publicar solo si:

1. Input, manifiesto y timeline son válidos.
2. Todos los assets referenciados existen y su SHA coincide.
3. Todos tienen `allowedForPublish=true`.
4. No hay secretos, URLs remotas o rutas absolutas.
5. Las pruebas de paridad y accesibilidad requeridas pasaron.
6. `build-report.json` registra versiones y warnings aceptados.

Un warning de licencia desconocida se eleva a `E_LICENSE` en `--publication`. Preview puede usar placeholders locales claramente identificados.
