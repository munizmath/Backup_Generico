#!/usr/bin/env python3
"""
Gerenciador de Configuração
Sistema centralizado para gerenciar configurações do sistema de backup
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from logging_config import get_logger

class ConfigManager:
    """Gerenciador de configurações do sistema"""
    
    def __init__(self, config_dir: str = "config"):
        self.logger = get_logger("config_manager")
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Arquivos de configuração
        self.backup_config_file = self.config_dir / "backup-config.txt"
        self.retention_config_file = self.config_dir / "retention_profiles.json"
        self.gui_config_file = self.config_dir / "gui_config.json"
        self.dashboard_config_file = self.config_dir / "dashboard_config.json"
        
        # Configurações padrão
        self.default_config = self._get_default_config()
        
        # Carregar configurações
        self.config = self._load_all_configs()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Obter configurações padrão"""
        return {
            "backup": {
                "backup_dir": os.path.join(os.getcwd(), "backups"),
                "max_backups": 5,
                "exclude_patterns": [
                    "node_modules",
                    "build",
                    ".git",
                    "logs",
                    "*.log",
                    ".env",
                    "dist",
                    "coverage",
                    ".nyc_output",
                    "temp",
                    "tmp"
                ],
                "compression_level": 6,
                "verify_checksum": True,
                "verify_integrity": True
            },
            "retention": {
                "default_profile": "dev-fast",
                "profiles": {
                    "dev-fast": {
                        "name": "Desenvolvimento Rápido",
                        "retention": {
                            "minute": "48h",
                            "hour": "7d",
                            "day": "4w",
                            "week": "3m",
                            "month": "6m"
                        },
                        "compression": "fast",
                        "encryption": False,
                        "remote_sync": False
                    }
                }
            },
            "gui": {
                "project_dir": "",
                "backup_dir": "",
                "project_name": "",
                "backup_type": "completo",
                "hours": "24",
                "commit_hash": "HEAD"
            },
            "dashboard": {
                "backup_dir": os.path.join(os.getcwd(), "backups")
            }
        }
    
    def _load_all_configs(self) -> Dict[str, Any]:
        """Carregar todas as configurações"""
        config = self.default_config.copy()
        
        # Carregar configuração de backup
        if self.backup_config_file.exists():
            config["backup"].update(self._load_backup_config())
        
        # Carregar configuração de retenção
        if self.retention_config_file.exists():
            config["retention"] = self._load_json_config(self.retention_config_file)
        
        # Carregar configuração da GUI
        if self.gui_config_file.exists():
            config["gui"] = self._load_json_config(self.gui_config_file)
        
        # Carregar configuração do dashboard
        if self.dashboard_config_file.exists():
            config["dashboard"] = self._load_json_config(self.dashboard_config_file)
        
        return config
    
    def _load_backup_config(self) -> Dict[str, Any]:
        """Carregar configuração de backup do arquivo .txt"""
        config = {}
        
        try:
            with open(self.backup_config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Converter tipos
                            if key == "MAX_BACKUPS":
                                config["max_backups"] = int(value)
                            elif key == "COMPRESSION_LEVEL":
                                config["compression_level"] = int(value)
                            elif key == "VERIFY_CHECKSUM":
                                config["verify_checksum"] = value.lower() == "true"
                            elif key == "VERIFY_INTEGRITY":
                                config["verify_integrity"] = value.lower() == "true"
                            elif key == "BACKUP_DIR":
                                config["backup_dir"] = value
                            elif key.startswith("EXCLUDE_"):
                                if "exclude_patterns" not in config:
                                    config["exclude_patterns"] = []
                                if value.lower() == "true":
                                    pattern = key.replace("EXCLUDE_", "").lower()
                                    if pattern == "node_modules":
                                        config["exclude_patterns"].append("node_modules")
                                    elif pattern == "build":
                                        config["exclude_patterns"].append("build")
                                    elif pattern == "git":
                                        config["exclude_patterns"].append(".git")
                                    elif pattern == "logs":
                                        config["exclude_patterns"].append("logs")
                                    elif pattern == "env":
                                        config["exclude_patterns"].append(".env")
                                    elif pattern == "dist":
                                        config["exclude_patterns"].append("dist")
                                    elif pattern == "coverage":
                                        config["exclude_patterns"].append("coverage")
        
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração de backup: {e}")
        
        return config
    
    def _load_json_config(self, config_file: Path) -> Dict[str, Any]:
        """Carregar configuração JSON"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar {config_file}: {e}")
            return {}
    
    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """Obter valor de configuração"""
        if key is None:
            return self.config.get(section, default)
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Definir valor de configuração"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def save_config(self, section: str) -> bool:
        """Salvar configuração de uma seção"""
        try:
            if section == "backup":
                self._save_backup_config()
            elif section in ["retention", "gui", "dashboard"]:
                config_file = getattr(self, f"{section}_config_file")
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config[section], f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuração {section} salva com sucesso")
            return True
        
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração {section}: {e}")
            return False
    
    def _save_backup_config(self) -> None:
        """Salvar configuração de backup"""
        backup_config = self.config["backup"]
        
        with open(self.backup_config_file, 'w', encoding='utf-8') as f:
            f.write("# Configuração do Sistema de Backup Genérico\n")
            f.write("# Edite este arquivo para personalizar as configurações\n\n")
            
            f.write(f"# Diretório padrão para backups\n")
            f.write(f"BACKUP_DIR={backup_config['backup_dir']}\n\n")
            
            f.write(f"# Número de backups a manter\n")
            f.write(f"MAX_BACKUPS={backup_config['max_backups']}\n\n")
            
            f.write("# Exclusões padrão\n")
            exclude_patterns = backup_config.get('exclude_patterns', [])
            f.write(f"EXCLUDE_NODE_MODULES={'true' if 'node_modules' in exclude_patterns else 'false'}\n")
            f.write(f"EXCLUDE_BUILD={'true' if 'build' in exclude_patterns else 'false'}\n")
            f.write(f"EXCLUDE_GIT={'true' if '.git' in exclude_patterns else 'false'}\n")
            f.write(f"EXCLUDE_LOGS={'true' if 'logs' in exclude_patterns else 'false'}\n")
            f.write(f"EXCLUDE_ENV={'true' if '.env' in exclude_patterns else 'false'}\n")
            f.write(f"EXCLUDE_DIST={'true' if 'dist' in exclude_patterns else 'false'}\n")
            f.write(f"EXCLUDE_COVERAGE={'true' if 'coverage' in exclude_patterns else 'false'}\n\n")
            
            f.write("# Configurações de compactação\n")
            f.write(f"COMPRESSION_LEVEL={backup_config['compression_level']}\n\n")
            
            f.write("# Configurações de verificação\n")
            f.write(f"VERIFY_CHECKSUM={'true' if backup_config['verify_checksum'] else 'false'}\n")
            f.write(f"VERIFY_INTEGRITY={'true' if backup_config['verify_integrity'] else 'false'}\n")
    
    def get_backup_dir(self) -> str:
        """Obter diretório de backup"""
        backup_dir = self.get("backup", "backup_dir")
        if not backup_dir:
            backup_dir = os.path.join(os.getcwd(), "backups")
        
        # Expandir variáveis de ambiente
        backup_dir = os.path.expandvars(backup_dir)
        backup_dir = os.path.expanduser(backup_dir)
        
        return backup_dir
    
    def get_exclude_patterns(self) -> list:
        """Obter padrões de exclusão"""
        return self.get("backup", "exclude_patterns", [])
    
    def update_from_env(self) -> None:
        """Atualizar configurações a partir de variáveis de ambiente"""
        env_mappings = {
            "BACKUP_DIR": ("backup", "backup_dir"),
            "MAX_BACKUPS": ("backup", "max_backups"),
            "PROJECT_NAME": ("gui", "project_name"),
            "PROJECT_DIR": ("gui", "project_dir"),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Converter tipos
                if key == "max_backups":
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                elif key in ["verify_checksum", "verify_integrity"]:
                    value = value.lower() in ["true", "1", "yes"]
                
                self.set(section, key, value)
                self.logger.info(f"Configuração atualizada de {env_var}: {value}")

# Instância global do gerenciador de configuração
config_manager = ConfigManager()

def get_config(section: str, key: str = None, default: Any = None) -> Any:
    """Função de conveniência para obter configuração"""
    return config_manager.get(section, key, default)

def set_config(section: str, key: str, value: Any) -> None:
    """Função de conveniência para definir configuração"""
    config_manager.set(section, key, value)

def save_config(section: str) -> bool:
    """Função de conveniência para salvar configuração"""
    return config_manager.save_config(section)
