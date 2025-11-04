#!/usr/bin/env python3
"""
Sistema de Versionamento para Backups
Gerencia versoes, changelog e controle de deploys
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib
import subprocess
from logging_config import get_logger, log_function_call

class VersionManager:
    def __init__(self, project_dir: str):
        self.logger = get_logger("version_manager")
        self.project_dir = Path(project_dir)
        self.version_file = self.project_dir / "VERSION.json"
        self.changelog_file = self.project_dir / "CHANGELOG.md"
        self.backup_versions_dir = self.project_dir / "backup_versions"
        
        # Criar diretório de versões se não existir
        try:
            self.backup_versions_dir.mkdir(exist_ok=True)
            self.logger.info(f"Diretório de versões criado: {self.backup_versions_dir}")
        except OSError as e:
            self.logger.error(f"Erro ao criar diretório de versões: {e}")
            # Usar diretório temporário como fallback
            self.backup_versions_dir = Path("backup_versions")
            self.backup_versions_dir.mkdir(exist_ok=True)
            self.logger.warning(f"Usando diretório temporário: {self.backup_versions_dir}")
        
        # Carregar versão atual
        self.current_version = self.load_version()
    
    def load_version(self) -> Dict:
        """Carregar versão atual"""
        if self.version_file.exists():
            with open(self.version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Versão inicial
        return {
            "version": "1.0.0",
            "build": 1,
            "created": datetime.now().isoformat(),
            "last_backup": None,
            "backup_count": 0,
            "git_commit": None,
            "git_branch": None,
            "changelog": []
        }
    
    def save_version(self):
        """Salvar versão atual"""
        with open(self.version_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_version, f, indent=2, ensure_ascii=False)
    
    def get_git_info(self) -> Dict:
        """Obter informações do Git"""
        try:
            # Commit atual
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  cwd=self.project_dir, capture_output=True, text=True)
            commit = result.stdout.strip()[:8] if result.returncode == 0 else None
            
            # Branch atual
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  cwd=self.project_dir, capture_output=True, text=True)
            branch = result.stdout.strip() if result.returncode == 0 else None
            
            # Status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  cwd=self.project_dir, capture_output=True, text=True)
            dirty = len(result.stdout.strip()) > 0 if result.returncode == 0 else False
            
            return {
                "commit": commit,
                "branch": branch,
                "dirty": dirty
            }
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            self.logger.warning(f"Erro ao obter informações do Git: {e}")
            return {"commit": None, "branch": None, "dirty": False}
    
    def create_backup_version(self, backup_name: str, backup_type: str, 
                            file_count: int, total_size: int) -> str:
        """Criar nova versão de backup"""
        # Incrementar build
        self.current_version["build"] += 1
        self.current_version["backup_count"] += 1
        self.current_version["last_backup"] = datetime.now().isoformat()
        
        # Obter informações do Git
        git_info = self.get_git_info()
        self.current_version["git_commit"] = git_info["commit"]
        self.current_version["git_branch"] = git_info["branch"]
        
        # Criar ID da versão
        version_id = f"v{self.current_version['version']}-build{self.current_version['build']}"
        
        # Criar metadados da versão
        version_data = {
            "version_id": version_id,
            "backup_name": backup_name,
            "backup_type": backup_type,
            "file_count": file_count,
            "total_size": total_size,
            "created": datetime.now().isoformat(),
            "git_commit": git_info["commit"],
            "git_branch": git_info["branch"],
            "git_dirty": git_info["dirty"],
            "project_path": str(self.project_dir),
            "backup_path": None  # Será preenchido pelo sistema de backup
        }
        
        # Salvar metadados da versão
        version_file = self.backup_versions_dir / f"{version_id}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2, ensure_ascii=False)
        
        # Atualizar versão principal
        self.save_version()
        
        return version_id
    
    def add_changelog_entry(self, version: str, changes: List[str], 
                          change_type: str = "patch"):
        """Adicionar entrada no changelog"""
        entry = {
            "version": version,
            "date": datetime.now().isoformat(),
            "type": change_type,  # major, minor, patch
            "changes": changes
        }
        
        self.current_version["changelog"].append(entry)
        self.save_version()
        
        # Atualizar CHANGELOG.md
        self.update_changelog_md()
    
    def update_changelog_md(self):
        """Atualizar arquivo CHANGELOG.md"""
        changelog_content = ["# Changelog", "", "Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.", ""]
        
        # Agrupar por versão
        versions = {}
        for entry in reversed(self.current_version["changelog"]):
            version = entry["version"]
            if version not in versions:
                versions[version] = []
            versions[version].append(entry)
        
        # Gerar conteúdo
        for version, entries in versions.items():
            changelog_content.append(f"## [{version}] - {entries[0]['date'][:10]}")
            changelog_content.append("")
            
            for entry in entries:
                changelog_content.append(f"### {entry['type'].title()}")
                for change in entry["changes"]:
                    changelog_content.append(f"- {change}")
                changelog_content.append("")
        
        # Salvar arquivo
        with open(self.changelog_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(changelog_content))
    
    def get_version_info(self) -> Dict:
        """Obter informações da versão atual"""
        return {
            "version": self.current_version["version"],
            "build": self.current_version["build"],
            "backup_count": self.current_version["backup_count"],
            "last_backup": self.current_version["last_backup"],
            "git_commit": self.current_version["git_commit"],
            "git_branch": self.current_version["git_branch"]
        }
    
    def list_backup_versions(self) -> List[Dict]:
        """Listar todas as versões de backup"""
        versions = []
        for version_file in self.backup_versions_dir.glob("*.json"):
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
            versions.append(version_data)
        
        # Ordenar por data de criação
        versions.sort(key=lambda x: x["created"], reverse=True)
        return versions
    
    def get_backup_version(self, version_id: str) -> Optional[Dict]:
        """Obter informações de uma versão específica"""
        version_file = self.backup_versions_dir / f"{version_id}.json"
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def create_release_tag(self, version: str, message: str = ""):
        """Criar tag de release no Git"""
        try:
            # Criar tag
            tag_name = f"backup-{version}"
            subprocess.run(['git', 'tag', '-a', tag_name, '-m', message or f"Backup version {version}"], 
                         cwd=self.project_dir, check=True)
            
            # Push da tag (opcional)
            # subprocess.run(['git', 'push', 'origin', tag_name], cwd=self.project_dir)
            
            self.logger.info(f"Tag de release criada: {tag_name}")
            return tag_name
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao criar tag: {e}")
            return None
    
    def generate_backup_report(self) -> str:
        """Gerar relatório de backup"""
        versions = self.list_backup_versions()
        
        report = [
            "# Relatório de Backups",
            f"Gerado em: {datetime.now().isoformat()}",
            "",
            f"**Versão Atual:** {self.current_version['version']}",
            f"**Build:** {self.current_version['build']}",
            f"**Total de Backups:** {self.current_version['backup_count']}",
            f"**Último Backup:** {self.current_version['last_backup']}",
            "",
            "## Histórico de Backups",
            ""
        ]
        
        for version in versions[:10]:  # Últimos 10 backups
            report.extend([
                f"### {version['version_id']}",
                f"- **Data:** {version['created']}",
                f"- **Tipo:** {version['backup_type']}",
                f"- **Arquivos:** {version['file_count']:,}",
                f"- **Tamanho:** {version['total_size']:,} bytes",
                f"- **Git Commit:** {version['git_commit']}",
                f"- **Git Branch:** {version['git_branch']}",
                ""
            ])
        
        return '\n'.join(report)

def main():
    import sys
    
    if len(sys.argv) < 3:
        logger = get_logger("version_manager")
        logger.error("Argumentos insuficientes")
        print("Uso: python version_manager.py <comando> <project_dir> [args...]")
        print("Comandos:")
        print("  create-backup <backup_name> <backup_type> <file_count> <total_size>")
        print("  add-changelog <version> <change1,change2,...> [type]")
        print("  list-versions")
        print("  get-version")
        print("  create-tag <version> [message]")
        print("  generate-report")
        sys.exit(1)
    
    command = sys.argv[1]
    project_dir = sys.argv[2]
    
    version_manager = VersionManager(project_dir)
    
    if command == "create-backup":
        if len(sys.argv) < 7:
            print("Uso: create-backup <backup_name> <backup_type> <file_count> <total_size>")
            sys.exit(1)
        
        backup_name = sys.argv[3]
        backup_type = sys.argv[4]
        file_count = int(sys.argv[5])
        total_size = int(sys.argv[6])
        
        version_id = version_manager.create_backup_version(backup_name, backup_type, file_count, total_size)
        print(f"Versão de backup criada: {version_id}")
    
    elif command == "add-changelog":
        if len(sys.argv) < 5:
            print("Uso: add-changelog <version> <change1,change2,...> [type]")
            sys.exit(1)
        
        version = sys.argv[3]
        changes = sys.argv[4].split(',')
        change_type = sys.argv[5] if len(sys.argv) > 5 else "patch"
        
        version_manager.add_changelog_entry(version, changes, change_type)
        print(f"Changelog atualizado para versão {version}")
    
    elif command == "list-versions":
        versions = version_manager.list_backup_versions()
        print(f"Encontradas {len(versions)} versões de backup:")
        for version in versions:
            print(f"  {version['version_id']}: {version['backup_name']} ({version['created']})")
    
    elif command == "get-version":
        info = version_manager.get_version_info()
        print(f"Versão: {info['version']}")
        print(f"Build: {info['build']}")
        print(f"Backups: {info['backup_count']}")
        print(f"Último backup: {info['last_backup']}")
        print(f"Git commit: {info['git_commit']}")
        print(f"Git branch: {info['git_branch']}")
    
    elif command == "create-tag":
        if len(sys.argv) < 4:
            print("Uso: create-tag <version> [message]")
            sys.exit(1)
        
        version = sys.argv[3]
        message = sys.argv[4] if len(sys.argv) > 4 else ""
        
        tag = version_manager.create_release_tag(version, message)
        if tag:
            print(f"Tag criada: {tag}")
    
    elif command == "generate-report":
        report = version_manager.generate_backup_report()
        report_file = Path(project_dir) / "BACKUP_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Relatório gerado: {report_file}")
    
    else:
        print(f"Comando não reconhecido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
