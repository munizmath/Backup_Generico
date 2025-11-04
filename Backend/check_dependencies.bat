@echo off
REM check_dependencies.bat - Verificar e instalar dependencias automaticamente

echo Verificando dependencias do sistema...
echo.

set DEPENDENCIES_FRONTEND=%~dp0Frontend\Dependencias
set DEPENDENCIES_BACKEND=%~dp0Backend\Dependencias

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale Python 3.8+ de https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    echo OK: Python encontrado
)

REM Verificar dependencias do Frontend
echo.
echo Verificando dependencias do Frontend...
if not exist "%DEPENDENCIES_FRONTEND%" (
    echo Criando diretorio de dependencias do Frontend...
    mkdir "%DEPENDENCIES_FRONTEND%"
)

REM Verificar se dependencias estao instaladas (verificar arquivo especifico)
if not exist "%DEPENDENCIES_FRONTEND%\psutil" (
    echo Instalando dependencias do Frontend...
    cd "%DEPENDENCIES_FRONTEND%"
    call download_dependencies.bat
    cd "%~dp0"
) else (
    echo OK: Dependencias do Frontend encontradas
)

REM Verificar dependencias do Backend
echo.
echo Verificando dependencias do Backend...
if not exist "%DEPENDENCIES_BACKEND%" (
    echo Criando diretorio de dependencias do Backend...
    mkdir "%DEPENDENCIES_BACKEND%"
)

REM Verificar se dependencias estao instaladas (verificar arquivo especifico)
if not exist "%DEPENDENCIES_BACKEND%\psutil" (
    echo Instalando dependencias do Backend...
    cd "%DEPENDENCIES_BACKEND%"
    call download_dependencies.bat
    cd "%~dp0"
) else (
    echo OK: Dependencias do Backend encontradas
)

REM Verificar ferramentas do sistema
echo.
echo Verificando ferramentas do sistema...

REM Verificar 7-Zip
7z >nul 2>&1
if %errorlevel% neq 0 (
    echo AVISO: 7-Zip nao encontrado
    if exist "%DEPENDENCIES_BACKEND%\7zip-installer.exe" (
        echo Instalador 7-Zip encontrado em: %DEPENDENCIES_BACKEND%
    )
) else (
    echo OK: 7-Zip encontrado
)

REM Verificar Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo AVISO: Git nao encontrado
    if exist "%DEPENDENCIES_BACKEND%\git-installer.exe" (
        echo Instalador Git encontrado em: %DEPENDENCIES_BACKEND%
    )
) else (
    echo OK: Git encontrado
)

REM Verificar PowerShell
powershell -Command "& {$PSVersionTable.PSVersion.Major}" >nul 2>&1
if %errorlevel% neq 0 (
    echo AVISO: PowerShell nao encontrado
    if exist "%DEPENDENCIES_BACKEND%\powershell7-installer.msi" (
        echo Instalador PowerShell 7 encontrado em: %DEPENDENCIES_BACKEND%
    )
) else (
    echo OK: PowerShell encontrado
)

echo.
echo Verificacao de dependencias concluida!
echo.
echo Dependencias do Frontend: %DEPENDENCIES_FRONTEND%
echo Dependencias do Backend: %DEPENDENCIES_BACKEND%
echo.
pause
