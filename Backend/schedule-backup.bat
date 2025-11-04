@echo off
REM schedule-backup.bat - Agendar backups automáticos
REM Uso: schedule-backup.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [FREQUENCY] [TIME]

echo ⏰ Configurando agendamento de backups...

REM Verificar parâmetros
if "%~1"=="" (
    echo ❌ Erro: Diretório do projeto não especificado
    echo Uso: schedule-backup.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [FREQUENCY] [TIME]
    echo Exemplo: schedule-backup.bat "C:\MeuProjeto" "C:\Backups" "MeuProjeto" "daily" "02:00"
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ❌ Erro: Diretório de backup não especificado
    echo Uso: schedule-backup.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [FREQUENCY] [TIME]
    pause
    exit /b 1
)

if "%~3"=="" (
    echo ❌ Erro: Nome do projeto não especificado
    echo Uso: schedule-backup.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [FREQUENCY] [TIME]
    pause
    exit /b 1
)

if "%~4"=="" (
    echo ❌ Erro: Frequência não especificada
    echo Uso: schedule-backup.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [FREQUENCY] [TIME]
    echo Frequências: daily, weekly, monthly
    pause
    exit /b 1
)

if "%~5"=="" (
    echo ❌ Erro: Horário não especificado
    echo Uso: schedule-backup.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [FREQUENCY] [TIME]
    echo Exemplo: schedule-backup.bat "C:\MeuProjeto" "C:\Backups" "MeuProjeto" "daily" "02:00"
    pause
    exit /b 1
)

set PROJECT_DIR=%~1
set BACKUP_DIR=%~2
set PROJECT_NAME=%~3
set FREQUENCY=%~4
set TIME=%~5

echo 📁 Projeto: %PROJECT_DIR%
echo 📁 Backup: %BACKUP_DIR%
echo 📦 Nome: %PROJECT_NAME%
echo ⏰ Frequência: %FREQUENCY%
echo 🕐 Horário: %TIME%

REM Verificar se o diretório do projeto existe
if not exist "%PROJECT_DIR%" (
    echo ❌ Erro: Diretório do projeto não encontrado: %PROJECT_DIR%
    pause
    exit /b 1
)

REM Criar diretório de backup se não existir
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Criar script de backup agendado
echo 📝 Criando script de backup agendado...
set SCHEDULE_SCRIPT=%BACKUP_DIR%\scheduled_backup_%PROJECT_NAME%.bat

(
echo @echo off
echo REM Script de backup agendado para %PROJECT_NAME%
echo REM Criado em: %date% %time%
echo.
echo echo ⏰ Executando backup agendado de %PROJECT_NAME%...
echo.
echo REM Executar backup completo
echo call "%~dp0backup-generic-template.bat" "%PROJECT_DIR%" "%BACKUP_DIR%" "%PROJECT_NAME%"
echo.
echo REM Log do agendamento
echo echo [%date% %time%] Backup agendado executado para %PROJECT_NAME% >> "%BACKUP_DIR%\schedule_log.txt"
) > "%SCHEDULE_SCRIPT%"

REM Criar tarefa agendada usando schtasks
echo 🔧 Configurando tarefa agendada...

REM Determinar frequência para schtasks
if "%FREQUENCY%"=="daily" (
    set SCHEDULE_FREQ=DAILY
) else if "%FREQUENCY%"=="weekly" (
    set SCHEDULE_FREQ=WEEKLY
) else if "%FREQUENCY%"=="monthly" (
    set SCHEDULE_FREQ=MONTHLY
) else (
    echo ❌ Erro: Frequência inválida. Use: daily, weekly, monthly
    pause
    exit /b 1
)

REM Criar tarefa agendada
schtasks /create /tn "Backup_%PROJECT_NAME%" /tr "%SCHEDULE_SCRIPT%" /sc %SCHEDULE_FREQ% /st %TIME% /f

if %errorlevel% equ 0 (
    echo ✅ Tarefa agendada criada com sucesso!
    echo.
    echo 📋 Detalhes da tarefa:
    echo   Nome: Backup_%PROJECT_NAME%
    echo   Frequência: %FREQUENCY%
    echo   Horário: %TIME%
    echo   Script: %SCHEDULE_SCRIPT%
    echo.
    echo 🔧 Para gerenciar a tarefa:
    echo   - Ver tarefas: schtasks /query /tn "Backup_%PROJECT_NAME%"
    echo   - Executar agora: schtasks /run /tn "Backup_%PROJECT_NAME%"
    echo   - Remover: schtasks /delete /tn "Backup_%PROJECT_NAME%" /f
    echo.
    echo 📝 Logs serão salvos em: %BACKUP_DIR%\schedule_log.txt
) else (
    echo ❌ Erro: Falha ao criar tarefa agendada
    echo.
    echo 🔧 Possíveis soluções:
    echo   1. Execute como administrador
    echo   2. Verifique se o Task Scheduler está funcionando
    echo   3. Verifique se o horário está no formato correto (HH:MM)
    pause
    exit /b 1
)

echo 🎉 Agendamento configurado com sucesso!
echo.
echo 📋 Próximos passos:
echo   1. Verifique se a tarefa foi criada no Task Scheduler
echo   2. Teste executando a tarefa manualmente
echo   3. Monitore os logs em: %BACKUP_DIR%\schedule_log.txt
echo.

pause

