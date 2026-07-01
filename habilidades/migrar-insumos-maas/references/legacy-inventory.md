# Inventario observado del repositorio legado

| Grupo | Conteo | Observaciones |
|---|---:|---|
| JSON de episodios válidos | 37 | 31 procesados y 6 por procesar al auditar. |
| Fondos | 54 | 9 lugares × 6 variantes. |
| Sprites PNG | 145 | 11 directorios; CSV describe 10 personajes. |
| Fondos de transición | 23 | WebP con nombres DALL·E. |
| Audio/video fuente | 132 | 125 MP3, 1 M4A y 6 MP4. |
| Fuentes | 3 TTF por copia | Nanum Gothic está duplicada en dos ubicaciones. |

Anomalías que el script debe reportar:

- `angy` y `condused`.
- Prefijos `Correct_` y duplicados con `(2)`.
- `Tortuga` no aparece en el CSV de personajes.
- `Coneja` tiene cobertura de mirada desigual.
- Nombres de marcas, juegos, bandas sonoras y “Tiene copyright”.
- MP4, JPEG y audios generados mezclados con fuentes.
- Ausencia general de metadata de autor/licencia salvo OFL de Nanum Gothic.

Los conteos son baseline, no una regla eterna. Guardar cada nueva auditoría como JSON para explicar cambios.
