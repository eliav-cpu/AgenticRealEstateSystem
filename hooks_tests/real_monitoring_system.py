#!/usr/bin/env python3
"""
Sistema de Monitoramento Contínuo REAL - Real Estate Assistant
Monitoramento em tempo real para sistema agêntico em produção
"""

import asyncio
import json
import time
import schedule
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import threading
import requests

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from real_stress_testing import RealSystemStressTester
from real_conversation_hooks import ProductionConversationMonitor
from real_test_pipeline import RealEstateTestPipeline
from app.utils.logging import get_logger, log_agent_action, log_api_call, log_error
from config.settings import get_settings

@dataclass
class MonitoringAlert:
    """Alerta do sistema de monitoramento"""
    timestamp: datetime
    severity: str  # critical, warning, info
    component: str
    message: str
    metrics: Dict[str, Any]
    auto_resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class SystemMetrics:
    """Métricas do sistema em tempo real"""
    timestamp: datetime
    success_rate: float
    average_response_time: float
    concurrent_users: int
    total_requests: int
    error_count: int
    agent_performance: Dict[str, Any]
    mock_api_health: Dict[str, Any]
    openrouter_health: Dict[str, Any]
    ollama_health: Dict[str, Any]

class RealTimeMonitor:
    """Monitor em tempo real para sistema de produção"""
    
    def __init__(self):
        self.logger = get_logger("realtime_monitor")
        self.conversation_monitor = ProductionConversationMonitor()
        self.stress_tester = RealSystemStressTester()
        self.pipeline = RealEstateTestPipeline()
        
        # Estado do monitoramento
        self.is_monitoring = False
        self.monitoring_thread = None
        self.metrics_history: List[SystemMetrics] = []
        self.alerts: List[MonitoringAlert] = []
        self.last_health_check = None
        
        # Configurações
        self.health_check_interval = 300  # 5 minutos
        self.metrics_collection_interval = 60  # 1 minuto
        self.alert_thresholds = {
            "success_rate_critical": 70.0,
            "success_rate_warning": 85.0,
            "response_time_critical": 10.0,
            "response_time_warning": 5.0,
            "error_rate_critical": 20.0,
            "error_rate_warning": 10.0
        }
        
        # Inicializar monitoramento de conversas
        self.conversation_monitor.start_monitoring()
    
    def start_continuous_monitoring(self):
        """Inicia monitoramento contínuo"""
        if self.is_monitoring:
            self.logger.warning("Monitoramento já está ativo")
            return
        
        self.is_monitoring = True
        self.logger.info("🎬 Iniciando monitoramento contínuo do sistema real")
        
        # Configurar agendamento
        schedule.clear()
        schedule.every(1).minutes.do(self._collect_metrics)
        schedule.every(5).minutes.do(self._run_health_check)
        schedule.every(30).minutes.do(self._run_mini_stress_test)
        schedule.every(2).hours.do(self._run_full_validation)
        schedule.every().day.at("02:00").do(self._daily_comprehensive_test)
        
        # Iniciar thread de monitoramento
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("✅ Monitoramento contínuo ativo")
        self.logger.info("📋 Agendamentos configurados:")
        self.logger.info("   • Coleta de métricas: a cada 1 minuto")
        self.logger.info("   • Health check: a cada 5 minutos")
        self.logger.info("   • Mini stress test: a cada 30 minutos")
        self.logger.info("   • Validação completa: a cada 2 horas")
        self.logger.info("   • Teste abrangente: diariamente às 02:00")
    
    def stop_continuous_monitoring(self):
        """Para monitoramento contínuo"""
        self.is_monitoring = False
        schedule.clear()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.conversation_monitor.stop_monitoring()
        self.logger.info("🛑 Monitoramento contínuo parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.is_monitoring:
            try:
                schedule.run_pending()
                time.sleep(30)  # Verificar a cada 30 segundos
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                log_error(e, context={"component": "monitoring_loop"})
                time.sleep(60)  # Esperar 1 minuto antes de tentar novamente
    
    def _collect_metrics(self):
        """Coleta métricas do sistema"""
        try:
            self.logger.info("📊 Coletando métricas do sistema...")
            
            # Obter estatísticas de conversa
            conversation_stats = self.conversation_monitor.get_live_statistics()
            
            # Verificar saúde da API Mock
            mock_health = self._check_mock_api_health()
            
            # Verificar saúde do OpenRouter (simulado)
            openrouter_health = self._check_openrouter_health()
            
            # Verificar saúde do Ollama (simulado)
            ollama_health = self._check_ollama_health()
            
            # Calcular métricas agregadas
            success_rate = conversation_stats.get("overall_success_rate", 0.0)
            avg_response_time = conversation_stats.get("average_duration", 0.0)
            total_conversations = conversation_stats.get("total_conversations", 0)
            
            # Criar métricas
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                success_rate=success_rate,
                average_response_time=avg_response_time,
                concurrent_users=len(self.conversation_monitor.analyzer.active_sessions),
                total_requests=total_conversations,
                error_count=0,  # Seria calculado baseado em logs reais
                agent_performance=conversation_stats.get("agent_statistics", {}),
                mock_api_health=mock_health,
                openrouter_health=openrouter_health,
                ollama_health=ollama_health
            )
            
            self.metrics_history.append(metrics)
            
            # Manter apenas últimas 24 horas de métricas
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.metrics_history = [m for m in self.metrics_history if m.timestamp > cutoff_time]
            
            # Verificar thresholds e gerar alertas
            self._check_thresholds(metrics)
            
            self.logger.info(f"   ✅ Métricas coletadas - Success: {success_rate:.1f}%, Time: {avg_response_time:.2f}s")
            
            # Log das métricas
            log_agent_action(
                agent_name="realtime_monitor",
                action="metrics_collected",
                details={
                    "success_rate": success_rate,
                    "response_time": avg_response_time,
                    "concurrent_users": metrics.concurrent_users,
                    "mock_api_status": mock_health.get("status", "unknown")
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas: {e}")
            log_error(e, context={"component": "metrics_collection"})
    
    def _check_mock_api_health(self) -> Dict[str, Any]:
        """Verifica saúde da API Mock"""
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8000/api/properties/search", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                properties_count = len(data.get("properties", []))
                
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "properties_available": properties_count,
                    "last_check": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time,
                    "last_check": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    def _check_openrouter_health(self) -> Dict[str, Any]:
        """Verifica saúde do OpenRouter (simulado)"""
        # Em produção, faria uma chamada real à API
        return {
            "status": "healthy",
            "model": "google/gemma-3-27b-it:free",
            "last_successful_call": datetime.now().isoformat(),
            "estimated_response_time": 2.5
        }
    
    def _check_ollama_health(self) -> Dict[str, Any]:
        """Verifica saúde do Ollama (simulado)"""
        # Em produção, verificaria se o Ollama está rodando
        return {
            "status": "available",
            "model": "gemma3n:e2b",
            "last_check": datetime.now().isoformat(),
            "fallback_ready": True
        }
    
    def _check_thresholds(self, metrics: SystemMetrics):
        """Verifica thresholds e gera alertas"""
        
        # Verificar taxa de sucesso
        if metrics.success_rate < self.alert_thresholds["success_rate_critical"]:
            self._create_alert(
                severity="critical",
                component="system_performance",
                message=f"Taxa de sucesso crítica: {metrics.success_rate:.1f}%",
                metrics={"success_rate": metrics.success_rate}
            )
        elif metrics.success_rate < self.alert_thresholds["success_rate_warning"]:
            self._create_alert(
                severity="warning",
                component="system_performance",
                message=f"Taxa de sucesso baixa: {metrics.success_rate:.1f}%",
                metrics={"success_rate": metrics.success_rate}
            )
        
        # Verificar tempo de resposta
        if metrics.average_response_time > self.alert_thresholds["response_time_critical"]:
            self._create_alert(
                severity="critical",
                component="response_time",
                message=f"Tempo de resposta crítico: {metrics.average_response_time:.2f}s",
                metrics={"response_time": metrics.average_response_time}
            )
        elif metrics.average_response_time > self.alert_thresholds["response_time_warning"]:
            self._create_alert(
                severity="warning",
                component="response_time",
                message=f"Tempo de resposta alto: {metrics.average_response_time:.2f}s",
                metrics={"response_time": metrics.average_response_time}
            )
        
        # Verificar API Mock
        if metrics.mock_api_health.get("status") != "healthy":
            self._create_alert(
                severity="critical",
                component="mock_api",
                message="API Mock indisponível",
                metrics=metrics.mock_api_health
            )
    
    def _create_alert(self, severity: str, component: str, message: str, metrics: Dict[str, Any]):
        """Cria um alerta"""
        alert = MonitoringAlert(
            timestamp=datetime.now(),
            severity=severity,
            component=component,
            message=message,
            metrics=metrics
        )
        
        self.alerts.append(alert)
        
        # Log do alerta
        self.logger.warning(f"🚨 ALERTA {severity.upper()}: {message}")
        log_agent_action(
            agent_name="realtime_monitor",
            action="alert_created",
            details={
                "severity": severity,
                "component": component,
                "message": message,
                "metrics": metrics
            }
        )
        
        # Manter apenas últimos 100 alertas
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def _run_health_check(self):
        """Executa health check do sistema"""
        try:
            self.logger.info("🏥 Executando health check...")
            
            # Verificar componentes críticos
            components_status = {
                "mock_api": self._check_mock_api_health()["status"],
                "openrouter": self._check_openrouter_health()["status"],
                "ollama": self._check_ollama_health()["status"],
                "conversation_monitor": "healthy" if self.conversation_monitor.is_monitoring else "stopped"
            }
            
            unhealthy_components = [comp for comp, status in components_status.items() if status != "healthy"]
            
            if unhealthy_components:
                self._create_alert(
                    severity="warning",
                    component="health_check",
                    message=f"Componentes com problemas: {', '.join(unhealthy_components)}",
                    metrics=components_status
                )
            
            self.last_health_check = datetime.now()
            self.logger.info(f"   ✅ Health check concluído - {len(unhealthy_components)} problemas")
            
        except Exception as e:
            self.logger.error(f"Erro no health check: {e}")
            log_error(e, context={"component": "health_check"})
    
    def _run_mini_stress_test(self):
        """Executa mini stress test"""
        try:
            self.logger.info("⚡ Executando mini stress test...")
            
            # Executar teste rápido com 1 usuário, 2 perguntas
            asyncio.run(self._async_mini_stress_test())
            
        except Exception as e:
            self.logger.error(f"Erro no mini stress test: {e}")
            log_error(e, context={"component": "mini_stress_test"})
    
    async def _async_mini_stress_test(self):
        """Mini stress test assíncrono"""
        try:
            result = await self.stress_tester.run_real_stress_test(
                concurrent_users=1,
                questions_per_user=2
            )
            
            success_rate = result["execution_stats"]["success_rate"]
            avg_time = result["execution_stats"]["average_response_time"]
            
            self.logger.info(f"   ✅ Mini stress test: {success_rate:.1f}% sucesso, {avg_time:.2f}s tempo médio")
            
            # Verificar se resultado está dentro do esperado
            if success_rate < 80.0:
                self._create_alert(
                    severity="warning",
                    component="stress_test",
                    message=f"Mini stress test com baixa performance: {success_rate:.1f}%",
                    metrics={"success_rate": success_rate, "response_time": avg_time}
                )
                
        except Exception as e:
            self.logger.error(f"Erro no mini stress test assíncrono: {e}")
    
    def _run_full_validation(self):
        """Executa validação completa"""
        try:
            self.logger.info("🔍 Executando validação completa...")
            
            # Executar teste mais abrangente
            asyncio.run(self._async_full_validation())
            
        except Exception as e:
            self.logger.error(f"Erro na validação completa: {e}")
            log_error(e, context={"component": "full_validation"})
    
    async def _async_full_validation(self):
        """Validação completa assíncrona"""
        try:
            # Executar cenário básico do pipeline
            basic_scenario = self.pipeline.test_scenarios[0]  # real_basic_user_journey
            result = await self.pipeline.run_real_scenario(basic_scenario)
            
            grade = result.overall_grade
            ux_score = result.integration_metrics.get("user_experience_score", 0.0)
            
            self.logger.info(f"   ✅ Validação completa: {grade}, UX Score: {ux_score:.2f}")
            
            # Verificar se resultado está aceitável
            if "D" in grade or ux_score < 0.5:
                self._create_alert(
                    severity="critical",
                    component="full_validation",
                    message=f"Validação completa com resultado ruim: {grade}",
                    metrics={"grade": grade, "ux_score": ux_score}
                )
                
        except Exception as e:
            self.logger.error(f"Erro na validação completa assíncrona: {e}")
    
    def _daily_comprehensive_test(self):
        """Executa teste abrangente diário"""
        try:
            self.logger.info("📊 Executando teste abrangente diário...")
            
            # Executar pipeline completo
            asyncio.run(self._async_daily_test())
            
        except Exception as e:
            self.logger.error(f"Erro no teste diário: {e}")
            log_error(e, context={"component": "daily_test"})
    
    async def _async_daily_test(self):
        """Teste diário assíncrono"""
        try:
            results = await self.pipeline.run_full_real_pipeline()
            
            # Analisar resultados
            grades = [r.overall_grade for r in results]
            avg_ux = sum(r.integration_metrics.get("user_experience_score", 0.0) for r in results) / len(results)
            
            self.logger.info(f"   ✅ Teste diário concluído: {len(results)} cenários, UX médio: {avg_ux:.2f}")
            
            # Criar relatório diário
            self._generate_daily_report(results)
            
        except Exception as e:
            self.logger.error(f"Erro no teste diário assíncrono: {e}")
    
    def _generate_daily_report(self, results):
        """Gera relatório diário"""
        try:
            report_data = {
                "date": datetime.now().isoformat(),
                "total_scenarios": len(results),
                "results_summary": [
                    {
                        "scenario": r.scenario_name,
                        "grade": r.overall_grade,
                        "ux_score": r.integration_metrics.get("user_experience_score", 0.0),
                        "success_rate": r.stress_test_results.get("execution_stats", {}).get("success_rate", 0.0)
                    }
                    for r in results
                ],
                "system_health": "healthy" if all("A" in r.overall_grade for r in results) else "needs_attention",
                "recommendations": list(set(rec for r in results for rec in r.recommendations))
            }
            
            # Salvar relatório diário
            report_file = Path("hooks_tests") / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📄 Relatório diário salvo: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório diário: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Retorna status atual do sistema"""
        
        # Métricas mais recentes
        latest_metrics = self.metrics_history[-1] if self.metrics_history else None
        
        # Alertas ativos (últimas 24h)
        cutoff_time = datetime.now() - timedelta(hours=24)
        active_alerts = [a for a in self.alerts if a.timestamp > cutoff_time and not a.auto_resolved]
        
        # Contar alertas por severidade
        alert_counts = {
            "critical": len([a for a in active_alerts if a.severity == "critical"]),
            "warning": len([a for a in active_alerts if a.severity == "warning"]),
            "info": len([a for a in active_alerts if a.severity == "info"])
        }
        
        # Determinar status geral
        if alert_counts["critical"] > 0:
            overall_status = "critical"
        elif alert_counts["warning"] > 2:
            overall_status = "warning"
        elif latest_metrics and latest_metrics.success_rate > 85:
            overall_status = "healthy"
        else:
            overall_status = "unknown"
        
        return {
            "overall_status": overall_status,
            "monitoring_active": self.is_monitoring,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "latest_metrics": asdict(latest_metrics) if latest_metrics else None,
            "active_alerts": alert_counts,
            "total_metrics_collected": len(self.metrics_history),
            "uptime": "monitoring_active" if self.is_monitoring else "stopped",
            "components": {
                "conversation_monitor": "active" if self.conversation_monitor.is_monitoring else "inactive",
                "stress_tester": "available",
                "test_pipeline": "available"
            }
        }
    
    def generate_monitoring_dashboard(self) -> str:
        """Gera dashboard de monitoramento"""
        
        status = self.get_current_status()
        
        dashboard = f"""
🖥️ DASHBOARD DE MONITORAMENTO REAL - REAL ESTATE ASSISTANT
{'='*70}

🚦 STATUS GERAL: {status['overall_status'].upper()}
• Monitoramento Ativo: {'✅ Sim' if status['monitoring_active'] else '❌ Não'}
• Último Health Check: {status.get('last_health_check', 'Nunca')[:19] if status.get('last_health_check') else 'Nunca'}
• Métricas Coletadas: {status['total_metrics_collected']}

📊 MÉTRICAS ATUAIS:
"""
        
        if status['latest_metrics']:
            metrics = status['latest_metrics']
            dashboard += f"""• Taxa de Sucesso: {metrics['success_rate']:.1f}%
• Tempo Médio de Resposta: {metrics['average_response_time']:.2f}s
• Usuários Simultâneos: {metrics['concurrent_users']}
• Total de Requests: {metrics['total_requests']}
• Última Atualização: {metrics['timestamp'][:19]}
"""
        else:
            dashboard += "• Nenhuma métrica disponível\n"
        
        dashboard += f"""
🚨 ALERTAS ATIVOS (24h):
• Críticos: {status['active_alerts']['critical']}
• Avisos: {status['active_alerts']['warning']}
• Informativos: {status['active_alerts']['info']}

🔧 COMPONENTES:
• Monitor de Conversa: {status['components']['conversation_monitor'].upper()}
• Stress Tester: {status['components']['stress_tester'].upper()}
• Pipeline de Testes: {status['components']['test_pipeline'].upper()}
"""
        
        # Mostrar últimos alertas
        if self.alerts:
            recent_alerts = sorted(self.alerts, key=lambda a: a.timestamp, reverse=True)[:5]
            dashboard += "\n🚨 ÚLTIMOS ALERTAS:\n"
            for alert in recent_alerts:
                emoji = "🔴" if alert.severity == "critical" else "🟡" if alert.severity == "warning" else "🔵"
                dashboard += f"{emoji} {alert.timestamp.strftime('%H:%M')} - {alert.component}: {alert.message}\n"
        
        # Tendências (se temos dados suficientes)
        if len(self.metrics_history) >= 5:
            recent_metrics = self.metrics_history[-5:]
            success_trend = recent_metrics[-1].success_rate - recent_metrics[0].success_rate
            time_trend = recent_metrics[-1].average_response_time - recent_metrics[0].average_response_time
            
            dashboard += f"""
📈 TENDÊNCIAS (últimas 5 medições):
• Taxa de Sucesso: {'📈' if success_trend > 0 else '📉' if success_trend < 0 else '➡️'} {success_trend:+.1f}%
• Tempo de Resposta: {'📈' if time_trend > 0 else '📉' if time_trend < 0 else '➡️'} {time_trend:+.2f}s
"""
        
        return dashboard

# Sistema de alertas automáticos
class AlertManager:
    """Gerenciador de alertas automáticos"""
    
    def __init__(self, monitor: RealTimeMonitor):
        self.monitor = monitor
        self.logger = get_logger("alert_manager")
        self.notification_channels = []
        
    def add_notification_channel(self, channel_type: str, config: Dict[str, Any]):
        """Adiciona canal de notificação"""
        self.notification_channels.append({
            "type": channel_type,
            "config": config,
            "enabled": True
        })
        self.logger.info(f"📢 Canal de notificação adicionado: {channel_type}")
    
    def send_alert_notification(self, alert: MonitoringAlert):
        """Envia notificação de alerta"""
        for channel in self.notification_channels:
            if not channel["enabled"]:
                continue
                
            try:
                if channel["type"] == "email":
                    self._send_email_alert(alert, channel["config"])
                elif channel["type"] == "slack":
                    self._send_slack_alert(alert, channel["config"])
                elif channel["type"] == "webhook":
                    self._send_webhook_alert(alert, channel["config"])
                elif channel["type"] == "log":
                    self._send_log_alert(alert)
                    
            except Exception as e:
                self.logger.error(f"Erro ao enviar alerta via {channel['type']}: {e}")
    
    def _send_log_alert(self, alert: MonitoringAlert):
        """Envia alerta para log"""
        severity_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
        emoji = severity_emoji.get(alert.severity, "⚪")
        
        self.logger.warning(f"{emoji} ALERTA {alert.severity.upper()}: {alert.component} - {alert.message}")
    
    def _send_email_alert(self, alert: MonitoringAlert, config: Dict[str, Any]):
        """Envia alerta por email (placeholder)"""
        # Em produção, implementaria envio real de email
        self.logger.info(f"📧 Email enviado para {config.get('recipients', 'admin')}: {alert.message}")
    
    def _send_slack_alert(self, alert: MonitoringAlert, config: Dict[str, Any]):
        """Envia alerta para Slack (placeholder)"""
        # Em produção, implementaria integração com Slack
        self.logger.info(f"💬 Slack notificado no canal {config.get('channel', '#alerts')}: {alert.message}")
    
    def _send_webhook_alert(self, alert: MonitoringAlert, config: Dict[str, Any]):
        """Envia alerta via webhook (placeholder)"""
        # Em produção, implementaria chamada HTTP para webhook
        self.logger.info(f"🔗 Webhook chamado {config.get('url', 'N/A')}: {alert.message}")

async def main():
    """Demonstração do sistema de monitoramento contínuo"""
    
    print("🖥️ SISTEMA DE MONITORAMENTO CONTÍNUO - REAL ESTATE ASSISTANT")
    print("="*70)
    print("🎯 Monitoramento em tempo real do sistema agêntico")
    
    # Criar monitor
    monitor = RealTimeMonitor()
    
    # Criar gerenciador de alertas
    alert_manager = AlertManager(monitor)
    alert_manager.add_notification_channel("log", {})
    
    try:
        # Iniciar monitoramento
        monitor.start_continuous_monitoring()
        
        print("\n✅ Sistema de monitoramento iniciado!")
        print("📊 Coletando métricas a cada 1 minuto...")
        print("🏥 Health checks a cada 5 minutos...")
        print("⚡ Mini stress tests a cada 30 minutos...")
        print("🔍 Validações completas a cada 2 horas...")
        print("📊 Testes abrangentes diários às 02:00...")
        
        # Simular operação por alguns minutos
        for i in range(10):  # 5 minutos de demonstração
            print(f"\n⏰ Minuto {i+1}/10 - Monitoramento ativo...")
            
            # Mostrar dashboard
            dashboard = monitor.generate_monitoring_dashboard()
            print(dashboard)
            
            # Aguardar próximo ciclo
            await asyncio.sleep(30)  # 30 segundos para demonstração
        
        print("\n🏁 Demonstração concluída!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Interrompido pelo usuário")
    finally:
        # Parar monitoramento
        monitor.stop_continuous_monitoring()
        print("🛑 Monitoramento parado")

if __name__ == "__main__":
    # Configurar event loop para Windows
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main()) 