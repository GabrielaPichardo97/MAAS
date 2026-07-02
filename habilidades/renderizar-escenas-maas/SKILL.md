---
name: renderizar-escenas-maas
description: Implementa el stage React/PixiJS y el laboratorio que componen fondos, sprites, texto, orientación, cámara y stacks canonical-v2 desde episode.manifest.json. Usar al construir el reproductor, previews de efectos, layouts, resize o accesibilidad visual.
---

# Renderizar escenas MAAS

1. Validar el manifiesto con `$definir-contratos-maas`.
2. Leer `references/layouts.md` antes de posicionar assets.
3. Resolver `spriteAssetId`, `backgroundAssetId` y URLs mediante `$resolver-media-maas`; no generar placeholders silenciosos.
4. Crear el stage según `references/pixi-renderer.md` y reutilizar `assets/pixi-stage-template/`.
5. Renderizar escena estática a una textura; después aplicar temblor y cámara mediante `$reproducir-efectos-maas`.
6. Integrar controles y adaptación responsiva según `references/responsive-player.md`.
7. Exponer captions en DOM aunque el texto visual esté dentro de Pixi.
8. Para canonical-v2, separar cámara y overlays y mostrar soporte, requisitos y fallback reales en `/effects/`.

## Invariantes

- Consumir la dirección ya aprobada desde el manifiesto; no reinterpretar el diálogo ni escoger efectos durante render.
- Coordenadas internas enteras sobre 1920×1080.
- Escalar el canvas con `contain`; no recalcular layouts desde el viewport.
- Conservar aspect ratio, alpha y orden de capas.
- Destruir texturas, listeners y `Application` al desmontar.
- Si falta media, mostrar el `requestId` y producir una ficha; publicación debe fallar.
