@echo off
REM backup-incremental.bat - Backup incremental para arquivos modificados
REM Uso: backup-incremental.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [HOURS]

echo 🔄 Iniciando backup incremental...

REM Verificar parâmetros
if "%~1"=="" (
    echo ❌ Erro: Diretório do projeto não especificado
    echo Uso: backup-incremental.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [HOURS]
    echo Exemplo: backup-incremental.bat "C:\MeuProjeto" "C:\Backups" "MeuProjeto" "24"
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ❌ Erro: Diretório de backup não especificado
    echo Uso: backup-incremental.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [HOURS]
    pause
    exit /b 1
)

if "%~3"=="" (
    echo ❌ Erro: Nome do projeto não especificado
    echo Uso: backup-incremental.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [HOURS]
    pause
    exit /b 1
)

if "%~4"=="" (
    echo ❌ Erro: Número de horas não especificado
    echo Uso: backup-incremental.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [HOURS]
    echo Exemplo: backup-incremental.bat "C:\MeuProjeto" "C:\Backups" "MeuProjeto" "24"
    pause
    exit /b 1
)

set PROJECT_DIR=%~1
set BACKUP_DIR=%~2
set PROJECT_NAME=%~3
set HOURS=%~4
set DATE=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DATE=%DATE: =0%
set BACKUP_NAME=%PROJECT_NAME%_incremental_%DATE%

echo 📁 Projeto: %PROJECT_DIR%
echo 📁 Backup: %BACKUP_DIR%
echo 📦 Nome: %BACKUP_NAME%
echo ⏰ Período: %HOURS% horas

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

REM Usar PowerShell para encontrar arquivos modificados
echo 🔍 Procurando arquivos modificados nas últimas %HOURS% horas...
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\get_modified_files.ps1" -ProjectDir "%PROJECT_DIR%" -Hours "%HOURS%" -ExcludeList "%BACKUP_DIR%\exclude_list.txt" -OutputFile "%TEMP_BACKUP%\modified_files.txt"

REM Verificar se há arquivos modificados
for /f %%i in ('type "%TEMP_BACKUP%\modified_files.txt" ^| find /c /v ""') do set FILE_COUNT=%%i

if %FILE_COUNT%==0 (
    echo ⚠️  Nenhum arquivo modificado nas últimas %HOURS% horas
    echo 📋 Backup incremental não necessário
    rmdir /s /q "%TEMP_BACKUP%"
    pause
    exit /b 0
)

echo 📊 Encontrados %FILE_COUNT% arquivos modificados

REM Copiar arquivos modificados
echo 📂 Copiando arquivos modificados...
for /f "delims=" %%i in ('type "%TEMP_BACKUP%\modified_files.txt"') do (
    set "file_path=%%i"
    set "relative_path=!file_path:%PROJECT_DIR%\=!"
    set "target_path=%TEMP_BACKUP%\!relative_path!"
    
    REM Criar diretório de destino se não existir
    for %%j in ("!target_path!") do (
        if not exist "%%~dpj" mkdir "%%~dpj"
    )
    
    REM Copiar arquivo
    copy "!file_path!" "!target_path!" >nul 2>&1
)

REM Compactar usando PowerShell
echo 📦 Compactando arquivos...
powershell -Command "& {Compress-Archive -Path '%TEMP_BACKUP%\*' -DestinationPath '%BACKUP_DIR%\%BACKUP_NAME%.zip' -Force}"

REM Limpar diretório temporário
rmdir /s /q "%TEMP_BACKUP%"

REM Verificar se o backup foi criado
if exist "%BACKUP_DIR%\%BACKUP_NAME%.zip" (
    echo ✅ Backup incremental criado com sucesso!
    echo 📊 Arquivo: %BACKUP_NAME%.zip
    echo 📁 Localização: %BACKUP_DIR%
    echo 📊 Arquivos incluídos: %FILE_COUNT%
    
    REM Mostrar tamanho do arquivo
    for %%F in ("%BACKUP_DIR%\%BACKUP_NAME%.zip") do (
        echo 📏 Tamanho: %%~zF bytes
    )
    
    REM Criar arquivo de metadados
    (
    echo Backup Incremental do %PROJECT_NAME% - %date% %time%
    echo.
    echo Arquivo: %BACKUP_NAME%.zip
    echo Projeto: %PROJECT_DIR%
    echo Backup: %BACKUP_DIR%
    echo Período: %HOURS% horas
    echo Arquivos incluídos: %FILE_COUNT%
    echo.
    echo Conteúdo incluído:
    echo - Apenas arquivos modificados nas últimas %HOURS% horas
    echo - Código fonte modificado
    echo - Configurações alteradas
    echo - Documentação atualizada
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
    echo ❌ Erro: Backup incremental não foi criado
    pause
    exit /b 1
)

REM Limpar backups incrementais antigos (manter apenas os últimos 10)
echo 🧹 Limpando backups incrementais antigos...
for /f "skip=10 delims=" %%i in ('dir /b /o-d "%BACKUP_DIR%\%PROJECT_NAME%_incremental_*.zip" 2^>nul') do (
    del "%BACKUP_DIR%\%%i" 2>nul
)

echo 🎉 Backup incremental concluído com sucesso!
echo.
echo 📋 Próximos passos:
echo   1. Verifique se o arquivo foi criado
echo   2. Anote o nome do backup: %BACKUP_NAME%
echo   3. Para restaurar, use: restore-incremental.bat %BACKUP_NAME% %PROJECT_DIR% %BACKUP_DIR%
echo.

pause
