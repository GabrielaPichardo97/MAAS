# Gramática del guion

## Índice

1. EBNF
2. Duraciones
3. Diálogo y OSD
4. Lugares y transiciones
5. Efectos
6. Compatibilidad legado

## 1. EBNF

```ebnf
document      = { blank | transition | speech }, EOF ;
speech        = header, newline, { blank | dialogue | osd }, place ;
header        = "[", character, "]", ws, "(", duration, "|", emotion, "|", stage, ")" ;
dialogue      = text, ws, camera ;
osd           = "OSD", ws, "(", sound, ")", ws, camera ;
place         = "**", place-name, "**" ;
transition    = "---", transition-text, "---" ;
camera        = "(", effect, [ "*", positive-number ], [ ws, target ], ")" ;
effect        = "ES" | "ZI" | "ZO" | "PA-I" | "PA-D" | "TI-A" | "TI-B" | "PP" ;
```

Los delimitadores `|` del header son obligatorios. `character`, `emotion`, `stage`, `text`, `sound`, `target` y nombres no pueden quedar vacíos.

## 2. Duraciones

Se aceptan `N segundo`, `N segundos` y `MM:SS`. Se convierten a `declaredDurationMs`. En `legacy-v1`, si existe audio:

```text
resolvedDurationMs = max(2000, floor((audioMs + 200) / 1000) * 1000)
```

En `canonical-v1`:

```text
resolvedDurationMs = max(declaredDurationMs, audioMs + 200)
```

Si no hay audio, se usa la duración declarada. Nunca sobrescribir el valor declarado.

## 3. Diálogo y OSD

- Cada línea de diálogo requiere exactamente un camera token al final.
- Paréntesis internos en el texto deben escaparse como `\(` y `\)` o reemplazarse por signos editoriales.
- `OSD` crea un cue `sfx`; el texto entre el primer paréntesis es la clave sonora.
- `OSD (...)` y `OSD (… )` representan silencio explícito, no ausencia de cue.
- `Bip bip` se conserva semánticamente y se presenta como `%!&$# >:(` solo en el renderer legado.

## 4. Lugares y transiciones

- Cada bloque de intervenciones termina en un lugar.
- El lugar se compara de forma Unicode case-insensitive contra `asset-manifest.json`.
- Un lugar desconocido es error. No elegir un fondo al azar.
- Una transición separa bloques y genera un cue propio; no pertenece al diálogo anterior.

## 5. Efectos

La intensidad predeterminada es `1.0` y debe ser mayor que cero. `PP` puede incluir objetivo: `(PP Pato)`. Otros efectos no admiten objetivo en modo estricto.

## 6. Compatibilidad legado

`ZO1.2`, `PA-D1.2` y equivalentes se normalizan a `ZO*1.2` y `PA-D*1.2` solo en modo legado, con `W_LEGACY_EFFECT_SYNTAX`. Múltiples OSD consecutivos no se eliminan: se conservan y se reportan para revisión.
