# Resultados verificables · EA2

Autoras: Antonella Cuvertino y Miriam Hammami. Actualización: 11/10/2026.

## Software

45 pruebas: 0 fallos y 0 omitidas. Cobertura de líneas: 93.8 %. Evidencia: reports/tests_ea2.xml y reports/coverage_ea2.json.

Incluyen las pruebas anteriores y las de continuidad, aislamiento, persistencia, borrado, concurrencia local, herramientas, API, errores y CrewAI real con generación simulada.

## Integración por proveedor

- demo / react: PASA; estados draft, draft; duración por caso 0.2 s, 0.1 s. Fuente: ea2_demo_react.json; fecha 2026-10-11T15:11:39.025996+00:00.

- ollama / crew: PASA; estados draft; duración por caso 156.9 s. Fuente: ea2_ollama_crew.json; fecha 2026-10-11T22:28:03.216670+00:00.

- ollama / react: PASA; estados draft, draft; duración por caso 117.0 s, 104.5 s. Fuente: ea2_ollama_react.json; fecha 2026-10-11T15:07:15.105966+00:00.

## Interfaz

Resultado: PASA. Continuación de facturación con antecedentes y memoria visible; CrewAI simulado: tres herramientas y fuentes internas/externas visibles; Pantalla móvil de 390 px sin desbordamiento horizontal; Borrado desde la interfaz: memoria vacía y sesión devuelve 404. Evidencia: reports/browser_checks_ea2.json.

## Alcance y límites

Los casos de integración son sintéticos y pequeños. No constituyen una evaluación independiente de fidelidad, relevancia o generalización. La validación de citas comprueba procedencia y coincidencia textual; la revisión semántica sigue siendo humana.

Las métricas de EA1 pertenecen a su implementación y prompt v3; no se transfieren al agente EA2 con prompt v4. La cobertura no mide calidad del LLM. Las latencias dependen del hardware y la carga.

Se observaron advertencias de deprecación en dependencias CrewAI/Pydantic durante las pruebas. No impidieron completarlas; revisar al actualizar versiones.
