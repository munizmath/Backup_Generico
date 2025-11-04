@echo off
REM test-backup.bat - Teste do sistema de backup

echo 🧪 Testando sistema de backup genérico...

REM Criar diretório de teste
set TEST_DIR=E:\BACKUPS\Backend_Backup\test_project
if exist "%TEST_DIR%" rmdir /s /q "%TEST_DIR%"
mkdir "%TEST_DIR%"

REM Criar arquivos de teste
echo Teste de backup > "%TEST_DIR%\teste.txt"
echo Arquivo de exemplo > "%TEST_DIR%\exemplo.txt"
mkdir "%TEST_DIR%\pasta_teste"
echo Conteudo da pasta > "%TEST_DIR%\pasta_teste\arquivo.txt"

REM Executar backup de teste
call backup-generic-template.bat "%TEST_DIR%" "E:\BACKUPS\Backend_Backup\backups" "TestProject"

REM Verificar se o backup foi criado
if exist "E:\BACKUPS\Backend_Backup\backups\TestProject_backup_*.zip" (
    echo ✅ Teste bem-sucedido!
    echo 📦 Backup criado: TestProject_backup_*.zip
) else (
    echo ❌ Teste falhou!
)

REM Limpar arquivos de teste
rmdir /s /q "%TEST_DIR%"

pause
