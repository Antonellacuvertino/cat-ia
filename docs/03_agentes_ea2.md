# CAT-IA · Experiencia 2: agentes, herramientas y memoria

Autoras: Antonella Cuvertino y Miriam Hammami.

Docente: Sebastián Ignacio Sánchez Morales. Actualización: 11/10/2026. La fecha de entrega de EA2 y la sección están pendientes de confirmar; 09/09/2026 corresponde a EA1.

## Qué cambió

EA1 analizaba cada ticket por separado mediante un flujo RAG fijo. EA2 incorpora una sesión persistente, una ventana de conversación, un resumen extractivo y herramientas tipadas. La interfaz permite elegir agente individual o equipo de tres roles. Conserva documentos, prioridad por reglas, citas y revisión humana.

La referencia recibida para esta implementación es el texto de RA2 e IL2.1–IL2.4 adjuntado por la estudiante. No se inventan ponderaciones ni aprobación del docente. Las decisiones de adaptación al equipo local se explicitan a continuación.

## IL2.1 · Herramientas

catia/tools.py construye herramientas con el decorador tool de langchain_core. Cada solicitud tiene un ToolContext propio: no comparte citas, resultados ni memoria con otras sesiones.

- tool_search_knowledge_base(query, top_k): recupera fragmentos internos y externos respetando filtro, umbral y presupuesto.
- tool_check_sla_policy(impact, service_down, security_incident): calcula prioridad y primera respuesta. Los argumentos deben coincidir con los campos ingresados por el operador.
- tool_draft_response(): llama al generador, valida Decision, comprueba citas contra los fragmentos de esta solicitud y fuerza needs_review=true. Sin evidencia no llama al generador.

La firma de SLA conserva los indicadores existentes, en lugar de una urgencia textual ambigua. La herramienta de borrador toma evidencia del estado validado, no de una lista fabricada por el planificador. Son adaptaciones deliberadas de las firmas orientativas recibidas.

El catálogo contiene funciones de aplicación; no integra Gmail, Microsoft, un servicio de ticketera ni MCP. El generador consulta Ollama por HTTP y la búsqueda usa las fuentes externas de Mozilla incorporadas al corpus. No se afirma que sean llamadas web a Mozilla en tiempo real. La validación de citas sigue sin demostrar fidelidad semántica.

## IL2.2 · Memoria corta y persistencia

catia/memory.py usa SQLite, incluido en Python. La ruta por defecto es runtime/memory.sqlite3 y está fuera del ZIP/Git. Una sesión tiene UUID, resumen, ventana de intercambios, contador y fecha de actualización UTC. La interfaz guarda únicamente el UUID en localStorage.

La ventana conserva por defecto tres intercambios redactados. Al superar ese número, la entrada humana más antigua se convierte en un extracto de hasta 240 caracteres que se incorpora a un resumen limitado a 900. La ventana y el resumen sobreviven a reiniciar el proceso. No se conserva el historial completo indefinidamente y no se entrena al modelo.

El resumen es extractivo y determinista, no un resumen generado por otra IA. Evita una llamada costosa al modelo local y puede perder matices o texto antiguo por truncamiento. Se usa la alternativa de ventana por session_id permitida en las instrucciones; no se depende de las clases históricas ConversationBufferWindowMemory/ConversationSummaryMemory.

El contexto entregado al generador incluye como máximo dos entradas previas recortadas y el resumen. La consulta RAG añade la última entrada previa al texto actual cuando el operador activa el contexto. Los borradores previos se muestran en pantalla, pero no se usan como evidencia ni se añaden a la consulta. Si cambia el tema, desactivar contexto o borrar el hilo. No hay detección semántica automática fiable de cambio de tema.

La misma sesión se serializa mediante locks del proceso. SQLite realiza las escrituras. Este diseño se verifica con un solo proceso de aplicación; no es una garantía de aislamiento transaccional de todo el flujo para varios workers. El UUID identifica el hilo, no autentica a una persona: el prototipo sigue siendo local, sin cuentas ni permisos multiusuario.

