---
name: migrar-insumos-maas
description: Inventaría, clasifica, mide, deduplica y audita licencias de fondos, sprites, fuentes, voces, música, SFX, transiciones y endings de un repositorio MAAS legado. Usar antes de copiar assets al nuevo repositorio o publicar un episodio HTML.
---

# Migrar insumos MAAS

1. Leer `references/asset-contract.md` y `references/licensing-policy.md`.
2. Ejecutar `scripts/build_asset_manifest.py LEGACY_ROOT --output asset-manifest.json`.
3. Revisar `references/legacy-inventory.md` y comparar conteos/anomalías.
4. Completar procedencia, autor, licencia y `allowedForPublish` mediante un archivo de overrides revisado.
5. Ejecutar `scripts/audit_assets.py asset-manifest.json --publication` antes de copiar o publicar.
6. Invocar `$resolver-media-maas catalog` para crear IDs semánticos sin renombrar las fuentes.
7. Copiar solo assets referenciados y autorizados; nunca copiar `Videos/`, `media/clips/` o `media/Caps/` como fuente del nuevo producto.

## Guardas

- No inferir licencia desde un nombre que diga "no copyright".
- Usar SHA-256 para deduplicar; no borrar duplicados automáticamente.
- Conservar rutas relativas y no seguir symlinks fuera de la raíz.
- Marcar metadata desconocida como `null`, no inventarla.
- No rechazar PNG existentes por tamaño, nombre o ausencia de derivados WebP; documentar mejoras como `quality-upgrade`.
