@echo off
REM pre-commit.bat - Hook Git para backup automático antes do commit

setlocal enabledelayedexpansion

echo 🔧 Git Hook - Pre-Commit Backup
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

REM Configurar diretórios
set BACKUP_DIR=E:\Backup\GitHooks
set PROJECT_NAME=%REPO_DIR:~-20%
set TIMESTAMP=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

REM Criar diretório de backup se não existir
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%" 2>nul

echo 📦 Criando backup pre-commit...
echo 🕐 Timestamp: %TIMESTAMP%
echo.

REM Criar backup do estado atual (incluindo arquivos untracked)
set BACKUP_NAME=%PROJECT_NAME%_precommit_%TIMESTAMP%

REM Usar snapshot consistente se disponível
if exist "%~dp0..\snapshot-consistent.bat" (
    call "%~dp0..\snapshot-consistent.bat" "%REPO_DIR%" "%BACKUP_DIR%" "%BACKUP_NAME%" "dev-fast"
) else (
    call "%~dp0..\backup-generic-template.bat" "%REPO_DIR%" "%BACKUP_DIR%" "%BACKUP_NAME%"
)

if %errorlevel% neq 0 (
    echo ❌ Erro no backup pre-commit
    echo ⚠️  Commit pode continuar, mas backup falhou
    exit /b 0
)

echo ✅ Backup pre-commit criado: %BACKUP_NAME%
echo.

REM Capturar informações do commit
set COMMIT_MSG=
for /f "delims=" %%i in ('git log -1 --format=%%s 2^>nul') do (
    set COMMIT_MSG=%%i
)

set BRANCH=
for /f "delims=" %%i in ('git branch --show-current 2^>nul') do (
    set BRANCH=%%i
)

REM Salvar informações do commit no backup
(
echo Git Pre-Commit Backup - %date% %time%
echo.
echo Repositório: %REPO_DIR%
echo Branch: %BRANCH%
echo Commit Message: %COMMIT_MSG%
echo Backup: %BACKUP_NAME%
echo.
echo Arquivos no commit:
git diff --cached --name-only 2^>nul
echo.
echo Arquivos modificados:
git diff --name-only 2^>nul
echo.
echo Arquivos untracked:
git ls-files --others --exclude-standard 2^>nul
) > "%BACKUP_DIR%\%BACKUP_NAME%_git_info.txt"

echo ✅ Informações do Git salvas
echo.

REM Limpar backups pre-commit antigos (manter apenas os últimos 5)
set COUNT=0
for /f "delims=" %%i in ('dir "%BACKUP_DIR%\*_precommit_*.zip" /b /o-d 2^>nul') do (
    set /a COUNT+=1
    if !COUNT! gtr 5 (
        echo 🗑️  Removendo backup pre-commit antigo: %%i
        del "%BACKUP_DIR%\%%i" 2>nul
        del "%BACKUP_DIR%\%%~ni_git_info.txt" 2>nul
    )
)

echo ✅ Hook pre-commit concluído
echo.
exit /b 0
