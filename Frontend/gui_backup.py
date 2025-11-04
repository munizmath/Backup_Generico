#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Backup Genérico - Interface Gráfica
Interface gráfica moderna para o sistema de backup genérico
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import os
import threading
import json
import datetime
from pathlib import Path
import webbrowser

class BackupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔒 Sistema de Backup Genérico")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configurações
        self.config_file = "config/gui_config.json"
        self.load_config()
        
        # Variáveis
        self.project_dir = tk.StringVar()
        self.backup_dir = tk.StringVar()
        self.project_name = tk.StringVar()
        self.backup_type = tk.StringVar(value="completo")
        self.hours = tk.StringVar(value="24")
        self.commit_hash = tk.StringVar(value="HEAD")
        self.password = tk.StringVar()
        
        # Configurar interface
        self.setup_ui()
        
        # Carregar configurações salvas
        self.load_saved_config()
    
    def setup_ui(self):
        """Configurar a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔒 Sistema de Backup Genérico", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de configuração
        config_frame = ttk.LabelFrame(main_frame, text="📁 Configurações do Projeto", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Diretório do projeto
        ttk.Label(config_frame, text="Diretório do Projeto:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(config_frame, textvariable=self.project_dir, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(config_frame, text="📁", command=self.browse_project_dir, width=3).grid(row=0, column=2, pady=2)
        
        # Diretório de backup
        ttk.Label(config_frame, text="Diretório de Backup:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(config_frame, textvariable=self.backup_dir, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(config_frame, text="📁", command=self.browse_backup_dir, width=3).grid(row=1, column=2, pady=2)
        
        # Nome do projeto
        ttk.Label(config_frame, text="Nome do Projeto:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(config_frame, textvariable=self.project_name, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        
        # Frame de opções de backup
        backup_frame = ttk.LabelFrame(main_frame, text="⚙️ Opções de Backup", padding="10")
        backup_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        backup_frame.columnconfigure(1, weight=1)
        
        # Tipo de backup
        ttk.Label(backup_frame, text="Tipo de Backup:").grid(row=0, column=0, sticky=tk.W, pady=2)
        backup_type_combo = ttk.Combobox(backup_frame, textvariable=self.backup_type, 
                                        values=["completo", "incremental", "git", "criptografado"], 
                                        state="readonly", width=47)
        backup_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        backup_type_combo.bind('<<ComboboxSelected>>', self.on_backup_type_change)
        
        # Opções específicas (inicialmente ocultas)
        self.options_frame = ttk.Frame(backup_frame)
        self.options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        self.options_frame.columnconfigure(1, weight=1)
        
        # Horas para backup incremental
        self.hours_label = ttk.Label(self.options_frame, text="Horas (Incremental):")
        self.hours_entry = ttk.Entry(self.options_frame, textvariable=self.hours, width=20)
        
        # Commit hash para backup Git
        self.commit_label = ttk.Label(self.options_frame, text="Commit Hash (Git):")
        self.commit_entry = ttk.Entry(self.options_frame, textvariable=self.commit_hash, width=20)
        
        # Senha para backup criptografado
        self.password_label = ttk.Label(self.options_frame, text="Senha (Criptografado):")
        self.password_entry = ttk.Entry(self.options_frame, textvariable=self.password, show="*", width=20)
        
        # Frame de botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # Botões principais
        ttk.Button(buttons_frame, text="📦 Fazer Backup", command=self.start_backup, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🔄 Restaurar", command=self.restore_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="📊 Listar Backups", command=self.list_backups).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🧹 Limpar Antigos", command=self.clean_old_backups).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="⚙️ Configurações", command=self.open_config).pack(side=tk.LEFT, padx=5)
        
        # Frame de log
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log de Atividades", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Área de log
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame de status
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Status
        self.status_label = ttk.Label(status_frame, text="Pronto")
        self.status_label.grid(row=0, column=1)
        
        # Configurar diretórios padrão
        # Usar configuração do config_manager ou diretório padrão
        try:
            from config_manager import get_config
            backup_dir_str = get_config("backup", "backup_dir")
            if backup_dir_str:
                backup_dir = Path(backup_dir_str)
            else:
                backup_dir = Path(os.path.join(os.getcwd(), "backups"))
        except ImportError:
            # Fallback se config_manager não estiver disponível
            backup_dir = Path(os.path.join(os.path.expanduser('~'), "backups"))
        
        # Criar diretório de backup se não existir
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.backup_dir.set(str(backup_dir))
    
    def on_backup_type_change(self, event=None):
        """Atualizar opções baseadas no tipo de backup selecionado"""
        # Limpar frame de opções
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        backup_type = self.backup_type.get()
        
        if backup_type == "incremental":
            self.hours_label.grid(row=0, column=0, sticky=tk.W, pady=2)
            self.hours_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        elif backup_type == "git":
            self.commit_label.grid(row=0, column=0, sticky=tk.W, pady=2)
            self.commit_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        elif backup_type == "criptografado":
            self.password_label.grid(row=0, column=0, sticky=tk.W, pady=2)
            self.password_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
    
    def browse_project_dir(self):
        """Abrir diálogo para selecionar diretório do projeto"""
        directory = filedialog.askdirectory(title="Selecionar Diretório do Projeto")
        if directory:
            self.project_dir.set(directory)
            # Auto-preencher nome do projeto baseado no diretório
            if not self.project_name.get():
                self.project_name.set(Path(directory).name)
    
    def browse_backup_dir(self):
        """Abrir diálogo para selecionar diretório de backup"""
        directory = filedialog.askdirectory(title="Selecionar Diretório de Backup")
        if directory:
            self.backup_dir.set(directory)
    
    def log_message(self, message):
        """Adicionar mensagem ao log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Atualizar status"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def start_backup(self):
        """Iniciar processo de backup"""
        if not self.validate_inputs():
            return
        
        # Executar backup em thread separada
        thread = threading.Thread(target=self.run_backup)
        thread.daemon = True
        thread.start()
    
    def validate_inputs(self):
        """Validar entradas do usuário"""
        if not self.project_dir.get():
            messagebox.showerror("Erro", "Selecione o diretório do projeto")
            return False
        
        if not self.backup_dir.get():
            messagebox.showerror("Erro", "Selecione o diretório de backup")
            return False
        
        if not self.project_name.get():
            messagebox.showerror("Erro", "Digite o nome do projeto")
            return False
        
        if not os.path.exists(self.project_dir.get()):
            messagebox.showerror("Erro", "Diretório do projeto não existe")
            return False
        
        backup_type = self.backup_type.get()
        if backup_type == "incremental" and not self.hours.get().isdigit():
            messagebox.showerror("Erro", "Horas deve ser um número")
            return False
        
        if backup_type == "criptografado" and not self.password.get():
            messagebox.showerror("Erro", "Digite a senha para backup criptografado")
            return False
        
        return True
    
    def run_backup(self):
        """Executar backup"""
        try:
            self.progress.start()
            self.update_status("Executando backup...")
            
            backup_type = self.backup_type.get()
            script_name = self.get_script_name(backup_type)
            
            if not script_name:
                self.log_message("❌ Tipo de backup não suportado")
                return
            
            # Construir comando
            cmd = [script_name, self.project_dir.get(), self.backup_dir.get(), self.project_name.get()]
            
            if backup_type == "incremental":
                cmd.append(self.hours.get())
            elif backup_type == "git":
                cmd.append(self.commit_hash.get())
            elif backup_type == "criptografado":
                cmd.append(self.password.get())
            
            self.log_message(f"🚀 Iniciando backup {backup_type}...")
            self.log_message(f"📁 Projeto: {self.project_dir.get()}")
            self.log_message(f"📁 Backup: {self.backup_dir.get()}")
            self.log_message(f"📦 Nome: {self.project_name.get()}")
            self.log_message(f"🔧 Script: {script_name}")
            self.log_message(f"🔧 Existe: {os.path.exists(script_name)}")
            self.log_message(f"🔧 Comando: {' '.join(cmd)}")
            
            # Executar comando
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                self.log_message("✅ Backup concluído com sucesso!")
                self.log_message(result.stdout)
                messagebox.showinfo("Sucesso", "Backup concluído com sucesso!")
            else:
                self.log_message("❌ Erro no backup:")
                self.log_message(result.stderr)
                messagebox.showerror("Erro", "Falha no backup. Verifique o log.")
            
        except Exception as e:
            self.log_message(f"❌ Erro: {str(e)}")
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
        finally:
            self.progress.stop()
            self.update_status("Pronto")
    
    def get_script_name(self, backup_type):
        """Obter nome do script baseado no tipo de backup"""
        # Caminho para a pasta Backend
        backend_path = Path(__file__).parent.parent / "Backend"
        scripts = {
            "completo": str(backend_path / "backup-generic-template.bat"),
            "incremental": str(backend_path / "backup-incremental.bat"),
            "git": str(backend_path / "backup-git.bat"),
            "criptografado": str(backend_path / "backup-encrypted.bat")
        }
        return scripts.get(backup_type)
    
    def restore_backup(self):
        """Abrir diálogo de restauração"""
        # Implementar diálogo de restauração
        messagebox.showinfo("Info", "Funcionalidade de restauração será implementada")
    
    def list_backups(self):
        """Listar backups disponíveis"""
        try:
            backup_path = Path(self.backup_dir.get())
            if not backup_path.exists():
                self.log_message("❌ Diretório de backup não existe")
                return
            
            backups = list(backup_path.glob("*.zip")) + list(backup_path.glob("*.enc"))
            if not backups:
                self.log_message("📋 Nenhum backup encontrado")
                return
            
            self.log_message(f"📋 Encontrados {len(backups)} backups:")
            for backup in sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True):
                size = backup.stat().st_size
                size_str = self.format_size(size)
                self.log_message(f"  📦 {backup.name} ({size_str})")
                
        except Exception as e:
            self.log_message(f"❌ Erro ao listar backups: {str(e)}")
    
    def clean_old_backups(self):
        """Limpar backups antigos"""
        try:
            # Implementar limpeza de backups antigos
            self.log_message("🧹 Limpeza de backups antigos será implementada")
        except Exception as e:
            self.log_message(f"❌ Erro na limpeza: {str(e)}")
    
    def open_config(self):
        """Abrir configurações"""
        try:
            config_path = Path("config/backup-config.txt")
            if config_path.exists():
                os.startfile(str(config_path))
            else:
                messagebox.showinfo("Info", "Arquivo de configuração não encontrado")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir configurações: {str(e)}")
    
    def format_size(self, size_bytes):
        """Formatar tamanho em bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def load_config(self):
        """Carregar configurações"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config
        except Exception as e:
            self.log_message(f"❌ Erro ao carregar configurações: {str(e)}")
        return {}
    
    def save_config(self):
        """Salvar configurações"""
        try:
            config = {
                "project_dir": self.project_dir.get(),
                "backup_dir": self.backup_dir.get(),
                "project_name": self.project_name.get(),
                "backup_type": self.backup_type.get(),
                "hours": self.hours.get(),
                "commit_hash": self.commit_hash.get()
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.log_message(f"❌ Erro ao salvar configurações: {str(e)}")
    
    def load_saved_config(self):
        """Carregar configurações salvas"""
        config = self.load_config()
        if config:
            self.project_dir.set(config.get("project_dir", ""))
            self.backup_dir.set(config.get("backup_dir", ""))
            self.project_name.set(config.get("project_name", ""))
            self.backup_type.set(config.get("backup_type", "completo"))
            self.hours.set(config.get("hours", "24"))
            self.commit_hash.set(config.get("commit_hash", "HEAD"))
    
    def on_closing(self):
        """Salvar configurações ao fechar"""
        self.save_config()
        self.root.destroy()

def main():
    """Função principal"""
    root = tk.Tk()
    app = BackupGUI(root)
    
    # Configurar fechamento
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Iniciar aplicação
    root.mainloop()

if __name__ == "__main__":
    main()

