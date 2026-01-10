# Analisis de fallas (reservas y economia)

## Contexto
- Basado en logs y un escaneo de keywords en texto completo (cache de paginas).
- El extractor de tablas reporto 0 tablas en todas las secciones; el contexto proviene de texto plano.
- Interpretacion: si hay keywords pero no se extraen filas, el problema suele ser formato/estructura.

## Tabla de diagnostico
| PDF | Reservas (evidencia en texto) | Economia (evidencia en texto) | Diagnostico probable | Accion sugerida |
| --- | --- | --- | --- | --- |
| Alpha One | Hay keywords de reservas ("mineral reserve", "reserve estimate") pero no se extrajo ninguna fila. | Solo aparece IRR; no se detectan costos/NPV. | Reservas: probable problema de estructura o formato en tablas. Economia: informacion parcial o narrativa sin tabla. | Revisar paginas con "reserve estimate" y priorizarlas; agregar heuristica para narrativa economica. |
| Colombia Crest | Hay keywords de reservas ("reserve estimate", "proven", "probable"). | Sin keywords de economia. | Reservas: probable problema de formato o tablas no parseadas. Economia: probable ausencia real. | Ajustar seleccion de paginas de reservas y revisar si existen tablas en PDF. |
| Sunward | Hay keywords de reservas ("mineral reserves", "proven", "probable"). | Hay menciones de "operating cost" y "economic analysis". | Reservas: probable problema de formato o tablas no parseadas. Economia: menciones narrativas sin tabla. | Priorizar paginas con keywords y reforzar extraccion narrativa de economia. |

## Nota
Este analisis es heuristico y debe validarse con una revision manual rapida de las paginas senaladas.
