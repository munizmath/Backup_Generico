@echo off
REM ===============================================
REM    SISTEMA DE BACKUP AVANCADO - UNIFICADO
REM ===============================================

chcp 65001 >nul
setlocal enabledelayedexpansion

REM Verificar dependencias automaticamente
echo Verificando dependencias do sistema...
call Backend\check_dependencies.bat
if %errorlevel% neq 0 (
    echo ERRO: Falha na verificacao de dependencias!
    echo.
    echo Possiveis solucoes:
    echo   1. Instale Python 3.8+ de https://www.python.org/downloads/
    echo   2. Marque "Add Python to PATH" durante a instalacao
    echo   3. Execute como administrador
    echo   4. Verifique se as dependencias estao instaladas
    pause
    exit /b 1
)

:start
cls
echo ===============================================
echo    SISTEMA DE BACKUP AVANCADO v2.0
echo ===============================================
echo.
echo Escolha uma opcao:
echo.
echo BACKUP E RESTAURACAO:
echo   1.  Interface Grafica Avancada (Recomendado)
echo   2.  Interface Grafica Basica
echo   3.  Dashboard de Monitoramento
echo   4.  Menu de Linha de Comando
echo.
echo CONFIGURACAO E MANUTENCAO:
echo   5.  Configurar Sistema
echo   6.  Criar Executaveis
echo   7.  Testar Sistema
echo   8.  Restore Cirurgico
echo   9.  Snapshot Consistente
echo.
echo SEGURANCA E CRIPTOGRAFIA:
echo   10. Gerenciar Criptografia
echo   11. Telemetria e Monitoramento
echo   12. Gerenciar Versoes
echo.
echo INSTALACAO E DEPENDENCIAS:
echo   13. Instalar Dependencias
echo   14. Instalacao Completa do Sistema
echo   15. Corrigir PyInstaller
echo.
echo   16. Sair
echo.
set /p choice="Digite sua escolha (1-16): "

REM Validar entrada
if "%choice%"=="" (
    echo ERRO: Nenhuma opcao selecionada!
    pause
    goto start
)

REM Verificar se e um numero valido
if "%choice%"=="1" goto gui_advanced
if "%choice%"=="2" goto gui_basic
if "%choice%"=="3" goto dashboard
if "%choice%"=="4" goto menu
if "%choice%"=="5" goto config
if "%choice%"=="6" goto build
if "%choice%"=="7" goto test
if "%choice%"=="8" goto restore_surgical
if "%choice%"=="9" goto snapshot_consistent
if "%choice%"=="10" goto encryption
if "%choice%"=="11" goto telemetry
if "%choice%"=="12" goto version_management
if "%choice%"=="13" goto install_dependencies
if "%choice%"=="14" goto full_install
if "%choice%"=="15" goto fix
if "%choice%"=="16" goto exit

REM Se chegou aqui, opcao invalida
echo ERRO: Opcao invalida! Digite um numero entre 1 e 16.
pause
goto start

REM ===============================================
REM    INTERFACES GRAFICAS
REM ===============================================

:gui_advanced
echo Iniciando Interface Grafica Avancada...
cd /d "%~dp0Frontend"
if exist "gui_backup_modern.py" (
    python gui_backup_modern.py
) else if exist "gui_backup_advanced.py" (
    python gui_backup_advanced.py
) else (
    echo ERRO: Arquivo de interface grafica nao encontrado!
    echo Verifique se voce esta no diretorio correto.
)
cd /d "%~dp0"
goto end

:gui_basic
echo Iniciando Interface Grafica Basica...
cd /d "%~dp0Frontend"
if exist "gui_backup_unified.py" (
    python gui_backup_unified.py
) else (
    echo ERRO: Arquivo gui_backup_unified.py nao encontrado!
    echo Verifique se voce esta no diretorio correto.
)
cd /d "%~dp0"
goto end

:dashboard
echo Iniciando Dashboard de Monitoramento...
cd /d "%~dp0Frontend"
if exist "dashboard_backup.py" (
    python dashboard_backup.py
) else (
    echo ERRO: Arquivo dashboard_backup.py nao encontrado!
    echo Verifique se voce esta no diretorio correto.
)
cd /d "%~dp0"
goto end

:menu
echo Iniciando Menu de Linha de Comando...
cd /d "%~dp0Backend"
if exist "menu-backup.bat" (
    call menu-backup.bat
) else (
    echo ERRO: Arquivo menu-backup.bat nao encontrado!
    echo Verifique se voce esta no diretorio correto.
)
cd /d "%~dp0"
goto end

REM ===============================================
REM    CONFIGURACAO E MANUTENCAO
REM ===============================================

:config
echo Configurando Sistema...
cd Backend
echo.
echo Configuracao do Sistema de Backup
echo =====================================
echo.
echo 1. Configurar diretorios de backup
echo 2. Configurar perfis de retencao
echo 3. Configurar criptografia
echo 4. Configurar telemetria
echo 5. Voltar ao menu principal
echo.
set /p config_choice="Digite sua escolha (1-5): "

