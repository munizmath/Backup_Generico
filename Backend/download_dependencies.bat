@echo off
REM download_dependencies.bat - Baixar dependencias do Backend

echo Baixando dependencias do Backend...
echo.

REM Criar diretorio de dependencias se nao existir
if not exist "Dependencias" mkdir "Dependencias"
cd Dependencias

echo Instalando dependencias Python para scripts do Backend...
pip install psutil>=5.8.0 --target .
pip install cryptography>=41.0.0 --target .
pip install structlog>=23.0.0 --target .
pip install pyyaml>=6.0 --target .
pip install pydantic>=2.0.0 --target .
pip install boto3>=1.28.0 --target .

echo.
echo Baixando ferramentas adicionais...
echo.

REM Baixar 7-Zip para compressao avancada
echo Baixando 7-Zip...
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.7-zip.org/a/7z2301-x64.exe' -OutFile '7zip-installer.exe'}"
if exist "7zip-installer.exe" (
    echo 7-Zip baixado com sucesso
) else (
    echo Erro ao baixar 7-Zip
)

REM Baixar Git para hooks
echo Baixando Git...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe' -OutFile 'git-installer.exe'}"
if exist "git-installer.exe" (
    echo Git baixado com sucesso
) else (
    echo Erro ao baixar Git
)

REM Baixar PowerShell 7 para scripts avancados
echo Baixando PowerShell 7...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/PowerShell/PowerShell/releases/download/v7.3.6/PowerShell-7.3.6-win-x64.msi' -OutFile 'powershell7-installer.msi'}"
if exist "powershell7-installer.msi" (
    echo PowerShell 7 baixado com sucesso
) else (
    echo Erro ao baixar PowerShell 7
)

echo.
echo Dependencias do Backend instaladas com sucesso!
echo Localizacao: %CD%
echo.
echo Ferramentas baixadas:
echo - 7-Zip: 7zip-installer.exe
echo - Git: git-installer.exe  
echo - PowerShell 7: powershell7-installer.msi
echo.
pause