La memoria persiste texto con redacción parcial de patrones sensibles, a diferencia de las trazas, que siguen omitiendo el ticket y el borrador. Deben usarse datos ficticios. DELETE elimina la ventana y resumen locales, sin borrar archivos JSON descargados ni copias de seguridad externas. No se afirma anonimización completa ni borrado forense.

## IL2.3 · Agente individual

catia/orchestration.py implementa un ciclo ReAct acotado sobre herramientas LangChain. Observa el ticket, selecciona una herramienta disponible, la ejecuta y vuelve a evaluar precondiciones. Con Ollama, una salida JSON restringida elige si empezar por búsqueda o política; cuando solo queda una acción válida, el programa la ejecuta directamente para ahorrar llamadas. El borrador siempre va después de búsqueda y política.

Hay un máximo de tres herramientas distintas por solicitud, lista permitida, contratos y rechazo de duplicados. No es un agente de autonomía abierta ni un planificador que puede ejecutar cualquier comando. La interfaz expone actor, herramienta, estado, duración y observaciones resumidas; no publica pensamientos internos del modelo.

En modo demo, la elección es determinista y se etiqueta langchain-react-demo. En modo real, se etiqueta langchain-react-ollama. La generación sigue usando Ollama y el esquema dinámico de citas. El conteo usage de la respuesta corresponde a la generación final; no agrega automáticamente el consumo del planificador ni todos los intercambios de CrewAI.

## IL2.3 · Equipo secuencial

El segundo modo utiliza CrewAI real: tres objetos Agent con role, goal y backstory, tres Task con context que incluye las tareas anteriores y Process.sequential. Cada rol dispone de una herramienta mínima: Triage consulta SLA; Investigador RAG recupera evidencia; Redactor genera la categoría y el borrador validado.

Para reducir inferencias redundantes, la clasificación definitiva se realiza junto con la redacción; Triage se concentra en el impacto y la política. Esta distribución se diferencia del ejemplo que proponía clasificar también en Triage. No se presentan dos clasificaciones independientes ni se atribuye esa decisión al agente de reglas SLA.

LocalStageLLM adapta el protocolo textual de herramientas de CrewAI al servidor local. En demo responde de manera determinista para ejercitar el framework sin LLM. En modo real consulta Ollama antes de ejecutar la herramienta usando JSON restringido a la acción de ese rol; valida el nombre y lo traduce a Action/Action Input. El rol tiene una sola acción autorizada, por lo que esa llamada no representa una elección autónoma entre alternativas. El texto libre inicial falló en la integración con el modelo pequeño; el contrato restringido evita depender de que reproduzca el formato de CrewAI. Tras una observación validada, la conclusión de la etapa se compone a partir del resultado de herramienta; el texto libre del agente no reemplaza el contrato final.

Se limita cada agente a dos iteraciones y cada adaptador a tres llamadas, con tiempo máximo por petición. No hay delegación ni memoria nativa de CrewAI: se usa la memoria controlada de CAT-IA. La telemetría/tracing se desactiva. Las dependencias de CrewAI son mayores y se instalan mediante instalar_ea2.bat; la instalación base permite el modo individual.

## Fallos y revisión humana

EA2 añade una opción visible para permitir simulación si falla el proveedor. Está desactivada por defecto. Si el operador la habilita y se produce un error de proveedor, se ejecuta el flujo individual con DemoGenerator. El resultado indica fallback_used=true, requested_provider=ollama, mode=demo, estado fallback_demo y advertencia. No se presenta como éxito del LLM ni como ejecución satisfactoria del equipo real solicitado.

Sin autorización de simulación se devuelve abstención explícita. Una salida inválida o dependencia ausente no se disfraza como simulación exitosa. La API continúa respondiendo con estado de negocio. Todos los borradores y abstenciones mantienen needs_review=true y human_approval_required=true. No existe botón de envío automático a clientes.

