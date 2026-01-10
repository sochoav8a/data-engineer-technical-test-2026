# Quality Rules

## Extraction rules
- No inventar reservas: si no hay Proven/Probable en el documento, dejar reservas vacias.
- No convertir unidades ni escalar valores: conservar raw, unit y value tal como aparecen.
- No inferir economia: si CAPEX/OPEX/NPV/IRR no aparecen, dejar null.
- Mantener trazabilidad: siempre incluir source_pages cuando se reporta un valor.

## Validaciones aplicadas
- Filtrado de reservas: solo categorias con Proven/Probable (incluye P&P / P+P).
- Conteo de filas vacias: se marca warning si no hay cantidades en recursos/reservas.
- Economia con valores: se marca warning si no hay numeros en CAPEX/OPEX/NPV/IRR.
