# CAT-IA · Agente funcional EP2

Ingeniería de Soluciones con IA · ISY0101. Autoras: Antonella Cuvertino y Miriam Hammami. Docente: Sebastián Ignacio Sánchez Morales. Revisión: 21/10/2026.

## Requerimiento y alcance

Nexo TI es una organización ficticia. El agente consulta procedimientos, continúa un caso, calcula prioridad y registra un borrador local pendiente de revisión. No envía mensajes ni modifica cuentas externas. El corpus mantiene siete documentos internos simulados y dos síntesis de guías de Mozilla; su origen y hashes están en data/sources.json.

La pauta EP2_ISY0101_Estudiante.pdf exige consulta, escritura, memoria corta y recuperación semántica de largo plazo, planificación explícita, al menos tres escenarios adaptativos, diagrama, decisiones y evidencia. La presentación es individual. El encargo representa 20% y la presentación 80% de EP2; la evaluación completa pondera 35% según la portada. La fecha límite se informa por AVA.

## Retroalimentación y correcciones

El docente revisó el commit 32e3a7b y reportó pruebas del 19/10/2026: continuidad correcta en facturación; fallo de recuperación con «me cobraron dos veces»; contaminación de factura al preguntar por VPN; citas literales que no respaldaban la respuesta. Sus latencias de 11–17 segundos corresponden a su equipo. Son observaciones aportadas por el docente, no mediciones repetidas aquí.

Se añadió catia/guardrails.py. expand_query amplía patrones conocidos de cobro repetido; es expansión léxica, no recuperación semántica. select_context identifica señales conocidas, descarta antecedentes incompatibles y limita continuaciones al segmento reciente. No elimina el historial visual al cambiar de tema. validate_alignment revisa categoría, respuesta y cita respecto al tema único detectado; ante desacuerdo devuelve evidence_mismatch y no publica el borrador.

No se atribuye el fallo al tamaño del modelo. Falta un experimento entre modelos con iguales casos, recuperación y criterios para sostener esa explicación. Los controles implementados reducen problemas concretos, pero pueden omitir cambios sutiles y hechos falsos dentro del mismo tema.

## Herramientas y escritura · IE1–IE2

catia/tools.py declara herramientas con langchain_core.tools.tool. Cada solicitud posee ToolContext aislado y los argumentos se vinculan a datos validados.

- tool_search_knowledge_base consulta el corpus respetando filtros y presupuesto. En modo híbrido también recupera entradas humanas anteriores del mismo hilo mediante embeddings. Devuelve identificadores y cantidad; no pensamientos privados.
- tool_check_sla_policy aplica prioridad y primera respuesta según impacto declarado. El modelo no puede modificar esos argumentos.
- tool_draft_response genera, comprueba citas y tema y escribe el borrador en SQLite case_notes mediante save_draft. Devuelve saved_draft_id y write_target. Es una herramienta de generación y escritura efectiva, no solo un texto que simula haber guardado algo.

La herramienta de escritura requiere búsqueda y política completadas. Sin documentos no genera ni escribe un borrador. Si la validación falla no se registra como aceptado. La persistencia del historial corto ocurre al terminar la solicitud, incluso para registrar el resultado de una abstención. Todo borrador queda needs_review=true; guardarlo no es aprobarlo ni enviarlo.

## Memoria corta · IE3

MemoryStore guarda sesiones UUID en SQLite. La ventana retiene tres intercambios; al excederla agrega extractos de hasta 240 caracteres de entradas humanas a un resumen limitado a 900. El resumen es determinista, no generado por un LLM. La ruta normal es runtime/memory.sqlite3, fuera de Git y ZIP.

El generador recibe como máximo dos entradas recientes recortadas, resumen filtrado y, si aplica, contexto semántico de entradas antiguas. Los borradores previos pueden verse en pantalla pero no se convierten en evidencia ni se insertan en la consulta de recuperación.

Un cambio de tema reconocido, como facturación a VPN, excluye antecedentes anteriores para esa consulta y muestra context_control.topic_change. Las consultas sin señal explícita conservan continuidad. Las mixtas o ambiguas requieren revisión: no hay detección universal de tema.

