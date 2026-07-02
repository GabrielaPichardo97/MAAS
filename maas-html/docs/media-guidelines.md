# Guía de media MAAS para HTML

## Principio

Los PNG existentes son válidos. Tamaño, nombre irregular o falta de WebP nunca bloquean un episodio si el asset requerido existe y su hash coincide.

## Personajes

- Fuente: PNG RGBA en sRGB y fondo transparente.
- Aceptado actualmente: 500×500; recomendado para nuevos: 1024×1024.
- Mantener escala, centro, línea de suelo y padding del personaje de referencia.
- Crear una mirada canónica `left`; Pixi genera la contraria con `mirrorX`.
- Nombre sugerido: `characters/<personaje>/<emotion>.left.png`.
- Evitar halos: los píxeles transparentes no deben conservar un matte blanco u oscuro visible al escalar.

## Fondos

- Aceptado actualmente: 960×540; recomendado para nuevos landscape: 1920×1080.
- Variantes: `center`, `character-left` y `character-right`.
- Para portrait canónico futuro: 1080×1920 nativo; las variantes laterales actuales siguen siendo válidas para `legacy-v1`.
- Nombre sugerido: `backgrounds/<lugar>/<orientation>.<layout>.png`.

## Faltantes

`reports/media-gaps.json` es la fuente de verdad automatizable. `reports/media-gaps.md` resume los huecos y `reports/media-requests/<catalog-sha>/` contiene una ficha JSON por imagen a producir.

Un hueco `catalog-gap` no bloquea. Sólo `episode-required` bloquea publicación; preview usa fallbacks declarados o muestra el `requestId` en pantalla.
