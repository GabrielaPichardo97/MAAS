# Resolución de personajes

El input usa aliases narrativos; el renderer usa IDs de assets.

Prioridad:

1. Mapping persistido del episodio.
2. Alias exacto del asset manifest.
3. Coincidencia Unicode casefold del nombre canónico.
4. En `legacy-v1`, identidad con `W_CHARACTER_IDENTITY` si no se solicitó validación de assets.
5. En `canonical-v1`, `E_CHARACTER`.

Una resolución mediante IA debe ejecutarse fuera del compilador, guardarse como JSON revisable y volver a entrar como mapping. Nunca hacer una llamada no determinista dentro del build.

Formato:

```json
{
  "Jefe": "rinoceronte-rojo",
  "Empleado_1": "cactus"
}
```
