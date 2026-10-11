# CAT-IA · Soporte con evidencia

Asistente de soporte para **Nexo TI**, una organización ficticia. Clasifica solicitudes, recupera documentación interna y externa y prepara respuestas con citas para revisión humana. La Experiencia 2 incorpora memoria de conversación y coordinación de herramientas.

**Autoras:** Antonella Cuvertino y Miriam Hammami

**Docente:** Sebastián Ignacio Sánchez Morales

**Asignatura:** ISY0101 · Ingeniería de Software

**Estado:** prototipo académico local · EA2 actualizada el 11/10/2026

## Funcionalidades

- RAG sobre nueve documentos: siete internos simulados y dos síntesis de guías de Mozilla con procedencia registrada.
- Sesiones persistentes en SQLite: tres intercambios recientes, resumen extractivo y borrado desde la interfaz.
- Agente individual con ciclo ReAct acotado y herramientas tipadas de LangChain.
- Equipo CrewAI secuencial: Triage, Investigador RAG y Redactor.
- Prioridad por política, validación de citas, trazas de herramientas y revisión humana obligatoria.
- Ollama para inferencia local; simulador explícito para ensayar sin modelo.

## Inicio rápido · Windows

Requisito: Python 3.12. La instalación necesita internet.

```powershell
.\instalar.bat
.\instalar_ea2.bat
.\iniciar.bat
```

Abre **http://127.0.0.1:8000**. El segundo instalador añade CrewAI; la instalación base permite el modo individual. No se necesitan Node ni servicios de base de datos: SQLite viene con Python. La API se documenta en http://127.0.0.1:8000/docs mientras la app está encendida.

Para practicar: selecciona **Cobro duplicado**, analiza el caso, activa **Usar antecedentes** y pregunta «¿Qué debo hacer en ese caso?». Revisa memoria, herramientas y fuentes. Borra el hilo cuando cambies de caso. Lee el aviso que identifica simulación o LLM.

## Configurar Ollama

Instala [Ollama](https://ollama.com/download) y descarga el modelo:

```powershell
ollama pull qwen2.5:1.5b
```

El instalador prepara `.env` desde `.env.example` si no existe. Edita la configuración y reinicia la app:

```dotenv
CATIA_PROVIDER=ollama
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:1.5b
CATIA_ORCHESTRATION=react
CATIA_MEMORY_WINDOW=3
CATIA_RETRIEVER=lexical
```

En el computador original, `iniciar_modelo_local.bat` usa la instalación portable de `.tools/` en el puerto **11435**. Esa instalación y sus modelos no se incluyen en GitHub ni en el ZIP. En otro equipo utiliza la instalación estándar y el puerto correspondiente.

Para ensayar sin inferencia configura `CATIA_PROVIDER=demo`. El respaldo automático a demo está desactivado: solo se permite con la casilla explícita de la interfaz y se identifica en el resultado. La recuperación híbrida opcional requiere `nomic-embed-text` y `CATIA_RETRIEVER=hybrid`; sus métricas no deben confundirse con las del recuperador TF-IDF evaluado.

## Documentos para presentar EA2

| Archivo | Uso |
|---|---|
| [Presentación EA2](deliverables/presentacion_EA2_CAT-IA.pdf) | Ocho diapositivas para la clase. |
| [Guion de Antonella y Miriam](deliverables/11_guion_clase_ea2.pdf) | Qué decir y cómo demostrar la app paso a paso. |
| [Dossier EA2](deliverables/dossier_EA2_CAT-IA.pdf) | Implementación, decisiones, guion y resultados consolidados. |
| [Arquitectura EA2](deliverables/arquitectura_EA2.pdf) | Componentes y flujo de la solución. |
| [Informe editable](docs/03_agentes_ea2.md) | Contratos, memoria, agentes, API y limitaciones. |
| [Resultados verificables](reports/EA2_RESULTADOS.md) | Evidencia de pruebas y alcance de las mediciones. |

Los Markdown son las fuentes editables de los PDF. EA1 se conserva en un [dossier consolidado](deliverables/dossier_completo_CAT-IA.pdf), su [presentación](deliverables/presentacion_CAT-IA.pdf) y su [arquitectura](deliverables/arquitectura_EA1.pdf). Sus secciones están en `docs/01`–`09`; describen la etapa anterior. Entrega EA1: 09/09/2026. Fecha de entrega EA2 por confirmar.

## Verificación y entrega

```powershell
# Software: no requiere Ollama; CrewAI se prueba si está instalado.
.\.venv\Scripts\python.exe -m pytest -q tests --junitxml=reports/tests_ea2.xml --cov=catia --cov-report=json:reports/coverage_ea2.json

# Integración real: requiere Ollama y el modelo configurado.
.\.venv\Scripts\python.exe -m scripts.smoke_ea2 --provider ollama --mode react --followup
.\.venv\Scripts\python.exe -m scripts.smoke_ea2 --provider ollama --mode crew

# Documentos y paquete de entrega.
.\.venv\Scripts\python.exe -m scripts.build_documents
.\.venv\Scripts\python.exe -m scripts.package
.\.venv\Scripts\python.exe -m scripts.check_package
```

`verificar.bat` reúne las pruebas de software, el ensayo simulado y la generación de PDF. El ZIP se crea en `dist/CAT-IA_entrega.zip`; no se versiona porque puede regenerarse. Su comprobación valida hashes y arranque desde una extracción con las dependencias del entorno actual.

Evidencia registrada al 11/10/2026: **45 pruebas sin fallos**, cobertura de líneas **93,8 %**, comprobaciones de interfaz y tres consultas reales de integración con Ollama (dos individuales y una con CrewAI). Estas consultas tardaron aproximadamente 105–157 segundos en este equipo. No constituyen una evaluación independiente de calidad del modelo.

## Organización del repositorio

| Carpeta | Contenido |
|---|---|
| `catia/` | API, contratos, recuperación, generación, memoria, herramientas y agentes. |
| `web/` | Interfaz HTML, CSS y JavaScript. |
| `data/`, `config/` | Corpus, manifiesto de fuentes y configuración RAG. |
| `prompts/` | Versiones v1–v3 de EA1 y v4 con continuidad para EA2. |
| `tests/`, `evaluation/` | Pruebas de software y casos de evaluación. |
| `reports/` | Evidencias identificadas por etapa, modelo y experimento. |
| `docs/`, `deliverables/` | Fuentes editables y siete PDF seleccionados para consulta y exposición. |
| `scripts/` | Evaluación, verificación y generación reproducible de entregables. |

Se conservan los experimentos y prompts anteriores para comparar resultados. Se omiten PDF por capítulo que duplicaban los dossiers. `.env`, memoria, trazas locales, modelos, entorno virtual, cachés y ZIP generados quedan excluidos del repositorio.

## Alcance y límites

La memoria aporta antecedentes; no entrena el modelo ni convierte respuestas anteriores en evidencia. Las fuentes externas están incorporadas al corpus: no hay búsqueda web en vivo ni conexión a cuentas de Gmail o Microsoft. El sistema no envía respuestas a clientes.

La coincidencia de una cita no demuestra fidelidad semántica. La revisión humana de fidelidad y relevancia sigue pendiente. El prototipo funciona en loopback, sin autenticación empresarial, y debe usarse con datos ficticios. El resumen puede perder matices. Las métricas EA1 no se transfieren al prompt v4 ni garantizan desempeño organizacional o una calificación.
