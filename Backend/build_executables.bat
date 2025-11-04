@echo off
REM build_executables.bat - Criar executáveis das interfaces gráficas

echo 🔨 Sistema de Criação de Executáveis
echo =====================================
echo.

echo 📋 Este script irá criar executáveis para:
echo   - Interface Gráfica (BackupGUI.exe)
echo   - Dashboard de Monitoramento (BackupDashboard.exe)
echo.

echo ⚠️  IMPORTANTE: Este processo pode demorar alguns minutos
echo    e requer conexão com a internet para baixar dependências.
echo.

set /p confirm="Deseja continuar? (s/n): "
if /i not "%confirm%"=="s" (
    echo Operação cancelada.
    pause
    exit /b 0
)

echo.
echo 🚀 Iniciando criação de executáveis...

REM Navegar para pasta Frontend
cd Frontend

REM Executar script de criação
call build_executable.bat

if %errorlevel% equ 0 (
    echo.
    echo ✅ Executáveis criados com sucesso!
    echo.
    echo 📁 Movendo executáveis para pasta raiz...
    
    REM Mover executáveis para pasta raiz
    if exist "Frontend\dist\BackupGUI.exe" (
        move "Frontend\dist\BackupGUI.exe" "BackupGUI.exe"
        echo ✅ BackupGUI.exe movido para pasta raiz
    )
    
    if exist "Frontend\dist\BackupDashboard.exe" (
        move "Frontend\dist\BackupDashboard.exe" "BackupDashboard.exe"
        echo ✅ BackupDashboard.exe movido para pasta raiz
    )
    
    REM Limpar pasta dist se estiver vazia
    if exist "Frontend\dist" (
        rmdir "Frontend\dist" 2>nul
    )
    
    echo.
    echo 📁 Localização dos executáveis:
    echo   - Interface Gráfica: BackupGUI.exe (pasta raiz)
    echo   - Dashboard: BackupDashboard.exe (pasta raiz)
    echo.
    echo 🚀 Para usar os executáveis:
    echo   1. Execute BackupGUI.exe para interface gráfica
    echo   2. Execute BackupDashboard.exe para dashboard
    echo   3. Ou use os scripts start_gui.bat e start_dashboard.bat
    echo.
) else (
    echo.
    echo ❌ Erro na criação dos executáveis
    echo.
    echo 🔧 Possíveis soluções:
    echo   1. Verifique se Python está instalado
    echo   2. Execute: pip install pyinstaller
    echo   3. Execute como administrador
    echo   4. Verifique conexão com internet
    echo.
)

pause
