#!/usr/bin/env python3
"""
Sistema de Telemetria e Monitoramento
Implementa métricas, alertas e logs estruturados
"""

import json
import time
import psutil
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, asdict

@dataclass
class BackupMetrics:
    """Métricas de backup"""
    timestamp: float
    backup_type: str
    project_name: str
    file_count: int
    total_size: int
    duration: float
    success: bool
    error_message: Optional[str] = None
    deduplication_ratio: float = 0.0
    compression_ratio: float = 0.0

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    disk_free_gb: float
    backup_count: int
    last_backup_time: Optional[float] = None

@dataclass
class Alert:
    """Alerta do sistema"""
    timestamp: float
    level: str  # INFO, WARNING, ERROR, CRITICAL
    category: str
    message: str
    resolved: bool = False
    resolved_at: Optional[float] = None

class TelemetrySystem:
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_dir = self.config_dir / "metrics"
        self.alerts_dir = self.config_dir / "alerts"
        self.logs_dir = self.config_dir / "logs"
        
        # Criar diretórios
        for dir_path in [self.metrics_dir, self.alerts_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Configurar logging
        self._setup_logging()
        
        # Carregar configuração
        self.config = self._load_config()
        
        # Inicializar métricas
        self.backup_metrics: List[BackupMetrics] = []
        self.system_metrics: List[SystemMetrics] = []
        self.alerts: List[Alert] = []
    
    def _load_config(self) -> Dict:
        """Carregar configuração de telemetria"""
        config_file = self.config_dir / "telemetry_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Configuração padrão
        return {
            "metrics_retention_days": 30,
            "alerts_retention_days": 90,
            "log_retention_days": 30,
            "alert_thresholds": {
                "cpu_percent": 80,
                "memory_percent": 85,
                "disk_percent": 90,
                "no_backup_hours": 24,
                "backup_failure_rate": 0.1
            },
            "notification_email": "",
            "prometheus_port": 9090
        }
    
    def _save_config(self):
        """Salvar configuração"""
        config_file = self.config_dir / "telemetry_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _setup_logging(self):
        """Configurar sistema de logging"""
        log_file = self.logs_dir / f"backup_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def record_backup_metrics(self, metrics: BackupMetrics):
        """Registrar métricas de backup"""
        self.backup_metrics.append(metrics)
        
        # Salvar em arquivo
        metrics_file = self.metrics_dir / f"backup_{int(metrics.timestamp)}.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(metrics), f, indent=2, ensure_ascii=False)
        
        # Log estruturado
        self.logger.info(f"Backup metrics recorded: {metrics.project_name} - {metrics.file_count} files, {metrics.total_size} bytes, {metrics.duration:.2f}s")
        
        # Verificar alertas
        self._check_backup_alerts(metrics)
    
    def record_system_metrics(self):
        """Registrar métricas do sistema"""
        # Usar diretório home para compatibilidade multiplataforma
        disk_path = os.path.expanduser('~')
        
        metrics = SystemMetrics(
            timestamp=time.time(),
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            disk_percent=psutil.disk_usage(disk_path).percent,
            disk_free_gb=psutil.disk_usage(disk_path).free / (1024**3),
            backup_count=len(self.backup_metrics),
            last_backup_time=max([m.timestamp for m in self.backup_metrics]) if self.backup_metrics else None
        )
        
        self.system_metrics.append(metrics)
        
        # Salvar em arquivo
        metrics_file = self.metrics_dir / f"system_{int(metrics.timestamp)}.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(metrics), f, indent=2, ensure_ascii=False)
        
        # Verificar alertas
        self._check_system_alerts(metrics)
    
    def _check_backup_alerts(self, metrics: BackupMetrics):
        """Verificar alertas relacionados a backup"""
        if not metrics.success:
            self.create_alert(
                level="ERROR",
                category="backup_failure",
                message=f"Backup failed for {metrics.project_name}: {metrics.error_message}"
            )
        
        # Verificar taxa de falha
        recent_backups = [m for m in self.backup_metrics if m.timestamp > time.time() - 3600]  # Última hora
        if len(recent_backups) > 0:
            failure_rate = sum(1 for m in recent_backups if not m.success) / len(recent_backups)
            if failure_rate > self.config["alert_thresholds"]["backup_failure_rate"]:
                self.create_alert(
                    level="WARNING",
                    category="backup_failure_rate",
                    message=f"High backup failure rate: {failure_rate:.1%}"
                )
    
    def _check_system_alerts(self, metrics: SystemMetrics):
        """Verificar alertas do sistema"""
        thresholds = self.config["alert_thresholds"]
        
        if metrics.cpu_percent > thresholds["cpu_percent"]:
            self.create_alert(
                level="WARNING",
                category="high_cpu",
                message=f"High CPU usage: {metrics.cpu_percent:.1f}%"
            )
        
        if metrics.memory_percent > thresholds["memory_percent"]:
            self.create_alert(
                level="WARNING",
                category="high_memory",
                message=f"High memory usage: {metrics.memory_percent:.1f}%"
            )
        
        if metrics.disk_percent > thresholds["disk_percent"]:
            self.create_alert(
                level="CRITICAL",
                category="low_disk_space",
                message=f"Low disk space: {metrics.disk_percent:.1f}% used"
            )
        
        # Verificar se não há backup há muito tempo
        if metrics.last_backup_time:
            hours_since_backup = (time.time() - metrics.last_backup_time) / 3600
            if hours_since_backup > thresholds["no_backup_hours"]:
                self.create_alert(
                    level="WARNING",
                    category="no_recent_backup",
                    message=f"No backup for {hours_since_backup:.1f} hours"
                )
    
    def create_alert(self, level: str, category: str, message: str):
        """Criar alerta"""
        alert = Alert(
            timestamp=time.time(),
            level=level,
            category=category,
            message=message
        )
        
        self.alerts.append(alert)
        
        # Salvar em arquivo
        alert_file = self.alerts_dir / f"alert_{int(alert.timestamp)}_{category}.json"
        with open(alert_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(alert), f, indent=2, ensure_ascii=False)
        
        # Log do alerta
        self.logger.warning(f"ALERT [{level}] {category}: {message}")
        
        # Enviar notificação (implementar conforme necessário)
        self._send_notification(alert)
    
    def _send_notification(self, alert: Alert):
        """Enviar notificação de alerta"""
        # Implementar envio de email, Slack, etc.
        if self.config.get("notification_email"):
            # Implementar envio de email
            pass
    
    def resolve_alert(self, alert_id: str):
        """Resolver alerta"""
        for alert in self.alerts:
            if f"{int(alert.timestamp)}_{alert.category}" == alert_id:
                alert.resolved = True
                alert.resolved_at = time.time()
                
                # Atualizar arquivo
                alert_file = self.alerts_dir / f"alert_{alert_id}.json"
                if alert_file.exists():
                    with open(alert_file, 'w', encoding='utf-8') as f:
                        json.dump(asdict(alert), f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Alert resolved: {alert_id}")
                break
    
    def get_metrics_summary(self, hours: int = 24) -> Dict:
        """Obter resumo das métricas"""
        cutoff_time = time.time() - (hours * 3600)
        
        recent_backups = [m for m in self.backup_metrics if m.timestamp > cutoff_time]
        recent_system = [m for m in self.system_metrics if m.timestamp > cutoff_time]
        active_alerts = [a for a in self.alerts if not a.resolved]
        
        if not recent_backups:
            return {
                "backups": 0,
                "success_rate": 0,
                "total_size": 0,
                "avg_duration": 0,
                "alerts": len(active_alerts)
            }
        
        success_count = sum(1 for m in recent_backups if m.success)
        total_size = sum(m.total_size for m in recent_backups)
        avg_duration = sum(m.duration for m in recent_backups) / len(recent_backups)
        
        return {
            "backups": len(recent_backups),
            "success_rate": success_count / len(recent_backups),
            "total_size": total_size,
            "avg_duration": avg_duration,
            "alerts": len(active_alerts),
            "system_health": self._calculate_system_health(recent_system)
        }
    
    def _calculate_system_health(self, recent_metrics: List[SystemMetrics]) -> Dict:
        """Calcular saúde do sistema"""
        if not recent_metrics:
            return {"status": "unknown", "score": 0}
        
        latest = recent_metrics[-1]
        
        # Calcular score de saúde (0-100)
        cpu_score = max(0, 100 - latest.cpu_percent)
        memory_score = max(0, 100 - latest.memory_percent)
        disk_score = max(0, 100 - latest.disk_percent)
        
        health_score = (cpu_score + memory_score + disk_score) / 3
        
        if health_score >= 80:
            status = "excellent"
        elif health_score >= 60:
            status = "good"
        elif health_score >= 40:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "status": status,
            "score": health_score,
            "cpu_percent": latest.cpu_percent,
            "memory_percent": latest.memory_percent,
            "disk_percent": latest.disk_percent
        }
    
    def cleanup_old_data(self):
        """Limpar dados antigos"""
        current_time = time.time()
        
        # Limpar métricas antigas
        metrics_retention = self.config["metrics_retention_days"] * 24 * 3600
        for metrics_file in self.metrics_dir.glob("*.json"):
            if metrics_file.stat().st_mtime < current_time - metrics_retention:
                metrics_file.unlink()
        
        # Limpar alertas antigos
        alerts_retention = self.config["alerts_retention_days"] * 24 * 3600
        for alert_file in self.alerts_dir.glob("*.json"):
            if alert_file.stat().st_mtime < current_time - alerts_retention:
                alert_file.unlink()
        
        # Limpar logs antigos
        logs_retention = self.config["log_retention_days"] * 24 * 3600
        for log_file in self.logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < current_time - logs_retention:
                log_file.unlink()
        
        self.logger.info("Old data cleaned up")

def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python telemetry_system.py <comando> <config_dir> [args...]")
        print("Comandos:")
        print("  record-backup <project_name> <backup_type> <file_count> <total_size> <duration> <success>")
        print("  record-system")
        print("  summary [hours]")
        print("  alerts")
        print("  resolve <alert_id>")
        print("  cleanup")
        sys.exit(1)
    
    command = sys.argv[1]
    config_dir = sys.argv[2]
    
    telemetry = TelemetrySystem(config_dir)
    
    if command == "record-backup":
        if len(sys.argv) < 9:
            print("Uso: record-backup <project_name> <backup_type> <file_count> <total_size> <duration> <success>")
            sys.exit(1)
        
        project_name = sys.argv[3]
        backup_type = sys.argv[4]
        file_count = int(sys.argv[5])
        total_size = int(sys.argv[6])
        duration = float(sys.argv[7])
        success = sys.argv[8].lower() == "true"
        
        metrics = BackupMetrics(
            timestamp=time.time(),
            backup_type=backup_type,
            project_name=project_name,
            file_count=file_count,
            total_size=total_size,
            duration=duration,
            success=success
        )
        
        telemetry.record_backup_metrics(metrics)
        print(f"✅ Backup metrics recorded: {project_name}")
    
    elif command == "record-system":
        telemetry.record_system_metrics()
        print("✅ System metrics recorded")
    
    elif command == "summary":
        hours = int(sys.argv[3]) if len(sys.argv) > 3 else 24
        summary = telemetry.get_metrics_summary(hours)
        
        print(f"📊 Resumo das últimas {hours} horas:")
        print(f"  Backups: {summary['backups']}")
        print(f"  Taxa de sucesso: {summary['success_rate']:.1%}")
        print(f"  Tamanho total: {summary['total_size']:,} bytes")
        print(f"  Duração média: {summary['avg_duration']:.2f}s")
        print(f"  Alertas ativos: {summary['alerts']}")
        print(f"  Saúde do sistema: {summary['system_health']['status']} ({summary['system_health']['score']:.1f})")
    
    elif command == "alerts":
        active_alerts = [a for a in telemetry.alerts if not a.resolved]
        print(f"🚨 {len(active_alerts)} alertas ativos:")
        for alert in active_alerts:
            print(f"  [{alert.level}] {alert.category}: {alert.message}")
    
    elif command == "resolve":
        if len(sys.argv) < 4:
            print("Uso: resolve <alert_id>")
            sys.exit(1)
        
        alert_id = sys.argv[3]
        telemetry.resolve_alert(alert_id)
        print(f"✅ Alert resolved: {alert_id}")
    
    elif command == "cleanup":
        telemetry.cleanup_old_data()
        print("✅ Old data cleaned up")
    
    else:
        print(f"❌ Comando não reconhecido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
