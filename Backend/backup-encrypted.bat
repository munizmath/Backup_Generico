@echo off
REM backup-encrypted.bat - Backup criptografado
REM Uso: backup-encrypted.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [PASSWORD]

echo 🔄 Iniciando backup criptografado...

REM Verificar parâmetros
if "%~1"=="" (
    echo ❌ Erro: Diretório do projeto não especificado
    echo Uso: backup-encrypted.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [PASSWORD]
    echo Exemplo: backup-encrypted.bat "C:\MeuProjeto" "C:\Backups" "MeuProjeto" "minhasenha123"
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ❌ Erro: Diretório de backup não especificado
    echo Uso: backup-encrypted.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [PASSWORD]
    pause
    exit /b 1
)

if "%~3"=="" (
    echo ❌ Erro: Nome do projeto não especificado
    echo Uso: backup-encrypted.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [PASSWORD]
    pause
    exit /b 1
)

if "%~4"=="" (
    echo ❌ Erro: Senha não especificada
    echo Uso: backup-encrypted.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [PASSWORD]
    echo Exemplo: backup-encrypted.bat "C:\MeuProjeto" "C:\Backups" "MeuProjeto" "minhasenha123"
    pause
    exit /b 1
)

set PROJECT_DIR=%~1
set BACKUP_DIR=%~2
set PROJECT_NAME=%~3
set PASSWORD=%~4
set DATE=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DATE=%DATE: =0%
set BACKUP_NAME=%PROJECT_NAME%_encrypted_%DATE%

echo 📁 Projeto: %PROJECT_DIR%
echo 📁 Backup: %BACKUP_DIR%
echo 📦 Nome: %BACKUP_NAME%
echo 🔐 Criptografia: AES-256

REM Verificar se o diretório do projeto existe
if not exist "%PROJECT_DIR%" (
    echo ❌ Erro: Diretório do projeto não encontrado: %PROJECT_DIR%
    pause
    exit /b 1
)

REM Criar diretório de backup se não existir
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Criar diretório temporário para o backup
set TEMP_BACKUP=%BACKUP_DIR%\temp_%BACKUP_NAME%
if exist "%TEMP_BACKUP%" rmdir /s /q "%TEMP_BACKUP%"
mkdir "%TEMP_BACKUP%"

REM Criar arquivo de exclusão genérico se não existir
if not exist "%BACKUP_DIR%\exclude_list.txt" (
    echo node_modules > "%BACKUP_DIR%\exclude_list.txt"
    echo build >> "%BACKUP_DIR%\exclude_list.txt"
    echo .git >> "%BACKUP_DIR%\exclude_list.txt"
    echo logs >> "%BACKUP_DIR%\exclude_list.txt"
    echo *.log >> "%BACKUP_DIR%\exclude_list.txt"
    echo .env >> "%BACKUP_DIR%\exclude_list.txt"
    echo dist >> "%BACKUP_DIR%\exclude_list.txt"
    echo coverage >> "%BACKUP_DIR%\exclude_list.txt"
    echo .nyc_output >> "%BACKUP_DIR%\exclude_list.txt"
    echo temp >> "%BACKUP_DIR%\exclude_list.txt"
    echo tmp >> "%BACKUP_DIR%\exclude_list.txt"
)

REM Copiar arquivos do projeto (excluindo arquivos desnecessários)
echo 📂 Copiando arquivos do projeto...
xcopy "%PROJECT_DIR%\*" "%TEMP_BACKUP%\" /E /I /Q /EXCLUDE:"%BACKUP_DIR%\exclude_list.txt" 2>nul

REM Compactar usando PowerShell
echo 📦 Compactando arquivos...
powershell -Command "& {Compress-Archive -Path '%TEMP_BACKUP%\*' -DestinationPath '%TEMP_BACKUP%\temp_backup.zip' -Force}"

REM Criptografar usando sistema Python seguro
echo 🔐 Criptografando backup...
python encryption_system.py encrypt "%TEMP_BACKUP%\temp_backup.zip" "%BACKUP_DIR%\%BACKUP_NAME%.enc" "%PASSWORD%"

REM Verificar se a criptografia foi bem-sucedida
if exist "%BACKUP_DIR%\%BACKUP_NAME%.enc" (
    echo ✅ Backup criptografado criado com sucesso!
    echo 📊 Arquivo: %BACKUP_NAME%.enc
    echo 📁 Localização: %BACKUP_DIR%
    echo 🔐 Criptografia: AES-256
    
    REM Mostrar tamanho do arquivo
    for %%F in ("%BACKUP_DIR%\%BACKUP_NAME%.enc") do (
        echo 📏 Tamanho: %%~zF bytes
    )
    
    REM Criar arquivo de metadados
    (
    echo Backup Criptografado do %PROJECT_NAME% - %date% %time%
    echo.
    echo Arquivo: %BACKUP_NAME%.enc
    echo Projeto: %PROJECT_DIR%
    echo Backup: %BACKUP_DIR%
    echo Criptografia: AES-256
    echo.
    echo Conteúdo incluído:
    echo - Código fonte
    echo - Arquivos de configuração
    echo - Documentação
    echo - Scripts
    echo.
    echo Excluído:
    echo - node_modules
    echo - build
    echo - .git
    echo - logs
    echo - .env
    echo - dist
    echo - coverage
    echo.
    echo IMPORTANTE:
    echo - Este arquivo está criptografado
    echo - Use restore-encrypted.bat para restaurar
    echo - Mantenha a senha em local seguro
    ) > "%BACKUP_DIR%\%BACKUP_NAME%_info.txt"
    
    echo 📝 Metadados salvos em: %BACKUP_NAME%_info.txt
    
) else (
    echo ❌ Erro: Backup criptografado não foi criado
    pause
    exit /b 1
)

REM Limpar diretório temporário
rmdir /s /q "%TEMP_BACKUP%"

REM Limpar backups criptografados antigos (manter apenas os últimos 3)
echo 🧹 Limpando backups criptografados antigos...
for /f "skip=3 delims=" %%i in ('dir /b /o-d "%BACKUP_DIR%\%PROJECT_NAME%_encrypted_*.enc" 2^>nul') do (
    del "%BACKUP_DIR%\%%i" 2>nul
)

echo 🎉 Backup criptografado concluído com sucesso!
echo.
echo 📋 Próximos passos:
echo   1. Verifique se o arquivo foi criado
echo   2. Anote o nome do backup: %BACKUP_NAME%
echo   3. Para restaurar, use: restore-encrypted.bat %BACKUP_NAME% %PROJECT_DIR% %BACKUP_DIR%
echo   4. Mantenha a senha em local seguro
echo.

pause

