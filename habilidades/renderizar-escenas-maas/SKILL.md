---
name: renderizar-escenas-maas
description: Implementa el stage React/PixiJS que compone fondos, sprites, texto, orientación y cámara desde episode.manifest.json. Usar al construir el reproductor, adaptar layouts horizontal/vertical, implementar resize o mejorar accesibilidad visual.
---

# Renderizar escenas MAAS

1. Validar el manifiesto con `$definir-contratos-maas`.
2. Leer `references/layouts.md` antes de posicionar assets.
3. Crear el stage según `references/pixi-renderer.md` y reutilizar `assets/pixi-stage-template/`.
4. Renderizar escena estática a una textura; después aplicar temblor y cámara mediante `$reproducir-efectos-maas`.
5. Integrar controles y adaptación responsiva según `references/responsive-player.md`.
6. Exponer captions en DOM aunque el texto visual esté dentro de Pixi.

## Invariantes

- Coordenadas internas enteras sobre 1920×1080.
- Escalar el canvas con `contain`; no recalcular layouts desde el viewport.
- Conservar aspect ratio, alpha y orden de capas.
- Destruir texturas, listeners y `Application` al desmontar.
