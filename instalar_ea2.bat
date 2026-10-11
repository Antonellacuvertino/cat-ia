@echo off
REM Instala ambos modos de EA2; la instalacion base ya permite el agente individual.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Ejecuta primero instalar.bat
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements-ea2.txt
if errorlevel 1 exit /b 1
echo EA2 instalada. Reinicia iniciar.bat para usar ambos modos.
pause
