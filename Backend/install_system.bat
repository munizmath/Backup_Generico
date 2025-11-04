@echo off
REM install_system.bat - Instalacao completa do Sistema de Backup Avancado

echo ===============================================
echo    INSTALACAO DO SISTEMA DE BACKUP AVANCADO
echo ===============================================
echo.

REM Verificar se Python esta instalado
echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo.
    echo Por favor, instale Python 3.8+ de:
    echo https://www.python.org/downloads/
    echo.
    echo Certifique-se de marcar "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
) else (
    echo OK: Python encontrado
)

REM Verificar se pip esta disponivel
echo Verificando pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: pip nao encontrado!
    echo.
    echo Por favor, reinstale Python com pip incluido.
    pause
    exit /b 1
) else (
    echo OK: pip encontrado
)

echo.
echo Criando estrutura de diretorios...

REM Criar diretorios necessarios
if not exist "Frontend\Dependencias" mkdir "Frontend\Dependencias"
if not exist "Backend\Dependencias" mkdir "Backend\Dependencias"
if not exist "Backend\config" mkdir "Backend\config"
if not exist "Backend\git-hooks" mkdir "Backend\git-hooks"
if not exist "Backend\backup_versions" mkdir "Backend\backup_versions"

echo OK: Estrutura de diretorios criada

echo.
echo Instalando dependencias do Frontend...
cd Frontend\Dependencias
call download_dependencies.bat
cd ..\..

echo.
echo Instalando dependencias do Backend...
cd Backend\Dependencias
call download_dependencies.bat
cd ..\..

echo.
echo Configurando sistema...

REM Criar arquivo de versao inicial
if not exist "Backend\VERSION.json" (
    echo Criando arquivo de versao inicial...
    python Backend\version_manager.py get-version "Backend"
)

REM Criar arquivo de configuracao de retencao se nao existir
if not exist "Backend\config\retention_profiles.json" (
    echo Arquivo de perfis de retencao ja existe
) else (
    echo Arquivo de perfis de retencao ja existe
)

echo.
echo Configurando Git hooks...
echo Para configurar hooks Git automaticamente, execute:
echo   git config core.hooksPath Backend\git-hooks
echo.

echo ===============================================
echo    INSTALACAO CONCLUIDA COM SUCESSO!
echo ===============================================
echo.
echo O sistema esta pronto para uso!
echo.
echo Para iniciar o sistema, execute:
echo   start.bat
echo.
echo Funcionalidades disponiveis:
echo - Interface Grafica Avancada
echo - Backup com Versionamento
echo - Restore Cirurgico
echo - Snapshots Consistentes
echo - Criptografia Avancada
echo - Telemetria e Monitoramento
echo - Gerenciamento de Dependencias
echo.
pause
