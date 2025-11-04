@echo off
REM restore-encrypted.bat - Restaurar backup criptografado
REM Uso: restore-encrypted.bat [BACKUP_NAME] [PROJECT_DIR] [BACKUP_DIR] [PASSWORD]

echo 🔄 Iniciando restauração criptografada...

REM Verificar parâmetros
if "%~1"=="" (
    echo ❌ Erro: Nome do backup não especificado
    echo Uso: restore-encrypted.bat [BACKUP_NAME] [PROJECT_DIR] [BACKUP_DIR] [PASSWORD]
    echo Exemplo: restore-encrypted.bat "MeuProjeto_encrypted_20241014_130702" "C:\MeuProjeto" "C:\Backups" "minhasenha123"
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ❌ Erro: Diretório do projeto não especificado
    echo Uso: restore-encrypted.bat [BACKUP_NAME] [PROJECT_DIR] [BACKUP_DIR] [PASSWORD]
    pause
    exit /b 1
)

if "%~3"=="" (
    echo ❌ Erro: Diretório de backup não especificado
    echo Uso: restore-encrypted.bat [BACKUP_NAME] [PROJECT_DIR] [BACKUP_DIR] [PASSWORD]
    pause
    exit /b 1
)

if "%~4"=="" (
    echo ❌ Erro: Senha não especificada
    echo Uso: restore-encrypted.bat [BACKUP_NAME] [PROJECT_DIR] [BACKUP_DIR] [PASSWORD]
    echo Exemplo: restore-encrypted.bat "MeuProjeto_encrypted_20241014_130702" "C:\MeuProjeto" "C:\Backups" "minhasenha123"
    pause
    exit /b 1
)

set BACKUP_NAME=%~1
set PROJECT_DIR=%~2
set BACKUP_DIR=%~3
set PASSWORD=%~4
set BACKUP_FILE=%BACKUP_DIR%\%BACKUP_NAME%.enc

echo 📦 Backup: %BACKUP_NAME%
echo 📁 Projeto: %PROJECT_DIR%
echo 📁 Backup: %BACKUP_DIR%
echo 🔐 Criptografia: AES-256

REM Verificar se o arquivo de backup existe
if not exist "%BACKUP_FILE%" (
    echo ❌ Erro: Arquivo de backup não encontrado: %BACKUP_FILE%
    echo.
    echo 📋 Backups criptografados disponíveis:
    dir "%BACKUP_DIR%\*_encrypted_*.enc" /b 2>nul
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

REM Descriptografar usando sistema Python seguro
echo 🔓 Descriptografando backup...
python encryption_system.py decrypt "%BACKUP_FILE%" "%TEMP_RESTORE%\temp_backup.zip" "%PASSWORD%"

if %errorlevel% neq 0 (
    echo ❌ Erro: Falha ao descriptografar o backup
    echo.
    echo 🔧 Possíveis causas:
    echo   1. Senha incorreta
    echo   2. Arquivo corrompido
    echo   3. Problema de permissão
    rmdir /s /q "%TEMP_RESTORE%"
    pause
    exit /b 1
)

REM Extrair backup descriptografado
echo 📦 Extraindo backup descriptografado...
powershell -Command "& {Expand-Archive -Path '%TEMP_RESTORE%\temp_backup.zip' -DestinationPath '%TEMP_RESTORE%' -Force}"

if %errorlevel% neq 0 (
    echo ❌ Erro: Falha ao extrair o backup
    rmdir /s /q "%TEMP_RESTORE%"
    pause
    exit /b 1
)

REM Criar diretório do projeto se não existir
if not exist "%PROJECT_DIR%" mkdir "%PROJECT_DIR%"

REM Restaurar arquivos
echo 📂 Restaurando arquivos...
xcopy "%TEMP_RESTORE%\*" "%PROJECT_DIR%\" /E /I /Q /Y

REM Limpar diretório temporário
rmdir /s /q "%TEMP_RESTORE%"

REM Verificar se a restauração foi bem-sucedida
if exist "%PROJECT_DIR%" (
    echo ✅ Restauração criptografada concluída com sucesso!
    echo 📁 Projeto restaurado em: %PROJECT_DIR%
    echo.
    echo 📋 Arquivos restaurados:
    echo - Backup criptografado foi descriptografado
    echo - Arquivos foram restaurados com sucesso
    echo - Backup do estado anterior salvo como: %PROJECT_NAME%_backup_antes_restore_*
    echo.
    echo 🔐 Segurança:
    echo - Arquivos temporários foram removidos
    echo - Senha não foi armazenada em arquivos
) else (
    echo ❌ Erro: Falha na restauração
    pause
    exit /b 1
)

echo 🎉 Restauração criptografada concluída com sucesso!
echo.
echo 📋 Próximos passos:
echo   1. Verifique se os arquivos foram restaurados corretamente
echo   2. Teste o projeto
echo   3. Se necessário, restaure o backup anterior
echo   4. Mantenha a senha em local seguro
echo.

pause

