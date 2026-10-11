# Guion sencillo para mostrar CAT-IA · EA2

Autoras: Antonella Cuvertino y Miriam Hammami. Docente: Sebastián Ignacio Sánchez Morales. Preparado el 11/10/2026.

## Preparación

En este computador están instaladas las dependencias EA2. En otro equipo ejecutar instalar.bat y después instalar_ea2.bat para habilitar CrewAI. Para inferencia real iniciar_modelo_local.bat corresponde únicamente al equipo que tiene la instalación portable; luego iniciar.bat y abrir http://127.0.0.1:8000. No iniciar dos servidores en el mismo puerto.

Para un ensayo rápido sin modelo, configurar CATIA_PROVIDER=demo en .env y reiniciar la aplicación. Para el LLM real usar ollama y comprobar su URL. Leer el aviso de modo antes de hablar. El modo equipo en CPU puede demorar más por sus consultas adicionales. No afirmar que el simulador es IA generativa.

## Diapositivas 1 y 2 · Antonella · 45 segundos

«Somos Antonella Cuvertino y Miriam Hammami. En esta segunda experiencia mejoramos CAT-IA, nuestro asistente de soporte para la empresa ficticia Nexo TI. Antes analizaba cada solicitud por separado. Ahora permite continuar una conversación y coordinar herramientas para preparar una respuesta con evidencia».

## Diapositiva 3 · Antonella · 40 segundos

«Organizamos el trabajo en tres herramientas. Una busca documentos; otra consulta las reglas de prioridad; y otra genera el borrador y comprueba sus citas. El agente solo puede usar herramientas permitidas, por eso no puede enviar correos ni ejecutar acciones sobre clientes».

Si preguntan por código: catia/tools.py, create_tools y execute_tool. La prioridad usa impacto declarado; no basta escribir URGENTE.

## Diapositiva 4 · Miriam · 40 segundos

«Cada conversación tiene su propio identificador. Conservamos los últimos tres intercambios y un resumen breve de entradas anteriores. Guardamos esto en SQLite para continuar después de reiniciar. El resumen es extractivo: recoge partes del texto, sin otra llamada de IA. Podemos borrar la memoria desde la pantalla».

Si preguntan por código: catia/memory.py, get, append y delete. La memoria no es entrenamiento y las respuestas anteriores no se convierten en documentos confiables.

## Diapositiva 5 · Miriam · 45 segundos

«Tenemos dos modos. El individual selecciona una herramienta disponible y sigue un ciclo limitado. En el equipo, CrewAI organiza tres roles en secuencia: Triage revisa la prioridad, el Investigador recupera documentos y el Redactor clasifica y prepara el borrador. En ambos casos una persona debe revisar la respuesta».

Si preguntan por código: catia/orchestration.py, run_react y run_crew. El modo individual usa herramientas de LangChain; el equipo utiliza objetos Agent, Task, context y Process.sequential de CrewAI.

## Diapositiva 6 · Demostración · 1 a 2 minutos más tiempo de inferencia

1. Abre la app. Di si estás usando demo o LLM real. Pulsa Borrar memoria y empezar para trabajar con un hilo limpio.

2. Selecciona Agente individual. Pulsa Cobro duplicado y después Analizar con evidencia. Muestra categoría, fuentes y Ver herramientas y agentes. El ejemplo desactiva contexto previo para no mezclar temas.

3. Activa Usar antecedentes de esta conversación. Escribe «¿Qué debo hacer en ese caso?» y vuelve a analizar. Muestra que el hilo conserva la consulta anterior sobre la factura. Verifica la respuesta, sin dar por correcto cualquier texto del modelo.

4. Abre Ver memoria de la conversación. Muestra los intercambios. Para enseñar el resumen, realiza más de tres consultas del mismo caso; evita hacerlo en vivo con LLM si el tiempo es corto. Se pueden preparar esos turnos antes o ensayarlos en demo.

5. Selecciona Equipo de 3 agentes. Envía de nuevo un caso claro. Muestra Triage, Investigador RAG y Redactor en las herramientas. Si ejecutas demo, explica que CrewAI sí se ejecuta, pero las decisiones del modelo son simuladas.

6. Pulsa Borrar memoria y empezar. Comprueba que desaparece el historial del hilo. Inicia un caso nuevo. No prometas que una pregunta genérica siempre se abstendrá: la similitud puede recuperar algún documento poco pertinente.

## Diapositiva 7 · Pruebas · 40 segundos

«Agregamos pruebas para comprobar que una sesión no use datos de otra, que la memoria persista, que se pueda borrar y que las herramientas rechacen acciones no permitidas. También distinguimos los ensayos con simulador de las pruebas reales con Ollama. Los resultados actuales están en el informe de EA2».

Para ejecutarlas: .\.venv\Scripts\python.exe -m pytest -q. Para evidencia detallada abrir reports/EA2_RESULTADOS.md. Leer el resultado real: no memorizar un número si luego cambia la suite.

## Diapositiva 8 · Cierre · 30 segundos

«El aporte de esta etapa es dar continuidad a los casos y hacer visible cómo colaboran memoria, herramientas y agentes. La aplicación sigue siendo un prototipo local. Las citas se comprueban, pero todavía necesitamos revisar si cada recomendación es correcta y pertinente antes de usarla».

## Si falla el modelo

Sin la casilla de respaldo se muestra un error controlado. Si habilitas Permitir simulación si falla el proveedor, la pantalla indica SIMULACIÓN DE RESPALDO cuando se utiliza. Di «el modelo falló; ahora mostramos el flujo simulado». No atribuyas ese borrador al LLM ni a una ejecución real del equipo.

## Tres respuestas cortas para practicar

¿Entrenaron una IA? «No modificamos los pesos del modelo. Adaptamos documentos, instrucciones, herramientas y memoria».

¿La memoria y el RAG son lo mismo? «No. La memoria conserva antecedentes del caso; el RAG busca documentos que respaldan la respuesta».

¿El sistema decide solo? «Decide dentro de un catálogo y límites programados. La prioridad sigue reglas y la persona revisa el borrador antes de usarlo».
