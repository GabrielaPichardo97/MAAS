# Política de resolución

1. Resolver personaje y lugar exactos.
2. Resolver emoción normalizada y mirada `left`.
3. Elegir el candidato de mayor `qualityRank`; desempatar por ID.
4. En preview, recorrer únicamente `fallbacks` declarados y registrar `fallbackApplied`.
5. En publicación, cualquier fallback o ausencia produce `E_ASSET`.
6. Una ausencia genera `media-gaps.json`, `media-gaps.md` y una ficha con nombre sugerido, dimensiones, transparencia, ancla, referencia y cue afectado.

Los reportes distinguen:

- `episode-required`: afecta al episodio actual.
- `catalog-gap`: falta en el paquete editorial estándar.
- `quality-upgrade`: existe media utilizable, pero conviene mejorarla.
