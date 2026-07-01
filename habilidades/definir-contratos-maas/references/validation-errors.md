# Códigos de validación

## Errores

| Código | Condición |
|---|---|
| `E_JSON_INVALID` | JSON ilegible o UTF-8 inválido. |
| `E_SCHEMA` | Campo ausente, adicional o con tipo/formato inválido. |
| `E_SCRIPT_HEADER` | Header incompleto o mal delimitado. |
| `E_DURATION` | Duración inválida o no positiva. |
| `E_DIALOGUE_CAMERA` | Diálogo sin camera token válido. |
| `E_EFFECT` | Código, intensidad u objetivo inválido. |
| `E_PLACE` | Lugar vacío, desconocido o ausente. |
| `E_CHARACTER` | Personaje no resoluble. |
| `E_EMOTION` | Emoción sin mapping o fallback explícito. |
| `E_ASSET` | Asset ausente, corrupto o incompatible. |
| `E_LICENSE` | Asset no autorizado para publicar. |
| `E_TIMELINE` | Cue negativo, desordenado o con solapamiento ilegal. |
| `E_SECRET` | Posible credencial dentro del bundle. |
| `E_HTML_INJECTION` | Uso de una API que interpreta HTML sin escapar. |
| `E_REMOTE_RUNTIME` | Dependencia o URL remota en una salida publicable. |

## Advertencias

| Código | Condición |
|---|---|
| `W_LEGACY_INPUT` | Se usó el adaptador de cinco campos históricos. |
| `W_LEGACY_DATE_TIMEZONE` | Fecha histórica sin zona horaria. |
| `W_LEGACY_EFFECT_SYNTAX` | Intensidad sin `*`. |
| `W_EDITORIAL_PREFIX` | Texto anterior al primer header. |
| `W_UNKNOWN_HEADER_DURATION` | Duración declarada sustituida por audio. |
| `W_FALLBACK_EXPRESSION` | Se usó una expresión alternativa declarada. |
| `W_UNUSED_STAGE_DIRECTION` | Dirección actoral preservada pero no animada. |
| `W_CHARACTER_IDENTITY` | Alias conservado como ID en legacy sin catálogo. |
| `W_EMOTION_HAPPY_FALLBACK` | Emoción desconocida convertida a happy en legacy. |
| `W_TRAILING_DIALOGUE_METADATA` | Metadata apareció después del camera token. |
| `W_MISSING_CAMERA_STATIC` | Línea legacy sin cámara recuperada como ES. |
| `W_LEGACY_HEADER_PARENTHESES` | Header legacy tenía paréntesis extra. |
| `W_ASSET_NAMING` | Nombre de asset histórico irregular. |
| `W_LICENSE_UNKNOWN` | Licencia todavía no documentada. |
| `W_DUPLICATE_CONTENT` | Dos IDs comparten el mismo SHA-256. |

Formato:

```json
{
  "code": "E_EFFECT",
  "severity": "error",
  "line": 12,
  "column": 28,
  "message": "La intensidad debe ser mayor que cero.",
  "suggestion": "Usa (ZI*1.2)."
}
```
