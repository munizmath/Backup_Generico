#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard de Monitoramento - Sistema de Backup Genérico
Dashboard avançado para monitorar e gerenciar backups
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import json
import datetime
from pathlib import Path
import threading
import psutil
import webbrowser

class BackupDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Dashboard de Monitoramento - Sistema de Backup")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Configurações
        self.config_file = "config/dashboard_config.json"
        self.load_config()
        
        # Dados
        self.backups_data = []
        self.system_info = {}
        
        # Configurar interface
        self.setup_ui()
        
        # Iniciar monitoramento
        self.start_monitoring()
    
    def setup_ui(self):
        """Configurar a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="📊 Dashboard de Monitoramento", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Frame de estatísticas do sistema
        system_frame = ttk.LabelFrame(main_frame, text="💻 Informações do Sistema", padding="10")
        system_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        system_frame.columnconfigure(1, weight=1)
        
        # CPU
        ttk.Label(system_frame, text="CPU:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.cpu_label = ttk.Label(system_frame, text="0%")
        self.cpu_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Memória
        ttk.Label(system_frame, text="Memória:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.memory_label = ttk.Label(system_frame, text="0%")
        self.memory_label.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Disco
        ttk.Label(system_frame, text="Disco:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.disk_label = ttk.Label(system_frame, text="0%")
        self.disk_label.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Espaço em disco
        ttk.Label(system_frame, text="Espaço Livre:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.free_space_label = ttk.Label(system_frame, text="0 GB")
        self.free_space_label.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Frame de backups
        backups_frame = ttk.LabelFrame(main_frame, text="📦 Gerenciamento de Backups", padding="10")
        backups_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        backups_frame.columnconfigure(0, weight=1)
        backups_frame.rowconfigure(1, weight=1)
        
        # Controles de backup
        controls_frame = ttk.Frame(backups_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        controls_frame.columnconfigure(0, weight=1)
        
        # Diretório de backup
        ttk.Label(controls_frame, text="Diretório de Backup:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.backup_dir_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.backup_dir_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(controls_frame, text="📁", command=self.browse_backup_dir, width=3).grid(row=0, column=2, pady=2)
        
        # Botões
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="🔄 Atualizar", command=self.refresh_backups).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="📊 Estatísticas", command=self.show_statistics).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🧹 Limpar Antigos", command=self.clean_old_backups).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="📋 Exportar Lista", command=self.export_list).pack(side=tk.LEFT, padx=5)
        
        # Lista de backups
        self.backups_tree = ttk.Treeview(backups_frame, columns=("Tipo", "Tamanho", "Data", "Status"), show="tree headings")
        self.backups_tree.heading("#0", text="Nome")
        self.backups_tree.heading("Tipo", text="Tipo")
        self.backups_tree.heading("Tamanho", text="Tamanho")
        self.backups_tree.heading("Data", text="Data")
        self.backups_tree.heading("Status", text="Status")
        
        self.backups_tree.column("#0", width=200)
        self.backups_tree.column("Tipo", width=100)
        self.backups_tree.column("Tamanho", width=100)
        self.backups_tree.column("Data", width=120)
        self.backups_tree.column("Status", width=80)
        
        # Scrollbar para a lista
        scrollbar = ttk.Scrollbar(backups_frame, orient=tk.VERTICAL, command=self.backups_tree.yview)
        self.backups_tree.configure(yscrollcommand=scrollbar.set)
        
        self.backups_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Frame de log
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log de Atividades", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Área de log
        self.log_text = tk.Text(log_frame, height=8, width=100)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar diretório padrão
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
        
        self.backup_dir_var.set(str(backup_dir))
    
    def log_message(self, message):
        """Adicionar mensagem ao log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_monitoring(self):
        """Iniciar monitoramento do sistema"""
        import time
        
        def monitor_loop():
            while True:
                try:
                    self.update_system_info()
                    self.root.after(0, self.refresh_backups)
                    time.sleep(5)  # Atualizar a cada 5 segundos
                except Exception as e:
                    self.log_message(f"Erro no monitoramento: {e}")
                    break
        
        thread = threading.Thread(target=monitor_loop)
        thread.daemon = True
        thread.start()
    
    def update_system_info(self):
        """Atualizar informações do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_label.config(text=f"{cpu_percent}%")
            
            # Memória
            memory = psutil.virtual_memory()
            self.memory_label.config(text=f"{memory.percent}%")
            
            # Disco - usar diretório home para compatibilidade multiplataforma
            disk_path = os.path.expanduser('~')
            disk = psutil.disk_usage(disk_path)
            disk_percent = (disk.used / disk.total) * 100
            self.disk_label.config(text=f"{disk_percent:.1f}%")
            
            # Espaço livre
            free_gb = disk.free / (1024**3)
            self.free_space_label.config(text=f"{free_gb:.1f} GB")
            
        except Exception as e:
            self.log_message(f"❌ Erro ao atualizar informações do sistema: {str(e)}")
    
    def browse_backup_dir(self):
        """Abrir diálogo para selecionar diretório de backup"""
        directory = filedialog.askdirectory(title="Selecionar Diretório de Backup")
        if directory:
            self.backup_dir_var.set(directory)
            self.refresh_backups()
    
    def refresh_backups(self):
        """Atualizar lista de backups"""
        try:
            # Limpar lista atual
            for item in self.backups_tree.get_children():
                self.backups_tree.delete(item)
            
            backup_dir = Path(self.backup_dir_var.get())
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
    
    def show_statistics(self):
        """Mostrar estatísticas dos backups"""
        try:
            backup_dir = Path(self.backup_dir_var.get())
            if not backup_dir.exists():
                messagebox.showerror("Erro", "Diretório de backup não existe")
                return
            
            # Calcular estatísticas
            backup_files = []
            for pattern in ["*.zip", "*.enc", "*.tar.gz"]:
                backup_files.extend(backup_dir.glob(pattern))
            
            if not backup_files:
                messagebox.showinfo("Estatísticas", "Nenhum backup encontrado")
                return
            
            total_size = sum(f.stat().st_size for f in backup_files)
            avg_size = total_size / len(backup_files)
            
            # Contar por tipo
            types = {"Completo": 0, "Incremental": 0, "Git": 0, "Criptografado": 0}
            for f in backup_files:
                if "_incremental_" in f.name:
                    types["Incremental"] += 1
                elif "_git_" in f.name:
                    types["Git"] += 1
                elif "_encrypted_" in f.name:
                    types["Criptografado"] += 1
                else:
                    types["Completo"] += 1
            
            # Mostrar estatísticas
            stats = f"""
