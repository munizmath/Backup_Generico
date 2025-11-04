#!/usr/bin/env python3
"""
Sistema de Captura de Metadados Contextuais
Captura informações do ambiente de desenvolvimento, Git, e contexto do editor
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import psutil
import platform

class MetadataCapture:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.metadata = {}
    
    def capture_git_info(self):
        """Capturar informações do Git"""
        try:
            # Branch atual
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  cwd=self.project_path, capture_output=True, text=True)
            if result.returncode == 0:
                self.metadata['git_branch'] = result.stdout.strip()
            
            # Commit atual
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  cwd=self.project_path, capture_output=True, text=True)
            if result.returncode == 0:
                self.metadata['git_commit'] = result.stdout.strip()[:8]
            
            # Status do repositório
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  cwd=self.project_path, capture_output=True, text=True)
            if result.returncode == 0:
                self.metadata['git_dirty'] = len(result.stdout.strip()) > 0
                self.metadata['git_changes'] = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Último commit
            result = subprocess.run(['git', 'log', '-1', '--format=%H|%an|%ae|%s|%ci'], 
                                  cwd=self.project_path, capture_output=True, text=True)
            if result.returncode == 0:
                parts = result.stdout.strip().split('|')
                if len(parts) >= 5:
                    self.metadata['last_commit'] = {
                        'hash': parts[0][:8],
                        'author': parts[1],
                        'email': parts[2],
                        'message': parts[3],
                        'date': parts[4]
                    }
            
        except Exception as e:
            self.metadata['git_error'] = str(e)
    
    def capture_workspace_info(self):
        """Capturar informações do workspace"""
        self.metadata['workspace'] = {
            'path': str(self.project_path.absolute()),
            'name': self.project_path.name,
            'parent': str(self.project_path.parent.name) if self.project_path.parent.name else None
        }
        
        # Detectar tipo de projeto
        project_type = self.detect_project_type()
        self.metadata['project_type'] = project_type
        
        # Arquivos de configuração encontrados
        config_files = []
        for config_file in ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle']:
            if (self.project_path / config_file).exists():
                config_files.append(config_file)
        self.metadata['config_files'] = config_files
    
    def detect_project_type(self):
        """Detectar tipo de projeto baseado nos arquivos"""
        if (self.project_path / 'package.json').exists():
            return 'nodejs'
        elif (self.project_path / 'requirements.txt').exists() or (self.project_path / 'pyproject.toml').exists():
            return 'python'
        elif (self.project_path / 'Cargo.toml').exists():
            return 'rust'
        elif (self.project_path / 'go.mod').exists():
            return 'go'
        elif (self.project_path / 'pom.xml').exists():
            return 'java'
        elif (self.project_path / 'build.gradle').exists():
            return 'android'
        elif (self.project_path / 'Dockerfile').exists():
            return 'docker'
        else:
            return 'unknown'
    
    def capture_editor_info(self):
        """Capturar informações do editor/IDE"""
        # Detectar editor ativo
        editor_info = {
            'active_editors': [],
            'cursor_session': None,
            'vscode_workspace': None
        }
        
        # Verificar se Cursor está ativo
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'cursor' in proc.info['name'].lower():
                    editor_info['active_editors'].append('cursor')
                    # Tentar capturar sessão do Cursor
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if '--session' in cmdline:
                        # Extrair session ID se disponível
                        editor_info['cursor_session'] = 'active'
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Verificar VS Code
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'code' in proc.info['name'].lower():
                    editor_info['active_editors'].append('vscode')
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Verificar se há workspace do VS Code
        vscode_workspace = self.project_path / '.vscode'
        if vscode_workspace.exists():
            editor_info['vscode_workspace'] = True
        
        self.metadata['editor'] = editor_info
    
    def capture_system_info(self):
        """Capturar informações do sistema"""
        self.metadata['system'] = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'python_version': sys.version,
            'timestamp': datetime.now().isoformat(),
            'timezone': str(datetime.now().astimezone().tzinfo),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_usage': psutil.disk_usage(str(self.project_path)).percent
        }
    
    def capture_file_stats(self):
        """Capturar estatísticas dos arquivos do projeto"""
        file_stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'largest_files': [],
            'recent_files': []
        }
        
        try:
            for file_path in self.project_path.rglob('*'):
                if file_path.is_file():
                    file_stats['total_files'] += 1
                    file_size = file_path.stat().st_size
                    file_stats['total_size'] += file_size
                    
                    # Contar por tipo
                    ext = file_path.suffix.lower()
                    file_stats['file_types'][ext] = file_stats['file_types'].get(ext, 0) + 1
                    
                    # Arquivos maiores
                    file_stats['largest_files'].append((str(file_path), file_size))
                    
                    # Arquivos recentes (últimas 24h)
                    mtime = file_path.stat().st_mtime
                    if mtime > (datetime.now().timestamp() - 86400):
                        file_stats['recent_files'].append((str(file_path), mtime))
            
            # Ordenar e limitar
            file_stats['largest_files'].sort(key=lambda x: x[1], reverse=True)
            file_stats['largest_files'] = file_stats['largest_files'][:10]
            
            file_stats['recent_files'].sort(key=lambda x: x[1], reverse=True)
            file_stats['recent_files'] = file_stats['recent_files'][:20]
            
        except Exception as e:
            file_stats['error'] = str(e)
        
        self.metadata['file_stats'] = file_stats
    
    def capture_all(self):
        """Capturar todos os metadados"""
        self.capture_git_info()
        self.capture_workspace_info()
        self.capture_editor_info()
        self.capture_system_info()
        self.capture_file_stats()
        
        return self.metadata
    
    def save_metadata(self, output_path):
        """Salvar metadados em arquivo JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) != 3:
        print("Uso: python metadata_capture.py <project_path> <output_file>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_file = sys.argv[2]
    
    capture = MetadataCapture(project_path)
    metadata = capture.capture_all()
    capture.save_metadata(output_file)
    
    print(f"Metadados capturados e salvos em: {output_file}")
    print(f"Total de arquivos: {metadata.get('file_stats', {}).get('total_files', 0)}")
    print(f"Tamanho total: {metadata.get('file_stats', {}).get('total_size', 0)} bytes")

if __name__ == "__main__":
    main()
