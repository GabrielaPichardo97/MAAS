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

El laboratorio de efectos vive en `http://127.0.0.1:4173/effects/`: permite buscar las 34 entradas, filtrar por familia o nivel de soporte, revisar parámetros y contraindicaciones, y copiar un token canonical-v2.

Cada efecto incluye una escena narrativa original para juzgarlo dentro de una intención dramática concreta. La versión pública se despliega con GitHub Actions en `https://gabrielapichardo97.github.io/MAAS/effects/`.

El reproductor también queda publicado en `https://gabrielapichardo97.github.io/MAAS/` y como HTML directo en `https://gabrielapichardo97.github.io/MAAS/episodes/episodio-0-prueba-renderizar/`.

Para abrir el build que incluye el laboratorio, ejecuta `pnpm run preview:player` después de `pnpm run build`.

`package:episode` protege outputs existentes y falla si `dist/site/` ya fue generado. Para reconstruirlo, elimina únicamente esa carpeta después de revisar que no contiene trabajo manual.

## Canalización de contenido

- `content:normalize`: vuelve a importar el JSON histórico sin modificar el original.
- `content:validate`: aplica el contrato estricto de `episode-source.json`.
- `content:build`: compila `legacy-v1`, sincroniza con el mapa de audio vacío y aplica `presentation.json`.
- `assets:inventory` y `assets:audit`: regeneran la evidencia de los 365 recursos legados.
- `media:catalog` y `media:validate`: crean IDs semánticos y verifican fuentes/hashes.
- `media:report-gaps`: genera `media-gaps.json`, `media-gaps.md` y fichas de producción sin bloquear episodios no afectados.

`content:build` ejecuta automáticamente inventario, catálogo, validación, resolución y staging. Los PNG staged se generan en `public/assets/` y no se versionan.

## Efectos canonical-v2

Un diálogo admite hasta tres roles explícitos:

```text
Esto cambia todo. {{fx motion.push-in.emphasis.subtle.v1.0.0 role=dominant intensity=0.3 target=speaker}}
```

Compila con `python tools/scripts/compile_episode.py INPUT --profile canonical-v2 --effect-catalog public/effects-catalog.json`. Un efecto asistido o preprocesado falla si falta su requisito e informa su alternativa; no se sustituye silenciosamente.

La salida final vive en `dist/site/`. Consulta [docs/media-guidelines.md](docs/media-guidelines.md) para crear faltantes y [docs/known-differences.md](docs/known-differences.md) para las limitaciones aceptadas.
