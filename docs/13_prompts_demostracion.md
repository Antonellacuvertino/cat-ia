# Guía de consultas, abstenciones y errores · CAT-IA

Actualización: 21/10/2026. Esta guía usa datos ficticios y no modifica cuentas reales. Los textos que escribes son consultas del usuario; prompts/v4.txt contiene las instrucciones del sistema.

## Preparación común

Abre http://127.0.0.1:8000. Verifica el modo real o demo. Para probar recuperación semántica debe aparecer Híbrida y estar disponible nomic-embed-text. Selecciona Agente individual, Fuentes internas y externas y cuatro fragmentos. Borra el hilo antes de una prueba independiente. Desactiva el respaldo a demo cuando quieras observar un fallo real del proveedor.

El resultado esperado sirve para contrastar la ejecución; no debes afirmar éxito sin leerla. El modelo puede producir evidence_mismatch incluso si la recuperación fue correcta.

## Caso A · Consulta conocida

Texto: «Mi factura tiene un cobro duplicado. ¿Qué información debo entregar para revisarlo?».

Espera información del procedimiento INT-FAC, sin reembolso garantizado. Muestra category, sources y las citas. La herramienta de borrador registra saved_draft_id en SQLite. El registro queda pendiente de revisión, no equivale a un ticket enviado.

## Caso B · Continuidad

En el mismo hilo, activa antecedentes y pregunta: «¿Qué debo hacer en ese caso?».

Espera que utilice la consulta de factura anterior. Muestra memory.used y previous_turns. Sin antecedentes, la frase no identifica por sí sola el problema; puede abstenerse o recuperar un fragmento poco pertinente. Por eso no sirve como pregunta inicial precisa.

## Caso C · Paráfrasis del profesor

Borra el hilo, desactiva antecedentes y escribe: «me cobraron dos veces».

Antes, TF-IDF no reconocía esa formulación. La versión revisada expande ese patrón a «factura cobro duplicado». El modo híbrido añade embeddings. Para distinguir sus aportes, mira retrieval_comparison en reports/feedback_real.json: compara consulta original, expansión y búsqueda híbrida sin expansión. No digas que una regla de sinónimos demuestra comprensión semántica general.

Prueba adicional: «me descontaron el doble». Las reglas cubren algunas formas, no todo el español. «Necesito revisar el importe repetido en el recibo» sirve para explorar una paráfrasis sin regla explícita; inspecciona la evidencia antes de darla por resuelta.

## Caso D · Cambio de tema

Después del caso de factura, deja los antecedentes activados y escribe: «no me conecta la VPN».

Espera context_control.topic_change=true y memoria anterior ignorada para esta consulta. La respuesta debe tratar conectividad y apoyarse en INT-NET; no facturación. Si aparece evidence_mismatch, el sistema retuvo una salida que no pasó las comprobaciones. El aviso reduce contaminación conocida, pero no detecta todos los cambios de tema ni resuelve casos ambiguos.

## Caso E · Generar una abstención controlada

Borra el hilo. Selecciona Solo externas. Desactiva antecedentes. Escribe: «me cobraron dos veces».

Resultado esperado: insufficient_context. Las fuentes externas del corpus son guías de Mozilla; no contienen el procedimiento de facturación de Nexo TI. El filtro excluye INT-FAC y el control temático descarta documentos ajenos. No es un fallo del servidor: la información necesaria no está disponible bajo ese filtro.

Corrección: vuelve a Internas y externas y repite. Explica que cambiar el filtro permite consultar la fuente adecuada; insistir con un prompt no crea un documento inexistente.

## Caso F · Información que no existe

Texto: «¿Cuál es el estado real de mi reembolso de la factura 12345?».

CAT-IA no consulta la base real de pagos. Puede recuperar el procedimiento general de facturación, pero eso no demuestra el estado de una factura. Una respuesta que confirme un reembolso sería incorrecta aunque cite INT-FAC. La validación temática puede NO detectarla: el tema coincide, pero el hecho no está en la fuente. Este es un límite que debes explicar, no un caso con error garantizado.

## Caso G · Entrada demasiado corta

Escribe «hola». El formulario exige al menos doce caracteres y no envía la consulta. Esto es validación de entrada, no una alucinación ni un error de recuperación.

Para observar el contrato HTTP, en /docs envía POST /api/tickets/analyze con {"text":"hola"}. La respuesta esperada es 422. No hagas esta prueba con datos personales.

## Caso H · Falla de proveedor reproducible

No existe un texto que garantice que Ollama falle. Un error de conexión se simula como condición del entorno, no pidiendo «genera un error» al chat.

Ejecuta: .\.venv\Scripts\python.exe -m pytest -q tests/test_feedback.py -k insufficient_source_and_provider_failure

La prueba inyecta una conexión fallida sin apagar tu Ollama ni cambiar .env. Comprueba provider_error y que no haya fallback silencioso. Para el caso de citas auténticas pero respuesta equivocada ejecuta: .\.venv\Scripts\python.exe -m pytest -q tests/test_feedback.py -k literal_quote

Es un ensayo controlado con una salida defectuosa, no una inferencia real fallida. El borrador se retiene con evidence_mismatch.

## Cómo explicar por qué no recibiste la información

- insufficient_context: la recuperación no entregó evidencia suficiente; revisa consulta, fuentes, filtro y umbral.
- evidence_mismatch: había citas reales, pero categoría, respuesta o citas no coinciden con el tema reconocido. No se ofrece el borrador sospechoso.
- provider_error: falló una dependencia o llamada; revisa el proveedor y los eventos. El mensaje general no demuestra que la causa sea falta de RAM.
- invalid_output: la salida incumplió un contrato u otra validación. Examina qué herramienta falló.
- 422: los datos de entrada no cumplen el contrato; corrige campos o longitud.
- draft: existe un borrador que pasó los controles programados. No significa certeza ni aprobación de fidelidad.

## Qué mostrar en el JSON descargado

Consulta status, warning, context_control, memory.used, sources, tool_events, requested_provider, mode y fallback_used. source.score es similitud de recuperación: no lo presentes como porcentaje de certeza. La prueba de calidad consiste en comparar las afirmaciones con los fragmentos y el requerimiento, además de pasar los controles automáticos.
