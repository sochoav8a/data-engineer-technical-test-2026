# Arquitectura del pipeline

## Objetivo
Extraer datos estructurados (metadata, resources, reserves, economics) desde reportes NI 43-101 y persistirlos en CSV/SQLite con trazabilidad por pagina.

## Enfoque two-stage
1) Extraccion de paginas con `pdftotext` y cache local.
2) Seleccion de paginas relevantes por heuristicas (keywords, tablas, densidad numerica) y opcionalmente embeddings.
3) Extraccion de tablas (Camelot + pdfplumber), filtrado y combinacion con texto.
4) LLM (Gemini) con schema estricto para extraer campos exactos.
5) Validaciones de calidad y warnings (no inventar reservas, no convertir unidades).

## Componentes principales
- `selector.py`: ranking de paginas por seccion y expansion por ventana.
- `table_extractor.py`: extraccion de tablas y scoring para priorizar las mas informativas.
- `llm.py`: prompts con JSON schema y validacion Pydantic.
- `quality.py`: reglas de calidad y warnings.
- `storage.py`: CSV/SQLite + normalizacion de `source_pages`.
- `observability.py`: logs estructurados y manifest de corrida.

## Trazabilidad
- `source_pages` se conserva en cada registro.
- `output/run_manifest.json` guarda tiempos, paginas seleccionadas y warnings.
- `output/coverage_report.md` resume cobertura y hallazgos.

## Decisiones clave
- No convertir unidades ni escalar valores para evitar errores.
- Mantener filas por area y totales cuando el reporte lo incluye.
- Si el documento declara ausencia de reservas o costos, se deja vacio y se reporta warning.
