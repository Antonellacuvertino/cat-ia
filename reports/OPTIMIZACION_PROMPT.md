# Optimización del prompt basada en errores observados

La evaluación de Qwen 2.5 1.5B con v2 obtuvo accuracy 0,80 y macro-F1 0,78 en 20 tickets sintéticos. Todos los casos con contexto produjeron borrador validado, pero cuatro categorías fueron incorrectas: T06, T12, T13 y T19. El contrato de salida no detecta por sí solo una categoría semánticamente incorrecta.

## Diagnóstico

T06 mezcló información de facturación con una intención de contratación. T12 clasificó phishing como Facturación pese a describir correctamente seguridad en la justificación. T13 se abstuvo de clasificar un posible incidente, aunque la categoría de soporte no exige confirmar la intrusión. T19 trató una cotización de soporte como una falla técnica: confundió el servicio mencionado con la intención del usuario.

## Cambio v3

Se explicita la taxonomía por intención del ticket: compra futura frente a cargos existentes, y reporte de seguridad frente a diagnóstico confirmado. Se separan hechos del ticket de documentos y ejemplos. Se añade un ejemplo comercial de un producto técnico y un ejemplo de phishing con palabras distintas del test. Se conserva la prohibición de inventar compromisos y el contrato de evidencia.

## Protocolo y limitación

Se conserva v2 y su reporte original. Se prueba v3 primero sobre desarrollo y luego se repite test como regresión. Esta comparación permite observar el efecto en los mismos casos, pero el test ya fue inspeccionado para diseñar v3: no es una medición independiente de generalización. El equipo debe validar con nuevos casos etiquetados por otra persona antes de afirmar rendimiento general. Los reportes guardan versión y hash del prompt y del corpus.

## Resultados ejecutados

v3 obtuvo macro-F1 0,905 y accuracy 0,875 en ocho casos de desarrollo. En la regresión de veinte casos obtuvo macro-F1 1,000 y accuracy 1,000, frente a 0,780 y 0,800 respectivamente de v2. Hubo 18 borradores generados y 2 abstenciones sin llamar al LLM por falta de evidencia. No hubo fallos de proveedor en esta corrida.

La mediana de latencia de v3 fue 45,42 segundos y el percentil 95 fue 71,36 segundos en este entorno CPU. La mejora de clasificación no implica que todos los borradores sean semánticamente correctos. Fidelidad y relevancia humanas siguen sin puntuación hasta revisar las respuestas. El informe conserva el error D08 del desarrollo y el primer rechazo de citas como evidencia de límites reales.
