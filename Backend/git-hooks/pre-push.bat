@echo off
REM pre-push.bat - Hook Git para backup automático antes do push

setlocal enabledelayedexpansion

echo 🔧 Git Hook - Pre-Push Backup
echo ==============================
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

REM Configurar diretórios
set BACKUP_DIR=E:\Backup\GitHooks
set PROJECT_NAME=%REPO_DIR:~-20%
set TIMESTAMP=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

REM Criar diretório de backup se não existir
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%" 2>nul

echo 📦 Criando backup pre-push...
echo 🕐 Timestamp: %TIMESTAMP%
echo.

REM Obter informações do push
set REMOTE=
set BRANCH=
for /f "tokens=1,2" %%a in ('git rev-parse --abbrev-ref --symbolic-full-name @{u} 2^>nul') do (
    set REMOTE=%%a
    set BRANCH=%%b
)

if not defined REMOTE (
    echo ⚠️  Nenhum remote configurado, usando backup local
    set REMOTE=local
    set BRANCH=main
)

echo 🌐 Remote: %REMOTE%
echo 🌿 Branch: %BRANCH%
echo.

REM Criar backup do estado atual
set BACKUP_NAME=%PROJECT_NAME%_prepush_%TIMESTAMP%

REM Usar snapshot consistente se disponível
if exist "%~dp0..\snapshot-consistent.bat" (
    call "%~dp0..\snapshot-consistent.bat" "%REPO_DIR%" "%BACKUP_DIR%" "%BACKUP_NAME%" "dev-secure"
) else (
    call "%~dp0..\backup-generic-template.bat" "%REPO_DIR%" "%BACKUP_DIR%" "%BACKUP_NAME%"
)

if %errorlevel% neq 0 (
    echo ❌ Erro no backup pre-push
    echo ⚠️  Push pode continuar, mas backup falhou
    exit /b 0
)

echo ✅ Backup pre-push criado: %BACKUP_NAME%
echo.

REM Capturar informações do push
set COMMITS_TO_PUSH=
for /f "delims=" %%i in ('git log %REMOTE%/%BRANCH%..HEAD --oneline 2^>nul') do (
    set COMMITS_TO_PUSH=!COMMITS_TO_PUSH!%%i
)

REM Salvar informações do push no backup
(
echo Git Pre-Push Backup - %date% %time%
echo.
echo Repositório: %REPO_DIR%
echo Remote: %REMOTE%
echo Branch: %BRANCH%
echo Backup: %BACKUP_NAME%
echo.
echo Commits sendo enviados:
git log %REMOTE%/%BRANCH%..HEAD --oneline 2^>nul
echo.
echo Arquivos modificados nos commits:
git diff %REMOTE%/%BRANCH%..HEAD --name-only 2^>nul
echo.
echo Estatísticas do push:
git diff --stat %REMOTE%/%BRANCH%..HEAD 2^>nul
) > "%BACKUP_DIR%\%BACKUP_NAME%_git_info.txt"

echo ✅ Informações do push salvas
echo.

REM Limpar backups pre-push antigos (manter apenas os últimos 3)
set COUNT=0
for /f "delims=" %%i in ('dir "%BACKUP_DIR%\*_prepush_*.zip" /b /o-d 2^>nul') do (
    set /a COUNT+=1
    if !COUNT! gtr 3 (
        echo 🗑️  Removendo backup pre-push antigo: %%i
        del "%BACKUP_DIR%\%%i" 2>nul
        del "%BACKUP_DIR%\%%~ni_git_info.txt" 2>nul
    )
)

echo ✅ Hook pre-push concluído
echo.
exit /b 0
