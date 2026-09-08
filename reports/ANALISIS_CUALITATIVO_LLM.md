# Análisis cualitativo de una inferencia real

La prueba de integración reports/llm_smoke.json utiliza Qwen 2.5 1.5B en Ollama local. La revisión descrita aquí fue realizada con asistencia de IA durante la implementación; no sustituye la revisión humana independiente solicitada al equipo.

## Hallazgos observados

El modelo identificó Soporte Técnico y resumió el problema de Firefox sin agregar una identidad. Seleccionó tres citas existentes, de EXT-COOKIE:0, EXT-NET:0 e INT-ACC:0. El esquema dinámico y el validador comprobaron que cada extracto pertenece a su fragmento.

La respuesta es general: sugiere consultar la guía, revisar conexión y extensiones y contactar soporte. La frase sobre un sitio que no se encuentre en la guía no está justificada como condición de escalamiento: las guías no son un catálogo de sitios del cliente. Esto ilustra por qué la validación mecánica de citas no equivale a fidelidad. Un operador debería eliminar esa condición y pedir el mensaje de error o confirmar el alcance.

## Fallo detectado y corrección

La primera ejecución fue rechazada por el validador; se conserva reports/llm_smoke_initial_rejected.json. La instrumentación inicial conservaba el estado de fallo, no el detalle completo de la respuesta descartada, por lo que no se puede reconstruir toda la causa semántica de ese intento. Durante el ajuste se eliminó la ambigüedad entre doc_id e id de fragmento en el prompt y se construyó un esquema dinámico con ids y extractos reales. Se exigió al menos una cita cuando existe contexto. La prueba posterior pasó el contrato sin eliminar la revisión humana.

## Próximo paso de evaluación

En la regresión v3 todas las categorías fueron correctas. Aun así, T13 añadió orientación sobre una cuenta bloqueada que el ticket no mencionaba. Esa recomendación existe en un documento recuperado, pero es poco pertinente para el reporte de un correo que solicita contraseña. Esto permite distinguir dos problemas: una afirmación sin respaldo y una orientación respaldada por un documento pero ajena a la necesidad concreta. El operador debería conservar el escalamiento de seguridad y retirar la orientación irrelevante.

Revisar todas las respuestas reales del dataset, no solo el ejemplo que funciona. Registrar recomendaciones no respaldadas, ambigüedades y omisiones. Completar la ficha humana con ambos integrantes. Si se modifica el prompt tras revisar estos casos, registrar la nueva versión y evaluar con casos nuevos; no llamar independiente a una evaluación utilizada para ajustar el sistema.
