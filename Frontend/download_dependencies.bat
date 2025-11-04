@echo off
REM download_dependencies.bat - Baixar dependencias do Frontend

echo Baixando dependencias do Frontend...
echo.

REM Criar diretorio de dependencias se nao existir
if not exist "Dependencias" mkdir "Dependencias"
cd Dependencias

echo Instalando dependencias Python...
pip install psutil>=5.8.0 --target .
pip install colorama>=0.4.4 --target .
pip install tqdm>=4.62.0 --target .
pip install pyinstaller>=5.0.0 --target .
pip install cryptography>=41.0.0 --target .
pip install matplotlib>=3.7.0 --target .
pip install pandas>=2.0.0 --target .
pip install numpy>=1.24.0 --target .
pip install structlog>=23.0.0 --target .
pip install pyyaml>=6.0 --target .
pip install pydantic>=2.0.0 --target .
pip install boto3>=1.28.0 --target .

echo.
echo Dependencias do Frontend instaladas com sucesso!
echo Localizacao: %CD%
echo.
pause
