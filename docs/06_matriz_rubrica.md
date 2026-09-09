# Matriz de trazabilidad de la pauta

Autoras: Antonella Cuvertino y Miriam Hammami.

Docente: Sebastián Ignacio Sánchez Morales. Fecha de entrega: 09/09/2026.

## IE1 · Diseño según requerimientos · 15 %

Evidencia: docs/01_propuesta_mejorada.md y requisitos RF/RNF del informe. Organización, problema, objetivos medibles, datos, restricciones y alcance explícitos. Pendiente externo: validación docente del caso ficticio y, si se exige, ajuste a organización real autorizada. No se afirma aprobación.

## IE2 · Prompts verificables · 10 %

Evidencia: prompts/v1.txt, prompts/v2.txt, prompts/v3.txt y catia/generation.py:build_messages. Rol, tarea, contexto, formato, ejemplos, fuentes y abstención. La versión activa v3 aborda errores medidos de v2; se conservan reportes y justificación en reports/OPTIMIZACION_PROMPT.md. Demo no distingue prompts; usar resultados de inferencia para argumentar diferencias.

## IE3 · Recuperación interna y externa funcional · 10 %

Evidencia: data/sources.json, archivos Markdown, catia/retrieval.py y prueba de recuperación de ambos tipos. La app opera con copias editoriales externas trazables, sin web en vivo. Para acreditar el flujo LLM completo debe funcionar Ollama en la presentación; la recuperación lexical ya es ejecutable sin él.

## IE4 · Coherencia datos/respuestas · 10 %

Evidencia: validación de citas en catia/agent.py, abstención y evaluation/dataset.json. Reports contiene evaluación ejecutada. Pendiente para evidencia semántica completa: revisión humana de salidas reales en evaluation/revision_humana.csv. Citas exactas no bastan para afirmar fidelidad.

## IE5 · Arquitectura integrada · 15 %

Evidencia: docs/02_informe_tecnico.md, módulos catia/ y recorrido del agente en pantalla. Ingesta, recuperación, contexto, generación, validación y revisión integrados. El diseño es un monolito modular con autonomía acotada.

## IE6 · Diagrama entregable · 10 %

Evidencia: docs/arquitectura.mmd, deliverables/arquitectura.pdf y diapositiva de arquitectura. Se representan datos internos/externos, índice, consulta, proveedor y salidas; las flechas distinguen ingesta de consulta.

## IE7 · Decisiones fundamentadas · 10 %

Evidencia: ADR01–ADR06 del informe y parámetros de código/configuración. Alternativas, beneficios y límites: RAG frente a entrenamiento, TF-IDF frente a dense, reglas frente a LLM y trazas locales. Metas empresariales no se presentan como impactos medidos.

## IE8 · Documentación y evidencia técnica · 10 %

Evidencia: propuesta, informe, manual, plan de pruebas, guía, diagramas, PDF y reports. Scripts permiten regenerar evaluación y artefactos. Autoras identificadas: Antonella Cuvertino y Miriam Hammami. Queda registrar aprobación docente y revisión humana cuando ocurran; las evaluaciones ejecutadas están en reports.

## IE9 · Lenguaje y comentarios técnicos · 10 %

Evidencia: docstrings de módulos, justificación de límites y fórmulas del plan. Se distinguen simulación, inferencia, pruebas con mocks, métricas de recuperación y evaluación humana.

## Defensa individual

Justificación 20 %: practicar ADR y alternativas de la guía. Dominio técnico en vivo 25 %: cambiar prompt, fuente, k o política sin ayuda externa. Cinco preguntas 35 %: preparar el banco completo y anclar cada respuesta al código. Comunicación 20 %: ensayar con cronómetro y terminología precisa. El proyecto entregado apoya la defensa; no reemplaza el dominio de cada estudiante ni garantiza nota.

## Estado honesto

Implementación y documentación están orientadas al descriptor superior. La calificación depende de comprobar funcionamiento real, coherencia semántica, aprobación del caso y dominio individual. No marcar todos los indicadores al 100 % solo por tener archivos: consultar reports y los pendientes antes de entregar.