if "%config_choice%"=="1" (
    set /p backup_dir="Digite o diretorio de backup (padrao: E:\Backup): "
    if "%backup_dir%"=="" set backup_dir=E:\Backup
    echo Backup directory: %backup_dir%
    echo Configuracao salva!
) else if "%config_choice%"=="2" (
    echo Editando perfis de retencao...
    if exist "config\retention_profiles.json" (
        notepad config\retention_profiles.json
    ) else (
        echo ERRO: Arquivo de configuracao nao encontrado!
    )
) else if "%config_choice%"=="3" (
    echo Inicializando sistema de criptografia...
    set /p password="Digite a senha mestra: "
    if exist "encryption_system.py" (
        python encryption_system.py init "config" "%password%"
    ) else (
        echo ERRO: Sistema de criptografia nao encontrado!
    )
) else if "%config_choice%"=="4" (
    echo Inicializando sistema de telemetria...
    if exist "telemetry_system.py" (
        python telemetry_system.py init "config"
    ) else (
        echo ERRO: Sistema de telemetria nao encontrado!
    )
) else if "%config_choice%"=="5" (
    cd ..
    goto start
) else (
    echo Opcao invalida
)
cd ..
goto end

:build
echo Criando Executaveis...
cd Backend
if exist "build_executables.bat" (
    call build_executables.bat
) else (
    echo ERRO: Arquivo build_executables.bat nao encontrado!
)
cd ..
goto end

:test
echo Testando Sistema...
cd Backend
if exist "test_all_scripts.bat" (
    call test_all_scripts.bat
) else (
    echo ERRO: Arquivo test_all_scripts.bat nao encontrado!
)
cd ..
goto end

:restore_surgical
echo Restore Cirurgico...
cd Backend
if exist "restore-surgical.bat" (
    call restore-surgical.bat
) else (
    echo ERRO: Arquivo restore-surgical.bat nao encontrado!
)
cd ..
goto end

:snapshot_consistent
echo Snapshot Consistente...
cd Backend
if exist "snapshot-consistent.bat" (
    set /p project_dir="Digite o diretorio do projeto: "
    set /p backup_dir="Digite o diretorio de backup: "
    set /p project_name="Digite o nome do projeto: "
    set /p profile="Digite o perfil (dev-fast/dev-secure/release/critical): "
    call snapshot-consistent.bat "%project_dir%" "%backup_dir%" "%project_name%" "%profile%"
) else (
    echo ERRO: Arquivo snapshot-consistent.bat nao encontrado!
)
cd ..
goto end

REM ===============================================
REM    SEGURANCA E CRIPTOGRAFIA
REM ===============================================

:encryption
echo Gerenciando Criptografia...
cd Backend
if exist "encryption_system.py" (
    echo.
    echo Sistema de Criptografia
    echo ==========================
    echo.
    echo 1. Inicializar Sistema de Criptografia
    echo 2. Criptografar Arquivo
    echo 3. Descriptografar Arquivo
    echo 4. Rotacionar Chaves
    echo 5. Estatisticas
    echo.
    set /p crypto_choice="Digite sua escolha (1-5): "

    if "%crypto_choice%"=="1" (
        set /p password="Digite a senha mestra: "
        python encryption_system.py init "config" "%password%"
    ) else if "%crypto_choice%"=="2" (
        set /p file_path="Digite o caminho do arquivo: "
        set /p output_path="Digite o caminho de saida: "
        set /p password="Digite a senha: "
        python encryption_system.py encrypt "%file_path%" "%output_path%" "%password%"
    ) else if "%crypto_choice%"=="3" (
        set /p encrypted_path="Digite o caminho do arquivo criptografado: "
        set /p output_path="Digite o caminho de saida: "
        set /p password="Digite a senha: "
        python encryption_system.py decrypt "%encrypted_path%" "%output_path%" "%password%"
    ) else if "%crypto_choice%"=="4" (
        set /p password="Digite a senha mestra: "
        python encryption_system.py rotate "config" "%password%"
    ) else if "%crypto_choice%"=="5" (
        python encryption_system.py stats "config"
    ) else (
        echo Opcao invalida
    )
) else (
    echo ERRO: Sistema de criptografia nao encontrado!
)
cd ..
goto end

