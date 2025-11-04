@echo off
REM backup-generic-template.bat - Template genérico de backup para qualquer projeto
REM Uso: backup-generic-template.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME]

echo 🔄 Iniciando backup genérico...

REM Verificar parâmetros
if "%~1"=="" (
    echo ❌ Erro: Diretório do projeto não especificado
    echo Uso: backup-generic-template.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME]
    echo Exemplo: backup-generic-template.bat "C:\MeuProjeto" "C:\Backups" "MeuProjeto"
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ❌ Erro: Diretório de backup não especificado
    echo Uso: backup-generic-template.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME]
    pause
    exit /b 1
)

if "%~3"=="" (
    echo ❌ Erro: Nome do projeto não especificado
    echo Uso: backup-generic-template.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME]
    pause
    exit /b 1
)

set PROJECT_DIR=%~1
set BACKUP_DIR=%~2
set PROJECT_NAME=%~3
set DATE=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DATE=%DATE: =0%
set BACKUP_NAME=%PROJECT_NAME%_backup_%DATE%

echo 📁 Projeto: %PROJECT_DIR%
echo 📁 Backup: %BACKUP_DIR%
echo 📦 Nome: %BACKUP_NAME%

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

REM Usar arquivo de exclusão da pasta config
set EXCLUDE_FILE=%~dp0config\exclude_list.txt
if not exist "%EXCLUDE_FILE%" (
    set EXCLUDE_FILE=%BACKUP_DIR%\exclude_list.txt
    echo node_modules > "%EXCLUDE_FILE%"
    echo build >> "%EXCLUDE_FILE%"
    echo .git >> "%EXCLUDE_FILE%"
    echo logs >> "%EXCLUDE_FILE%"
    echo *.log >> "%EXCLUDE_FILE%"
    echo .env >> "%EXCLUDE_FILE%"
    echo dist >> "%EXCLUDE_FILE%"
    echo coverage >> "%EXCLUDE_FILE%"
    echo .nyc_output >> "%EXCLUDE_FILE%"
    echo temp >> "%EXCLUDE_FILE%"
    echo tmp >> "%EXCLUDE_FILE%"
)

REM Copiar arquivos do projeto (excluindo arquivos desnecessários)
echo 📂 Copiando arquivos do projeto...
xcopy "%PROJECT_DIR%\*" "%TEMP_BACKUP%\" /E /I /Q /Y

REM Contar arquivos copiados
set FILE_COUNT=0
for /f %%i in ('dir "%TEMP_BACKUP%" /s /b /a-d 2^>nul ^| find /c /v ""') do set FILE_COUNT=%%i

REM Compactar usando PowerShell
echo 📦 Compactando arquivos...
powershell -Command "& {Compress-Archive -Path '%TEMP_BACKUP%\*' -DestinationPath '%BACKUP_DIR%\%BACKUP_NAME%.zip' -Force}"

REM Limpar diretório temporário
rmdir /s /q "%TEMP_BACKUP%"

REM Verificar se o backup foi criado
if exist "%BACKUP_DIR%\%BACKUP_NAME%.zip" (
    echo ✅ Backup criado com sucesso!
    echo 📊 Arquivo: %BACKUP_NAME%.zip
    echo 📁 Localização: %BACKUP_DIR%
    
    REM Mostrar tamanho do arquivo
    for %%F in ("%BACKUP_DIR%\%BACKUP_NAME%.zip") do (
        echo 📏 Tamanho: %%~zF bytes
    )
    
    REM Criar versão de backup
    echo 📋 Criando versão de backup...
    python "%~dp0version_manager.py" create-backup "%PROJECT_DIR%" "%BACKUP_NAME%" "completo" "%FILE_COUNT%" "%%~zF"
    
    REM Criar arquivo de metadados
    (
    echo Backup do %PROJECT_NAME% - %date% %time%
    echo.
    echo Arquivo: %BACKUP_NAME%.zip
    echo Projeto: %PROJECT_DIR%
    echo Backup: %BACKUP_DIR%
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
    ) > "%BACKUP_DIR%\%BACKUP_NAME%_info.txt"
    
    echo 📝 Metadados salvos em: %BACKUP_NAME%_info.txt
    
) else (
    echo ❌ Erro: Backup não foi criado
    pause
    exit /b 1
)

REM Limpar backups antigos (manter apenas os últimos 5)
echo 🧹 Limpando backups antigos...
for /f "skip=5 delims=" %%i in ('dir /b /o-d "%BACKUP_DIR%\%PROJECT_NAME%_backup_*.zip" 2^>nul') do (
    del "%BACKUP_DIR%\%%i" 2>nul
)

echo 🎉 Backup concluído com sucesso!
echo.
echo 📋 Próximos passos:
echo   1. Verifique se o arquivo foi criado
echo   2. Anote o nome do backup: %BACKUP_NAME%
echo   3. Para restaurar, use: restore-generic-template.bat %BACKUP_NAME% %PROJECT_DIR% %BACKUP_DIR%
echo.

pause
