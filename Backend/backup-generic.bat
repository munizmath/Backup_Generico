@echo off
REM backup-generic.bat - Script genérico de backup para qualquer projeto
REM Uso: backup-generic.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME]

echo 🔄 Iniciando backup genérico...

REM Verificar parâmetros
if "%~1"=="" (
    echo ❌ Erro: Diretório do projeto não especificado
    echo Uso: backup-generic.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME]
    echo Exemplo: backup-generic.bat "C:\MeuProjeto" "C:\Backups" "MeuProjeto"
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ❌ Erro: Diretório de backup não especificado
    echo Uso: backup-generic.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME]
    pause
    exit /b 1
)

if "%~3"=="" (
    echo ❌ Erro: Nome do projeto não especificado
    echo Uso: backup-generic.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME]
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

REM Verificar se o diretório foi criado com sucesso
if not exist "%BACKUP_DIR%" (
    echo ❌ Erro: Não foi possível criar o diretório de backup: %BACKUP_DIR%
    pause
    exit /b 1
)

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
echo   3. Para restaurar, use: restore-generic.bat %BACKUP_NAME% %PROJECT_DIR% %BACKUP_DIR%
echo.

pause
