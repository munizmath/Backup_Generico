#!/usr/bin/env python3
"""
Sistema de Logging Centralizado
Configuração consistente de logging para todo o sistema de backup
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class BackupLogger:
    """Logger centralizado para o sistema de backup"""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def get_logger(cls, name: str = "backup_system", log_level: str = "INFO") -> logging.Logger:
        """Obter logger configurado"""
        if not cls._initialized:
            cls._setup_logging()
        
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def _setup_logging(cls):
        """Configurar sistema de logging"""
        if cls._initialized:
            return
        
        # Criar diretório de logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configurar formato de log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Configurar handler para arquivo
        log_file = log_dir / f"backup_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        # Configurar handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # Configurar logger raiz
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Configurar níveis específicos
        logging.getLogger('boto3').setLevel(logging.WARNING)
        logging.getLogger('botocore').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        cls._initialized = True
    
    @classmethod
    def set_level(cls, level: str):
        """Definir nível de log"""
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger().setLevel(numeric_level)
    
    @classmethod
    def add_file_handler(cls, log_file: Path, logger_name: str = "backup_system"):
        """Adicionar handler de arquivo específico"""
        logger = cls.get_logger(logger_name)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

def get_logger(name: str = "backup_system") -> logging.Logger:
    """Função de conveniência para obter logger"""
    return BackupLogger.get_logger(name)

def log_function_call(func):
    """Decorator para logar chamadas de função"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Chamando {func.__name__} com args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} executado com sucesso")
            return result
        except Exception as e:
            logger.error(f"Erro em {func.__name__}: {e}")
            raise
    return wrapper

def log_backup_operation(operation: str, project: str, **kwargs):
    """Log específico para operações de backup"""
    logger = get_logger("backup_operations")
    logger.info(f"Operação: {operation} | Projeto: {project} | Detalhes: {kwargs}")

def log_system_event(event: str, level: str = "INFO", **kwargs):
    """Log para eventos do sistema"""
    logger = get_logger("system_events")
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, f"Evento: {event} | Detalhes: {kwargs}")

# Configurar logging na importação
BackupLogger._setup_logging()
