---
name: creativa-ensamblar-episodio-maas
description: Ensambla una dirección cinematográfica aprobada en episode-source.json canonical-v2, mapa de personajes y presentación de media, y coordina validación, compilación, resolución y empaquetado HTML. Usar sólo después de aprobación editorial; bloquea diálogo alterado, efectos inválidos y media requerida ausente.
---

# Creativa · Ensamblar episodio MAAS

1. Leer `references/assembly-pipeline.md`.
2. Validar adaptación y dirección con sus skills; exigir `approval.status: approved`.
3. Ejecutar `scripts/assemble_episode.py DIRECTION --adaptation ADAPTATION --effect-catalog CATALOG --output-source episode-source.json --character-map character-map.json --presentation presentation.json`.
4. Invocar `$definir-contratos-maas` y `$compilar-guion-maas` con perfil `canonical-v2` y el catálogo exacto.
5. Invocar `$resolver-media-maas resolve` en modo `publication`. Si falla, ejecutar `scripts/render_media_gaps.py` sobre `episode-gaps.json` y detenerse.
6. Invocar `$resolver-media-maas stage`; no copiar media por rutas inventadas.
7. Construir el player, invocar `$empaquetar-episodio-maas` y verificar el bundle con `--publication`.

## Guardas

- No ensamblar una propuesta pendiente, rechazada o sin identidad/fecha de aprobación.
- No alterar `verbatimText`, elegir fallbacks de media ni omitir requisitos de efectos.
- No sobrescribir outputs existentes ni modificar `media/`.
- Conservar source, manifest, reporte de huecos y build report como evidencia del flujo.
