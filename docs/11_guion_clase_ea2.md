# Guion individual · CAT-IA · EP2

Ingeniería de Soluciones con IA (ISY0101). Autoras: Antonella Cuvertino y Miriam Hammami. Docente: Sebastián Ignacio Sánchez Morales. Actualización: 21/10/2026.

La pauta indica presentación individual: cada integrante debe practicar el recorrido completo. El repositorio representa 20% y la presentación 80% de esta evaluación. La fecha límite se consulta en AVA.

## Antes de presentar

Ejecuta instalar.bat e instalar_ea2.bat si es otro computador. Inicia Ollama con los modelos qwen2.5:1.5b y nomic-embed-text descargados. Configura CATIA_PROVIDER=ollama y CATIA_RETRIEVER=hybrid. En este computador portable, OLLAMA_URL usa 11435; una instalación estándar suele usar 11434. Ejecuta iniciar.bat y abre http://127.0.0.1:8000. Confirma el aviso LLM y recuperador híbrido. No basta que health responda para garantizar que el modelo genera.

Abre la presentación en docs/presentacion_EA2_CAT-IA.pdf y los archivos catia/orchestration.py, catia/tools.py, catia/guardrails.py y reports/FEEDBACK_RESULTADOS.md. Lee también docs/13_prompts_demostracion.md. Usa datos ficticios. Ensaya las consultas antes: la latencia varía por equipo; el profesor informó 11–17 segundos en el suyo, no es una promesa para el nuestro.

## Diapositivas 1 y 2 · 40 segundos

«Soy [tu nombre]. Con mi compañera desarrollamos CAT-IA para la organización ficticia Nexo TI. El problema es atender solicitudes usando procedimientos dispersos sin perder los antecedentes del caso. El agente consulta documentos, determina la prioridad según una política y prepara un borrador que registra localmente. Una persona siempre lo revisa».

## Diapositiva 3 · Diagrama · 45 segundos

«La solicitud entra por la API. El sistema selecciona el contexto del hilo y el modo de trabajo. Las herramientas consultan la política, recuperan documentos y generan un borrador. Antes de registrarlo, comprobamos citas y coherencia temática. Si falta evidencia o falla una herramienta, mostramos una abstención o un error controlado».

Señala las flechas, la memoria y las ramas de fallo. No enumeres módulos sin explicar qué información pasa entre ellos.

## Diapositiva 4 · Decisiones de diseño · 40 segundos

«Elegimos LangChain para declarar herramientas con argumentos validados y CrewAI para mostrar roles con tareas secuenciales. SQLite resuelve la persistencia de este prototipo sin desplegar otro servidor. Ollama permite ejecutar localmente el modelo. Agregamos embeddings para comparar significado aproximado, aunque requieren un modelo adicional y evaluación en español».

## Diapositiva 5 · Autonomía · 35 segundos

«El modelo puede elegir entre buscar o consultar la política al inicio del flujo individual, y redacta la respuesta. El código decide los pasos obligatorios, el número máximo de llamadas y los controles. En CrewAI los roles están predefinidos. No presentamos esta autonomía limitada como un agente que pueda ejecutar cualquier acción».

## Diapositiva 6 · Memoria · 40 segundos

«La ventana conserva tres intercambios y un resumen extractivo. Además, registramos hasta veinte borradores pendientes con la entrada humana. En modo híbrido recuperamos por similitud entradas del mismo hilo, incluso si salieron de la ventana. Los borradores previos no se convierten en fuentes documentales. El borrado elimina ambos almacenamientos del hilo».

## Diapositivas 7 y 8 · Retroalimentación · 50 segundos

«El profesor encontró una paráfrasis que TF-IDF no reconocía y una respuesta sobre facturación cuando el usuario había cambiado a VPN. Además, las citas eran auténticas pero no respaldaban esa respuesta. Incorporamos un control de cambio de tema y una validación temática adicional. La expansión por sinónimos y los embeddings son mecanismos distintos. No hemos demostrado que cambiar a un modelo más grande resuelva estos errores».

## Diapositiva 9 · Demostración

Borra memoria, usa Agente individual y fuentes internas y externas. Ejecuta en orden:

1. «Mi factura tiene un cobro duplicado». Muestra el borrador, INT-FAC y saved_draft_id en las herramientas.
2. «¿Qué debo hacer en ese caso?» con antecedentes activados. Muestra el uso del hilo.
3. «no me conecta la VPN» sin borrar el hilo. Muestra el aviso de cambio de tema y verifica que no aconseje revisar facturas. Si se retiene el borrador, explica evidence_mismatch.
4. Cambia Fuentes consultadas a Solo externas. Envía «me cobraron dos veces» sin antecedentes. Explica por qué falta el procedimiento interno y el sistema se abstiene. Restaura el filtro.
5. Si queda tiempo, repite un caso claro con Equipo de 3 agentes y muestra Triage, Investigador y Redactor.

No ocultes una salida distinta de la esperada. Descarga el JSON y señala status, sources, tool_events, context_control, warning y timings. La pauta valora explicar un fallo con evidencia.

## Diapositiva 10 · 30 segundos

«Las pruebas comprueban contratos y los escenarios reproducibles. Las inferencias guardadas muestran lo que ocurrió en esos casos, no una garantía general. El aporte es continuar el trabajo, hacer visibles las herramientas y detectar algunas respuestas desalineadas antes de que el operador las use».

## Si te piden cambiar algo en vivo

Para top_k, usa el selector de fragmentos y explica que más contexto puede aumentar cobertura y ruido. Para impacto, cambia Personas afectadas y Servicio interrumpido: la prioridad sale de priority_for en catia/agent.py. Para ignorar antecedentes, desactiva la casilla y muestra context_control. Para ver el prompt, abre prompts/v4.txt: es una instrucción, no entrenamiento. Si editas código debes reiniciar la app; no prometas que se recarga automáticamente.

## Preguntas para practicar

Consulta docs/14_preguntas_defensa.md. Practica cada respuesta con el archivo abierto y un ejemplo de tu aplicación. No memorices métricas históricas como si fueran resultados del código actual.
