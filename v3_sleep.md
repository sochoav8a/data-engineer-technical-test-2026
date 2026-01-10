# v3_sleep

## Como ejecutar

### Local
```
python run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db
```

### Con flags
- Sin embeddings ni retries:
```
python run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db --no-embeddings --no-retries
```
- Paralelizar:
```
python run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db --workers 3
```

## Tecnologias usadas (y por que)
- google-genai: LLM estable y con buena ventana de contexto.
- Pydantic: esquemas estrictos para evitar alucinaciones de formato.
- pdfplumber/camelot: intento de tablas deterministas antes del LLM.
- SQLite + CSV: salida estructurada facil de inspeccionar.

## Desafios y limitaciones
- Tablas embebidas o con layout complejo no siempre se extraen.
- Algunas secciones estan narradas, no tabuladas.
- Costos y tiempo suben al usar embeddings + retries.

## Propuesta de produccion (1000-10k PDFs)
- Ingesta: S3 + evento a Lambda o cola.
- Orquestacion: Airflow/Dagster con workers paralelos.
- Procesamiento: contenedores con escalado horizontal.
- Observabilidad: logs estructurados + metricas por PDF.
- Calidad: validaciones por reglas (no inventar reservas, no convertir unidades).
- Costos: modelo por corrida + cache de embeddings + retries selectivos.
