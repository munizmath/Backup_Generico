#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Backup Genérico - Interface Gráfica Unificada
Interface gráfica moderna com Dashboard integrado e controles de backup
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
import psutil
import time

class BackupGUIUnified:
    def __init__(self, root):
        self.root = root
        self.root.title("🔒 Sistema de Backup Genérico - Unificado")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Configurações
        self.config_file = "config/gui_config.json"
        
        # Variáveis de controle
        self.backup_process = None
        self.is_paused = False
        self.is_stopped = False
        self.backup_thread = None
        
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
        
        # Carregar configurações após UI estar pronta
        self.load_saved_config()
        
        # Iniciar monitoramento do sistema
        self.start_system_monitoring()
    
    def setup_ui(self):
        """Configurar a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔒 Sistema de Backup Genérico - Unificado", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Aba 1: Backup
        self.setup_backup_tab()
        
        # Aba 2: Dashboard
        self.setup_dashboard_tab()
        
        # Aba 3: Configurações
        self.setup_config_tab()
    
    def setup_backup_tab(self):
        """Configurar aba de backup"""
        backup_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(backup_frame, text="📦 Backup")
        
        # Configurar grid
        backup_frame.columnconfigure(1, weight=1)
        
        # Frame de configuração
        config_frame = ttk.LabelFrame(backup_frame, text="📁 Configurações do Projeto", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
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
        backup_options_frame = ttk.LabelFrame(backup_frame, text="⚙️ Opções de Backup", padding="10")
        backup_options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        backup_options_frame.columnconfigure(1, weight=1)
        
        # Tipo de backup
        ttk.Label(backup_options_frame, text="Tipo de Backup:").grid(row=0, column=0, sticky=tk.W, pady=2)
        backup_type_combo = ttk.Combobox(backup_options_frame, textvariable=self.backup_type, 
                                        values=["completo", "incremental", "git", "criptografado"], 
                                        state="readonly", width=47)
        backup_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        backup_type_combo.bind('<<ComboboxSelected>>', self.on_backup_type_change)
        
        # Opções específicas (inicialmente ocultas)
        self.options_frame = ttk.Frame(backup_options_frame)
        self.options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        self.options_frame.columnconfigure(1, weight=1)
        
        # Controles de backup
        controls_frame = ttk.LabelFrame(backup_frame, text="🎮 Controles", padding="10")
        controls_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botões de controle
        self.start_button = ttk.Button(controls_frame, text="▶️ Iniciar Backup", command=self.start_backup)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = ttk.Button(controls_frame, text="⏸️ Pausar", command=self.pause_backup, state="disabled")
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.stop_button = ttk.Button(controls_frame, text="⏹️ Parar", command=self.stop_backup, state="disabled")
        self.stop_button.grid(row=0, column=2, padx=5)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(controls_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Log de operações
        log_frame = ttk.LabelFrame(backup_frame, text="📋 Log de Operações", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status
        status_frame = ttk.Frame(backup_frame)
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0)
        self.status_label = ttk.Label(status_frame, text="Pronto")
        self.status_label.grid(row=0, column=1)
        
        # Configurar diretórios padrão
        self.backup_dir.set("E:/Backup")
    
    def setup_dashboard_tab(self):
        """Configurar aba de dashboard"""
        dashboard_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Configurar grid
        dashboard_frame.columnconfigure(0, weight=1)
        dashboard_frame.columnconfigure(1, weight=1)
        dashboard_frame.rowconfigure(1, weight=1)
        
        # Frame de estatísticas do sistema
        system_frame = ttk.LabelFrame(dashboard_frame, text="💻 Sistema", padding="10")
        system_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # CPU
        self.cpu_label = ttk.Label(system_frame, text="CPU: 0%")
        self.cpu_label.grid(row=0, column=0, padx=10)
        
        # RAM
        self.ram_label = ttk.Label(system_frame, text="RAM: 0%")
        self.ram_label.grid(row=0, column=1, padx=10)
        
        # Disco
        self.disk_label = ttk.Label(system_frame, text="Disco: 0%")
        self.disk_label.grid(row=0, column=2, padx=10)
        
        # Frame de backups
        backups_frame = ttk.LabelFrame(dashboard_frame, text="📦 Backups", padding="10")
        backups_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        backups_frame.columnconfigure(0, weight=1)
        backups_frame.rowconfigure(1, weight=1)
        
        # Controles de backup
        backup_controls = ttk.Frame(backups_frame)
        backup_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(backup_controls, text="Diretório:").grid(row=0, column=0, padx=(0, 5))
        self.dashboard_backup_dir = ttk.Entry(backup_controls, textvariable=self.backup_dir, width=40)
        self.dashboard_backup_dir.grid(row=0, column=1, padx=(0, 5))
        ttk.Button(backup_controls, text="🔄", command=self.refresh_backups).grid(row=0, column=2)
        
        # Lista de backups
        self.backups_tree = ttk.Treeview(backups_frame, columns=("Tipo", "Tamanho", "Data", "Status"), show="tree headings")
        self.backups_tree.heading("#0", text="Arquivo")
        self.backups_tree.heading("Tipo", text="Tipo")
        self.backups_tree.heading("Tamanho", text="Tamanho")
        self.backups_tree.heading("Data", text="Data")
        self.backups_tree.heading("Status", text="Status")
        
        scrollbar = ttk.Scrollbar(backups_frame, orient="vertical", command=self.backups_tree.yview)
        self.backups_tree.configure(yscrollcommand=scrollbar.set)
        
        self.backups_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Frame de log do dashboard
        log_frame = ttk.LabelFrame(dashboard_frame, text="📋 Log do Sistema", padding="10")
        log_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.dashboard_log = scrolledtext.ScrolledText(log_frame, height=15, width=50)
        self.dashboard_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def setup_config_tab(self):
        """Configurar aba de configurações"""
        config_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(config_frame, text="⚙️ Configurações")
        
        # Configurações do sistema
        system_config = ttk.LabelFrame(config_frame, text="🔧 Configurações do Sistema", padding="10")
        system_config.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Diretório de backup padrão
        ttk.Label(system_config, text="Diretório de Backup Padrão:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(system_config, textvariable=self.backup_dir, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Configurações de backup
        backup_config = ttk.LabelFrame(config_frame, text="📦 Configurações de Backup", padding="10")
        backup_config.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Máximo de backups
        self.max_backups = tk.StringVar(value="5")
        ttk.Label(backup_config, text="Máximo de Backups:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(backup_config, textvariable=self.max_backups, width=10).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Botões de ação
        actions_frame = ttk.Frame(config_frame)
        actions_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(actions_frame, text="💾 Salvar Configurações", command=self.save_config).grid(row=0, column=0, padx=5)
        ttk.Button(actions_frame, text="🔄 Carregar Configurações", command=self.load_config).grid(row=0, column=1, padx=5)
        ttk.Button(actions_frame, text="🧹 Limpar Backups Antigos", command=self.clean_old_backups).grid(row=0, column=2, padx=5)
    
    def start_system_monitoring(self):
        """Iniciar monitoramento do sistema"""
        def monitor():
            while True:
                try:
                    # CPU
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.cpu_label.config(text=f"CPU: {cpu_percent}%")
                    
                    # RAM
                    memory = psutil.virtual_memory()
                    self.ram_label.config(text=f"RAM: {memory.percent}%")
                    
                    # Disco
                    disk = psutil.disk_usage('/')
                    disk_percent = (disk.used / disk.total) * 100
                    self.disk_label.config(text=f"Disco: {disk_percent:.1f}%")
                    
                    # Atualizar log do dashboard
                    self.dashboard_log.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sistema: CPU {cpu_percent}%, RAM {memory.percent}%\n")
                    self.dashboard_log.see(tk.END)
                    
                    time.sleep(5)  # Atualizar a cada 5 segundos
                except:
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def start_backup(self):
        """Iniciar backup"""
        if not self.validate_inputs():
            return
        
        self.is_stopped = False
        self.is_paused = False
        
        # Atualizar botões
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.stop_button.config(state="normal")
        
        # Iniciar thread de backup
        self.backup_thread = threading.Thread(target=self.run_backup, daemon=True)
        self.backup_thread.start()
    
    def pause_backup(self):
        """Pausar backup"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="▶️ Retomar")
            self.log_message("⏸️ Backup pausado")
        else:
            self.pause_button.config(text="⏸️ Pausar")
            self.log_message("▶️ Backup retomado")
    
    def stop_backup(self):
        """Parar backup"""
        self.is_stopped = True
        self.is_paused = False
        
        # Atualizar botões
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        
        self.log_message("⏹️ Backup interrompido pelo usuário")
        self.update_status("Interrompido")
    
    def run_backup(self):
        """Executar backup em thread separada"""
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
            
            # Executar comando no diretório correto
            project_root = Path(__file__).parent.parent
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))
            
            if self.is_stopped:
                self.log_message("⏹️ Backup cancelado")
                return
            
            if result.returncode == 0:
                self.log_message("✅ Backup concluído com sucesso!")
                self.log_message(result.stdout)
                self.update_status("Concluído")
            else:
                self.log_message("❌ Erro no backup:")
                self.log_message(result.stderr)
                self.update_status("Erro")
            
        except Exception as e:
            self.log_message(f"❌ Erro: {str(e)}")
            self.update_status("Erro")
        finally:
            self.progress.stop()
            # Atualizar botões
            self.start_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")
            # Atualizar dashboard
            self.refresh_backups()
    
    def get_script_name(self, backup_type):
        """Obter nome do script baseado no tipo de backup"""
        # Usar diretório absoluto do projeto
        project_root = Path(__file__).parent.parent
        backend_path = project_root / "Backend"
        scripts = {
            "completo": str(backend_path / "backup-generic-template.bat"),
            "incremental": str(backend_path / "backup-incremental.bat"),
            "git": str(backend_path / "backup-git.bat"),
            "criptografado": str(backend_path / "backup-encrypted.bat")
        }
        return scripts.get(backup_type)
    
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
    
    def on_backup_type_change(self, event=None):
        """Atualizar opções baseadas no tipo de backup selecionado"""
        # Limpar frame de opções
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        backup_type = self.backup_type.get()
        
        if backup_type == "incremental":
            ttk.Label(self.options_frame, text="Horas (Incremental):").grid(row=0, column=0, sticky=tk.W, pady=2)
            ttk.Entry(self.options_frame, textvariable=self.hours, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        elif backup_type == "git":
            ttk.Label(self.options_frame, text="Commit Hash (Git):").grid(row=0, column=0, sticky=tk.W, pady=2)
            ttk.Entry(self.options_frame, textvariable=self.commit_hash, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        elif backup_type == "criptografado":
            ttk.Label(self.options_frame, text="Senha (Criptografado):").grid(row=0, column=0, sticky=tk.W, pady=2)
            ttk.Entry(self.options_frame, textvariable=self.password, show="*", width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
    
    def browse_project_dir(self):
        """Selecionar diretório do projeto"""
        directory = filedialog.askdirectory(title="Selecionar Diretório do Projeto")
        if directory:
            self.project_dir.set(directory)
    
    def browse_backup_dir(self):
        """Selecionar diretório de backup"""
        directory = filedialog.askdirectory(title="Selecionar Diretório de Backup")
        if directory:
            self.backup_dir.set(directory)
    
    def log_message(self, message):
        """Adicionar mensagem ao log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def update_status(self, status):
        """Atualizar status"""
        self.status_label.config(text=status)
    
    def refresh_backups(self):
        """Atualizar lista de backups"""
        try:
            # Limpar lista atual
            for item in self.backups_tree.get_children():
                self.backups_tree.delete(item)
            
            backup_dir = Path(self.backup_dir.get())
            if not backup_dir.exists():
                self.log_message("❌ Diretório de backup não existe")
                return
            
            # Buscar arquivos de backup
            backup_files = []
            for pattern in ["*.zip", "*.enc", "*.tar.gz"]:
                backup_files.extend(backup_dir.glob(pattern))
            
            if not backup_files:
                self.log_message("📋 Nenhum backup encontrado")
                return
            
            # Ordenar por data de modificação
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Adicionar à lista
            for backup_file in backup_files:
                stat = backup_file.stat()
                size = self.format_size(stat.st_size)
                date = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M")
                
                # Determinar tipo
                if "_incremental_" in backup_file.name:
                    backup_type = "Incremental"
                elif "_git_" in backup_file.name:
                    backup_type = "Git"
                elif "_encrypted_" in backup_file.name:
                    backup_type = "Criptografado"
                else:
                    backup_type = "Completo"
                
                # Status (verificar integridade básica)
                status = "✅ OK" if stat.st_size > 0 else "❌ Vazio"
                
                # Adicionar à árvore
                self.backups_tree.insert("", "end", text=backup_file.name, 
                                       values=(backup_type, size, date, status))
            
            self.log_message(f"📊 {len(backup_files)} backups encontrados")
            
        except Exception as e:
            self.log_message(f"❌ Erro ao atualizar backups: {str(e)}")
    
    def format_size(self, size_bytes):
        """Formatar tamanho em bytes para formato legível"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def save_config(self):
        """Salvar configurações"""
        config = {
            "project_dir": self.project_dir.get(),
            "backup_dir": self.backup_dir.get(),
            "project_name": self.project_name.get(),
            "backup_type": self.backup_type.get(),
            "max_backups": self.max_backups.get()
        }
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.log_message("✅ Configurações salvas")
        except Exception as e:
            self.log_message(f"❌ Erro ao salvar configurações: {str(e)}")
    
    def load_config(self):
        """Carregar configurações"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                self.project_dir.set(config.get("project_dir", ""))
                self.backup_dir.set(config.get("backup_dir", "E:/Backup"))
                self.project_name.set(config.get("project_name", ""))
                self.backup_type.set(config.get("backup_type", "completo"))
                self.max_backups.set(config.get("max_backups", "5"))
                
                self.log_message("✅ Configurações carregadas")
        except Exception as e:
            self.log_message(f"❌ Erro ao carregar configurações: {str(e)}")
    
    def load_saved_config(self):
        """Carregar configurações salvas"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Aplicar configurações carregadas
                if 'project_dir' in config:
                    self.project_dir.set(config['project_dir'])
                if 'backup_dir' in config:
                    self.backup_dir.set(config['backup_dir'])
                if 'project_name' in config:
                    self.project_name.set(config['project_name'])
                if 'backup_type' in config:
                    self.backup_type.set(config['backup_type'])
                if 'hours' in config:
                    self.hours.set(config['hours'])
                if 'commit_hash' in config:
                    self.commit_hash.set(config['commit_hash'])
                
                self.log_message("✅ Configurações carregadas")
        except Exception as e:
            self.log_message(f"❌ Erro ao carregar configurações: {str(e)}")
    
    def clean_old_backups(self):
        """Limpar backups antigos"""
        try:
            backup_dir = Path(self.backup_dir.get())
            if not backup_dir.exists():
                self.log_message("❌ Diretório de backup não existe")
                return
            
            max_backups = int(self.max_backups.get())
            backup_files = list(backup_dir.glob("*.zip")) + list(backup_dir.glob("*.enc"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            if len(backup_files) > max_backups:
                files_to_remove = backup_files[max_backups:]
                for file in files_to_remove:
                    file.unlink()
                    self.log_message(f"🗑️ Removido: {file.name}")
                
                self.log_message(f"✅ {len(files_to_remove)} backups antigos removidos")
                self.refresh_backups()
            else:
                self.log_message("📋 Nenhum backup antigo para remover")
                
        except Exception as e:
            self.log_message(f"❌ Erro ao limpar backups: {str(e)}")

def main():
    root = tk.Tk()
    app = BackupGUIUnified(root)
    root.mainloop()

if __name__ == "__main__":
    main()
