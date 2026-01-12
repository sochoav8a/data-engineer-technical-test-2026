# Escalado en cloud (propuesta)

## Objetivo
Procesar 1k-10k PDFs con trazabilidad, control de costos y observabilidad.

## Arquitectura propuesta
- **Ingesta**: bucket (S3/GCS) con evento por nuevo PDF.
- **Cola**: SQS/PubSub para desacoplar ingestiones.
- **Orquestacion**: Airflow/Dagster/Step Functions para batches y retries.
- **Compute**: contenedores en K8s/Batch/Lambda segun tamano de PDF.
- **LLM**: Gemini/OpenAI con rate limits y cuotas por cliente.
- **Storage**: DB relacional (Postgres) + data lake (S3) para outputs.
- **Observabilidad**: logs estructurados, metricas por etapa, alertas.

## Estrategia de paralelismo
- PDFs son independientes: se procesan en paralelo por documento.
- Limitar concurrencia por proveedor LLM.
- Cache de paginas y embeddings por hash de archivo.

## Control de costos
- Procesar solo paginas relevantes (two-stage).
- Desactivar embeddings o retries si el documento es corto.
- Medir tokens y tiempo por PDF para ajustar modelos.

## Seguridad
- Secrets en vault/secret manager.
- Control de acceso a buckets y DB.
- Registro de auditoria por `run_id`.
