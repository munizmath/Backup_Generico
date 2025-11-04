#!/usr/bin/env python3
"""
Script de Validação das Correções
Verifica se todas as correções foram aplicadas corretamente
"""

import os
import sys
from pathlib import Path
from logging_config import get_logger

def validate_crypto_fixes():
    """Validar correções de criptografia"""
    logger = get_logger("validation")
    
    # Verificar se os scripts .bat foram atualizados
    backup_encrypted = Path("backup-encrypted.bat")
    restore_encrypted = Path("restore-encrypted.bat")
    
    issues = []
    
    if backup_encrypted.exists():
        with open(backup_encrypted, 'r', encoding='utf-8') as f:
            content = f.read()
            if "ConvertTo-SecureString" in content and "Key (1..32)" in content:
                issues.append("backup-encrypted.bat ainda contém criptografia insegura")
            elif "encryption_system.py" not in content:
                issues.append("backup-encrypted.bat não foi atualizado para usar encryption_system.py")
    
    if restore_encrypted.exists():
        with open(restore_encrypted, 'r', encoding='utf-8') as f:
            content = f.read()
            if "ConvertTo-SecureString" in content and "Key (1..32)" in content:
                issues.append("restore-encrypted.bat ainda contém criptografia insegura")
            elif "encryption_system.py" not in content:
                issues.append("restore-encrypted.bat não foi atualizado para usar encryption_system.py")
    
    if issues:
        logger.error("Problemas de criptografia encontrados:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    else:
        logger.info("✅ Correções de criptografia validadas")
        return True

def validate_dependency_fixes():
    """Validar correções de dependências"""
    logger = get_logger("validation")
    
    requirements_file = Path("Frontend/requirements.txt")
    issues = []
    
    if requirements_file.exists():
        with open(requirements_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "smtplib-ssl" in content:
                issues.append("smtplib-ssl ainda está no requirements.txt")
    
    if issues:
        logger.error("Problemas de dependências encontrados:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    else:
        logger.info("✅ Correções de dependências validadas")
        return True

def validate_exception_handling():
    """Validar correções de tratamento de exceções"""
    logger = get_logger("validation")
    
    version_manager = Path("version_manager.py")
    issues = []
    
    if version_manager.exists():
        with open(version_manager, 'r', encoding='utf-8') as f:
            content = f.read()
            if "except:" in content and "except OSError" not in content:
                issues.append("version_manager.py ainda contém except: genérico")
    
    if issues:
        logger.error("Problemas de tratamento de exceções encontrados:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    else:
        logger.info("✅ Correções de tratamento de exceções validadas")
        return True

def validate_powershell_refactoring():
    """Validar refatoração do PowerShell"""
    logger = get_logger("validation")
    
    backup_incremental = Path("backup-incremental.bat")
    get_modified_files_script = Path("scripts/get_modified_files.ps1")
    
    issues = []
    
    if backup_incremental.exists():
        with open(backup_incremental, 'r', encoding='utf-8') as f:
            content = f.read()
            if "Get-ChildItem -Path" in content and "Where-Object" in content and "ForEach-Object" in content:
                issues.append("backup-incremental.bat ainda contém comando PowerShell complexo")
    
    if not get_modified_files_script.exists():
        issues.append("Script PowerShell get_modified_files.ps1 não foi criado")
    
    if issues:
        logger.error("Problemas de refatoração PowerShell encontrados:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    else:
        logger.info("✅ Refatoração PowerShell validada")
        return True

def validate_logging_implementation():
    """Validar implementação de logging"""
    logger = get_logger("validation")
    
    logging_config = Path("logging_config.py")
    version_manager = Path("version_manager.py")
    
    issues = []
    
    if not logging_config.exists():
        issues.append("logging_config.py não foi criado")
    
    if version_manager.exists():
        with open(version_manager, 'r', encoding='utf-8') as f:
            content = f.read()
            if "from logging_config import" not in content:
                issues.append("version_manager.py não importa logging_config")
            if "print(" in content and "logger." not in content:
                issues.append("version_manager.py ainda usa print() em vez de logging")
    
    if issues:
        logger.error("Problemas de logging encontrados:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    else:
        logger.info("✅ Implementação de logging validada")
        return True

def validate_config_fixes():
    """Validar correções de configuração"""
    logger = get_logger("validation")
    
    config_manager = Path("config_manager.py")
    backup_config = Path("config/backup-config.txt")
    
    issues = []
    
    if not config_manager.exists():
        issues.append("config_manager.py não foi criado")
    
    if backup_config.exists():
        with open(backup_config, 'r', encoding='utf-8') as f:
            content = f.read()
            if "E:\\BACKUPS" in content:
                issues.append("backup-config.txt ainda contém caminhos hardcoded")
    
    if issues:
        logger.error("Problemas de configuração encontrados:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    else:
        logger.info("✅ Correções de configuração validadas")
        return True

def main():
    """Executar todas as validações"""
    logger = get_logger("validation")
    logger.info("🔍 Iniciando validação das correções...")
    
    validations = [
        ("Criptografia", validate_crypto_fixes),
        ("Dependências", validate_dependency_fixes),
        ("Tratamento de Exceções", validate_exception_handling),
        ("Refatoração PowerShell", validate_powershell_refactoring),
        ("Sistema de Logging", validate_logging_implementation),
        ("Configurações", validate_config_fixes)
    ]
    
    passed = 0
    total = len(validations)
    
    for name, validation_func in validations:
        logger.info(f"\n📋 Validando {name}...")
        if validation_func():
            passed += 1
    
    logger.info(f"\n📊 Resultado da Validação:")
    logger.info(f"✅ Passou: {passed}/{total}")
    logger.info(f"❌ Falhou: {total - passed}/{total}")
    
    if passed == total:
        logger.info("🎉 Todas as correções foram aplicadas com sucesso!")
        return 0
    else:
        logger.error("⚠️  Algumas correções precisam ser revisadas")
        return 1

if __name__ == "__main__":
    sys.exit(main())
