@echo off
REM fix_pyinstaller.bat - Corrigir problema do PyInstaller com pathlib

echo 🔧 Corrigindo problema do PyInstaller...

echo 📦 Desinstalando pacote pathlib problemático...
python -m pip uninstall pathlib -y

if %errorlevel% neq 0 (
    echo ⚠️ Aviso: Não foi possível desinstalar pathlib automaticamente
    echo.
    echo 📋 Execute manualmente:
    echo   python -m pip uninstall pathlib
    echo.
    pause
)

echo.
echo 🧹 Limpando cache do PyInstaller...
if exist "Frontend\build" rmdir /s /q "Frontend\build"
if exist "Frontend\dist" rmdir /s /q "Frontend\dist"
if exist "Frontend\*.spec" del "Frontend\*.spec"

echo.
echo ✅ Correção concluída!
echo.
echo 🚀 Agora você pode tentar criar os executáveis novamente:
echo   start.bat → Opção 5: 🔨 Criar Executáveis
echo.

pause
