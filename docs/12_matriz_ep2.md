# Trazabilidad EP2 · Pauta oficial

ISY0101 · Ingeniería de Soluciones con IA. Referencia: EP2_ISY0101_Estudiante.pdf, páginas 2–8. Actualización: 21/10/2026. Cada indicador del encargo pondera 10%; el encargo vale 20% de EP2 y la presentación individual 80%. Esta matriz localiza evidencia; no asigna una calificación.

| Indicador | Implementación y evidencia | Límite que se debe explicar |
|---|---|---|
| IE1: consulta, escritura y decisiones | catia/tools.py; saved_draft_id; catia/orchestration.py | Autonomía acotada; el código impone los pasos obligatorios. |
| IE2: framework e instalación | requirements.txt, requirements-ea2.txt, README, instaladores; prueba CrewAI | CrewAI es opcional para la base; debe estar instalado para demostrar equipo. |
| IE3: memoria corta | catia/memory.py; tests/test_ea2.py | Ventana y resumen pierden detalle; cambio de tema usa reglas. |
| IE4: recuperación semántica | OllamaEmbeddings; search_notes; feedback_real.json | Requiere hybrid y el modelo descargado. No cruza hilos. La búsqueda en español tiene errores observados. |
| IE5: planificación | run_react y run_crew; lista permitida y precondiciones | No hay planificador de autonomía abierta. |
| IE6: adaptación | Continuidad, cambio a VPN, filtro externo, proveedor fallido; test_feedback.py | Errores inyectados se distinguen de inferencia real. |
| IE7: README y diagrama | README; docs/arquitectura.mmd; presentación PDF en docs/ | La arquitectura describe un prototipo local. |
| IE8: justificación | ADR-01 a ADR-05 en docs/03_agentes_ea2.md | No se afirma que un modelo mayor corregiría el problema. |
| IE9: flujo y pruebas | reports/FEEDBACK_RESULTADOS.md; JSON, JUnit y navegador | Regresión conocida, no prueba independiente de generalización. |
| IE10: precisión técnica | Comentarios, ADR, guion, resultados y preguntas | No confundir similitud, certeza, citas auténticas y fidelidad. |

## Defensa individual

Justificación 20%; dominio técnico aplicado en vivo 25%; cinco preguntas individuales 35%; comunicación técnica 20%. El guion de docs/11_guion_clase_ea2.md cubre el proyecto completo para cada estudiante. docs/13_prompts_demostracion.md incluye condiciones, salidas esperadas y cómo explicar fallos. docs/14_preguntas_defensa.md desarrolla conceptos anclados al código.
