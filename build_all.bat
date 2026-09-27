@echo off
REM ===================================================================
REM Script de compilación automática para Tok-Transcript
REM Genera la versión Portable y el Instalador Windows
REM ===================================================================

echo [1/3] Limpiando carpetas de compilaciones anteriores...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q dist-installer 2>nul

echo [2/3] Compilando ejecutable portable con PyInstaller...
pyinstaller pyinstaller.spec --clean
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] La compilacion con PyInstaller fallo.
    pause
    exit /b %ERRORLEVEL%
)

echo [OK] Version portable generada en: dist\TokTranscript\

echo [3/3] Buscando Inno Setup (ISCC.exe) para compilar el instalador...
set ISCC_PATH="%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not exist %ISCC_PATH% (
    set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if not exist %ISCC_PATH% (
    set ISCC_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
)

if exist %ISCC_PATH% (
    echo Compilando instalador setup.exe con Inno Setup...
    %ISCC_PATH% installer.iss
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Instalador generado en: dist-installer\TokTranscript-Setup-v1.0.0.exe
    ) else (
        echo [ALERTA] Inno Setup fallo al compilar.
    )
) else (
    echo [AVISO] Inno Setup no esta instalado en las rutas por defecto.
    echo Puedes instalarlo ejecutando: winget install JRSoftware.InnoSetup -e
    echo Y luego ejecutar: "ISCC.exe installer.iss" para generar el instalador.
)

echo ===================================================================
echo Proceso finalizado con exito!
echo ===================================================================
pause
