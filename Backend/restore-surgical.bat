@echo off
REM restore-surgical.bat - Sistema de Restores Cirúrgicos
REM Permite restaurar arquivos específicos, por timestamp, ou por hunk

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo 🔧 Sistema de Restores Cirúrgicos
    echo ==================================
    echo.
    echo Uso:
    echo   restore-surgical.bat --file ^<path^> --at ^<timestamp^> [backup_dir]
    echo   restore-surgical.bat --hunk ^<path^> --lines ^<start-end^> [backup_dir]
    echo   restore-surgical.bat --list [backup_dir]
    echo   restore-surgical.bat --search ^<pattern^> [backup_dir]
    echo.
    echo Exemplos:
    echo   restore-surgical.bat --file "src/app.py" --at "2024-10-14 15:30"
    echo   restore-surgical.bat --hunk "src/utils.py" --lines "10-25"
    echo   restore-surgical.bat --list
    echo   restore-surgical.bat --search "app.py"
    echo.
    pause
    exit /b 1
)

set BACKUP_DIR=%~3
if "%BACKUP_DIR%"=="" set BACKUP_DIR=E:\Backup

echo 🔧 Restore Cirúrgico
echo ====================
echo.

if "%~1"=="--list" (
    call :list_backups
    goto :end
)

if "%~1"=="--search" (
    call :search_files "%~2"
    goto :end
)

if "%~1"=="--file" (
    call :restore_file "%~2" "%~4"
    goto :end
)

if "%~1"=="--hunk" (
    call :restore_hunk "%~2" "%~4"
    goto :end
)

echo ❌ Comando não reconhecido: %~1
pause
exit /b 1

:list_backups
echo 📋 Listando backups disponíveis...
echo.

for /f "delims=" %%i in ('dir "%BACKUP_DIR%\*.zip" /b /o-d 2^>nul') do (
    set BACKUP_FILE=%%i
    set BACKUP_NAME=!BACKUP_FILE:.zip=!
    
    echo 📦 !BACKUP_NAME!
    
    REM Extrair timestamp do nome do arquivo
    for /f "tokens=3,4 delims=_" %%a in ("!BACKUP_NAME!") do (
        set DATE_PART=%%a
        set TIME_PART=%%b
    )
    
    if defined DATE_PART (
        echo   📅 Data: !DATE_PART!
        echo   🕐 Hora: !TIME_PART!
    )
    
    REM Verificar se existe arquivo de metadados
    if exist "%BACKUP_DIR%\!BACKUP_NAME!_info.txt" (
        echo   📄 Metadados: Disponível
    ) else (
        echo   📄 Metadados: Não encontrado
    )
    
    echo.
)
goto :eof

:search_files
set SEARCH_PATTERN=%~1
echo 🔍 Buscando arquivos contendo: %SEARCH_PATTERN%
echo.

for /f "delims=" %%i in ('dir "%BACKUP_DIR%\*.zip" /b /o-d 2^>nul') do (
    set BACKUP_FILE=%%i
    set BACKUP_NAME=!BACKUP_FILE:.zip=!
    
    echo 📦 Verificando: !BACKUP_NAME!
    
    REM Criar diretório temporário
    set TEMP_DIR=%TEMP%\backup_search_!RANDOM!
    mkdir "!TEMP_DIR!" 2>nul
    
    REM Extrair backup temporariamente
    powershell -Command "& {Expand-Archive -Path '%BACKUP_DIR%\!BACKUP_FILE!' -DestinationPath '!TEMP_DIR!' -Force}" 2>nul
    
    if exist "!TEMP_DIR!" (
        REM Buscar arquivos que correspondem ao padrão
        for /r "!TEMP_DIR!" %%f in (*%SEARCH_PATTERN%*) do (
            set REL_PATH=%%f
            set REL_PATH=!REL_PATH:%TEMP_DIR%\=!
            echo   📄 !REL_PATH!
        )
        
        REM Limpar diretório temporário
        rmdir /s /q "!TEMP_DIR!" 2>nul
    )
    
    echo.
)
goto :eof

:restore_file
set TARGET_FILE=%~1
set TIMESTAMP=%~2

echo 📄 Restaurando arquivo: %TARGET_FILE%
echo 🕐 Timestamp: %TIMESTAMP%
echo.

REM Encontrar backup mais próximo do timestamp
set BEST_BACKUP=
set BEST_TIME=0

