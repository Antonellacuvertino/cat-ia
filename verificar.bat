@echo off
cd /d "%~dp0"
REM Ejecuta pruebas de comportamiento y guarda cobertura y resultados JUnit.
".venv\Scripts\python.exe" -m pytest --cov=catia --cov-report=term-missing --cov-report=json:reports/coverage_ea2.json --junitxml=reports/tests_ea2.xml
if errorlevel 1 exit /b 1
REM Evalua el simulador de forma explicita; esta ejecucion no mide un LLM real.
".venv\Scripts\python.exe" -m scripts.evaluate --provider demo
if errorlevel 1 exit /b 1
REM Prueba la continuidad EA2 con simulador; no acredita calidad del LLM.
".venv\Scripts\python.exe" -m scripts.smoke_ea2 --provider demo --mode react --followup
if errorlevel 1 exit /b 1
REM Regenera documentos y presentacion a partir del Markdown y las evidencias guardadas.
".venv\Scripts\python.exe" -m scripts.build_documents
pause
