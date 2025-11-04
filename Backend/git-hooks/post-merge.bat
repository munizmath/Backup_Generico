@echo off
REM post-merge.bat - Hook Git para backup automático após merge/rebase

setlocal enabledelayedexpansion

echo 🔧 Git Hook - Post-Merge Backup
echo ================================
echo.

REM Obter diretório do repositório Git
for /f "delims=" %%i in ('git rev-parse --show-toplevel 2^>nul') do (
    set REPO_DIR=%%i
)

if not defined REPO_DIR (
    echo ❌ Não é um repositório Git válido
    exit /b 1
)

echo 📁 Repositório: %REPO_DIR%
echo.

REM Verificar se é um merge ou rebase
set OPERATION=unknown
if exist "%REPO_DIR%\.git\MERGE_HEAD" set OPERATION=merge
if exist "%REPO_DIR%\.git\rebase-merge" set OPERATION=rebase

echo 🔄 Operação detectada: %OPERATION%
echo.

REM Configurar diretórios
set BACKUP_DIR=E:\Backup\GitHooks
set PROJECT_NAME=%REPO_DIR:~-20%
set TIMESTAMP=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

REM Criar diretório de backup se não existir
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%" 2>nul

echo 📦 Criando backup post-%OPERATION%...
echo 🕐 Timestamp: %TIMESTAMP%
echo.

REM Criar backup do estado após merge/rebase
set BACKUP_NAME=%PROJECT_NAME%_post%OPERATION%_%TIMESTAMP%

REM Usar snapshot consistente se disponível
if exist "%~dp0..\snapshot-consistent.bat" (
    call "%~dp0..\snapshot-consistent.bat" "%REPO_DIR%" "%BACKUP_DIR%" "%BACKUP_NAME%" "dev-secure"
) else (
    call "%~dp0..\backup-generic-template.bat" "%REPO_DIR%" "%BACKUP_DIR%" "%BACKUP_NAME%"
)

if %errorlevel% neq 0 (
    echo ❌ Erro no backup post-%OPERATION%
    exit /b 0
)

echo ✅ Backup post-%OPERATION% criado: %BACKUP_NAME%
echo.

REM Capturar informações do merge/rebase
set MERGE_COMMIT=
if "%OPERATION%"=="merge" (
    for /f "delims=" %%i in ('git rev-parse MERGE_HEAD 2^>nul') do (
        set MERGE_COMMIT=%%i
    )
)

set BRANCH=
for /f "delims=" %%i in ('git branch --show-current 2^>nul') do (
    set BRANCH=%%i
)

REM Salvar informações do merge/rebase no backup
(
echo Git Post-%OPERATION% Backup - %date% %time%
echo.
echo Repositório: %REPO_DIR%
echo Branch: %BRANCH%
echo Operação: %OPERATION%
echo Backup: %BACKUP_NAME%
if defined MERGE_COMMIT (
    echo Merge Commit: %MERGE_COMMIT%
)
echo.
echo Commits recentes:
git log --oneline -10 2^>nul
echo.
echo Arquivos modificados recentemente:
git diff HEAD~1 --name-only 2^>nul
echo.
echo Status do repositório:
git status --porcelain 2^>nul
) > "%BACKUP_DIR%\%BACKUP_NAME%_git_info.txt"

echo ✅ Informações do %OPERATION% salvas
echo.

REM Limpar backups post-merge/rebase antigos (manter apenas os últimos 5)
set COUNT=0
for /f "delims=" %%i in ('dir "%BACKUP_DIR%\*_post*.zip" /b /o-d 2^>nul') do (
    set /a COUNT+=1
    if !COUNT! gtr 5 (
        echo 🗑️  Removendo backup post-operacao antigo: %%i
        del "%BACKUP_DIR%\%%i" 2>nul
        del "%BACKUP_DIR%\%%~ni_git_info.txt" 2>nul
    )
)

echo ✅ Hook post-%OPERATION% concluído
echo.
exit /b 0
