# Resultados ejecutados de CAT-IA

## Evidencia de software

Pruebas registradas: 33. Fallos y errores: 0. Cobertura de líneas: 94.5 %.

JUnit: reports/tests.xml. Cobertura: reports/coverage.json. Estos resultados validan software y contratos; los mocks no ejecutan un LLM.

## Interfaz en navegador

Microsoft Edge headless / CDP. Modo: demo. Comprobaciones completadas: Firefox: borrador y ambas fuentes; Facturación: categoría y resultado renderizados; Sin evidencia: abstención visible; Viewport 390 px: sin desbordamiento horizontal. Capturas incluidas en reports/.

## Evaluación del simulador y recuperación lexical

Fecha: 2026-09-08T03:46:46.850085+00:00. Casos test: 20. Proveedor: demo. Modelo: simulador-extractivo-v1 (sin LLM).

Accuracy categoría: 1.000. Macro-F1: 1.000. Accuracy prioridad: 1.000.

Precisión documental: 0.801. Recall documental: 1.000. MRR: 0.972.

Accuracy abstención: 1.000. Latencia interna p50: 1.05 ms; p95: 2.48 ms.

No se atribuyen estas cifras a un LLM. Dataset pequeño y sintético creado junto a la implementación; requiere etiquetas independientes y casos más difíciles.

## Evaluación semántica

Fidelidad y relevancia humanas: pendientes de completar en evaluation/revision_humana.csv. El código verifica identificadores y extractos exactos, no que una recomendación esté lógicamente respaldada.

## Experimento de recuperación en desarrollo

k=2: precisión 0.929, recall 0.952. k=4: precisión 0.893, recall 1.000.

En los ocho casos dev, k=2 reduce ruido y pierde parte de la cobertura; k=4 conserva más evidencia. Esta comparación respalda priorizar recall en la configuración por defecto, sin declarar que k=4 sea óptimo para otros corpus.

## Evaluación del LLM real

Modelo: qwen2.5:1.5b. Prompt: v3. Casos: 20. Fecha: 2026-09-08T18:02:03.593693+00:00.

Accuracy categoría: 1.000; macro-F1: 1.000. Estados: {'draft': 18, 'insufficient_context': 2}.

Latencia interna p50: 45.42 s; p95: 71.36 s. Prueba en CPU; no extrapolar a otros equipos.

La clasificación incluye abstenciones y fallos como No determinado. La integridad de las citas se impone por contrato; la revisión semántica por los estudiantes sigue pendiente.

## Comparación de prompts

Macro-F1 v2: 0.780; v3: 1.000. Se ajustó la taxonomía por intención del ticket.

El test se inspeccionó para diseñar v3: esta reevaluación es una regresión sobre casos conocidos, no prueba independiente de generalización. Ver reports/OPTIMIZACION_PROMPT.md.

## Prueba real de inferencia

Modelo: qwen2.5:1.5b. Estado: draft. Duración: 45240.6 ms. Evidencia completa en reports/llm_smoke.json.

Una consulta real es una prueba de integración; no sustituye evaluación completa del conjunto test ni revisión humana.
