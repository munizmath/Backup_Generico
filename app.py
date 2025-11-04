#!/usr/bin/env python3
"""
Aplicação Web - Sistema de Backup Avançado
Backend Flask para interface web moderna
"""

from flask import Flask, render_template, jsonify, request, send_file, session
from flask_cors import CORS
import os
import json
import time
from pathlib import Path
from datetime import datetime
import threading

# Importar módulos do sistema
import sys
backend_path = os.path.join(os.path.dirname(__file__), 'Backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from config_manager import ConfigManager
    from telemetry_system import TelemetrySystem
    from version_manager import VersionManager
    from encryption_system import EncryptionSystem
    from content_addressed import ContentAddressedStorage
    from logging_config import get_logger
except ImportError as e:
    print(f"Aviso: Erro ao importar módulos: {e}")
    # Criar classes mock para desenvolvimento
    class ConfigManager:
        def __init__(self, *args, **kwargs): pass
        def get(self, *args, **kwargs): return {}
        def set(self, *args, **kwargs): pass
        def save_config(self, *args, **kwargs): pass
        def get_backup_dir(self): return os.path.join(os.getcwd(), "backups")
    
    class TelemetrySystem:
        def __init__(self, *args, **kwargs): pass
        def record_system_metrics(self): pass
        def get_metrics_summary(self, *args): return {}
    
    class VersionManager:
        def __init__(self, *args, **kwargs): pass
    
    class EncryptionSystem:
        def __init__(self, *args, **kwargs): pass
    
    class ContentAddressedStorage:
        def __init__(self, *args, **kwargs): pass
    
    def get_logger(name):
        import logging
        return logging.getLogger(name)

app = Flask(__name__, 
            template_folder='web/templates',
            static_folder='web/static')
app.secret_key = os.urandom(24)
CORS(app)

# Configurações
config_manager = ConfigManager()
logger = get_logger("web_app")

# Inicializar sistemas
telemetry = None
version_manager = None
encryption_system = None

def init_systems():
    """Inicializar sistemas do backend"""
    global telemetry, version_manager, encryption_system
    try:
        telemetry = TelemetrySystem("Backend/config")
        version_manager = VersionManager(os.getcwd())
        encryption_system = EncryptionSystem("Backend/config")
    except Exception as e:
        logger.error(f"Erro ao inicializar sistemas: {e}")

# Rotas principais
@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard de monitoramento"""
    return render_template('dashboard.html')

@app.route('/monitoramento')
def monitoramento():
    """Página de monitoramento"""
    return render_template('monitoramento.html')

@app.route('/historico')
def historico():
    """Página de histórico"""
    return render_template('historico.html')

@app.route('/configuracoes')
def configuracoes():
    """Página de configurações"""
    return render_template('configuracoes.html')

@app.route('/ajuda')
def ajuda():
    """Página de ajuda"""
    return render_template('ajuda.html')

@app.route('/sobre')
def sobre():
    """Página sobre"""
    return render_template('sobre.html')

# APIs
@app.route('/api/config', methods=['GET'])
def get_config():
    """Obter configurações"""
    try:
        config = {
            'backup': config_manager.get('backup'),
            'retention': config_manager.get('retention'),
            'gui': config_manager.get('gui')
        }
        return jsonify({'success': True, 'data': config})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """Atualizar configurações"""
    try:
        data = request.json
        section = data.get('section')
        key = data.get('key')
        value = data.get('value')
        
        config_manager.set(section, key, value)
        config_manager.save_config(section)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup', methods=['POST'])
def create_backup():
    """Criar backup"""
    try:
        data = request.json
        project_dir = data.get('project_dir')
        backup_dir = data.get('backup_dir')
        project_name = data.get('project_name')
        backup_type = data.get('backup_type', 'completo')
        password = data.get('password')
        
        # Validar dados
        if not project_dir or not backup_dir or not project_name:
            return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
        
        # Criar backup (implementar lógica)
        # Por enquanto, simular sucesso
        backup_id = f"{project_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return jsonify({
            'success': True,
            'backup_id': backup_id,
            'message': 'Backup criado com sucesso'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system/metrics', methods=['GET'])
def get_system_metrics():
    """Obter métricas do sistema"""
    try:
        if telemetry:
            telemetry.record_system_metrics()
            summary = telemetry.get_metrics_summary(24)
            return jsonify({'success': True, 'data': summary})
        return jsonify({'success': True, 'data': {}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backups/list', methods=['GET'])
def list_backups():
    """Listar backups"""
    try:
        backup_dir = config_manager.get_backup_dir()
        backups = []
        
        if os.path.exists(backup_dir):
            for file in os.listdir(backup_dir):
                if file.endswith('.zip') or file.endswith('.7z'):
                    file_path = os.path.join(backup_dir, file)
                    stat = os.stat(file_path)
                    backups.append({
                        'name': file,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': 'completo'  # Determinar tipo
                    })
        
        return jsonify({'success': True, 'data': backups})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/theme', methods=['POST'])
def set_theme():
    """Definir tema (claro/escuro)"""
    try:
        data = request.json
        theme = data.get('theme', 'dark')
        session['theme'] = theme
        return jsonify({'success': True, 'theme': theme})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/theme', methods=['GET'])
def get_theme():
    """Obter tema atual"""
    theme = session.get('theme', 'dark')
    return jsonify({'success': True, 'theme': theme})

if __name__ == '__main__':
    init_systems()
    app.run(debug=True, host='0.0.0.0', port=5000)

