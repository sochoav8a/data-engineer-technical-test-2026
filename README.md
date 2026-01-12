# data-engineer-technical-test-2026

Pipeline para extraer datos estructurados de reportes NI 43-101.

## Quickstart
```
python run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db
```

## Outputs
- `output/metadata.csv`, `output/resources.csv`, `output/reserves.csv`, `output/economics.csv`
- `output/json/*.json`
- `output/extractions.db`
- `output/run_manifest.json` + logs en `output/logs/run.log`

## Scripts utiles
- Reporte de cobertura:
```
python scripts/report_coverage.py --manifest output/run_manifest.json --csv-dir output --output output/coverage_report.md
```
- Estimacion de costo:
```
python scripts/estimate_cost.py --manifest output/run_manifest.json --output-dir output
```

## Flags comunes
- `--no-embeddings`, `--no-retries`
- `--workers N`
- `--only-resources`, `--only-reserves`


La documentación de los procesos se pueden encontrar en la carpeta docs/