📊 Estatísticas dos Backups

📦 Total de Backups: {len(backup_files)}
💾 Tamanho Total: {self.format_size(total_size)}
📏 Tamanho Médio: {self.format_size(avg_size)}

📋 Por Tipo:
  • Completo: {types['Completo']}
  • Incremental: {types['Incremental']}
  • Git: {types['Git']}
  • Criptografado: {types['Criptografado']}

📅 Último Backup: {datetime.datetime.fromtimestamp(max(f.stat().st_mtime for f in backup_files)).strftime("%d/%m/%Y %H:%M")}
            """
            
            messagebox.showinfo("Estatísticas", stats)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular estatísticas: {str(e)}")
    
    def clean_old_backups(self):
        """Limpar backups antigos"""
        try:
            backup_dir = Path(self.backup_dir_var.get())
            if not backup_dir.exists():
                messagebox.showerror("Erro", "Diretório de backup não existe")
                return
            
            # Implementar lógica de limpeza
            self.log_message("🧹 Limpeza de backups antigos será implementada")
            messagebox.showinfo("Info", "Funcionalidade de limpeza será implementada")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na limpeza: {str(e)}")
    
    def export_list(self):
        """Exportar lista de backups"""
        try:
            backup_dir = Path(self.backup_dir_var.get())
            if not backup_dir.exists():
                messagebox.showerror("Erro", "Diretório de backup não existe")
                return
            
            # Buscar arquivos de backup
            backup_files = []
            for pattern in ["*.zip", "*.enc", "*.tar.gz"]:
                backup_files.extend(backup_dir.glob(pattern))
            
            if not backup_files:
                messagebox.showinfo("Info", "Nenhum backup para exportar")
                return
            
            # Salvar lista
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("Lista de Backups\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for backup_file in sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True):
                        stat = backup_file.stat()
                        size = self.format_size(stat.st_size)
                        date = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M")
                        f.write(f"{backup_file.name}\n")
                        f.write(f"  Tamanho: {size}\n")
                        f.write(f"  Data: {date}\n\n")
                
                self.log_message(f"📋 Lista exportada para: {filename}")
                messagebox.showinfo("Sucesso", f"Lista exportada para:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar lista: {str(e)}")
    
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
                    return json.load(f)
        except Exception as e:
            self.log_message(f"❌ Erro ao carregar configurações: {str(e)}")
        return {}
    
    def save_config(self):
        """Salvar configurações"""
        try:
            config = {
                "backup_dir": self.backup_dir_var.get()
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.log_message(f"❌ Erro ao salvar configurações: {str(e)}")
    
    def on_closing(self):
        """Salvar configurações ao fechar"""
        self.save_config()
        self.root.destroy()

def main():
    """Função principal"""
    root = tk.Tk()
    app = BackupDashboard(root)
    
    # Configurar fechamento
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Iniciar aplicação
    root.mainloop()

if __name__ == "__main__":
    main()

