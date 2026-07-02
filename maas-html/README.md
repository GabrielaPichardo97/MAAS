# MAAS HTML · primer preview

Este subproyecto convierte el Episodio 0 histórico en un reproductor React + PixiJS estático. Usa los PNG reales de Pato, Cactus, Conejo, Pata, Oficina y Pasillo; sólo prepara los assets requeridos y conserva `media/` intacta.

## Requisitos

- Python 3.11 o superior.
- Node.js 20 o superior.
- pnpm 9 o superior.

En Codex Desktop se pueden usar los runtimes incluidos. En esta máquina, agrega temporalmente el Node empaquetado al `PATH` antes de ejecutar pnpm:

```powershell
$runtime="$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies"
$env:PATH="$runtime\bin;$runtime\node\bin;$env:PATH"
pnpm --version
```

## Primera construcción

Desde `maas-html/`:

```powershell
pnpm install
pnpm run content:validate
pnpm run content:build
pnpm run test:python
pnpm test
pnpm run build
pnpm run package:episode
pnpm run verify:bundle
pnpm run preview:episode
```

Abre `http://127.0.0.1:4173/` o `http://127.0.0.1:4173/episodes/episodio-0-prueba-renderizar/`. El bundle requiere un servidor HTTP; no se promete soporte para `file://`.

`package:episode` protege outputs existentes y falla si `dist/site/` ya fue generado. Para reconstruirlo, elimina únicamente esa carpeta después de revisar que no contiene trabajo manual.

## Canalización de contenido

- `content:normalize`: vuelve a importar el JSON histórico sin modificar el original.
- `content:validate`: aplica el contrato estricto de `episode-source.json`.
- `content:build`: compila `legacy-v1`, sincroniza con el mapa de audio vacío y aplica `presentation.json`.
- `assets:inventory` y `assets:audit`: regeneran la evidencia de los 365 recursos legados.
- `media:catalog` y `media:validate`: crean IDs semánticos y verifican fuentes/hashes.
- `media:report-gaps`: genera `media-gaps.json`, `media-gaps.md` y fichas de producción sin bloquear episodios no afectados.

`content:build` ejecuta automáticamente inventario, catálogo, validación, resolución y staging. Los PNG staged se generan en `public/assets/` y no se versionan.

La salida final vive en `dist/site/`. Consulta [docs/media-guidelines.md](docs/media-guidelines.md) para crear faltantes y [docs/known-differences.md](docs/known-differences.md) para las limitaciones aceptadas.
