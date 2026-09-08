# Propuesta de proyecto: CAT-IA

## Identificación y estado

Nombre: Clasificador y Asistente de Tickets con Inteligencia Artificial. Asignatura: Ingeniería de Soluciones con Inteligencia Artificial, ISY0101. Equipo: completar nombres de los dos integrantes, sección y docente antes de entregar. Estado: propuesta reformulada y prototipo académico; aprobación docente pendiente de acreditar.

Esta propuesta amplía el PDF original del estudiante: conserva clasificación por categorías, prioridad y salida estructurada, y añade RAG, control de contexto, validación, pruebas y documentación. La pauta permite una organización ficticia con preferencia por una real. Se adopta un escenario ficticio explícito para no atribuir a una empresa información, problemas o mediciones no verificados.

## Organización

Nexo TI es una empresa ficticia chilena de soporte informático a pymes. Como supuesto de diseño, cuenta con 20 colaboradores y una mesa de ayuda de 4 operadores. Atiende problemas de acceso a portales, conectividad, consultas comerciales, facturación y sugerencias. Estas cifras describen el escenario académico; no son datos de una organización observada.

## Problema y relevancia

Un operador debe leer cada ticket, distinguir categoría e impacto y consultar procedimientos repartidos en varios documentos. El uso inconsistente de políticas puede producir derivaciones incorrectas y promesas de solución que la organización no puede respaldar. Un clasificador aislado tampoco conoce los procedimientos internos vigentes ni explica de dónde obtuvo su recomendación.

Hipótesis: recuperar evidencia relevante y mostrarla junto al borrador puede reducir tiempo de triage y mejorar consistencia. No se afirma haber medido una reducción. Se propone validarla con un experimento manual asistido y sin asistencia sobre los mismos casos, alternando el orden entre participantes.

## Objetivo general

Implementar y evaluar un asistente de triage que clasifique tickets y prepare respuestas basadas en fuentes internas y externas, conservando trazabilidad y revisión humana.

## Objetivos medibles y criterios de aceptación

- O1: alcanzar macro-F1 de categoría de al menos 0,85 en un conjunto etiquetado y revisado por el equipo, con resultados del LLM reportados separadamente del simulador.
- O2: obtener recall documental de al menos 0,85 y precisión documental de al menos 0,70 en recuperación, documentando k, umbral, corpus y etiquetas.
- O3: verificar que todo borrador aceptado por el validador incluya citas existentes y extractos exactos; medir por separado si cada afirmación está semánticamente respaldada.
- O4: obtener al menos 0,90 de fidelidad humana y mediana de relevancia de al menos 4/5 en las respuestas del LLM. Son metas pendientes, no resultados observados.
- O5: producir abstención ante los casos sin evidencia y conservar revisión humana en todos los resultados. Registrar fallos de proveedor sin sustituirlos por simulación.
- O6: proponer una reducción de 30 % en tiempo mediano de triage frente al procedimiento manual. Validar en un piloto posterior; no incluir como logro actual.

## Datos y uso

Siete documentos internos simulados describen SLA, acceso, facturación, comercial, sugerencias, conectividad y seguridad. Dos síntesis en español de documentación real de Mozilla complementan procedimientos sobre Firefox. Las fuentes están en Markdown UTF-8; el manifiesto JSON registra origen, versión, tipo, transformación y hash. Se incluyen 28 tickets sintéticos: 8 de desarrollo y 20 de prueba. No se ingieren los tickets de evaluación como conocimiento ni se usan datos personales reales.

## Alcance funcional

El operador escribe un ticket, declara alcance e interrupción, y recibe categoría, prioridad, primera respuesta esperada, borrador, citas y traza. Puede variar k y filtrar fuentes para analizar el comportamiento. El sistema no envía correos, crea cuentas, reinicia equipos, devuelve dinero ni cierra incidentes. El agente tiene autonomía acotada para coordinar recuperación, consulta de política y generación; no es un agente con herramientas de ejecución arbitraria.

## Restricciones

Trabajo en pareja, ejecución local, corpus pequeño, recursos de hardware limitados y plazo académico de cinco semanas. Los modelos locales requieren descarga y memoria suficientes. La autenticación empresarial, integración con una ticketera y despliegue público quedan fuera de esta versión. El prototipo minimiza datos mediante redacción básica y trazas sin ticket; no constituye una solución certificada de anonimización o cumplimiento normativo.

## Justificación de LLM, RAG y agente

El LLM aporta comprensión de formulaciones variadas y redacción contextual. RAG aporta conocimiento actualizable sin reentrenar. El flujo acotado coordina tareas y permite inspeccionar qué herramienta intervino. Las políticas deterministas controlan decisiones contractuales sencillas. La combinación es pertinente porque clasificación, información empresarial y generación tienen necesidades distintas y se prueban por separado.

## Plan de cinco semanas

Semana 1: seleccionar caso, levantar supuestos y proponer objetivos. Semana 2: presentar la propuesta y validar alcance; inventariar fuentes. Semana 3: implementar recuperación, prompts y contratos. Semana 4: integrar interfaz, pruebas y evaluación; revisar casos de error. Semana 5: documentar resultados, ensayar cambios en vivo y entregar. Adaptar las fechas al cronograma real: no representar estas actividades como trabajo ya realizado durante cinco semanas.

Reparto sugerido: integrante A lidera recuperación y datos; integrante B lidera API y experiencia de uso. Ambos revisan prompts, pruebas y documentación y deben poder explicar el proyecto completo. Registrar en un historial de cambios las contribuciones reales.

## Referencias

Material docente aportado: propuesta-proyecto-ia.pdf, presentaciones de infraestructura y evaluación RAG y notebooks de evaluación y LangSmith. Fuentes externas de conocimiento: https://support.mozilla.org/en-US/kb/clear-cookies-and-site-data-firefox y https://support.mozilla.org/en-US/kb/firefox-cant-load-websites-other-browsers-can. API de inferencia local: https://docs.ollama.com/api/chat. Consultadas para esta implementación en septiembre de 2026.
