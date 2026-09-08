@echo off
REM Trabaja desde la carpeta de este archivo, aunque se abra con doble clic.
cd /d "%~dp0"
REM Crea un entorno Python aislado para las dependencias del proyecto.
python -m venv .venv
if errorlevel 1 exit /b 1
REM Instala las versiones declaradas en requirements.txt; requiere acceso a paquetes.
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
REM Crea la configuracion inicial solo si no existe; conserva los ajustes del usuario.
if not exist .env copy .env.example .env
echo Instalacion terminada. Ejecuta iniciar.bat
pause
