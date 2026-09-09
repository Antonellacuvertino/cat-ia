# CAT-IA
Soporte con evidencia
Clasificación de tickets y respuestas fundamentadas con LLM + RAG.
Nexo TI · Organización ficticia académica.
Autoras: Antonella Cuvertino y Miriam Hammami.
ISY0101 · Sección y docente: pendientes de informar.

## 01 · El problema
- La mesa de ayuda debe clasificar y consultar procedimientos dispersos.
- La urgencia escrita no siempre representa el impacto real.
- Un borrador sin evidencia puede inventar políticas o compromisos.
- Hipótesis: asistencia contextual mejora consistencia y tiempo de triage.

## 02 · Caso y objetivos
- Nexo TI: escenario ficticio de soporte a pymes; datos internos simulados.
- Meta: macro-F1 de clasificación ≥ 0,85 con evaluación real del LLM.
- Meta: recall documental ≥ 0,85 y precisión ≥ 0,70.
- Alcance: preparar un borrador; la decisión final sigue siendo humana.

## 03 · Fuentes de conocimiento
- 7 documentos internos: SLA, acceso, facturación, comercial, mejoras, red y seguridad.
- 2 síntesis de fuentes reales de Mozilla: cookies y conectividad de Firefox.
- Manifiesto: origen, tipo, versión, transformación, fecha y SHA-256.
- 28 tickets sintéticos: 8 desarrollo + 20 prueba; no forman parte del índice.

## 04 · Arquitectura de la solución
- Interfaz local → API FastAPI → agente de flujo acotado.
- Corpus → fragmentos → índice TF-IDF → recuperación y contexto.
- Política de prioridad + LLM local → contrato y citas → operador.
- Ver diagrama de arquitectura: ingesta, consulta y traza.

## 05 · Cómo recuperamos evidencia
- Fragmentos de 110 palabras; solapamiento de 20.
- Baseline: TF-IDF y similitud coseno; no es embedding neuronal.
- k=4, umbral inicial 0,06 y límite de 6500 caracteres documentales.
- Embeddings densos opcionales: requieren evaluación separada y calibración.

## 06 · Prompts y control de contexto
- v1: zero-shot; v2: contexto y ejemplos; v3: taxonomía ajustada con errores medidos.
- Instrucciones separadas del ticket y de los documentos.
- No inventar precios, devoluciones ni plazos de resolución.
- Solicitar citas y justificación breve; abstenerse si falta evidencia.

## 07 · Generación y validación
- Ollama: LLM local con JSON Schema y temperatura 0.
- Pydantic valida campos y categorías; el agente verifica citas exactas.
- Una cita real no demuestra que la recomendación esté respaldada.
- Demo es un simulador explícito; nunca oculta un fallo del LLM.

## 08 · Demostración
- Ticket Firefox: recuperar una guía externa y un procedimiento interno.
- Mostrar categoría, prioridad, borrador, citas y recorrido.
- Ticket de astronomía: comprobar abstención.
- URGENTE comercial: explicar por qué permanece Baja con impacto individual.

## 09 · Pruebas y resultados
- Pruebas de validación, prioridad, recuperación, citas, fallos y API.
- Resultados reproducibles en reports/; distinguir siempre el modo evaluado.
- Dataset sintético pequeño: no demuestra generalización empresarial.
- Fidelidad y relevancia necesitan revisión semántica del LLM real.

## 10 · Decisiones de ingeniería
- Monolito modular: menor operación y responsabilidades separadas.
- RAG: conocimiento actualizable y trazable sin reentrenar.
- Política determinista: primera respuesta por impacto declarado.
- Trazas locales: hashes y tiempos sin persistir el texto del ticket.

## 11 · Límites y próximos pasos
- Caso ficticio y aprobación docente por confirmar.
- Completar revisión humana de fidelidad y relevancia de las respuestas.
- El test se usó para ajustar v3: falta validación con casos nuevos.
- Antes de producción: autenticación, permisos, privacidad y piloto real.

## 12 · Cambio en vivo y cierre
- Variar k o incorporar una fuente y repetir el mismo caso.
- Explicar el efecto con evidencia, sin prometer mejora automática.
- El valor de CAT-IA es asistir con contexto y hacer revisable el resultado.
- Preguntas y revisión del código.
