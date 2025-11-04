@echo off
REM setup-backup.bat - Configuração inicial do sistema de backup genérico

echo 🔧 Configurando sistema de backup genérico...

REM Criar diretório de configuração
set CONFIG_DIR=%~dp0config
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

REM Criar arquivo de configuração padrão
echo 📝 Criando arquivo de configuração...
(
echo # Configuração do Sistema de Backup Genérico
echo # Edite este arquivo para personalizar as configurações
echo.
echo # Diretório padrão para backups
echo BACKUP_DIR=%~dp0backups
echo.
echo # Número de backups a manter
echo MAX_BACKUPS=5
echo.
echo # Exclusões padrão
echo EXCLUDE_NODE_MODULES=true
echo EXCLUDE_BUILD=true
echo EXCLUDE_GIT=true
echo EXCLUDE_LOGS=true
echo EXCLUDE_ENV=true
echo EXCLUDE_DIST=true
echo EXCLUDE_COVERAGE=true
echo.
echo # Configurações de compactação
echo COMPRESSION_LEVEL=6
echo.
echo # Configurações de verificação
echo VERIFY_CHECKSUM=true
echo VERIFY_INTEGRITY=true
) > "%CONFIG_DIR%\backup-config.txt"

REM Criar diretório de backups padrão
set BACKUP_DIR=%~dp0backups
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Criar arquivo de exclusões personalizado
echo 📝 Criando arquivo de exclusões...
(
echo # Arquivos e diretórios a serem excluídos do backup
echo # Adicione um item por linha
echo.
echo # Dependências
echo node_modules
echo.
echo # Builds e distribuições
echo build
echo dist
echo.
echo # Controle de versão
echo .git
echo .svn
echo.
echo # Logs
echo logs
echo *.log
echo.
echo # Configurações sensíveis
echo .env
echo .env.local
echo .env.production
echo.
echo # Cobertura de testes
echo coverage
echo .nyc_output
echo.
echo # Arquivos temporários
echo temp
echo tmp
echo cache
echo.
echo # IDEs
echo .vscode
echo .idea
echo.
echo # Sistema operacional
echo Thumbs.db
echo .DS_Store
) > "%CONFIG_DIR%\exclude_list.txt"

REM Criar script de teste
echo 📝 Criando script de teste...
(
echo @echo off
echo REM test-backup.bat - Teste do sistema de backup
echo.
echo echo 🧪 Testando sistema de backup genérico...
echo.
echo REM Criar diretório de teste
echo set TEST_DIR=%~dp0test_project
echo if exist "%%TEST_DIR%%" rmdir /s /q "%%TEST_DIR%%"
echo mkdir "%%TEST_DIR%%"
echo.
echo REM Criar arquivos de teste
echo echo Teste de backup > "%%TEST_DIR%%\test.txt"
echo echo console.log^('Hello World'^) > "%%TEST_DIR%%\test.js"
echo echo { "name": "test" } > "%%TEST_DIR%%\test.json"
echo.
echo REM Executar backup de teste
echo call backup-generic.bat "%%TEST_DIR%%" "%~dp0backups" "TestProject"
echo.
echo REM Verificar se o backup foi criado
echo if exist "%~dp0backups\TestProject_backup_*.zip" ^(
echo     echo ✅ Teste bem-sucedido!
echo     echo 📦 Backup criado: TestProject_backup_*.zip
echo ^) else ^(
echo     echo ❌ Teste falhou!
echo ^)
echo.
echo REM Limpar arquivos de teste
echo rmdir /s /q "%%TEST_DIR%%"
echo.
echo pause
) > "%~dp0test-backup.bat"

REM Criar README
echo 📝 Criando documentação...
(
echo # 🔒 Sistema de Backup Genérico
echo.
echo Sistema de backup genérico que pode ser usado para qualquer projeto.
echo.
echo ## 🚀 Configuração Inicial
echo.
echo 1. Execute o setup:
echo    ```cmd
echo    setup-backup.bat
echo    ```
echo.
echo 2. Edite as configurações em `config/backup-config.txt`
echo.
echo 3. Personalize as exclusões em `config/exclude_list.txt`
echo.
echo ## 📦 Como Usar
echo.
echo ### Backup de um Projeto
echo ```cmd
echo backup-generic.bat "C:\MeuProjeto" "C:\Backups" "MeuProjeto"
echo ```
echo.
echo ### Restaurar um Backup
echo ```cmd
echo restore-generic.bat "MeuProjeto_backup_20241014_130702" "C:\MeuProjeto" "C:\Backups"
echo ```
echo.
echo ### Testar o Sistema
echo ```cmd
echo test-backup.bat
echo ```
echo.
echo ## 📁 Estrutura de Arquivos
echo.
echo ```
echo Backend_Backup/
echo ├── backup-generic.bat      # Script principal de backup
echo ├── restore-generic.bat     # Script de restauração
echo ├── setup-backup.bat        # Configuração inicial
echo ├── test-backup.bat         # Teste do sistema
echo ├── config/
echo │   ├── backup-config.txt   # Configurações
echo │   └── exclude_list.txt    # Lista de exclusões
echo └── backups/                # Diretório de backups
echo ```
echo.
echo ## ⚙️ Configurações
echo.
echo Edite `config/backup-config.txt` para personalizar:
echo - Diretório de backups padrão
echo - Número de backups a manter
echo - Configurações de compactação
echo - Opções de verificação
echo.
echo ## 🚨 Solução de Problemas
echo.
echo ### Erro: "PowerShell não encontrado"
echo - PowerShell já vem instalado no Windows
echo - Se não funcionar, execute: `powershell -ExecutionPolicy Bypass`
echo.
echo ### Erro: "Permissão negada"
echo - Execute como administrador
echo - Verifique permissões das pastas
echo.
echo ### Erro: "Arquivo não encontrado"
echo - Verifique se os caminhos estão corretos
echo - Use aspas para caminhos com espaços
echo.
echo ## 📞 Suporte
echo.
echo - Consulte este README para documentação completa
echo - Execute `test-backup.bat` para diagnosticar problemas
echo - Verifique `config/backup-config.txt` para configurações
echo.
echo ---
echo.
echo **Desenvolvido para uso genérico em qualquer projeto**
) > "%~dp0README.md"

echo ✅ Configuração concluída com sucesso!
echo.
echo 📋 Arquivos criados:
echo   - config/backup-config.txt (configurações)
echo   - config/exclude_list.txt (exclusões)
echo   - test-backup.bat (teste do sistema)
echo   - README.md (documentação)
echo   - backups/ (diretório de backups)
echo.
echo 🚀 Próximos passos:
echo   1. Edite config/backup-config.txt para personalizar
echo   2. Execute test-backup.bat para testar
echo   3. Use backup-generic.bat para fazer backups
echo.

pause
