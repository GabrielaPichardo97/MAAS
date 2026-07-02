# Pipeline de ensamblado

Entradas obligatorias:

- `dialogue-adaptation.json` validado y sin diagnósticos bloqueantes.
- `cinematic-direction.json` cuyo hash apunte a esa adaptación y esté aprobado.
- Catálogo canonical-v2 versionado.

Salidas deterministas:

- `episode-source.json`: contrato existente, perfil posterior canonical-v2.
- `character-map.json`: alias editorial a ID semántico.
- `presentation.json`: label y posición de personajes, más IDs de lugares.

Después del ensamblado, usar las herramientas técnicas existentes. Resolver media en modo publicación: cualquier fallback o ausencia genera `E_ASSET`, se documenta en JSON/Markdown y bloquea el HTML final.
