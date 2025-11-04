@echo off
REM test_all_scripts.bat - Teste completo de todos os scripts do sistema

echo ===============================================
echo    TESTE COMPLETO DO SISTEMA DE BACKUP
echo ===============================================
echo.

set ERROR_COUNT=0
set TOTAL_TESTS=0

REM Testar scripts do Backend
echo ===============================================
echo TESTANDO SCRIPTS DO BACKEND
echo ===============================================

set /a TOTAL_TESTS+=1
echo Testando: backup-generic-template.bat
if exist "backup-generic-template.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: backup-encrypted.bat
if exist "backup-encrypted.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: restore-surgical.bat
if exist "restore-surgical.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: snapshot-consistent.bat
if exist "snapshot-consistent.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: version_manager.py
if exist "version_manager.py" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: metadata_capture.py
if exist "metadata_capture.py" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: content-addressed.py
if exist "content-addressed.py" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: encryption_system.py
if exist "encryption_system.py" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: telemetry_system.py
if exist "telemetry_system.py" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: check_dependencies.bat
if exist "check_dependencies.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: build_executables.bat
if exist "build_executables.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: fix_pyinstaller.bat
if exist "fix_pyinstaller.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: install_system.bat
if exist "install_system.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

REM Testar scripts do Frontend
echo ===============================================
echo TESTANDO SCRIPTS DO FRONTEND
echo ===============================================

set /a TOTAL_TESTS+=1
echo Testando: ..\Frontend\gui_backup_advanced.py
if exist "..\Frontend\gui_backup_advanced.py" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: ..\Frontend\gui_backup_unified.py
if exist "..\Frontend\gui_backup_unified.py" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: ..\Frontend\dashboard_backup.py
if exist "..\Frontend\dashboard_backup.py" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: ..\Frontend\start_gui.bat
if exist "..\Frontend\start_gui.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: ..\Frontend\start_dashboard.bat
if exist "..\Frontend\start_dashboard.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: ..\Frontend\requirements.txt
if exist "..\Frontend\requirements.txt" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

REM Testar arquivos de configuracao
echo ===============================================
echo TESTANDO ARQUIVOS DE CONFIGURACAO
echo ===============================================

set /a TOTAL_TESTS+=1
echo Testando: config\retention_profiles.json
if exist "config\retention_profiles.json" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: config\.backupignore
if exist "config\.backupignore" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

REM Testar dependencias
echo ===============================================
echo TESTANDO DEPENDENCIAS
echo ===============================================

set /a TOTAL_TESTS+=1
echo Testando: Dependencias\download_dependencies.bat
if exist "Dependencias\download_dependencies.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: ..\Frontend\Dependencias\download_dependencies.bat
if exist "..\Frontend\Dependencias\download_dependencies.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

REM Testar hooks Git
echo ===============================================
echo TESTANDO HOOKS GIT
echo ===============================================

set /a TOTAL_TESTS+=1
echo Testando: git-hooks\pre-commit.bat
if exist "git-hooks\pre-commit.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: git-hooks\pre-push.bat
if exist "git-hooks\pre-push.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

set /a TOTAL_TESTS+=1
echo Testando: git-hooks\post-merge.bat
if exist "git-hooks\post-merge.bat" (
    echo   OK: Arquivo encontrado
) else (
    echo   ERRO: Arquivo nao encontrado
    set /a ERROR_COUNT+=1
)
echo.

REM Testar Python
echo ===============================================
echo TESTANDO PYTHON E DEPENDENCIAS
echo ===============================================

set /a TOTAL_TESTS+=1
echo Testando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo   OK: Python encontrado
) else (
    echo   ERRO: Python nao encontrado
    set /a ERROR_COUNT+=1
)

set /a TOTAL_TESTS+=1
echo Testando pip...
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo   OK: pip encontrado
) else (
    echo   ERRO: pip nao encontrado
    set /a ERROR_COUNT+=1
)

REM Testar scripts Python
echo.
echo Testando scripts Python...

set /a TOTAL_TESTS+=1
echo Testando version_manager.py...
python version_manager.py get-version "%~dp0" >nul
if %errorlevel% equ 0 (
    echo   OK: version_manager.py funcional
) else (
    echo   ERRO: version_manager.py com problemas
    set /a ERROR_COUNT+=1
)

set /a TOTAL_TESTS+=1
echo Testando metadata_capture.py...
python metadata_capture.py "%~dp0" "test_metadata.json" >nul
timeout /t 3 /nobreak >nul
if exist "test_metadata.json" (
    echo   OK: metadata_capture.py funcional
    del test_metadata.json 2>nul
) else (
    echo   ERRO: metadata_capture.py com problemas
    set /a ERROR_COUNT+=1
)

REM Testar diretorios
echo ===============================================
echo TESTANDO ESTRUTURA DE DIRETORIOS
echo ===============================================

set /a TOTAL_TESTS+=1
echo Testando: config
if exist "config" (
    echo   OK: Diretorio encontrado
) else (
    echo   ERRO: Diretorio nao encontrado
    set /a ERROR_COUNT+=1
)

set /a TOTAL_TESTS+=1
echo Testando: Dependencias
if exist "Dependencias" (
    echo   OK: Diretorio encontrado
) else (
    echo   ERRO: Diretorio nao encontrado
    set /a ERROR_COUNT+=1
)

set /a TOTAL_TESTS+=1
echo Testando: git-hooks
if exist "git-hooks" (
    echo   OK: Diretorio encontrado
) else (
    echo   ERRO: Diretorio nao encontrado
    set /a ERROR_COUNT+=1
)

set /a TOTAL_TESTS+=1
echo Testando: backup_versions
if exist "backup_versions" (
    echo   OK: Diretorio encontrado
) else (
    echo   ERRO: Diretorio nao encontrado
    set /a ERROR_COUNT+=1
)

set /a TOTAL_TESTS+=1
echo Testando: ..\Frontend\Dependencias
if exist "..\Frontend\Dependencias" (
    echo   OK: Diretorio encontrado
) else (
    echo   ERRO: Diretorio nao encontrado
    set /a ERROR_COUNT+=1
)

REM Resumo final
echo ===============================================
echo RESUMO DOS TESTES
echo ===============================================
echo.
echo Total de testes: %TOTAL_TESTS%
echo Erros encontrados: %ERROR_COUNT%
echo.

if %ERROR_COUNT% equ 0 (
    echo ✅ TODOS OS TESTES PASSARAM!
    echo O sistema esta funcionando corretamente.
) else (
    echo ❌ %ERROR_COUNT% ERROS ENCONTRADOS!
    echo Verifique os erros acima e corrija-os.
)

echo.
pause