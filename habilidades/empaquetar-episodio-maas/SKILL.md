---
name: empaquetar-episodio-maas
description: Construye y verifica carpetas HTML estáticas por episodio MAAS, copia assets hasheados autorizados, genera build-report.json y aplica controles de seguridad/publicación. Usar después de compilar y antes de desplegar o compartir un episodio.
---

# Empaquetar episodio MAAS

1. Leer `references/output-layout.md`, `references/build-security.md` y `references/publication.md`.
2. Construir primero el player con Vite.
3. Ejecutar `scripts/build_episode.py MANIFEST --player-dist DIST_PLAYER --output DIST_ROOT`.
4. Si se incluyen assets, proporcionar asset manifest y raíz de origen; bloquear cualquier asset no autorizado.
5. Ejecutar `scripts/verify_bundle.py DIST_ROOT --publication`.
6. Publicar únicamente si el reporte es válido.

## Guardas

- No limpiar ni sobrescribir outputs sin autorización explícita.
- No insertar contenido con `innerHTML` ni serializar variables de entorno.
- Mantener rutas relativas y same-origin.
- No permitir llamadas TTS/OpenAI desde el bundle.
