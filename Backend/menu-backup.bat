@echo off
REM menu-backup.bat - Menu principal do sistema de backup genérico

:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🔒 SISTEMA DE BACKUP GENÉRICO              ║
echo ║                                                              ║
echo ║  Sistema de backup genérico para qualquer projeto            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 📋 Escolha uma opção:
echo.
echo 1. 🔧 Configurar sistema
echo 2. 📦 Fazer backup completo
echo 3. ⚡ Fazer backup incremental
echo 4. 🔗 Fazer backup Git
echo 5. 🔐 Fazer backup criptografado
echo 6. 🔄 Restaurar backup
echo 7. ⏰ Agendar backups
echo 8. 🎨 Interface Gráfica (Frontend)
echo 9. 📊 Dashboard (Frontend)
echo 10. 🧪 Testar sistema
echo 11. 📋 Listar backups
echo 12. 🧹 Limpar backups antigos
echo 13. 📖 Ver documentação
echo 14. ❌ Sair
echo.
set /p choice="Digite sua escolha (1-14): "

if "%choice%"=="1" goto config
if "%choice%"=="2" goto backup
if "%choice%"=="3" goto incremental
if "%choice%"=="4" goto git
if "%choice%"=="5" goto encrypted
if "%choice%"=="6" goto restore
if "%choice%"=="7" goto schedule
if "%choice%"=="8" goto gui
if "%choice%"=="9" goto dashboard
if "%choice%"=="10" goto test
if "%choice%"=="11" goto list
if "%choice%"=="12" goto clean
if "%choice%"=="13" goto docs
if "%choice%"=="14" goto exit
goto invalid

:config
cls
echo 🔧 Configurando sistema de backup...
call setup-backup.bat
pause
goto menu

:backup
cls
echo 📦 Fazer backup de um projeto
echo.
set /p project_dir="Digite o caminho do projeto: "
set /p backup_dir="Digite o diretório de backup (ou pressione Enter para usar padrão): "
set /p project_name="Digite o nome do projeto: "

if "%backup_dir%"=="" set backup_dir=%~dp0backups

echo.
echo Executando backup...
call backup-generic.bat "%project_dir%" "%backup_dir%" "%project_name%"
pause
goto menu

:restore
cls
echo 🔄 Restaurar backup
echo.
set /p backup_name="Digite o nome do backup (sem .zip): "
set /p project_dir="Digite o diretório do projeto: "
set /p backup_dir="Digite o diretório de backup (ou pressione Enter para usar padrão): "

if "%backup_dir%"=="" set backup_dir=%~dp0backups

echo.
echo Executando restauração...
call restore-generic-template.bat "%backup_name%" "%project_dir%" "%backup_dir%"
pause
goto menu

:schedule
cls
echo ⏰ Agendar backups automáticos
echo.
set /p project_dir="Digite o caminho do projeto: "
set /p backup_dir="Digite o diretório de backup (ou pressione Enter para usar padrão): "
set /p project_name="Digite o nome do projeto: "
set /p frequency="Digite a frequência (daily/weekly/monthly): "
set /p time="Digite o horário (HH:MM): "

if "%backup_dir%"=="" set backup_dir=%~dp0backups

echo.
echo Configurando agendamento...
call schedule-backup.bat "%project_dir%" "%backup_dir%" "%project_name%" "%frequency%" "%time%"
pause
goto menu

:gui
cls
echo 🎨 Iniciando Interface Gráfica...
echo.
echo 📋 Navegando para pasta Frontend...
cd ..\Frontend
if %errorlevel% neq 0 (
    echo ❌ Erro: Não foi possível navegar para pasta Frontend
    pause
    goto menu
)

echo 📋 Verificando dependências...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Instale Python primeiro.
    pause
    goto menu
)

echo ✅ Python encontrado
echo 🚀 Iniciando interface gráfica...
start_gui.bat
pause
goto menu

:dashboard
cls
echo 📊 Iniciando Dashboard de Monitoramento...
echo.
echo 📋 Navegando para pasta Frontend...
cd ..\Frontend
if %errorlevel% neq 0 (
    echo ❌ Erro: Não foi possível navegar para pasta Frontend
    pause
    goto menu
)

echo 📋 Verificando dependências...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Instale Python primeiro.
    pause
    goto menu
)

echo ✅ Python encontrado
echo 🚀 Iniciando dashboard...
start_dashboard.bat
pause
goto menu

:test
cls
echo 🧪 Testando sistema de backup...
call test-backup.bat
pause
goto menu

:list
cls
echo 📊 Listando backups disponíveis...
echo.
if exist "%~dp0backups\*_backup_*.zip" (
    echo Backups encontrados:
    echo.
    dir "%~dp0backups\*_backup_*.zip" /b
    echo.
    echo Total de arquivos:
    dir "%~dp0backups\*_backup_*.zip" /b | find /c /v ""
) else (
    echo Nenhum backup encontrado.
)
echo.
pause
goto menu

:clean
cls
echo 🧹 Limpando backups antigos...
echo.
set /p max_backups="Digite o número de backups a manter (padrão: 5): "
if "%max_backups%"=="" set max_backups=5

echo Mantendo os últimos %max_backups% backups...
for /f "skip=%max_backups% delims=" %%i in ('dir /b /o-d "%~dp0backups\*_backup_*.zip" 2^>nul') do (
    echo Removendo: %%i
    del "%~dp0backups\%%i" 2>nul
)
echo Limpeza concluída!
pause
goto menu

:docs
cls
echo 📖 Abrindo documentação...
if exist "%~dp0README.md" (
    start notepad "%~dp0README.md"
) else (
    echo Documentação não encontrada. Execute setup-backup.bat primeiro.
)
pause
goto menu

:invalid
echo ❌ Opção inválida. Tente novamente.
pause
goto menu

:exit
echo 👋 Obrigado por usar o Sistema de Backup Genérico!
exit /b 0