## Memoria persistente y semántica · IE4

case_notes guarda como máximo veinte registros por hilo, independientes de la ventana corta. Cada registro contiene un UUID, la entrada humana redactada y el borrador pendiente. save_draft elimina registros anteriores al límite. DELETE /api/sessions/{id} borra tanto sesiones como case_notes del hilo.

Con CATIA_RETRIEVER=hybrid y nomic-embed-text disponible, la búsqueda combina TF-IDF y embeddings del corpus. search_notes obtiene vectores de la consulta y de las entradas humanas persistidas, filtra temas incompatibles y recupera hasta dos con coseno mínimo 0,65. Los identifica como semantic_history_ids en la observación. Sus textos se agregan a conversation_context.semantic_history como antecedentes no confiables, nunca como citas documentales.

La recuperación está aislada al mismo UUID y permite continuar tras reiniciar; no conecta hilos distintos ni implementa identidad multiusuario. Los vectores se calculan en memoria al consultar, no se persisten en una base vectorial. Para veinte registros por hilo es sencillo; con mayor volumen se necesitaría indexación y políticas de retención más completas.

En modo lexical no existe esta recuperación semántica de historial. Ese modo sirve como baseline o ensayo de bajo costo, pero no debe presentarse como evidencia del requisito semántico. reports/feedback_real.json compara recuperación original, expansión y modo híbrido y guarda la prueba de memoria con embeddings reales.

## Planificación y decisiones · IE5–IE6

run_react implementa un ciclo explícito de tres herramientas distintas. Al inicio Ollama elige por JSON restringido entre búsqueda y política; cuando solo queda una acción válida, el código la ejecuta directamente. Borrador y escritura requieren ambas consultas completadas. La política se aplica también si falla el planificador. No hay acciones arbitrarias ni bucles abiertos.

run_crew crea tres Agent, tres Task y Process.sequential con contexto de tareas previas: Triage consulta SLA, Investigador busca y Redactor genera y registra. Cada rol tiene una sola herramienta. LocalStageLLM traduce una acción JSON validada al protocolo Action/Action Input de CrewAI. No se presenta como elección libre entre varias acciones en cada rol. Las observaciones finales se componen desde el resultado validado.

Escenarios reproducibles: continuidad del mismo tema; cambio de factura a VPN con descarte de contexto; ausencia de INT-FAC al filtrar externas; salida incorrecta inyectada que activa evidence_mismatch; proveedor desconectado simulado que activa provider_error. docs/13_prompts_demostracion.md indica pasos, salidas y explicación. Los fallos se detienen y no se disfrazan como éxito.

El respaldo a DemoGenerator requiere casilla explícita y un fallo de proveedor. Se identifica como fallback_demo, con requested_provider y mode distintos. Una salida desalineada no se convierte silenciosamente en simulación exitosa.

## Arquitectura y flujo · IE7–IE9

docs/arquitectura.mmd y deliverables/arquitectura_EA2.pdf representan la implementación actual. El diagrama está también dentro de docs/presentacion_EA2_CAT-IA.pdf. El README contiene un diagrama Mermaid y enlaces a las instrucciones. La presentación se guarda en docs/ como pide la pauta, sin otra copia idéntica en deliverables/.

Flujo: interfaz → API y validación → selección de contexto → modo individual/equipo → consulta documental y de memoria → política → generación → citas y coherencia temática → registro local → revisión humana. Una entrada inválida devuelve 422. Ausencia de fuentes devuelve insufficient_context; desalineación devuelve evidence_mismatch; fallos de herramientas quedan en tool_events y se devuelve un resultado controlado.

## ADR-01 · Framework y control

Decisión: herramientas tipadas LangChain y comparación opcional con CrewAI. Requerimiento: integrar consultas, escritura y decisiones visibles. Alternativa: funciones Python directas sin biblioteca; eran suficientes para EA1, pero no mostraban contratos de herramientas y roles de un framework. Costo: más dependencias y llamadas. No se exige un framework específico; la selección no garantiza escalabilidad empresarial.

