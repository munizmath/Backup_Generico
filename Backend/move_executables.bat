@echo off
REM move_executables.bat - Mover executáveis existentes para pasta raiz

echo 📁 Movendo executáveis para pasta raiz...

REM Verificar se existem executáveis na pasta Frontend\dist
if exist "Frontend\dist\BackupGUI.exe" (
    echo ✅ Encontrado BackupGUI.exe em Frontend\dist
    move "Frontend\dist\BackupGUI.exe" "BackupGUI.exe"
    echo ✅ BackupGUI.exe movido para pasta raiz
) else (
    echo ❌ BackupGUI.exe não encontrado em Frontend\dist
)

if exist "Frontend\dist\BackupDashboard.exe" (
    echo ✅ Encontrado BackupDashboard.exe em Frontend\dist
    move "Frontend\dist\BackupDashboard.exe" "BackupDashboard.exe"
    echo ✅ BackupDashboard.exe movido para pasta raiz
) else (
    echo ❌ BackupDashboard.exe não encontrado em Frontend\dist
)

REM Verificar se existem executáveis na pasta Frontend
if exist "Frontend\BackupGUI.exe" (
    echo ✅ Encontrado BackupGUI.exe em Frontend
    move "Frontend\BackupGUI.exe" "BackupGUI.exe"
    echo ✅ BackupGUI.exe movido para pasta raiz
)

if exist "Frontend\BackupDashboard.exe" (
    echo ✅ Encontrado BackupDashboard.exe em Frontend
    move "Frontend\BackupDashboard.exe" "BackupDashboard.exe"
    echo ✅ BackupDashboard.exe movido para pasta raiz
)

REM Limpar pasta dist se estiver vazia
if exist "Frontend\dist" (
    rmdir "Frontend\dist" 2>nul
    if %errorlevel% equ 0 (
        echo ✅ Pasta Frontend\dist removida (vazia)
    )
)

echo.
echo 📋 Verificando executáveis na pasta raiz:
if exist "BackupGUI.exe" (
    echo ✅ BackupGUI.exe - OK
) else (
    echo ❌ BackupGUI.exe - NÃO ENCONTRADO
)

if exist "BackupDashboard.exe" (
    echo ✅ BackupDashboard.exe - OK
) else (
    echo ❌ BackupDashboard.exe - NÃO ENCONTRADO
)

echo.
echo ✅ Movimentação concluída!
echo.
echo 🚀 Agora você pode executar diretamente:
echo   - BackupGUI.exe (Interface Gráfica)
echo   - BackupDashboard.exe (Dashboard)
echo   - start_gui.bat (Script que usa executável se disponível)
echo   - start_dashboard.bat (Script que usa executável se disponível)
echo.

pause