## API y configuración

- POST /api/sessions crea un hilo y devuelve session_id.
- GET /api/sessions/{session_id} devuelve ventana, resumen y contador del hilo local.
- DELETE /api/sessions/{session_id} elimina su memoria.
- POST /api/tickets/analyze conserva los campos anteriores y admite session_id, orchestration=react/crew, use_context y allow_demo_fallback. Si no se proporciona sesión, crea una nueva.
- GET /api/health declara memoria habilitada, modo por defecto y disponibilidad de CrewAI, además del modelo y corpus. No prueba inferencia real.

CATIA_ORCHESTRATION selecciona react o crew. CATIA_MEMORY_WINDOW controla N entre 1 y 8. CATIA_MEMORY_DB permite cambiar el archivo SQLite. CATIA_PROVIDER elige demo u ollama; OLLAMA_URL debe coincidir con el puerto del servicio. No se necesitan credenciales cloud para estos modos.

EA2 usa prompts/v4.txt para añadir continuidad sin reescribir las versiones históricas. El baseline Agent y scripts.evaluate conservan experimentos EA1 con su selección de versión. En /api/health la configuración RAG puede mantener v3 como baseline; el resultado EA2 informa v4 como versión efectivamente utilizada. La evaluación EA2 se ejecuta con scripts.smoke_ea2 y sus reportes separados.

## IL2.4 · Arquitectura y archivos

docs/arquitectura.mmd representa el flujo actual. docs/arquitectura_ea1.mmd conserva el diagrama anterior. deliverables/arquitectura_EA2.pdf y presentacion_EA2_CAT-IA.pdf muestran la arquitectura y explicación de EA2. La presentación anterior se conserva como EA1. El informe y los resultados se reúnen en dossier_EA2_CAT-IA.pdf; el guion se conserva también separado para practicar.

ConversationAgent extiende el baseline en catia/agent.py. Las rutas se conectan en catia/api.py; los contratos en catia/schemas.py. Las nuevas responsabilidades están separadas en memory.py, tools.py y orchestration.py. prompts/v4.txt delimita los antecedentes como datos no confiables. tests/test_ea2.py verifica los nuevos comportamientos.

## Pruebas y evidencia

reports/tests_ea2.xml y reports/coverage_ea2.json registran la suite EA1+EA2 ejecutada. Los casos incluyen continuidad, aislamiento, ventana, resumen, persistencia al reabrir, borrado, concurrencia de un hilo, redacción, precondiciones, argumentos, lista permitida, planificación alternativa, fallos y ciclo de sesiones API.

La prueba CrewAI con DemoGenerator ejecuta el framework y las herramientas reales usando decisiones simuladas; no acredita la calidad del modelo. scripts.smoke_ea2 --provider ollama --mode react/crew registra inferencia real separada si la ejecución termina sin fallback. El informe EA2 generado lee esos resultados y muestra estados efectivos, incluidos los fallos. No se trasladan los 20 aciertos de v3 a v4.

La fidelidad y relevancia humanas siguen pendientes. Una prueba de integración exitosa no demuestra generalización ni cumplimiento de toda una pauta aún no entregada íntegramente. El desempeño en CPU, el resumen extractivo y la ausencia de autenticación siguen siendo limitaciones.

## Referencias de implementación

LangChain, herramientas tipadas y decorador: https://reference.langchain.com/python/langchain-core/tools/convert/tool. CrewAI, tareas y contexto secuencial: https://docs.crewai.com/en/concepts/tasks. CrewAI, contratos de herramientas: https://docs.crewai.com/en/concepts/tools. CrewAI, adaptadores de modelos: https://docs.crewai.com/en/concepts/llms. Referencias consultadas durante la implementación de EA2; versiones instaladas principales en requirements.txt y requirements-ea2.txt.
