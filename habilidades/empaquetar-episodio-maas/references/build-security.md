# Seguridad de build

- Validar `episodeId` antes de usarlo como ruta.
- Resolver rutas y comprobar que permanezcan dentro de sus raíces.
- Prohibir `..`, rutas absolutas, symlinks escapando la raíz y protocolos en paths de assets.
- Escapar texto mediante APIs de React/Pixi; prohibir `dangerouslySetInnerHTML` e `innerHTML`.
- CSP mínima: `default-src 'self'`, media/img/connect/script restringidos a self; `data:` solo para imagen aprobada.
- Buscar patrones de secretos: `OPENAI_API_KEY`, `ELEVEN`, `GOOGLE_SERVICE_ACCOUNT`, claves PEM y tokens Bearer.
- Source maps de producción son optativos y no deben contener secretos ni paths privados.
- Dependencias remotas/CDN están prohibidas durante playback.
