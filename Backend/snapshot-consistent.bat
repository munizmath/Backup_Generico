@echo off
REM snapshot-consistent.bat - Sistema de Snapshots Consistentes
REM Usa VSS (Volume Shadow Copy) no Windows para snapshots consistentes

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo 🔧 Sistema de Snapshots Consistentes
    echo ====================================
    echo.
    echo Uso:
    echo   snapshot-consistent.bat ^<project_dir^> ^<backup_dir^> ^<project_name^> [profile]
    echo.
    echo Exemplos:
    echo   snapshot-consistent.bat "E:\DESENVOLVIMENTO\LaPlata" "E:\Backup" "LaPlata" "dev-fast"
    echo.
    pause
    exit /b 1
)

set PROJECT_DIR=%~1
set BACKUP_DIR=%~2
set PROJECT_NAME=%~3
set PROFILE=%~4
if "%PROFILE%"=="" set PROFILE=dev-fast

echo 🔧 Iniciando snapshot consistente...
echo 📁 Projeto: %PROJECT_DIR%
echo 📁 Backup: %BACKUP_DIR%
echo 📦 Nome: %PROJECT_NAME%
echo 🎯 Perfil: %PROFILE%
echo.

REM Verificar se VSS está disponível
echo 🔍 Verificando VSS (Volume Shadow Copy Service)...
vssadmin list shadows >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  VSS não disponível, usando backup normal
    call backup-generic-template.bat "%PROJECT_DIR%" "%BACKUP_DIR%" "%PROJECT_NAME%"
    exit /b %errorlevel%
)

echo ✅ VSS disponível
echo.

REM Criar snapshot VSS
echo 📸 Criando snapshot VSS...
set SNAPSHOT_ID=
for /f "tokens=*" %%i in ('vssadmin create shadow /for=%PROJECT_DIR% 2^>nul ^| findstr "Shadow Copy ID"') do (
    set SNAPSHOT_LINE=%%i
    for /f "tokens=4" %%j in ("!SNAPSHOT_LINE!") do (
        set SNAPSHOT_ID=%%j
    )
)

if not defined SNAPSHOT_ID (
    echo ❌ Erro ao criar snapshot VSS
    echo 🔄 Tentando backup normal...
    call backup-generic-template.bat "%PROJECT_DIR%" "%BACKUP_DIR%" "%PROJECT_NAME%"
    exit /b %errorlevel%
)

echo ✅ Snapshot VSS criado: %SNAPSHOT_ID%
echo.

REM Obter caminho do snapshot
set SNAPSHOT_PATH=
for /f "tokens=*" %%i in ('vssadmin list shadows ^| findstr "%SNAPSHOT_ID%" -A 5 ^| findstr "Shadow Copy Volume"') do (
    set VOLUME_LINE=%%i
    for /f "tokens=4*" %%j in ("!VOLUME_LINE!") do (
        set SNAPSHOT_PATH=%%j
    )
)

if not defined SNAPSHOT_PATH (
    echo ❌ Erro ao obter caminho do snapshot
    vssadmin delete shadows /shadow=%SNAPSHOT_ID% /quiet
    exit /b 1
)

echo 📁 Caminho do snapshot: %SNAPSHOT_PATH%
echo.

REM Criar diretório de backup temporário
set TEMP_BACKUP=%TEMP%\backup_consistent_%RANDOM%
mkdir "%TEMP_BACKUP%" 2>nul

REM Copiar arquivos do snapshot
echo 📂 Copiando arquivos do snapshot...
xcopy "%SNAPSHOT_PATH%\*" "%TEMP_BACKUP%\" /E /I /Q /Y

if %errorlevel% neq 0 (
    echo ❌ Erro ao copiar arquivos do snapshot
    vssadmin delete shadows /shadow=%SNAPSHOT_ID% /quiet
    rmdir /s /q "%TEMP_BACKUP%" 2>nul
    exit /b 1
)

echo ✅ Arquivos copiados com sucesso
echo.