for /f "delims=" %%i in ('dir "%BACKUP_DIR%\*.zip" /b /o-d 2^>nul') do (
    set BACKUP_FILE=%%i
    set BACKUP_NAME=!BACKUP_FILE:.zip=!
    
    REM Extrair timestamp do nome do arquivo
    for /f "tokens=3,4 delims=_" %%a in ("!BACKUP_NAME!") do (
        set DATE_PART=%%a
        set TIME_PART=%%b
    )
    
    if defined DATE_PART (
        REM Verificar se este backup contém o arquivo
        call :check_file_in_backup "!BACKUP_FILE!" "%TARGET_FILE%"
        if !errorlevel! equ 0 (
            set BEST_BACKUP=!BACKUP_FILE!
            goto :found_backup
        )
    )
)

if not defined BEST_BACKUP (
    echo ❌ Nenhum backup encontrado contendo o arquivo: %TARGET_FILE%
    pause
    exit /b 1
)

:found_backup
echo ✅ Backup encontrado: %BEST_BACKUP%
echo.

REM Criar diretório temporário
set TEMP_DIR=%TEMP%\backup_restore_!RANDOM!
mkdir "!TEMP_DIR!" 2>nul

REM Extrair backup
echo 📦 Extraindo backup...
powershell -Command "& {Expand-Archive -Path '%BACKUP_DIR%\%BEST_BACKUP%' -DestinationPath '!TEMP_DIR!' -Force}" 2>nul

if not exist "!TEMP_DIR!" (
    echo ❌ Erro ao extrair backup
    pause
    exit /b 1
)

REM Encontrar arquivo no backup
set FOUND_FILE=
for /r "!TEMP_DIR!" %%f in ("%TARGET_FILE%") do (
    set FOUND_FILE=%%f
)

if not defined FOUND_FILE (
    echo ❌ Arquivo não encontrado no backup: %TARGET_FILE%
    rmdir /s /q "!TEMP_DIR!" 2>nul
    pause
    exit /b 1
)

echo ✅ Arquivo encontrado: !FOUND_FILE!

REM Perguntar onde restaurar
set /p RESTORE_PATH="📁 Onde restaurar o arquivo? (pressione Enter para restaurar no local original): "

if "%RESTORE_PATH%"=="" (
    set RESTORE_PATH=%TARGET_FILE%
)

REM Criar diretório de destino se necessário
for %%d in ("!RESTORE_PATH!") do (
    if not exist "%%~dpd" mkdir "%%~dpd" 2>nul
)

REM Copiar arquivo
copy "!FOUND_FILE!" "!RESTORE_PATH!" >nul 2>&1

if exist "!RESTORE_PATH!" (
    echo ✅ Arquivo restaurado com sucesso: !RESTORE_PATH!
) else (
    echo ❌ Erro ao restaurar arquivo
)

REM Limpar diretório temporário
rmdir /s /q "!TEMP_DIR!" 2>nul
goto :eof

:check_file_in_backup
set BACKUP_FILE=%~1
set TARGET_FILE=%~2

REM Criar diretório temporário para verificação
set CHECK_DIR=%TEMP%\backup_check_!RANDOM!
mkdir "!CHECK_DIR!" 2>nul

REM Extrair backup temporariamente
powershell -Command "& {Expand-Archive -Path '%BACKUP_DIR%\%BACKUP_FILE%' -DestinationPath '!CHECK_DIR!' -Force}" 2>nul

REM Verificar se arquivo existe
for /r "!CHECK_DIR!" %%f in ("%TARGET_FILE%") do (
    rmdir /s /q "!CHECK_DIR!" 2>nul
    exit /b 0
)

rmdir /s /q "!CHECK_DIR!" 2>nul
exit /b 1

:restore_hunk
set TARGET_FILE=%~1
set LINES=%~2

echo 📄 Restaurando hunk: %TARGET_FILE% (linhas %LINES%)
echo.

REM Implementação básica - restaurar arquivo completo
REM Em uma implementação mais avançada, aqui seria feita a extração de hunk específico
echo ⚠️  Funcionalidade de hunk em desenvolvimento
echo 📄 Restaurando arquivo completo: %TARGET_FILE%

call :restore_file "%TARGET_FILE%" ""
goto :eof

:end
echo.
echo ✅ Operação concluída!
pause
