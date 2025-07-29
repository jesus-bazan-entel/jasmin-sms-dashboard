@echo off
REM 🚀 Script de Inicio Rápido - Jasmin SMS Dashboard Backend (Windows)
REM Versión: 2.0.0
REM Descripción: Inicia el backend FastAPI con todas las dependencias

setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           🚀 JASMIN SMS DASHBOARD BACKEND STARTER            ║
echo ║                     Enterprise Edition v2.0.0               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Verificar si estamos en el directorio correcto
if not exist "main.py" (
    echo [ERROR] No se encontró main.py. Asegúrate de estar en el directorio raíz del proyecto.
    pause
    exit /b 1
)

echo [INFO] Iniciando Jasmin SMS Dashboard Backend...

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH.
    echo Por favor instala Python 3.11 o superior desde https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python version: %PYTHON_VERSION%

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo [WARNING] Entorno virtual no encontrado. Creando...
    python -m venv venv
    echo [SUCCESS] Entorno virtual creado
)

REM Activar entorno virtual
echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar e instalar dependencias
if not exist "venv\Lib\site-packages\fastapi" (
    echo [INFO] Instalando dependencias...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo [SUCCESS] Dependencias instaladas
) else (
    echo [INFO] Dependencias ya instaladas
)

REM Verificar archivo .env
if not exist ".env" (
    echo [WARNING] Archivo .env no encontrado.
    if exist ".env.example" (
        echo [INFO] Copiando .env.example a .env...
        copy .env.example .env
        echo [WARNING] ⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones
        echo [WARNING]    Especialmente la configuración de base de datos y claves secretas
        echo.
        set /p "edit_env=¿Quieres abrir el archivo .env para editarlo? (y/n): "
        if /i "!edit_env!"=="y" (
            notepad .env
        )
    ) else (
        echo [ERROR] No se encontró .env.example. Crea manualmente el archivo .env
        pause
        exit /b 1
    )
)

echo.
echo [SUCCESS] 🎉 ¡Configuración completada!
echo.
echo [INFO] Configuración:
echo   • Backend API: http://localhost:8000
echo   • Documentación API: http://localhost:8000/docs
echo   • Documentación Redoc: http://localhost:8000/redoc
echo   • WebSocket: ws://localhost:8000/ws
echo.
echo [INFO] Credenciales de administrador por defecto:
echo   • Email: admin@jasmin.com
echo   • Password: admin123
echo.

echo Selecciona el modo de inicio:
echo 1) Desarrollo (con recarga automática)
echo 2) Producción (optimizado)
echo 3) Solo verificar configuración (no iniciar)
echo.
set /p "mode=Opción (1-3): "

if "%mode%"=="1" (
    echo [INFO] Iniciando en modo desarrollo...
    echo.
    echo [WARNING] Presiona Ctrl+C para detener el servidor
    echo.
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
) else if "%mode%"=="2" (
    echo [INFO] Iniciando en modo producción...
    echo.
    echo [WARNING] Presiona Ctrl+C para detener el servidor
    echo.
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
) else if "%mode%"=="3" (
    echo [SUCCESS] Configuración verificada correctamente
    echo [INFO] Para iniciar manualmente:
    echo   • Desarrollo: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    echo   • Producción: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    echo.
    echo [INFO] No olvides configurar PostgreSQL y Redis si planeas usar funcionalidades completas
) else (
    echo [ERROR] Opción inválida
    pause
    exit /b 1
)

echo [SUCCESS] Script completado
pause