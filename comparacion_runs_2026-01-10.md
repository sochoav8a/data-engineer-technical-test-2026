# comparacion_runs_2026-01-10

## Resumen
- Run A: embeddings + retries (primera corrida, cache miss de paginas).
- Run B: sin embeddings y sin retries (segunda corrida, cache hit de paginas).
- Tiempo total: 523.385s vs 144.022s (~3.6x mas rapido).
- Cobertura: casi igual; unica perdida clara en Run B es Resources de Alpha One (4 -> 0) porque los retries estaban desactivados.

## Configuracion
- Run A comando:
```
python run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db
```
- Run B comando:
```
python run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db --no-embeddings --no-retries
```

## Tiempo total
| Run | Duracion (s) | Duracion (aprox) |
| --- | --- | --- |
| A | 523.385 | 8m 43s |
| B | 144.022 | 2m 24s |

## Tiempo por PDF (segun logs)
| PDF | Run A (s) | Run B (s) | Mejora |
| --- | --- | --- | --- |
| Aris | 81.395 | 26.049 | ~3.1x |
| Alpha One | 98.305 | 21.594 | ~4.6x |
| Colombia Crest | 98.503 | 25.292 | ~3.9x |
| Mineros | 120.412 | 35.732 | ~3.4x |
| Sunward | 124.608 | 35.218 | ~3.5x |

## Cobertura comparada
Resources (filas):
- Run A: Aris 4, Alpha One 4, Colombia Crest 6, Mineros 4, Sunward 14.
- Run B: Aris 4, Alpha One 0, Colombia Crest 6, Mineros 4, Sunward 14.

Reserves (filas):
- Run A y Run B: solo Aris 3 y Mineros 3.

Economics:
- Ambos runs: 5 filas (una por PDF), pero solo 2 con valores numericos (Aris y Mineros).

## Observaciones clave
- Embeddings: en Run A la seleccion de paginas para metadata costo ~40-50s por PDF (embedding calls). En Run B la seleccion tomo ~0.01s.
- Retries: Run A hizo 6 llamadas extra (Alpha One: resources+economics; Colombia Crest: reserves+economics; Sunward: reserves+economics). Solo parece ayudar a Resources en Alpha One; el resto no mejoro cobertura.
- Cache de paginas: Run B tuvo cache_hit true en todos los PDFs, reduciendo page extraction a ~0s. Esto explica parte del ahorro de tiempo y no es solo por desactivar embeddings/retries.
- Table extraction: en ambos runs el extractor de tablas reporto 0 tablas, no aporto al contexto.

## Conclusiones
- Para estos 5 PDFs, desactivar embeddings y retries reduce tiempo drasticamente sin perder casi cobertura.
- La unica perdida visible es Resources en Alpha One, que dependio del retry. Si ese caso es critico, se puede activar retries solo para resources o solo cuando el primer pass devuelve 0.



########################################################################################################33333



░▒▓   …/Test_DataEngineer2026   main !?   v3.13.11 (.venv)   base   04:05  
❯ python run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db

