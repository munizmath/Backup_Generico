@echo off
REM build_executable.bat - Criar executável da interface gráfica

echo 🔨 Criando executável da interface gráfica...

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erro: Python não encontrado
    echo.
    echo 📋 Para instalar Python:
    echo   1. Acesse: https://www.python.org/downloads/
    echo   2. Baixe a versão mais recente
    echo   3. Execute o instalador
    echo   4. Marque "Add Python to PATH"
    echo   5. Execute este script novamente
    pause
    exit /b 1
)

REM Instalar PyInstaller se não estiver instalado
echo 📦 Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Instalando PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ❌ Erro ao instalar PyInstaller
        pause
        exit /b 1
    )
)

REM Instalar dependências
echo 📦 Instalando dependências...
pip install -r requirements.txt

REM Criar executável da interface gráfica unificada
echo 🔨 Criando executável da interface gráfica unificada...
pyinstaller --onefile --windowed --name "BackupGUI" gui_backup_unified.py

if %errorlevel% neq 0 (
    echo ❌ Erro ao criar executável da interface gráfica
    pause
    exit /b 1
)

REM Criar executável do dashboard
echo 🔨 Criando executável do dashboard...
pyinstaller --onefile --windowed --name "BackupDashboard" dashboard_backup.py

if %errorlevel% neq 0 (
    echo ❌ Erro ao criar executável do dashboard
    pause
    exit /b 1
)

REM Verificar se executáveis foram criados
if not exist "dist\BackupGUI.exe" (
    echo ❌ BackupGUI.exe não foi criado
    pause
    exit /b 1
)

if not exist "dist\BackupDashboard.exe" (
    echo ❌ BackupDashboard.exe não foi criado
    pause
    exit /b 1
)

REM Limpar arquivos temporários
rmdir /s /q "build" 2>nul
del "*.spec" 2>nul

echo ✅ Executáveis criados com sucesso!
echo.
echo 📁 Localização dos executáveis:
echo   - Interface Gráfica Unificada: dist\BackupGUI.exe
echo   - Dashboard: dist\BackupDashboard.exe
echo.
echo 🚀 Para usar os executáveis:
echo   1. Navegue até a pasta dist
echo   2. Execute BackupGUI.exe para interface gráfica unificada
echo   3. Execute BackupDashboard.exe para dashboard
echo.

pause