## ADR-02 · Memoria

Decisión: ventana, resumen extractivo y registros SQLite acotados por hilo. Requerimiento: continuidad, persistencia y borrado verificables. Alternativas: historial completo en el prompt o resumen por LLM; aumentan contexto, costo o riesgo de errores. Límite: truncamiento y aislamiento solo local, sin autenticación. Los locks serializan el hilo dentro de un proceso, no garantizan transacciones completas entre varios workers.

## ADR-03 · Recuperación

Decisión: conservar TF-IDF como baseline y habilitar híbrido con embeddings para la demostración EP2. Requerimiento: recuperar paráfrasis y contexto persistente por similitud. Alternativa: solo reglas de sinónimos; mejora casos conocidos pero no cumple por sí sola recuperación semántica. Costo: descarga adicional, latencia y calibración. La similitud no es certeza; el filtro temático reduce algunos resultados ajenos sin resolver todos los falsos positivos.

## ADR-04 · Validación

Decisión: combinar contrato JSON, pertenencia literal de citas y coherencia temática antes de escribir. Requerimiento: impedir el caso de una respuesta de factura con citas de VPN. Alternativa: juez LLM adicional por cada afirmación; demanda recursos y también puede equivocarse. Límite: las reglas no prueban implicación semántica y pueden rechazar paráfrasis válidas o aceptar hechos falsos del mismo tema. La revisión humana permanece obligatoria.

## ADR-05 · Modelo local

Decisión: mantener qwen2.5:1.5b y ejecutar embeddings locales. Requerimiento: reproducibilidad en un equipo con recursos limitados y ausencia de credenciales cloud. Alternativa: un modelo mayor o remoto; requeriría medir calidad, costo y latencia antes de migrar. No se afirma que 1,5B cause los errores observados ni que un modelo mayor los elimine.

## API, instalación y pruebas

README.md y .env.example describen variables y arranque. GET /api/health informa configuración; no prueba inferencia. POST /api/tickets/analyze admite session_id, orchestration, use_context y allow_demo_fallback. POST/GET/DELETE /api/sessions permiten crear, consultar y borrar memoria corta; el borrado también elimina registros persistentes.

El prompt de EA2 sigue siendo v4; los controles nuevos son código, no entrenamiento ni cambios ocultos al prompt. La traza informa el prompt utilizado. usage cuenta tokens de generación final, no todas las llamadas de planificación o embeddings.

tests/test_feedback.py reproduce fallos controlados, cambio de tema, citas ajenas, escritura y borrado. reports/tests_feedback.xml y coverage_feedback.json registran la suite actual. scripts.evaluate_feedback ejecuta Ollama y embeddings reales con P1–P3. reports/FEEDBACK_RESULTADOS.md separa resultados actuales y anteriores. Las pruebas con mocks no acreditan calidad del LLM.

## Limitaciones y privacidad

Prototipo local con datos ficticios. Redacción parcial de patrones sensibles; no anonimización garantizada. Memoria y borradores persisten en runtime hasta borrado o límites; las descargas del navegador no se borran al eliminar un hilo. No hay autenticación, búsqueda entre usuarios ni conectores a sistemas reales. La fidelidad semántica completa y la generalización siguen pendientes de evaluación independiente.

## Referencias

Pauta local: EP2_ISY0101_Estudiante.pdf, páginas 1–8, facilitada por la estudiante. Retroalimentación docente copiada en la conversación, revisión del commit 32e3a7b y pruebas declaradas del 19/10/2026.

LangChain Core 1.6.9: https://reference.langchain.com/python/langchain-core/tools/convert/tool. CrewAI 1.15.27: https://docs.crewai.com/en/concepts/tasks y https://docs.crewai.com/en/concepts/tools. Ollama: https://docs.ollama.com/api/embed. Modelos: https://ollama.com/library/qwen2.5 y https://ollama.com/library/nomic-embed-text. Dependencias exactas en requirements.txt y requirements-ea2.txt; la versión local de Ollama se consulta con ollama --version.