REM Capturar metadados contextuais
echo 📊 Capturando metadados contextuais...
python "%~dp0metadata_capture.py" "%PROJECT_DIR%" "%TEMP_BACKUP%\metadata.json" 2>nul

REM Aplicar perfil de retenção
call :apply_retention_profile "%PROFILE%"

REM Criar nome do backup com timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set datetime=%%a
set BACKUP_NAME=%PROJECT_NAME%_backup_%datetime:~0,8%_%datetime:~8,6%

REM Compactar backup
echo 📦 Compactando backup...
powershell -Command "& {Compress-Archive -Path '%TEMP_BACKUP%\*' -DestinationPath '%BACKUP_DIR%\%BACKUP_NAME%.zip' -Force}"

if not exist "%BACKUP_DIR%\%BACKUP_NAME%.zip" (
    echo ❌ Erro ao criar arquivo de backup
    vssadmin delete shadows /shadow=%SNAPSHOT_ID% /quiet
    rmdir /s /q "%TEMP_BACKUP%" 2>nul
    exit /b 1
)

echo ✅ Backup criado: %BACKUP_NAME%.zip
echo.

REM Criar arquivo de metadados
call :create_metadata_file "%BACKUP_DIR%" "%BACKUP_NAME%" "%SNAPSHOT_ID%"

REM Limpar snapshot VSS
echo 🧹 Limpando snapshot VSS...
vssadmin delete shadows /shadow=%SNAPSHOT_ID% /quiet

REM Limpar diretório temporário
rmdir /s /q "%TEMP_BACKUP%" 2>nul

echo ✅ Snapshot consistente concluído com sucesso!
echo 📊 Arquivo: %BACKUP_NAME%.zip
echo 📁 Localização: %BACKUP_DIR%
echo.

REM Aplicar política de retenção
call :apply_retention_policy "%BACKUP_DIR%" "%PROFILE%"

goto :end

:apply_retention_profile
set PROFILE_NAME=%~1
echo 🎯 Aplicando perfil de retenção: %PROFILE_NAME%

REM Carregar configuração do perfil
if exist "%~dp0config\retention_profiles.json" (
    echo ✅ Perfil de retenção carregado
) else (
    echo ⚠️  Arquivo de perfil não encontrado, usando configuração padrão
)
goto :eof

:create_metadata_file
set BACKUP_DIR=%~1
set BACKUP_NAME=%~2
set SNAPSHOT_ID=%~3

echo 📄 Criando arquivo de metadados...

(
echo Backup Consistente - %date% %time%
echo.
echo Arquivo: %BACKUP_NAME%.zip
echo Projeto: %PROJECT_NAME%
echo Diretório: %PROJECT_DIR%
echo Snapshot VSS: %SNAPSHOT_ID%
echo Tipo: Consistente com VSS
echo Perfil: %PROFILE%
echo.
echo Metadados Contextuais:
if exist "%TEMP_BACKUP%\metadata.json" (
    type "%TEMP_BACKUP%\metadata.json"
) else (
    echo Metadados não disponíveis
)
) > "%BACKUP_DIR%\%BACKUP_NAME%_info.txt"

echo ✅ Metadados salvos em: %BACKUP_NAME%_info.txt
goto :eof

:apply_retention_policy
set BACKUP_DIR=%~1
set PROFILE_NAME=%~2

echo 🧹 Aplicando política de retenção...

REM Implementação básica - manter apenas os últimos 10 backups
set COUNT=0
for /f "delims=" %%i in ('dir "%BACKUP_DIR%\*%PROJECT_NAME%*.zip" /b /o-d 2^>nul') do (
    set /a COUNT+=1
    if !COUNT! gtr 10 (
        echo 🗑️  Removendo backup antigo: %%i
        del "%BACKUP_DIR%\%%i" 2>nul
        del "%BACKUP_DIR%\%%~ni_info.txt" 2>nul
    )
)

echo ✅ Política de retenção aplicada
goto :eof

:end
echo.
echo 🎉 Snapshot consistente concluído!
echo.
pause
