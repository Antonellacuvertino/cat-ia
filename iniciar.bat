@echo off
REM Fija la carpeta del proyecto antes de importar catia.api.
cd /d "%~dp0"
REM Comprueba que la instalacion preparo el interprete del entorno virtual.
if not exist ".venv\Scripts\python.exe" (
  echo Ejecuta primero instalar.bat
  pause
  exit /b 1
)
echo Abre http://127.0.0.1:8000 en tu navegador.
echo Para detener: Ctrl+C. El modo se configura en .env.
REM Inicia API y frontend en loopback. Mantener esta ventana abierta durante la demostracion.
".venv\Scripts\python.exe" -m uvicorn catia.api:app --host 127.0.0.1 --port 8000
pause
