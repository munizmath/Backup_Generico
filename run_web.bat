@echo off
REM Script para iniciar o servidor web
echo Iniciando Sistema de Backup Avançado Web...
echo.

cd /d %~dp0

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado!
    echo Por favor, instale Python 3.8 ou superior.
    pause
    exit /b 1
)

REM Verificar se Flask está instalado
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependências...
    pip install -r web/requirements.txt
    if errorlevel 1 (
        echo ERRO: Falha ao instalar dependências!
        pause
        exit /b 1
    )
)

REM Iniciar servidor
echo.
echo Servidor iniciando em http://localhost:5000
echo Pressione Ctrl+C para parar o servidor
echo.
python app.py

pause

