@echo off
setlocal

REM Ejecutar siempre desde la carpeta del script
cd /d "%~dp0"

set "VENV_DIR="
set "ACTIVATE_BAT="
set "PYTHON_EXE="
set "PORT=8000"
set "HOST=127.0.0.1"
set "RUN_SEED=0"

echo.
echo [1/8] Verificando Python...
where python >nul 2>nul
if errorlevel 1 (
    echo No se encontro Python en PATH.
    echo Instala Python y vuelve a ejecutar este script.
    exit /b 1
)

echo.
echo [2/8] Verificando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    set "VENV_DIR=venv"
) else if exist ".venv\Scripts\activate.bat" (
    set "VENV_DIR=.venv"
) else (
    set "VENV_DIR=venv"
    echo No existe venv ni .venv. Creando entorno virtual en "%VENV_DIR%"...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Error al crear el entorno virtual.
        exit /b 1
    )
)
set "ACTIVATE_BAT=%VENV_DIR%\Scripts\activate.bat"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
echo Entorno virtual seleccionado: %VENV_DIR%

echo.
echo [3/8] Activando entorno virtual...
call "%ACTIVATE_BAT%"
if errorlevel 1 (
    echo Error al activar el entorno virtual.
    exit /b 1
)

echo.
echo [4/8] Instalando dependencias...
if not exist "requirements.txt" (
    echo No se encontro requirements.txt en %CD%.
    exit /b 1
)
pip install -r requirements.txt
if errorlevel 1 (
    echo Error instalando dependencias.
    exit /b 1
)

echo.
echo [5/8] Aplicando migraciones...
"%PYTHON_EXE%" manage.py migrate
if errorlevel 1 (
    echo Error aplicando migraciones.
    exit /b 1
)

echo.
echo [6/8] Verificando si ejecutar seed...
if /I "%SEED%"=="1" (
    set "RUN_SEED=1"
    echo SEED=1 detectado: se ejecutara seed de forma forzada.
) else (
    if not exist "db.sqlite3" (
        set "RUN_SEED=1"
        echo db.sqlite3 no existe: se ejecutara seed.
    ) else (
        "%PYTHON_EXE%" manage.py shell -c "from comisiones.models import Venta, Incidencia; import sys; sys.exit(0 if (Venta.objects.exists() or Incidencia.objects.exists()) else 1)"
        if errorlevel 1 (
            set "RUN_SEED=1"
            echo Base de datos vacia: se ejecutara seed.
        ) else (
            echo Base de datos con datos: seed omitido.
        )
    )
)

if "%RUN_SEED%"=="1" (
    echo.
    echo Ejecutando seed demo...
    "%PYTHON_EXE%" manage.py seed
    if errorlevel 1 (
        echo Error ejecutando seed.
        exit /b 1
    )
)

echo.
echo [7/8] Opcional - crear superusuario
choice /C SN /N /M "Deseas crear un superusuario ahora? (S/N): "
if errorlevel 2 goto skip_superuser
if errorlevel 1 (
    echo.
    echo Iniciando formulario interactivo de superusuario...
    "%PYTHON_EXE%" manage.py createsuperuser
    if errorlevel 1 (
        echo Error creando superusuario.
        exit /b 1
    )
)

:skip_superuser
echo.
echo [8/8] Abriendo navegador y ejecutando servidor...
start "" "http://%HOST%:%PORT%/"
echo Servidor disponible en: http://%HOST%:%PORT%/
echo.
"%PYTHON_EXE%" manage.py runserver %HOST%:%PORT%

endlocal
