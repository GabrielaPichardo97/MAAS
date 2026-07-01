# Contrato de `episode-source.json`

## Índice

1. Formato estricto
2. Adaptador legado
3. Normalización
4. Ejemplo completo

## 1. Formato estricto

El archivo debe ser JSON UTF-8 y cumplir `episode-source.schema.json`.

| Campo | Tipo | Regla |
|---|---|---|
| `schemaVersion` | string | Constante `1.0`. |
| `episodeId` | string | `^[a-z0-9]+(?:-[a-z0-9]+)*$`, máximo 100 caracteres. |
| `title` | string | Entre 1 y 200 caracteres después de trim. |
| `language` | string | Etiqueta BCP 47 básica, por ejemplo `es-MX`. |
| `status` | enum | `draft`, `ready` o `published`. |
| `seed` | integer | 0 a 2,147,483,647. Si falta, derivar de SHA-256 de `episodeId`. |
| `source` | object | Opcional; `url`, `createdAt` e `importedFrom`. |
| `content` | string | Guion no vacío descrito en `script-grammar.md`. |

Campos adicionales están prohibidos para detectar errores tipográficos.

## 2. Adaptador legado

El modo `legacy` acepta `title`, `content`, `url`, `status` y `sendDate`.

- `status=procesar` se mapea a `ready`.
- `status=procesado` se mapea a `published`.
- `sendDate=YYYYMMDDhhmmss` se convierte a ISO 8601 sin inventar zona horaria; se registra `W_LEGACY_DATE_TIMEZONE`.
- `episodeId` se deriva del título mediante Unicode NFKD, eliminación de diacríticos y slug ASCII.
- Un campo legado desconocido se conserva únicamente en el reporte de importación.

El adaptador devuelve un documento nuevo; nunca renombra, borra o reescribe el original.

## 3. Normalización

- Decodificar estrictamente como UTF-8; no reemplazar bytes inválidos.
- Convertir CRLF y CR a LF.
- Eliminar BOM inicial.
- Conservar texto y puntuación; no eliminar apóstrofes.
- Permitir encabezados editoriales antes del primer personaje, pero emitir advertencia.
- Usar `seed` para toda selección de transición, variante sonora o fallback aprobado.

## 4. Ejemplo completo

```json
{
  "schemaVersion": "1.0",
  "episodeId": "episodio-28-libertad-financiera",
  "title": "Libertad financiera",
  "language": "es-MX",
  "status": "ready",
  "seed": 2801,
  "source": {
    "url": "https://example.test/documento",
    "createdAt": "2025-04-05T08:20:55Z",
    "importedFrom": "MAAS/Guiones/capitulos"
  },
  "content": "[Pato] (4 segundos | Intriga | Inclina la cabeza)\n¿Sabías la noticia? (ZI*1.2)\nOSD (Dum!) (PP Pato)\n\n**CAFETERÍA**"
}
```
