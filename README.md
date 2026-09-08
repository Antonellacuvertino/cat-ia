# CAT-IA · Soporte con evidencia

Proyecto académico de Ingeniería de Software para ISY0101. Asistente de clasificación de tickets y propuestas de respuesta con recuperación aumentada. Organización ficticia: **Nexo TI**. No hay aprobación docente ni resultados organizacionales reales acreditados.

## Inicio rápido en Windows

1. Instalar Python 3.12 y ejecutar `instalar.bat` (requiere internet para dependencias).
2. Ejecutar `iniciar.bat` y abrir http://127.0.0.1:8000.
3. Seleccionar un caso de ejemplo y pulsar **Analizar con evidencia**.
4. Revisar categoría, prioridad, borrador, citas y recorrido del agente.
5. Ejecutar `verificar.bat` para pruebas, evaluación del simulador y PDF.

La entrega contiene las dependencias fijadas en `requirements.txt`. La carpeta `.venv` es local y se excluye del ZIP. No requiere Node, base de datos ni cuentas para el modo de práctica.

## Activar el LLM real

En el equipo donde se preparó esta entrega hay una instalación portable en `.tools/ollama` y modelos en `.tools/models`. `iniciar_modelo_local.bat` inicia ese servicio en el puerto 11435; mantener su ventana abierta y luego ejecutar `iniciar.bat`. La configuración local usa ese puerto. En otro equipo, el ZIP no incluye binarios ni modelos: seguir la instalación estándar de abajo, cuyo puerto es 11434.

Instalar Ollama desde https://ollama.com/download y ejecutar:

```powershell
ollama pull qwen2.5:1.5b
Copy-Item .env.example .env
```

Editar `.env`: `CATIA_PROVIDER=ollama`. Iniciar Ollama y reiniciar CAT-IA. Si ya existe `.env`, editarlo sin sobreescribirlo. La primera descarga del modelo requiere internet y varios GB libres; el rendimiento depende del equipo. Se propone un modelo pequeño, no se afirma que alcance las métricas objetivo sin evaluación.

Para recuperación semántica opcional:

```powershell
ollama pull nomic-embed-text
```

Configurar `CATIA_RETRIEVER=hybrid`. Combina coseno TF-IDF con coseno de embeddings densos. El comportamiento multilingüe del modelo de embeddings debe evaluarse en el corpus español antes de preferirlo. La ruta evaluada sin modelos es `lexical` (TF-IDF), una recuperación vectorial dispersa, no embeddings semánticos.

## Comandos de evaluación

La prueba real breve se ejecuta con `.\.venv\Scripts\python.exe -m scripts.smoke_llm`; guarda `reports/llm_smoke.json` y falla si no obtiene borrador validado. Para verificar la interfaz con CDP se requiere `requirements-browser.txt`; el script `scripts/check_browser.py` documenta el puerto de depuración esperado. Las capturas y el resultado del navegador están en reports.

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=catia --cov-report=json:reports/coverage.json --junitxml=reports/tests.xml
.\.venv\Scripts\python.exe -m scripts.evaluate --provider demo
.\.venv\Scripts\python.exe -m scripts.evaluate --provider ollama --prompt v2
.\.venv\Scripts\python.exe -m scripts.evaluate --provider ollama --prompt v3
.\.venv\Scripts\python.exe -m scripts.evaluate --provider ollama --prompt v1
.\.venv\Scripts\python.exe -m scripts.evaluate --provider ollama --baseline
.\.venv\Scripts\python.exe -m scripts.build_documents
.\.venv\Scripts\python.exe -m scripts.package
```

La evaluación CLI usa recuperación lexical para comparar en condiciones constantes. Activar `hybrid` en la app no cambia esa evaluación. Para medir embeddings, extender explícitamente el experimento y registrar el modelo; no atribuirle resultados del baseline lexical.

## Documentos

- `docs/01_propuesta_mejorada.md`: organización, objetivos y viabilidad.
- `docs/02_informe_tecnico.md`: requisitos, arquitectura, datos, decisiones y API.
- `docs/03_plan_pruebas.md`: pruebas, métricas, protocolo y evidencia.
- `docs/04_manual_usuario.md`: instalación, uso y resolución de problemas.
- `docs/05_guia_defensa.md`: explicación del código, guion, preguntas y cambios en vivo.
- `docs/06_matriz_rubrica.md`: IE1–IE9, archivos y estado verificable.
- `docs/07_presentacion.md`: contenido editable de las diapositivas.
- `docs/08_entrega.md`: pasos pendientes y preparación de entrega.
- `docs/09_demostracion_paso_a_paso.md`: clics, comandos, qué decir y recorrido del código comentado.
- `deliverables/`: PDF de los documentos y presentación.
- `reports/`: pruebas y métricas efectivamente ejecutadas.

## Estructura

`catia/` contiene configuración, contratos, recuperación, proveedores, agente y API. `web/` contiene la interfaz sin frameworks de frontend. `data/` contiene las fuentes y su manifiesto con hashes. `prompts/` conserva v1 zero-shot, v2 contextual y v3 con taxonomía optimizada a partir de errores observados. `evaluation/` separa desarrollo y prueba. `tests/` valida comportamientos. `scripts/` reproduce los artefactos.

## Límites importantes

El modo **demo** es un simulador, no un LLM. Las pruebas con mocks validan contratos, no inferencia real. La comprobación de citas exactas no demuestra fidelidad semántica; el operador debe comprobarla. Hay evaluaciones del LLM local en `reports/`, incluyendo una regresión de v3 sobre casos conocidos. No se garantiza una calificación: falta la aprobación del caso, la revisión semántica humana y la defensa individual. La aplicación se ejecuta en loopback y no incluye autenticación empresarial ni persistencia de tickets. Las fuentes externas son síntesis verificadas, no búsqueda web en vivo.
