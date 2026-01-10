# comparacion_embeddings_retries

## Contexto
- PDFs: 5 (Aris, Alpha One, Colombia Crest, Mineros, Sunward).
- Objetivo: comparar cobertura y tiempo con y sin embeddings/retries.
- Nota: el output se sobreescribe en cada corrida; la comparacion usa un run con embeddings+retries vs un run sin ambos.

## Runs

### A) Embeddings + retries
Comando:
```
python run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db
```

### B) No embeddings + no retries
Comando:
```
python run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db --no-embeddings --no-retries
```

## Conclusiones resumidas
- Para estos 5 PDFs, embeddings/retries no aumentan reservas ni economia; la mejora es marginal en resources.
- El costo/tiempo baja significativamente sin embeddings ni retries.
- Si futuros PDFs tienen mas ruido o tablas dispersas, embeddings/retries pueden recuperar datos, pero hoy el valor es limitado.
