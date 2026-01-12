# Operacion local

## Requisitos
- Python 3.11+
- Dependencias en `requirements.txt` y `requirements-dev.txt`

## Ejecutar pipeline local
```bash
python run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db
```

Opciones utiles:
```bash
python run_pipeline.py --no-embeddings --no-retries
python run_pipeline.py --only-resources
python run_pipeline.py --only-reserves
```

## Ejecutar con Docker (pipeline aislado)
```bash
docker build -t ni43-pipeline .
docker run --rm -v "$PWD:/app" ni43-pipeline --data-dir data --output-dir output --sqlite-path output/extractions.db
```

## Demo con Airflow (local)
```bash
docker compose -f docker-compose.airflow.yaml up
```

Notas:
- El DAG es `ni43_extraction`.
- El contenedor monta el repo en `/opt/airflow/repo`.

## Outputs
- `output/metadata.csv`
- `output/resources.csv`
- `output/reserves.csv`
- `output/economics.csv`
- `output/extractions.db`
- `output/run_manifest.json`
- `output/coverage_report.md`
