@echo off
REM backup-git.bat - Backup baseado em Git
REM Uso: backup-git.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [COMMIT_HASH]

echo 🔄 Iniciando backup baseado em Git...

REM Verificar parâmetros
if "%~1"=="" (
    echo ❌ Erro: Diretório do projeto não especificado
    echo Uso: backup-git.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [COMMIT_HASH]
    echo Exemplo: backup-git.bat "C:\MeuProjeto" "C:\Backups" "MeuProjeto" "HEAD"
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ❌ Erro: Diretório de backup não especificado
    echo Uso: backup-git.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [COMMIT_HASH]
    pause
    exit /b 1
)

if "%~3"=="" (
    echo ❌ Erro: Nome do projeto não especificado
    echo Uso: backup-git.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [COMMIT_HASH]
    pause
    exit /b 1
)

if "%~4"=="" (
    echo ❌ Erro: Commit hash não especificado
    echo Uso: backup-git.bat [PROJECT_DIR] [BACKUP_DIR] [PROJECT_NAME] [COMMIT_HASH]
    echo Exemplo: backup-git.bat "C:\MeuProjeto" "C:\Backups" "MeuProjeto" "HEAD"
    pause
    exit /b 1
)

set PROJECT_DIR=%~1
set BACKUP_DIR=%~2
set PROJECT_NAME=%~3
set COMMIT_HASH=%~4
set DATE=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DATE=%DATE: =0%
set BACKUP_NAME=%PROJECT_NAME%_git_%DATE%

echo 📁 Projeto: %PROJECT_DIR%
echo 📁 Backup: %BACKUP_DIR%
echo 📦 Nome: %BACKUP_NAME%
echo 🔗 Commit: %COMMIT_HASH%

REM Verificar se o diretório do projeto existe
if not exist "%PROJECT_DIR%" (
    echo ❌ Erro: Diretório do projeto não encontrado: %PROJECT_DIR%
    pause
    exit /b 1
)

REM Verificar se é um repositório Git
if not exist "%PROJECT_DIR%\.git" (
    echo ❌ Erro: Diretório não é um repositório Git: %PROJECT_DIR%
    echo.
    echo 🔧 Para inicializar um repositório Git:
    echo   1. cd "%PROJECT_DIR%"
    echo   2. git init
    echo   3. git add .
    echo   4. git commit -m "Initial commit"
    pause
    exit /b 1
)

REM Criar diretório de backup se não existir
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Criar diretório temporário para o backup
set TEMP_BACKUP=%BACKUP_DIR%\temp_%BACKUP_NAME%
if exist "%TEMP_BACKUP%" rmdir /s /q "%TEMP_BACKUP%"
mkdir "%TEMP_BACKUP%"

REM Obter informações do Git
echo 🔍 Obtendo informações do Git...
cd /d "%PROJECT_DIR%"

REM Verificar se o commit existe
git rev-parse --verify %COMMIT_HASH% >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erro: Commit não encontrado: %COMMIT_HASH%
    echo.
    echo 📋 Commits disponíveis:
    git log --oneline -10
    pause
    exit /b 1
)

REM Obter informações do commit
for /f "tokens=*" %%i in ('git rev-parse %COMMIT_HASH%') do set COMMIT_FULL=%%i
for /f "tokens=*" %%i in ('git log -1 --format=%%s %COMMIT_HASH%') do set COMMIT_MESSAGE=%%i
for /f "tokens=*" %%i in ('git log -1 --format=%%an %COMMIT_HASH%') do set COMMIT_AUTHOR=%%i
for /f "tokens=*" %%i in ('git log -1 --format=%%ad %COMMIT_HASH%') do set COMMIT_DATE=%%i
for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set CURRENT_BRANCH=%%i
if "%CURRENT_BRANCH%"=="" set CURRENT_BRANCH=detached

echo 📊 Commit: %COMMIT_FULL%
echo 📝 Mensagem: %COMMIT_MESSAGE%
echo 👤 Autor: %COMMIT_AUTHOR%
echo 📅 Data: %COMMIT_DATE%
echo 🌿 Branch: %CURRENT_BRANCH%

REM Fazer checkout do commit específico
echo 🔄 Fazendo checkout do commit %COMMIT_HASH%...
git checkout %COMMIT_HASH% >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erro: Falha ao fazer checkout do commit
    pause
    exit /b 1
)

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

REM Voltar para a branch original
echo 🔄 Voltando para a branch original...
git checkout %CURRENT_BRANCH% >nul 2>&1

REM Compactar usando PowerShell
echo 📦 Compactando arquivos...
powershell -Command "& {Compress-Archive -Path '%TEMP_BACKUP%\*' -DestinationPath '%BACKUP_DIR%\%BACKUP_NAME%.zip' -Force}"

REM Limpar diretório temporário
rmdir /s /q "%TEMP_BACKUP%"

REM Verificar se o backup foi criado
if exist "%BACKUP_DIR%\%BACKUP_NAME%.zip" (
    echo ✅ Backup Git criado com sucesso!
    echo 📊 Arquivo: %BACKUP_NAME%.zip
    echo 📁 Localização: %BACKUP_DIR%
    
    REM Mostrar tamanho do arquivo
    for %%F in ("%BACKUP_DIR%\%BACKUP_NAME%.zip") do (
        echo 📏 Tamanho: %%~zF bytes
    )
    
    REM Criar arquivo de metadados
    (
    echo Backup Git do %PROJECT_NAME% - %date% %time%
    echo.
    echo Arquivo: %BACKUP_NAME%.zip
    echo Projeto: %PROJECT_DIR%
    echo Backup: %BACKUP_DIR%
    echo.
    echo Informações do Git:
    echo - Commit: %COMMIT_FULL%
    echo - Mensagem: %COMMIT_MESSAGE%
    echo - Autor: %COMMIT_AUTHOR%
    echo - Data: %COMMIT_DATE%
    echo - Branch: %CURRENT_BRANCH%
    echo.
    echo Conteúdo incluído:
    echo - Código fonte do commit %COMMIT_HASH%
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
    echo ❌ Erro: Backup Git não foi criado
    pause
    exit /b 1
)

REM Limpar backups Git antigos (manter apenas os últimos 5)
echo 🧹 Limpando backups Git antigos...
for /f "skip=5 delims=" %%i in ('dir /b /o-d "%BACKUP_DIR%\%PROJECT_NAME%_git_*.zip" 2^>nul') do (
    del "%BACKUP_DIR%\%%i" 2>nul
)

echo 🎉 Backup Git concluído com sucesso!
echo.
echo 📋 Próximos passos:
echo   1. Verifique se o arquivo foi criado
echo   2. Anote o nome do backup: %BACKUP_NAME%
echo   3. Para restaurar, use: restore-git.bat %BACKUP_NAME% %PROJECT_DIR% %BACKUP_DIR%
echo.

pause

