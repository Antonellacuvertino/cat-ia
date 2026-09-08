@echo off
cd /d "%~dp0"
REM Ejecuta pruebas de comportamiento y guarda cobertura y resultados JUnit.
".venv\Scripts\python.exe" -m pytest --cov=catia --cov-report=term-missing --cov-report=json:reports/coverage.json --junitxml=reports/tests.xml
if errorlevel 1 exit /b 1
REM Evalua el simulador de forma explicita; esta ejecucion no mide un LLM real.
".venv\Scripts\python.exe" -m scripts.evaluate --provider demo
if errorlevel 1 exit /b 1
REM Regenera documentos y presentacion a partir del Markdown y las evidencias guardadas.
".venv\Scripts\python.exe" -m scripts.build_documents
pause