2026-01-10 04:05:21,444 INFO {"dry_run": false, "event": "run_start", "max_workers": 1, "pdfs": 5, "run_id": "2026-01-10T09:05:21.444736+00:00", "strategy": "two_stage"}
2026-01-10 04:05:21,444 INFO {"event": "pdf_start", "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "sections": ["economics", "metadata", "reserves", "resources"], "strategy": "two_stage"}
/home/sov/
data-engineer-technical-test-2026
/Test_DataEngineer2026/src/pipeline/embeddings.py:76: FutureWarning: 

All support for the `google.generativeai` package has ended. It will no longer be receiving 
updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
See README for more details:

https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md

  import google.generativeai as genai
2026-01-10 04:06:14,037 INFO {"cache_hit": false, "duration_sec": 0.628, "event": "pages_extracted", "page_count": 61, "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf"}
2026-01-10 04:06:14,037 INFO {"duration_sec": 49.508, "event": "pages_selected", "pages": [12, 13, 60], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "metadata"}
2026-01-10 04:06:14,038 INFO {"duration_sec": 0.865, "event": "pages_selected", "pages": [7, 8, 9, 31, 32, 33, 35, 36, 37, 38, 39], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "resources"}
2026-01-10 04:06:14,038 INFO {"duration_sec": 0.809, "event": "pages_selected", "pages": [7, 8, 9, 10, 31, 32, 33, 37, 38, 39, 40], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "reserves"}
2026-01-10 04:06:14,038 INFO {"duration_sec": 0.78, "event": "pages_selected", "pages": [12, 13, 14, 35, 36, 37, 38, 39, 49, 50, 51, 52], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "economics"}
2026-01-10 04:06:14,038 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [7, 8, 9, 31, 32, 33, 35, 36, 37, 38, 39], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "resources", "tables": 0}
2026-01-10 04:06:14,038 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [7, 8, 9, 10, 31, 32, 33, 37, 38, 39, 40], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "reserves", "tables": 0}
2026-01-10 04:06:14,038 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [12, 13, 14, 35, 36, 37, 38, 39, 49, 50, 51, 52], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "economics", "tables": 0}
2026-01-10 04:06:17,549 INFO {"duration_sec": 3.511, "event": "section_extracted", "input_chars": 10686, "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "retry": false, "section": "metadata"}
2026-01-10 04:06:25,532 INFO {"duration_sec": 7.983, "event": "section_extracted", "input_chars": 41085, "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "retry": false, "section": "resources"}
2026-01-10 04:06:32,688 INFO {"duration_sec": 7.155, "event": "section_extracted", "input_chars": 44353, "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "retry": false, "section": "reserves"}
2026-01-10 04:06:42,839 INFO {"duration_sec": 10.151, "event": "section_extracted", "input_chars": 36970, "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "retry": false, "section": "economics"}
2026-01-10 04:06:42,842 INFO {"duration_sec": 81.395, "economics_has_values": true, "event": "pdf_end", "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "reserves": 3, "resources": 4, "warnings": 0}
2026-01-10 04:06:42,843 INFO {"event": "pdf_start", "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "sections": ["economics", "metadata", "reserves", "resources"], "strategy": "two_stage"}
2026-01-10 04:07:30,111 INFO {"cache_hit": false, "duration_sec": 1.077, "event": "pages_extracted", "page_count": 65, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf"}
2026-01-10 04:07:30,111 INFO {"duration_sec": 46.128, "event": "pages_selected", "pages": [4, 8, 15], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "metadata"}
2026-01-10 04:07:30,111 INFO {"duration_sec": 0.02, "event": "pages_selected", "pages": [6, 7, 8, 16, 17, 18, 40, 41, 42, 48, 49, 50, 51, 52], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "resources"}
2026-01-10 04:07:30,111 INFO {"duration_sec": 0.02, "event": "pages_selected", "pages": [6, 7, 8, 16, 17, 18, 40, 41, 42, 48, 49, 50, 51, 52], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "reserves"}
2026-01-10 04:07:30,111 INFO {"duration_sec": 0.021, "event": "pages_selected", "pages": [6, 7, 8, 14, 15, 16, 17, 18, 55, 56, 57, 58], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "economics"}
2026-01-10 04:07:30,111 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [6, 7, 8, 16, 17, 18, 40, 41, 42, 48, 49, 50, 51, 52], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "resources", "tables": 0}
2026-01-10 04:07:30,111 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [6, 7, 8, 16, 17, 18, 40, 41, 42, 48, 49, 50, 51, 52], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "reserves", "tables": 0}
2026-01-10 04:07:30,112 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [6, 7, 8, 14, 15, 16, 17, 18, 55, 56, 57, 58], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "economics", "tables": 0}
2026-01-10 04:07:34,123 INFO {"duration_sec": 4.012, "event": "section_extracted", "input_chars": 7769, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "retry": false, "section": "metadata"}
2026-01-10 04:07:38,957 INFO {"duration_sec": 4.833, "event": "section_extracted", "input_chars": 29961, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "retry": false, "section": "resources"}
2026-01-10 04:07:45,612 INFO {"duration_sec": 6.655, "event": "section_extracted", "input_chars": 29961, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "retry": false, "section": "reserves"}
2026-01-10 04:07:50,612 INFO {"duration_sec": 5.001, "event": "section_extracted", "input_chars": 29108, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "retry": false, "section": "economics"}
2026-01-10 04:08:01,995 INFO {"duration_sec": 10.534, "event": "section_extracted", "input_chars": 124693, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "retry": true, "section": "resources"}
2026-01-10 04:08:21,147 INFO {"duration_sec": 18.319, "event": "section_extracted", "input_chars": 61025, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "retry": true, "section": "economics"}
2026-01-10 04:08:21,155 INFO {"duration_sec": 98.305, "economics_has_values": false, "event": "pdf_end", "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "reserves": 0, "resources": 4, "warnings": 4}
2026-01-10 04:08:21,155 INFO {"event": "pdf_start", "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "sections": ["economics", "metadata", "reserves", "resources"], "strategy": "two_stage"}
2026-01-10 04:09:19,426 INFO {"cache_hit": false, "duration_sec": 0.947, "event": "pages_extracted", "page_count": 84, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf"}
2026-01-10 04:09:19,427 INFO {"duration_sec": 45.324, "event": "pages_selected", "pages": [8, 13, 23], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "metadata"}
2026-01-10 04:09:19,427 INFO {"duration_sec": 9.51, "event": "pages_selected", "pages": [19, 20, 21, 26, 27, 28, 40, 41, 42, 43, 44, 45, 50, 51, 52], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "resources"}
2026-01-10 04:09:19,427 INFO {"duration_sec": 0.851, "event": "pages_selected", "pages": [2, 3, 4, 9, 10, 11, 38, 39, 40, 41, 42, 50, 51, 52], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "reserves"}
2026-01-10 04:09:19,427 INFO {"duration_sec": 1.637, "event": "pages_selected", "pages": [9, 10, 11, 12, 13, 38, 39, 40, 41, 42], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "economics"}
2026-01-10 04:09:19,427 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [19, 20, 21, 26, 27, 28, 40, 41, 42, 43, 44, 45, 50, 51, 52], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "resources", "tables": 0}
2026-01-10 04:09:19,427 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [2, 3, 4, 9, 10, 11, 38, 39, 40, 41, 42, 50, 51, 52], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "reserves", "tables": 0}
2026-01-10 04:09:19,427 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [9, 10, 11, 12, 13, 38, 39, 40, 41, 42], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "economics", "tables": 0}
2026-01-10 04:09:23,009 INFO {"duration_sec": 3.582, "event": "section_extracted", "input_chars": 7963, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "retry": false, "section": "metadata"}
2026-01-10 04:09:37,800 INFO {"duration_sec": 14.79, "event": "section_extracted", "input_chars": 31446, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "retry": false, "section": "resources"}
2026-01-10 04:09:41,523 INFO {"duration_sec": 3.723, "event": "section_extracted", "input_chars": 37085, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "retry": false, "section": "reserves"}
2026-01-10 04:09:46,438 INFO {"duration_sec": 4.915, "event": "section_extracted", "input_chars": 26970, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "retry": false, "section": "economics"}
2026-01-10 04:09:53,821 INFO {"duration_sec": 4.5, "event": "section_extracted", "input_chars": 64331, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "retry": true, "section": "reserves"}
2026-01-10 04:09:59,657 INFO {"duration_sec": 4.91, "event": "section_extracted", "input_chars": 81544, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "retry": true, "section": "economics"}
2026-01-10 04:09:59,666 INFO {"duration_sec": 98.503, "economics_has_values": false, "event": "pdf_end", "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "reserves": 0, "resources": 6, "warnings": 3}
2026-01-10 04:09:59,666 INFO {"event": "pdf_start", "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "sections": ["economics", "metadata", "reserves", "resources"], "strategy": "two_stage"}
2026-01-10 04:11:33,671 INFO {"cache_hit": false, "duration_sec": 2.67, "event": "pages_extracted", "page_count": 241, "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf"}
2026-01-10 04:11:33,671 INFO {"duration_sec": 44.176, "event": "pages_selected", "pages": [10, 32, 196], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "metadata"}
2026-01-10 04:11:33,671 INFO {"duration_sec": 34.652, "event": "pages_selected", "pages": [21, 22, 23, 87, 88, 89, 108, 109, 110, 115, 116, 117, 118], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "resources"}
2026-01-10 04:11:33,671 INFO {"duration_sec": 5.644, "event": "pages_selected", "pages": [22, 23, 24, 25, 108, 109, 110, 117, 118, 119, 157, 158, 159], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "reserves"}
2026-01-10 04:11:33,671 INFO {"duration_sec": 6.858, "event": "pages_selected", "pages": [3, 4, 5, 6, 7, 8, 29, 30, 31, 213, 214, 215], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "economics"}
2026-01-10 04:11:33,671 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [21, 22, 23, 87, 88, 89, 108, 109, 110, 115, 116, 117, 118], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "resources", "tables": 0}
2026-01-10 04:11:33,671 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [22, 23, 24, 25, 108, 109, 110, 117, 118, 119, 157, 158, 159], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "reserves", "tables": 0}
2026-01-10 04:11:33,672 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [3, 4, 5, 6, 7, 8, 29, 30, 31, 213, 214, 215], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "economics", "tables": 0}
2026-01-10 04:11:37,448 INFO {"duration_sec": 3.776, "event": "section_extracted", "input_chars": 11096, "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "retry": false, "section": "metadata"}
2026-01-10 04:11:44,923 INFO {"duration_sec": 7.474, "event": "section_extracted", "input_chars": 40667, "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "retry": false, "section": "resources"}
2026-01-10 04:11:53,419 INFO {"duration_sec": 8.496, "event": "section_extracted", "input_chars": 40021, "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "retry": false, "section": "reserves"}
2026-01-10 04:12:00,078 INFO {"duration_sec": 6.658, "event": "section_extracted", "input_chars": 43416, "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "retry": false, "section": "economics"}
2026-01-10 04:12:00,088 INFO {"duration_sec": 120.412, "economics_has_values": true, "event": "pdf_end", "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "reserves": 3, "resources": 4, "warnings": 0}
2026-01-10 04:12:00,089 INFO {"event": "pdf_start", "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "sections": ["economics", "metadata", "reserves", "resources"], "strategy": "two_stage"}
2026-01-10 04:13:10,118 INFO {"cache_hit": false, "duration_sec": 2.61, "event": "pages_extracted", "page_count": 187, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf"}
2026-01-10 04:13:10,118 INFO {"duration_sec": 40.599, "event": "pages_selected", "pages": [0, 121, 157], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "metadata"}
2026-01-10 04:13:10,118 INFO {"duration_sec": 20.268, "event": "pages_selected", "pages": [12, 13, 14, 15, 16, 129, 130, 131, 132, 133, 134, 135, 136], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "resources"}
2026-01-10 04:13:10,118 INFO {"duration_sec": 4.197, "event": "pages_selected", "pages": [14, 15, 16, 91, 92, 93, 101, 102, 103, 132, 133, 134, 135], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "reserves"}
2026-01-10 04:13:10,118 INFO {"duration_sec": 2.352, "event": "pages_selected", "pages": [89, 90, 91, 92, 93, 131, 132, 133, 145, 146, 147], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "economics"}
2026-01-10 04:13:10,119 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [12, 13, 14, 15, 16, 129, 130, 131, 132, 133, 134, 135, 136], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "resources", "tables": 0}
2026-01-10 04:13:10,119 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [14, 15, 16, 91, 92, 93, 101, 102, 103, 132, 133, 134, 135], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "reserves", "tables": 0}
2026-01-10 04:13:10,119 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [89, 90, 91, 92, 93, 131, 132, 133, 145, 146, 147], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "economics", "tables": 0}
2026-01-10 04:13:12,442 INFO {"duration_sec": 2.322, "event": "section_extracted", "input_chars": 7162, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "retry": false, "section": "metadata"}
2026-01-10 04:13:44,302 INFO {"duration_sec": 31.86, "event": "section_extracted", "input_chars": 44074, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "retry": false, "section": "resources"}
2026-01-10 04:13:48,007 INFO {"duration_sec": 3.704, "event": "section_extracted", "input_chars": 46672, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "retry": false, "section": "reserves"}
2026-01-10 04:13:51,181 INFO {"duration_sec": 3.173, "event": "section_extracted", "input_chars": 34573, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "retry": false, "section": "economics"}
2026-01-10 04:13:59,474 INFO {"duration_sec": 3.002, "event": "section_extracted", "input_chars": 95268, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "retry": true, "section": "reserves"}
2026-01-10 04:14:04,696 INFO {"duration_sec": 3.574, "event": "section_extracted", "input_chars": 72197, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "retry": true, "section": "economics"}
2026-01-10 04:14:04,705 INFO {"duration_sec": 124.608, "economics_has_values": false, "event": "pdf_end", "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "reserves": 0, "resources": 14, "warnings": 3}
2026-01-10 04:14:04,830 INFO {"duration_sec": 523.385, "event": "run_end", "pdfs": 5, "run_id": "2026-01-10T09:05:21.444736+00:00"}

░▒▓   …/Test_DataEngineer2026   main !?   v3.13.11 (.venv)   base   04:14  
❯ python run_pipeline.py --data-dir data --output-dir output --sqlite-path output/extractions.db --no-embeddings --no-retries

2026-01-10 04:14:59,954 INFO {"dry_run": false, "event": "run_start", "max_workers": 1, "pdfs": 5, "run_id": "2026-01-10T09:14:59.954261+00:00", "strategy": "two_stage"}
2026-01-10 04:14:59,954 INFO {"event": "pdf_start", "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "sections": ["economics", "metadata", "reserves", "resources"], "strategy": "two_stage"}
2026-01-10 04:15:00,019 INFO {"cache_hit": true, "duration_sec": 0.001, "event": "pages_extracted", "page_count": 61, "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf"}
2026-01-10 04:15:00,019 INFO {"duration_sec": 0.014, "event": "pages_selected", "pages": [0, 13, 59], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "metadata"}
2026-01-10 04:15:00,019 INFO {"duration_sec": 0.019, "event": "pages_selected", "pages": [5, 6, 7, 8, 9, 35, 36, 37, 38, 39], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "resources"}
2026-01-10 04:15:00,019 INFO {"duration_sec": 0.014, "event": "pages_selected", "pages": [7, 8, 9, 10, 24, 25, 26, 31, 32, 33, 38, 39, 40], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "reserves"}
2026-01-10 04:15:00,019 INFO {"duration_sec": 0.014, "event": "pages_selected", "pages": [12, 13, 14, 35, 36, 37, 38, 39, 49, 50, 51, 52], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "economics"}
2026-01-10 04:15:00,019 INFO {"event": "page_cache_hit", "page_count": 61, "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf"}
2026-01-10 04:15:00,019 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [5, 6, 7, 8, 9, 35, 36, 37, 38, 39], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "resources", "tables": 0}
2026-01-10 04:15:00,020 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [7, 8, 9, 10, 24, 25, 26, 31, 32, 33, 38, 39, 40], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "reserves", "tables": 0}
2026-01-10 04:15:00,020 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [12, 13, 14, 35, 36, 37, 38, 39, 49, 50, 51, 52], "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "section": "economics", "tables": 0}
/home/sov/
data-engineer-technical-test-2026
/Test_DataEngineer2026/src/pipeline/llm.py:70: FutureWarning: 

All support for the `google.generativeai` package has ended. It will no longer be receiving 
updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
See README for more details:

https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md

  import google.generativeai as genai
2026-01-10 04:15:03,609 INFO {"duration_sec": 3.59, "event": "section_extracted", "input_chars": 6573, "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "retry": false, "section": "metadata"}
2026-01-10 04:15:10,422 INFO {"duration_sec": 6.812, "event": "section_extracted", "input_chars": 35160, "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "retry": false, "section": "resources"}
2026-01-10 04:15:17,709 INFO {"duration_sec": 7.286, "event": "section_extracted", "input_chars": 49214, "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "retry": false, "section": "reserves"}
2026-01-10 04:15:26,003 INFO {"duration_sec": 8.294, "event": "section_extracted", "input_chars": 36970, "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "retry": false, "section": "economics"}
2026-01-10 04:15:26,005 INFO {"duration_sec": 26.049, "economics_has_values": true, "event": "pdf_end", "pdf": "sedar__000003116_Aris_Mining_Corporation__technical-report__878C2FBC.pdf", "reserves": 3, "resources": 4, "warnings": 0}
2026-01-10 04:15:26,005 INFO {"event": "pdf_start", "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "sections": ["economics", "metadata", "reserves", "resources"], "strategy": "two_stage"}
2026-01-10 04:15:26,055 INFO {"cache_hit": true, "duration_sec": 0.0, "event": "pages_extracted", "page_count": 65, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf"}
2026-01-10 04:15:26,055 INFO {"duration_sec": 0.011, "event": "pages_selected", "pages": [15, 45, 47], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "metadata"}
2026-01-10 04:15:26,055 INFO {"duration_sec": 0.012, "event": "pages_selected", "pages": [6, 7, 8, 16, 17, 18, 40, 41, 42, 48, 49, 50, 51, 52], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "resources"}
2026-01-10 04:15:26,056 INFO {"duration_sec": 0.012, "event": "pages_selected", "pages": [6, 7, 8, 16, 17, 18, 40, 41, 42, 48, 49, 50, 56, 57, 58], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "reserves"}
2026-01-10 04:15:26,056 INFO {"duration_sec": 0.012, "event": "pages_selected", "pages": [6, 7, 8, 14, 15, 16, 17, 18, 40, 41, 42, 48, 49, 50], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "economics"}
2026-01-10 04:15:26,056 INFO {"event": "page_cache_hit", "page_count": 65, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf"}
2026-01-10 04:15:26,056 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [6, 7, 8, 16, 17, 18, 40, 41, 42, 48, 49, 50, 51, 52], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "resources", "tables": 0}
2026-01-10 04:15:26,056 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [6, 7, 8, 16, 17, 18, 40, 41, 42, 48, 49, 50, 56, 57, 58], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "reserves", "tables": 0}
2026-01-10 04:15:26,056 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [6, 7, 8, 14, 15, 16, 17, 18, 40, 41, 42, 48, 49, 50], "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "section": "economics", "tables": 0}
2026-01-10 04:15:29,996 INFO {"duration_sec": 3.94, "event": "section_extracted", "input_chars": 3730, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "retry": false, "section": "metadata"}
2026-01-10 04:15:39,828 INFO {"duration_sec": 9.831, "event": "section_extracted", "input_chars": 29961, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "retry": false, "section": "resources"}
2026-01-10 04:15:43,002 INFO {"duration_sec": 3.175, "event": "section_extracted", "input_chars": 34150, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "retry": false, "section": "reserves"}
2026-01-10 04:15:47,600 INFO {"duration_sec": 4.597, "event": "section_extracted", "input_chars": 31226, "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "retry": false, "section": "economics"}
2026-01-10 04:15:47,604 INFO {"duration_sec": 21.594, "economics_has_values": false, "event": "pdf_end", "pdf": "sedar__Alpha_One_Corporation__technical-report__C03783C6.pdf", "reserves": 0, "resources": 0, "warnings": 4}
2026-01-10 04:15:47,604 INFO {"event": "pdf_start", "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "sections": ["economics", "metadata", "reserves", "resources"], "strategy": "two_stage"}
2026-01-10 04:15:47,662 INFO {"cache_hit": true, "duration_sec": 0.001, "event": "pages_extracted", "page_count": 84, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf"}
2026-01-10 04:15:47,663 INFO {"duration_sec": 0.014, "event": "pages_selected", "pages": [8, 13, 23], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "metadata"}
2026-01-10 04:15:47,663 INFO {"duration_sec": 0.013, "event": "pages_selected", "pages": [19, 20, 21, 26, 27, 28, 40, 41, 42, 43, 44, 45, 50, 51, 52], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "resources"}
2026-01-10 04:15:47,663 INFO {"duration_sec": 0.013, "event": "pages_selected", "pages": [2, 3, 4, 9, 10, 11, 38, 39, 40, 41, 42, 50, 51, 52], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "reserves"}
2026-01-10 04:15:47,663 INFO {"duration_sec": 0.013, "event": "pages_selected", "pages": [9, 10, 11, 13, 14, 15, 38, 39, 40, 41, 42, 50, 51, 52], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "economics"}
2026-01-10 04:15:47,663 INFO {"event": "page_cache_hit", "page_count": 84, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf"}
2026-01-10 04:15:47,663 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [19, 20, 21, 26, 27, 28, 40, 41, 42, 43, 44, 45, 50, 51, 52], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "resources", "tables": 0}
2026-01-10 04:15:47,664 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [2, 3, 4, 9, 10, 11, 38, 39, 40, 41, 42, 50, 51, 52], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "reserves", "tables": 0}
2026-01-10 04:15:47,664 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [9, 10, 11, 13, 14, 15, 38, 39, 40, 41, 42, 50, 51, 52], "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "section": "economics", "tables": 0}
2026-01-10 04:15:51,398 INFO {"duration_sec": 3.734, "event": "section_extracted", "input_chars": 7963, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "retry": false, "section": "metadata"}
2026-01-10 04:16:04,608 INFO {"duration_sec": 13.209, "event": "section_extracted", "input_chars": 31446, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "retry": false, "section": "resources"}
2026-01-10 04:16:08,397 INFO {"duration_sec": 3.789, "event": "section_extracted", "input_chars": 37085, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "retry": false, "section": "reserves"}
2026-01-10 04:16:12,896 INFO {"duration_sec": 4.499, "event": "section_extracted", "input_chars": 38683, "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "retry": false, "section": "economics"}
2026-01-10 04:16:12,907 INFO {"duration_sec": 25.292, "economics_has_values": false, "event": "pdf_end", "pdf": "sedar__Colombia_Crest_Gold_Corp__technical-report__D11891E2.pdf", "reserves": 0, "resources": 6, "warnings": 3}
2026-01-10 04:16:12,907 INFO {"event": "pdf_start", "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "sections": ["economics", "metadata", "reserves", "resources"], "strategy": "two_stage"}
2026-01-10 04:16:13,103 INFO {"cache_hit": true, "duration_sec": 0.002, "event": "pages_extracted", "page_count": 241, "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf"}
2026-01-10 04:16:13,103 INFO {"duration_sec": 0.045, "event": "pages_selected", "pages": [32, 196, 201], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "metadata"}
2026-01-10 04:16:13,103 INFO {"duration_sec": 0.047, "event": "pages_selected", "pages": [21, 22, 23, 87, 88, 89, 107, 108, 109, 115, 116, 117, 118], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "resources"}
2026-01-10 04:16:13,103 INFO {"duration_sec": 0.048, "event": "pages_selected", "pages": [22, 23, 24, 25, 108, 109, 110, 117, 118, 119, 157, 158, 159], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "reserves"}
2026-01-10 04:16:13,103 INFO {"duration_sec": 0.05, "event": "pages_selected", "pages": [3, 4, 5, 6, 7, 8, 29, 30, 31, 213, 214, 215], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "economics"}
2026-01-10 04:16:13,103 INFO {"event": "page_cache_hit", "page_count": 241, "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf"}
2026-01-10 04:16:13,103 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [21, 22, 23, 87, 88, 89, 107, 108, 109, 115, 116, 117, 118], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "resources", "tables": 0}
2026-01-10 04:16:13,103 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [22, 23, 24, 25, 108, 109, 110, 117, 118, 119, 157, 158, 159], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "reserves", "tables": 0}
2026-01-10 04:16:13,104 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [3, 4, 5, 6, 7, 8, 29, 30, 31, 213, 214, 215], "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "section": "economics", "tables": 0}
2026-01-10 04:16:17,461 INFO {"duration_sec": 4.357, "event": "section_extracted", "input_chars": 10952, "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "retry": false, "section": "metadata"}
2026-01-10 04:16:25,804 INFO {"duration_sec": 8.343, "event": "section_extracted", "input_chars": 43031, "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "retry": false, "section": "resources"}
2026-01-10 04:16:41,655 INFO {"duration_sec": 15.851, "event": "section_extracted", "input_chars": 40021, "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "retry": false, "section": "reserves"}
2026-01-10 04:16:48,640 INFO {"duration_sec": 6.984, "event": "section_extracted", "input_chars": 43416, "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "retry": false, "section": "economics"}
2026-01-10 04:16:48,650 INFO {"duration_sec": 35.732, "economics_has_values": true, "event": "pdf_end", "pdf": "sedar__Mineros_SA__technical-report__2B2256D4.pdf", "reserves": 3, "resources": 4, "warnings": 0}
2026-01-10 04:16:48,651 INFO {"event": "pdf_start", "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "sections": ["economics", "metadata", "reserves", "resources"], "strategy": "two_stage"}
2026-01-10 04:16:48,767 INFO {"cache_hit": true, "duration_sec": 0.001, "event": "pages_extracted", "page_count": 187, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf"}
2026-01-10 04:16:48,767 INFO {"duration_sec": 0.029, "event": "pages_selected", "pages": [19, 121, 157], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "metadata"}
2026-01-10 04:16:48,767 INFO {"duration_sec": 0.028, "event": "pages_selected", "pages": [12, 13, 14, 15, 16, 129, 130, 131, 132, 133, 134, 135, 136], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "resources"}
2026-01-10 04:16:48,767 INFO {"duration_sec": 0.028, "event": "pages_selected", "pages": [89, 90, 91, 92, 93, 101, 102, 103, 132, 133, 134], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "reserves"}
2026-01-10 04:16:48,767 INFO {"duration_sec": 0.029, "event": "pages_selected", "pages": [89, 90, 91, 92, 93, 131, 132, 133, 145, 146, 147], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "economics"}
2026-01-10 04:16:48,767 INFO {"event": "page_cache_hit", "page_count": 187, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf"}
2026-01-10 04:16:48,767 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [12, 13, 14, 15, 16, 129, 130, 131, 132, 133, 134, 135, 136], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "resources", "tables": 0}
2026-01-10 04:16:48,767 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [89, 90, 91, 92, 93, 101, 102, 103, 132, 133, 134], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "reserves", "tables": 0}
2026-01-10 04:16:48,767 INFO {"duration_sec": 0.0, "event": "tables_extracted", "pages": [89, 90, 91, 92, 93, 131, 132, 133, 145, 146, 147], "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "section": "economics", "tables": 0}
2026-01-10 04:16:53,452 INFO {"duration_sec": 4.685, "event": "section_extracted", "input_chars": 8198, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "retry": false, "section": "metadata"}
2026-01-10 04:17:17,517 INFO {"duration_sec": 24.065, "event": "section_extracted", "input_chars": 44074, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "retry": false, "section": "resources"}
2026-01-10 04:17:21,000 INFO {"duration_sec": 3.482, "event": "section_extracted", "input_chars": 42339, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "retry": false, "section": "reserves"}
2026-01-10 04:17:23,868 INFO {"duration_sec": 2.868, "event": "section_extracted", "input_chars": 34573, "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "retry": false, "section": "economics"}
2026-01-10 04:17:23,883 INFO {"duration_sec": 35.218, "economics_has_values": false, "event": "pdf_end", "pdf": "sedar__Sunward_Resources_Ltd__technical-report__278C5D9A.pdf", "reserves": 0, "resources": 14, "warnings": 3}
2026-01-10 04:17:23,977 INFO {"duration_sec": 144.022, "event": "run_end", "pdfs": 5, "run_id": "2026-01-10T09:14:59.954261+00:00"}

░▒▓   …/Test_DataEngineer2026   main !?   v3.13.11 (.venv)   base   04:18  
❯ 