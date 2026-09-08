@echo off
cd /d "%~dp0"
REM Este lanzador requiere la instalacion portable ya preparada en este equipo.
if not exist ".tools\ollama\ollama.exe" (
  echo Ollama portable no esta incluido en el ZIP. Instala Ollama segun README.
  pause
  exit /b 1
)
REM Usa el puerto 11435, que debe coincidir con OLLAMA_URL en .env.
set OLLAMA_HOST=127.0.0.1:11435
REM Busca los modelos descargados en la carpeta local excluida del ZIP.
set OLLAMA_MODELS=%~dp0.tools\models
echo Servidor LLM local. Manten esta ventana abierta y ejecuta iniciar.bat.
REM Mantiene disponible el servidor que atiende las llamadas del generador.
".tools\ollama\ollama.exe" serve
pause
