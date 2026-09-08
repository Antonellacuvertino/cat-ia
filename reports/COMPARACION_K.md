# Comparación controlada de recuperación

Se ejecutaron dos configuraciones sobre los mismos ocho casos de desarrollo y el mismo corpus: k=2 y k=4. La recuperación es TF-IDF; el proveedor demo no interviene en el ranking. Se mantuvieron umbral 0,06, fragmentación 110/20 y presupuesto 6500 caracteres.

Con k=2, precisión documental 0,929 y recall 0,952. Con k=4, precisión 0,893 y recall 1,000. Reducir k retiró ruido, pero perdió parte de la evidencia relevante. Se conserva k=4 como configuración inicial porque prioriza cobertura manteniendo precisión sobre la meta 0,70.

Los resultados corresponden a un corpus sintético pequeño, no establecen un óptimo universal. Los tiempos de estas corridas coexistieron con inferencia en CPU y no deben interpretarse como un benchmark de rendimiento controlado. Evidencia: evaluation_demo_dev_v2_k2.json y evaluation_demo_dev_v2_k4.json.
