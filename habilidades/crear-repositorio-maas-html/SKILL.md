---
name: crear-repositorio-maas-html
description: Crea desde cero un repositorio MAAS HTML con React, TypeScript, Vite, PixiJS, compilador Python, schemas, pruebas y CI. Usar para iniciar la migración completa o reconstruir el starter sin depender del renderer de video legado.
---

# Crear repositorio MAAS HTML

1. Ejecutar `scripts/check_prerequisites.py`.
2. Leer `references/architecture.md` y confirmar que el destino está vacío.
3. Ejecutar `scripts/scaffold_repository.py DESTINO` para copiar el starter, schemas y herramientas de las skills hermanas.
4. Ejecutar en el nuevo repositorio `python -m unittest discover tests/python`, `npm install`, `npm test` y `npm run build`.
5. Invocar, en orden: `$definir-contratos-maas`, `$migrar-insumos-maas`, `$compilar-guion-maas`, `$reproducir-efectos-maas`, `$renderizar-escenas-maas`, `$sincronizar-audio-maas`, `$empaquetar-episodio-maas` y `$auditar-paridad-maas`.

## Guardas

- No inicializar sobre un directorio no vacío sin `--force`; aun con `--force`, no sobrescribir archivos existentes.
- No copiar outputs MP4, cachés, secretos ni assets sin licencia.
- Mantener Python como herramienta de build y TypeScript como runtime del navegador.
- Usar `legacy-v1` hasta que la auditoría apruebe `canonical-v1`.