:telemetry
echo Telemetria e Monitoramento...
cd Backend
if exist "telemetry_system.py" (
    echo.
    echo Sistema de Telemetria
    echo ========================
    echo.
    echo 1. Registrar Metricas de Backup
    echo 2. Registrar Metricas do Sistema
    echo 3. Mostrar Resumo
    echo 4. Listar Alertas
    echo 5. Limpar Dados Antigos
    echo.
    set /p telemetry_choice="Digite sua escolha (1-5): "

    if "%telemetry_choice%"=="1" (
        set /p project_name="Nome do projeto: "
        set /p backup_type="Tipo de backup: "
        set /p file_count="Numero de arquivos: "
        set /p total_size="Tamanho total: "
        set /p duration="Duracao: "
        set /p success="Sucesso (true/false): "
        python telemetry_system.py record-backup "config" "%project_name%" "%backup_type%" "%file_count%" "%total_size%" "%duration%" "%success%"
    ) else if "%telemetry_choice%"=="2" (
        python telemetry_system.py record-system "config"
    ) else if "%telemetry_choice%"=="3" (
        set /p hours="Horas (padrao 24): "
        if "%hours%"=="" set hours=24
        python telemetry_system.py summary "config" "%hours%"
    ) else if "%telemetry_choice%"=="4" (
        python telemetry_system.py alerts "config"
    ) else if "%telemetry_choice%"=="5" (
        python telemetry_system.py cleanup "config"
    ) else (
        echo Opcao invalida
    )
) else (
    echo ERRO: Sistema de telemetria nao encontrado!
)
cd ..
goto end

:version_management
echo Gerenciando Versoes...
cd Backend
if exist "version_manager.py" (
    echo.
    echo Gerenciamento de Versoes
    echo ===========================
    echo.
    echo 1. Listar Versoes de Backup
    echo 2. Mostrar Versao Atual
    echo 3. Adicionar Changelog
    echo 4. Criar Tag de Release
    echo 5. Gerar Relatorio de Backups
    echo.
    set /p version_choice="Digite sua escolha (1-5): "

    if "%version_choice%"=="1" (
        python version_manager.py list-versions "%~dp0.."
    ) else if "%version_choice%"=="2" (
        python version_manager.py get-version "%~dp0.."
    ) else if "%version_choice%"=="3" (
        set /p version="Digite a versao: "
        set /p changes="Digite as mudancas (separadas por virgula): "
        set /p change_type="Digite o tipo (major/minor/patch): "
        python version_manager.py add-changelog "%~dp0.." "%version%" "%changes%" "%change_type%"
    ) else if "%version_choice%"=="4" (
        set /p version="Digite a versao: "
        set /p message="Digite a mensagem (opcional): "
        python version_manager.py create-tag "%~dp0.." "%version%" "%message%"
    ) else if "%version_choice%"=="5" (
        python version_manager.py generate-report "%~dp0.."
    ) else (
        echo Opcao invalida
    )
) else (
    echo ERRO: Sistema de versionamento nao encontrado!
)
cd ..
goto end

REM ===============================================
REM    INSTALACAO E DEPENDENCIAS
REM ===============================================

:install_dependencies
echo Instalando Dependencias...
echo.
echo Gerenciamento de Dependencias
echo ================================
echo.
echo 1. Instalar Dependencias do Frontend
echo 2. Instalar Dependencias do Backend
echo 3. Instalar Todas as Dependencias
echo 4. Verificar Dependencias
echo.
set /p dep_choice="Digite sua escolha (1-4): "

if "%dep_choice%"=="1" (
    if exist "Frontend\Dependencias\download_dependencies.bat" (
        cd Frontend\Dependencias
        call download_dependencies.bat
        cd ..\..
    ) else (
        echo ERRO: Script de dependencias do Frontend nao encontrado!
    )
) else if "%dep_choice%"=="2" (
    if exist "Backend\Dependencias\download_dependencies.bat" (
        cd Backend\Dependencias
        call download_dependencies.bat
        cd ..\..
    ) else (
        echo ERRO: Script de dependencias do Backend nao encontrado!
    )
) else if "%dep_choice%"=="3" (
    echo Instalando dependencias do Frontend...
    if exist "Frontend\Dependencias\download_dependencies.bat" (
        cd Frontend\Dependencias
        call download_dependencies.bat
        cd ..\..
    )
    echo.
    echo Instalando dependencias do Backend...
    if exist "Backend\Dependencias\download_dependencies.bat" (
        cd Backend\Dependencias
        call download_dependencies.bat
        cd ..\..
    )
) else if "%dep_choice%"=="4" (
    call Backend\check_dependencies.bat
) else (
    echo Opcao invalida
)
goto end

:full_install
echo Instalacao Completa do Sistema...
cd Backend
if exist "install_system.bat" (
    call install_system.bat
) else (
    echo ERRO: Arquivo install_system.bat nao encontrado!
)
cd ..
goto end

:fix
echo Corrigindo PyInstaller...
cd Backend
if exist "fix_pyinstaller.bat" (
    call fix_pyinstaller.bat
) else (
    echo ERRO: Arquivo fix_pyinstaller.bat nao encontrado!
)
cd ..
goto end

REM ===============================================
REM    FINALIZACAO
REM ===============================================

:exit
echo.
echo ===============================================
echo    OBRIGADO POR USAR O SISTEMA DE BACKUP!
echo ===============================================
echo.
echo Para mais informacoes, consulte o README.md
echo GitHub: https://github.com/seu-usuario/sistema-backup
echo.
exit /b 0

:end
echo.
echo Operacao concluida!
echo.
echo Pressione qualquer tecla para voltar ao menu principal...
pause >nul
goto start