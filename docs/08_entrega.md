# Preparación de la entrega

## Archivos principales

Entregar dist/CAT-IA_entrega.zip con código, requirements.txt, configuración de ejemplo, fuentes, prompts, pruebas, evaluación, documentación y PDF. El ZIP excluye .venv, .env, runtime, cachés, herramientas locales y modelos. Los binarios/modelos se instalan según el README. La presentación es deliverables/presentacion_CAT-IA.pdf; el informe y la guía están en la misma carpeta.

## Antes de entregar

1. Completar nombres de integrantes, sección, fecha y docente en propuesta y presentación.
2. Confirmar aprobación del caso ficticio o reformular con la organización autorizada.
3. Ejecutar Ollama y al menos una consulta real; luego evaluación v1/v2 y baseline según el plan.
4. Completar revisión humana de fidelidad y relevancia; registrar resultados sin atribuir cifras demo al LLM.
5. Ejecutar verificar.bat, revisar reports y regenerar PDF. scripts.build_documents no inventa resultados pendientes.
6. Ejecutar scripts.package y verificar instalación desde una carpeta nueva o equipo de la pareja.
7. Ensayar la demo y cambios en vivo sin apoyo externo. Ambos integrantes deben comprender el código.
8. Revisar que el ZIP no contenga secretos o datos personales reales.
9. Subir a AVA y enviar al correo del docente dentro del plazo indicado por él. El proyecto no realiza ese envío automáticamente.

## Honestidad de la evidencia

La comprobación del paquete se guarda fuera del ZIP, en dist/package_check.json, con el hash del archivo verificado. El paquete incorpora su propio MANIFEST_ENTREGA.json. La prueba de extracción reutiliza las dependencias instaladas: verifica completitud de fuentes y arranque aislado, no representa una instalación en un sistema operativo diferente.

No afirmar que una organización ficticia es real, que el docente aprobó el caso sin constancia, que resultados sintéticos son observaciones empresariales ni que un mock es inferencia. Identificar asistencia utilizada conforme a las reglas del curso y asumir responsabilidad de entender, probar y defender el código. La defensa exige resolver personalmente un nuevo requerimiento.

## Material del curso

Los PDF y notebooks aportados son referencias de estudio. No se redistribuyen íntegros en el ZIP. La entrega contiene código y documentos nuevos adaptados a la pauta, junto con fuentes propias simuladas y síntesis externas referenciadas. Los ejemplos de API Gateway/IDaaS aportados no se incorporan como requisitos adicionales: esta pauta evalúa LLM/RAG, y el prototipo local no necesita microservicios ni identidad empresarial para demostrar el flujo.
