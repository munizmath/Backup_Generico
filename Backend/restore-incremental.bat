@echo off
REM restore-incremental.bat - Restaurar backup incremental
REM Uso: restore-incremental.bat [BACKUP_NAME] [PROJECT_DIR] [BACKUP_DIR]

echo 🔄 Iniciando restauração incremental...

REM Verificar parâmetros
if "%~1"=="" (
    echo ❌ Erro: Nome do backup não especificado
    echo Uso: restore-incremental.bat [BACKUP_NAME] [PROJECT_DIR] [BACKUP_DIR]
    echo Exemplo: restore-incremental.bat "MeuProjeto_incremental_20241014_130702" "C:\MeuProjeto" "C:\Backups"
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ❌ Erro: Diretório do projeto não especificado
    echo Uso: restore-incremental.bat [BACKUP_NAME] [PROJECT_DIR] [BACKUP_DIR]
    pause
    exit /b 1
)

if "%~3"=="" (
    echo ❌ Erro: Diretório de backup não especificado
    echo Uso: restore-incremental.bat [BACKUP_NAME] [PROJECT_DIR] [BACKUP_DIR]
    pause
    exit /b 1
)

set BACKUP_NAME=%~1
set PROJECT_DIR=%~2
set BACKUP_DIR=%~3
set BACKUP_FILE=%BACKUP_DIR%\%BACKUP_NAME%.zip

echo 📦 Backup: %BACKUP_NAME%
echo 📁 Projeto: %PROJECT_DIR%
echo 📁 Backup: %BACKUP_DIR%

REM Verificar se o arquivo de backup existe
if not exist "%BACKUP_FILE%" (
    echo ❌ Erro: Arquivo de backup não encontrado: %BACKUP_FILE%
    echo.
    echo 📋 Backups incrementais disponíveis:
    dir "%BACKUP_DIR%\*_incremental_*.zip" /b 2>nul
    pause
    exit /b 1
)

REM Fazer backup do estado atual antes de restaurar
echo 🔄 Fazendo backup do estado atual...
set CURRENT_BACKUP=%PROJECT_NAME%_backup_antes_restore_%DATE%
call backup-generic-template.bat "%PROJECT_DIR%" "%BACKUP_DIR%" "%PROJECT_NAME%_antes_restore"

REM Criar diretório temporário para extração
set TEMP_RESTORE=%BACKUP_DIR%\temp_restore_%BACKUP_NAME%
if exist "%TEMP_RESTORE%" rmdir /s /q "%TEMP_RESTORE%"
mkdir "%TEMP_RESTORE%"

REM Extrair backup
echo 📦 Extraindo backup incremental...
powershell -Command "& {Expand-Archive -Path '%BACKUP_FILE%' -DestinationPath '%TEMP_RESTORE%' -Force}"

if %errorlevel% neq 0 (
    echo ❌ Erro: Falha ao extrair o backup
    rmdir /s /q "%TEMP_RESTORE%"
    pause
    exit /b 1
)

REM Criar diretório do projeto se não existir
if not exist "%PROJECT_DIR%" mkdir "%PROJECT_DIR%"

REM Restaurar arquivos (sobrescrever arquivos existentes)
echo 📂 Restaurando arquivos modificados...
xcopy "%TEMP_RESTORE%\*" "%PROJECT_DIR%\" /E /I /Q /Y

REM Limpar diretório temporário
rmdir /s /q "%TEMP_RESTORE%"

REM Verificar se a restauração foi bem-sucedida
if exist "%PROJECT_DIR%" (
    echo ✅ Restauração incremental concluída com sucesso!
    echo 📁 Projeto restaurado em: %PROJECT_DIR%
    echo.
    echo 📋 Arquivos restaurados:
    echo - Apenas arquivos modificados foram restaurados
    echo - Arquivos existentes foram sobrescritos
    echo - Backup do estado anterior salvo como: %PROJECT_NAME%_backup_antes_restore_*
    echo.
    echo ⚠️  IMPORTANTE: Este é um backup incremental
    echo    - Apenas arquivos modificados foram restaurados
    echo    - Para restauração completa, use restore-generic-template.bat
) else (
    echo ❌ Erro: Falha na restauração
    pause
    exit /b 1
)

echo 🎉 Restauração incremental concluída com sucesso!
echo.
echo 📋 Próximos passos:
echo   1. Verifique se os arquivos foram restaurados corretamente
echo   2. Teste o projeto
echo   3. Se necessário, restaure o backup anterior
echo.

pause
