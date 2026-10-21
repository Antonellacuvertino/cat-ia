# Revisión docente · Evidencia actual

Actualización documental: 21/10/2026.

## Software

51 pruebas; 0 fallos; 0 omitidas. Cobertura de líneas: 88.8 %. Fuentes: tests_feedback.xml y coverage_feedback.json.

Cobertura: ejecución separada sin la prueba CrewAI. La suite completa sí la incluye; se separó para evitar el costo de instrumentar su catálogo de importación.

Los ensayos de fallo de proveedor y salida desalineada inyectan errores controlados. No son inferencias fallidas reales. Las pruebas de CrewAI ejecutan su framework con generador simulado.

## Regresión con Ollama y embeddings reales

Fecha de ejecución: 2026-10-21T20:29:11.672310+00:00. Modelo: qwen2.5:1.5b; embeddings: nomic-embed-text.

- P1a: draft; categoría Facturación; cambio de tema False; tiempo 60.0 s.

- P1b: draft; categoría Facturación; cambio de tema False; tiempo 65.4 s.

- P2: draft; categoría Facturación; cambio de tema False; tiempo 66.1 s.

- P3: evidence_mismatch; categoría No determinado; cambio de tema True; tiempo 67.9 s.

Regresión completa: False. Registros recuperados por similitud: 1.

## Comparación de recuperación

me cobraron dos veces: lexical_original: sin fragmentos; lexical_expanded: INT-FAC:0; hybrid: INT-SLA:90, INT-COM:0, INT-NET:0, INT-SLA:0.

me descontaron el doble: lexical_original: sin fragmentos; lexical_expanded: INT-FAC:0; hybrid: INT-SLA:90, EXT-COOKIE:0, INT-SUG:0, INT-COM:0.

no me conecta la VPN: lexical_original: INT-NET:0; lexical_expanded: INT-NET:0; hybrid: INT-NET:0, INT-SEC:0, INT-ACC:0, EXT-NET:0.

necesito revisar el importe repetido en el recibo: lexical_original: INT-FAC:0, EXT-NET:0, EXT-COOKIE:0; lexical_expanded: INT-FAC:0, EXT-NET:0, EXT-COOKIE:0; hybrid: INT-FAC:0, EXT-NET:0, EXT-COOKIE:0, INT-SLA:90.

## Interfaz con simulador

Resultado: True. Cambio de factura a VPN: aviso visible y antecedentes excluidos; Solo externas + cobro: abstención visible y sin fuentes ajenas; Vista móvil sin desbordamiento; Borrado de sesión desde la interfaz. Fuente: browser_feedback.json.

## Interpretación

La expansión es una regla léxica; los embeddings producen recuperación semántica aproximada. Las coincidencias de los casos conocidos no demuestran generalización. El control temático no verifica todas las afirmaciones.

En la ejecución registrada, P3 devolvió evidence_mismatch: el sistema retuvo el borrador, no resolvió satisfactoriamente la consulta de VPN. La regresión completa figura False por ese motivo. La recuperación híbrida sin expansión no ubicó INT-FAC entre los primeros cuatro para algunas paráfrasis; no se afirma superioridad general del modelo de embeddings.

El profesor informó 11–17 segundos en su equipo durante pruebas del 19/10/2026. Esa cifra no se compara causalmente con otra máquina ni demuestra un efecto del tamaño del modelo. No se realizó comparación entre tamaños de LLM.

Los informes EA2_RESULTADOS.md, tests_ea2.xml y ea2_ollama_*.json describen la versión anterior al control temático. No deben atribuirse a esta revisión.
