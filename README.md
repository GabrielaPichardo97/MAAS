# MAAS

MAAS transforma guiones y diálogos en episodios HTML reproducibles con personajes, fondos, cámara, efectos visuales y controles accesibles. El repositorio conserva juntos el material creativo, la media real, las skills de producción y el reproductor web.

## Demo pública

GitHub Pages publica tres entradas:

- [Reproductor de ejemplo](https://gabrielapichardo97.github.io/MAAS/)
- [Episodio 0 · HTML directo](https://gabrielapichardo97.github.io/MAAS/episodes/episodio-0-prueba-renderizar/)
- [Catálogo interactivo de 34 efectos](https://gabrielapichardo97.github.io/MAAS/effects/)

Cada efecto del catálogo tiene una escena original, contexto narrativo, parámetros, contraindicaciones, nivel de soporte y token canonical-v2.

## Estructura

| Ruta | Contenido |
|---|---|
| `Guiones/` | Guiones históricos y fuentes de episodios. |
| `media/` | PNG y demás media fuente; no se reorganiza ni se publica directamente. |
| `habilidades/` | Skills MAAS para adaptar, dirigir, compilar, resolver media y empaquetar. |
| `maas-html/` | Reproductor React/PixiJS, compilador Python, catálogo y pruebas. |
| `.github/workflows/pages.yml` | Construcción y despliegue reproducible de GitHub Pages. |

## Requisitos

- Python 3.11 o superior.
- Node.js 20 o superior.
- pnpm 9 o superior.

## Inicio rápido

```powershell
cd maas-html
pnpm install
pnpm run content:build
pnpm test
pnpm run test:python
pnpm run build
pnpm run test:e2e
pnpm run preview:player
```

Después abre `http://127.0.0.1:4173/`, `http://127.0.0.1:4173/episodes/episodio-0-prueba-renderizar/` o `http://127.0.0.1:4173/effects/`.

`content:build` inventaría la media disponible, recompila el Episodio 0, resuelve personajes y fondos por ID semántico y copia únicamente los assets requeridos a `maas-html/public/assets/`.

## De diálogo ordinario a HTML

La familia `creativa-*` mantiene el texto hablado sin reescritura:

1. `$creativa-adaptar-dialogo-maas` convierte conversación etiquetada o teatral en `dialogue-adaptation.json`.
2. `$creativa-dirigir-escena-maas` propone actuación, puesta, cámara y efectos; los tokens siguen pendientes.
3. Tras aprobación explícita, `$creativa-ensamblar-episodio-maas` produce `episode-source.json`, `character-map.json` y `presentation.json`.
4. Las skills técnicas compilan canonical-v2, resuelven media real y empaquetan el HTML.

Un diálogo canonical-v2 puede terminar con hasta tres efectos, uno por rol:

```text
Esto cambia todo. {{fx motion.push-in.emphasis.subtle.v1.0.0 role=dominant intensity=0.3 target=speaker}}
```

Consulta los `SKILL.md` de `habilidades/creativa-*` para los contratos completos y las guardas de fidelidad, aprobación y media.

## Contenido y media

- No se inventan rutas a PNG ni se eligen sustituciones silenciosas.
- Preview sólo usa fallbacks declarados; publicación falla ante media requerida ausente.
- Los assets web se resuelven por ID y se publican con nombres SHA-256.
- `media/` permanece como fuente inmutable; `public/assets/` es un artefacto regenerable.

## Pruebas

```powershell
cd maas-html
pnpm run test:python   # contratos, compilador, catálogo, media y suite creativa
pnpm test              # fórmulas de efectos y escenas del catálogo
pnpm run build         # build local
pnpm run build:pages   # build con base /MAAS/
pnpm run test:e2e      # reproductor y catálogo, desktop y móvil
```

## GitHub Pages

El workflow de Pages ejecuta las pruebas, regenera el episodio y su media staged, construye con base `/MAAS/` y despliega `maas-html/dist/player`. Los HTML y JSON publicados no dependen de llamadas a OpenAI, ElevenLabs ni servicios remotos en runtime.
