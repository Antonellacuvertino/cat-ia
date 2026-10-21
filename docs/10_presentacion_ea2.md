# CAT-IA · Agente funcional
Ingeniería de Soluciones con IA · ISY0101
Antonella Cuvertino y Miriam Hammami
Docente: Sebastián Ignacio Sánchez Morales
EP2 · Presentación individual · 21/10/2026

## 01 · Problema y propósito
- Nexo TI es una empresa ficticia con solicitudes de soporte.
- CAT-IA consulta documentos, mantiene contexto y registra un borrador.
- El operador revisa la evidencia antes de responder al cliente.

## 02 · Orquestación
- Diagrama del flujo real, con memoria, herramientas y validación.

## 03 · Por qué estos componentes
- LangChain: contratos de herramientas; CrewAI: roles secuenciales.
- SQLite: persistencia local sencilla, sin servidor adicional.
- Ollama: inferencia local; embeddings: búsqueda por similitud.

## 04 · Qué decide cada parte
- El modelo elige el orden inicial y redacta con el contexto disponible.
- El código impone límites, prioridad, filtros y validaciones.
- La persona revisa el borrador: ningún agente envía respuestas.

## 05 · Memoria y recuperación
- Corto plazo: tres intercambios y resumen extractivo.
- Largo plazo: hasta veinte registros; búsqueda semántica en el mismo hilo.
- Un cambio de tema conocido excluye antecedentes incompatibles.

## 06 · Lo que detectó el profesor
- Una paráfrasis de cobro no recuperaba el documento.
- La memoria de factura contaminó una consulta nueva sobre VPN.
- La cita existía, pero no justificaba lo que decía la respuesta.

## 07 · Correcciones y límites
- Comparamos TF-IDF, expansión léxica y recuperación híbrida.
- Comprobamos coherencia temática y retenemos borradores sospechosos.
- Estos controles son acotados: no certifican fidelidad semántica.

## 08 · Demostración reproducible
- Continuidad: cobro duplicado → «¿Qué hago en ese caso?».
- Cambio: «no me conecta la VPN» en el mismo hilo.
- Sin fuente: cobro duplicado con filtro «Solo externas».

## 09 · Evidencia y conclusión
- Mostrar reports/FEEDBACK_RESULTADOS.md y las trazas.
- Distinguir inferencia real, pruebas simuladas y fallos controlados.
- No atribuimos la falla al tamaño del modelo sin compararlo.
