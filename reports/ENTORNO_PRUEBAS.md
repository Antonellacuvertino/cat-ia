# Entorno y avisos de las pruebas

Ejecución local en Windows con Python 3.12.5. Las versiones de dependencias del proyecto se fijan en requirements.txt. La verificación visual opcional utiliza requirements-browser.txt.

La suite final de software registró 33 pruebas aprobadas y dos avisos de deprecación: Starlette advierte sobre el uso de httpx con TestClient y sobre el alias anyio.abc.BlockingPortal. No hubo errores ni fallos de pruebas. No se ocultaron los avisos mediante filtros. Son compatibilidades a revisar en una actualización futura de dependencias; el entorno exacto probado permanece fijado.

La inferencia utiliza Ollama portable 0.33.3 y Qwen 2.5 1.5B sobre CPU. Los JSON de cada corrida registran el modelo, prompt, corpus, configuración, uso y duración. El equipo ejecutaba otras herramientas de desarrollo durante parte de las mediciones: no se presentan las latencias como un benchmark controlado ni se extrapolan a otro hardware.

Los resultados del navegador corresponden a Microsoft Edge headless en escritorio y viewport de 390 píxeles, en modo demo. La inferencia real se verificó por separado mediante el mismo agente de aplicación. La verificación del ZIP utiliza una extracción temporal con las dependencias instaladas, no una máquina virtual limpia.
