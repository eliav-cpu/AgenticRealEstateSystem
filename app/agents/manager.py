"""
Manager Agent - Lê logs em tempo real e fornece insights ao Supervisor.

Responsabilidades:
- Ler logs em TEMPO REAL (stream contínuo)
- Analisar performance dos agentes
- Identificar gargalos e erros
- Fornecer insights ao Supervisor continuamente
"""

import json
import os
import asyncio
from typing import Dict, Any, List, Optional, AsyncIterator
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

from ..utils.logging import get_logger, log_agent_action, log_error
from ..utils.logfire_config import AgentExecutionContext
from config.settings import get_settings


class LogEntry(BaseModel):
    """Structured log entry."""
    timestamp: datetime
    level: str
    logger: str
    message: str
    agent: Optional[str] = None
    duration: Optional[float] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class AgentMetrics(BaseModel):
    """Performance metrics for a single agent."""
    agent_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    avg_duration: float = 0.0
    min_duration: float = 0.0
    max_duration: float = 0.0
    error_rate: float = 0.0
    last_execution: Optional[datetime] = None


class RealtimeMetrics(BaseModel):
    """Real-time system metrics."""
    total_requests: int = 0
    total_errors: int = 0
    avg_response_time: float = 0.0
    agents_active: List[str] = Field(default_factory=list)
    bottlenecks: List[str] = Field(default_factory=list)
    health_score: float = 1.0  # 0.0 to 1.0
    timestamp: datetime = Field(default_factory=datetime.now)


class Anomaly(BaseModel):
    """Detected anomaly in the system."""
    type: str  # error_spike, slow_response, routing_loop, etc.
    severity: str  # low, medium, high, critical
    description: str
    affected_agent: Optional[str] = None
    detected_at: datetime = Field(default_factory=datetime.now)
    recommended_action: str


class Recommendation(BaseModel):
    """Recommendation for the Supervisor."""
    priority: str  # low, medium, high
    category: str  # performance, quality, routing, error
    message: str
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class ManagerAgent:
    """
    Manager agent that monitors system health and provides insights.

    Reads logs in real-time, analyzes performance, and provides
    recommendations to the Supervisor agent.
    """

    def __init__(self, log_dir: str = "logs"):
        self.logger = get_logger("manager_agent")
        self.settings = get_settings()
        self.log_dir = Path(log_dir)
        self._agent: Optional[Agent] = None

        # Metrics storage
        self._agent_metrics: Dict[str, AgentMetrics] = {}
        self._recent_logs: List[LogEntry] = []
        self._max_recent_logs = 1000

        # Log files to monitor
        self._log_files = {
            "agents": self.log_dir / "agents.log",
            "handoffs": self.log_dir / "handoffs.log",
            "performance": self.log_dir / "performance.log",
            "api": self.log_dir / "api.log",
            "errors": self.log_dir / "errors.log",
        }

        # File positions for streaming
        self._file_positions: Dict[str, int] = {}

        # Thresholds for anomaly detection
        self.thresholds = {
            "slow_response_seconds": 5.0,
            "error_rate_percent": 10.0,
            "handoff_limit": 5,
            "response_time_spike_multiplier": 3.0,
        }

    async def _get_agent(self) -> Agent:
        """Get or create the PydanticAI agent."""
        if self._agent is None:
            # Ensure GROQ_API_KEY is set in environment (required by PydanticAI GroqModel)
            if self.settings.groq.api_key:
                os.environ['GROQ_API_KEY'] = self.settings.groq.api_key
            model = GroqModel(self.settings.groq.default_model)
            self._agent = Agent(model)
        return self._agent

    def _parse_log_line(self, line: str) -> Optional[LogEntry]:
        """Parse a JSON log line into a LogEntry."""
        try:
            data = json.loads(line.strip())
            return LogEntry(
                timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
                level=data.get("level", "INFO"),
                logger=data.get("logger", "unknown"),
                message=data.get("message", ""),
                agent=data.get("agent") or data.get("agent_name"),
                duration=data.get("duration_seconds") or data.get("duration"),
                extra=data
            )
        except (json.JSONDecodeError, Exception):
            return None

    async def stream_logs(self, log_types: List[str] = None) -> AsyncIterator[LogEntry]:
        """
        Stream logs in real-time from specified log files.

        Args:
            log_types: List of log types to stream (agents, handoffs, performance, api, errors)

        Yields:
            LogEntry objects as they appear in the logs
        """
        if log_types is None:
            log_types = list(self._log_files.keys())

        self.logger.info(f"Starting log stream for: {log_types}")

        # Initialize file positions
        for log_type in log_types:
            log_file = self._log_files.get(log_type)
            if log_file and log_file.exists():
                self._file_positions[log_type] = log_file.stat().st_size

        while True:
            for log_type in log_types:
                log_file = self._log_files.get(log_type)
                if not log_file or not log_file.exists():
                    continue

                current_pos = self._file_positions.get(log_type, 0)
                file_size = log_file.stat().st_size

                if file_size > current_pos:
                    try:
                        with open(log_file, 'r') as f:
                            f.seek(current_pos)
                            for line in f:
                                entry = self._parse_log_line(line)
                                if entry:
                                    self._recent_logs.append(entry)
                                    if len(self._recent_logs) > self._max_recent_logs:
                                        self._recent_logs.pop(0)
                                    yield entry
                            self._file_positions[log_type] = f.tell()
                    except Exception as e:
                        self.logger.error(f"Error reading {log_type} log: {e}")

            await asyncio.sleep(0.5)  # Poll every 500ms

    def read_logs(self, log_type: str, limit: int = 100) -> List[LogEntry]:
        """
        Read the most recent logs of a specific type.

        Args:
            log_type: Type of log to read
            limit: Maximum number of entries to return

        Returns:
            List of LogEntry objects
        """
        log_file = self._log_files.get(log_type)
        if not log_file or not log_file.exists():
            return []

        entries = []
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    entry = self._parse_log_line(line)
                    if entry:
                        entries.append(entry)
        except Exception as e:
            self.logger.error(f"Error reading {log_type} logs: {e}")

        return entries

    async def analyze_agent_performance(self) -> Dict[str, AgentMetrics]:
        """
        Analyze performance metrics for all agents.

        Returns:
            Dictionary of agent names to their performance metrics
        """
        self.logger.info("Analyzing agent performance")

        with AgentExecutionContext("manager", "analyze_performance") as span:
            # Read performance and agent logs
            perf_logs = self.read_logs("performance", limit=500)
            agent_logs = self.read_logs("agents", limit=500)

            # Aggregate metrics by agent
            agent_data: Dict[str, Dict] = defaultdict(lambda: {
                "durations": [],
                "successes": 0,
                "failures": 0,
                "last_exec": None
            })

            for entry in perf_logs + agent_logs:
                agent = entry.agent or self._extract_agent_from_message(entry.message)
                if not agent:
                    continue

                if entry.duration:
                    agent_data[agent]["durations"].append(entry.duration)

                if "success" in entry.message.lower() or "completed" in entry.message.lower():
                    agent_data[agent]["successes"] += 1
                elif "error" in entry.message.lower() or "failed" in entry.message.lower():
                    agent_data[agent]["failures"] += 1

                agent_data[agent]["last_exec"] = entry.timestamp

            # Build metrics
            for agent_name, data in agent_data.items():
                durations = data["durations"]
                total = data["successes"] + data["failures"]

                self._agent_metrics[agent_name] = AgentMetrics(
                    agent_name=agent_name,
                    total_executions=total,
                    successful_executions=data["successes"],
                    failed_executions=data["failures"],
                    avg_duration=sum(durations) / len(durations) if durations else 0.0,
                    min_duration=min(durations) if durations else 0.0,
                    max_duration=max(durations) if durations else 0.0,
                    error_rate=(data["failures"] / total * 100) if total > 0 else 0.0,
                    last_execution=data["last_exec"]
                )

            if span:
                span.set_attributes({
                    "manager.agents_analyzed": len(self._agent_metrics),
                    "manager.total_logs_processed": len(perf_logs) + len(agent_logs)
                })

            log_agent_action(
                agent_name="manager",
                action="performance_analyzed",
                details={"agents_count": len(self._agent_metrics)}
            )

            return self._agent_metrics

    def _extract_agent_from_message(self, message: str) -> Optional[str]:
        """Extract agent name from log message."""
        for agent in ["search_agent", "property_agent", "scheduling_agent", "supervisor", "router"]:
            if agent in message.lower():
                return agent
        return None

    async def analyze_realtime_metrics(self) -> RealtimeMetrics:
        """
        Get real-time system metrics.

        Returns:
            RealtimeMetrics with current system state
        """
        # Use recent logs (last 5 minutes)
        cutoff = datetime.now() - timedelta(minutes=5)
        recent = [log for log in self._recent_logs if log.timestamp > cutoff]

        total_requests = len(recent)
        errors = len([log for log in recent if log.level == "ERROR"])
        durations = [log.duration for log in recent if log.duration]

        avg_response_time = sum(durations) / len(durations) if durations else 0.0

        # Active agents
        active_agents = list(set(log.agent for log in recent if log.agent))

        # Identify bottlenecks
        bottlenecks = []
        for agent, metrics in self._agent_metrics.items():
            if metrics.avg_duration > self.thresholds["slow_response_seconds"]:
                bottlenecks.append(f"{agent}: slow ({metrics.avg_duration:.2f}s avg)")
            if metrics.error_rate > self.thresholds["error_rate_percent"]:
                bottlenecks.append(f"{agent}: high error rate ({metrics.error_rate:.1f}%)")

        # Calculate health score
        health_score = 1.0
        if errors > 0:
            health_score -= min(0.3, errors / total_requests * 0.5) if total_requests > 0 else 0.1
        if avg_response_time > 3.0:
            health_score -= 0.2
        if len(bottlenecks) > 0:
            health_score -= 0.1 * len(bottlenecks)
        health_score = max(0.0, min(1.0, health_score))

        return RealtimeMetrics(
            total_requests=total_requests,
            total_errors=errors,
            avg_response_time=avg_response_time,
            agents_active=active_agents,
            bottlenecks=bottlenecks,
            health_score=health_score
        )

    async def detect_anomalies(self) -> List[Anomaly]:
        """
        Detect anomalies in the system based on log patterns.

        Returns:
            List of detected anomalies
        """
        self.logger.info("Detecting anomalies")
        anomalies = []

        # Check error logs for spikes
        error_logs = self.read_logs("errors", limit=50)
        if len(error_logs) > 10:
            recent_errors = [e for e in error_logs if e.timestamp > datetime.now() - timedelta(minutes=5)]
            if len(recent_errors) > 5:
                anomalies.append(Anomaly(
                    type="error_spike",
                    severity="high",
                    description=f"Detected {len(recent_errors)} errors in the last 5 minutes",
                    recommended_action="Review error logs and check agent health"
                ))

        # Check for slow responses
        for agent_name, metrics in self._agent_metrics.items():
            if metrics.avg_duration > self.thresholds["slow_response_seconds"]:
                anomalies.append(Anomaly(
                    type="slow_response",
                    severity="medium",
                    description=f"{agent_name} has average response time of {metrics.avg_duration:.2f}s",
                    affected_agent=agent_name,
                    recommended_action="Consider optimizing prompts or model configuration"
                ))

        # Check for high error rates
        for agent_name, metrics in self._agent_metrics.items():
            if metrics.error_rate > self.thresholds["error_rate_percent"]:
                anomalies.append(Anomaly(
                    type="high_error_rate",
                    severity="high",
                    description=f"{agent_name} has {metrics.error_rate:.1f}% error rate",
                    affected_agent=agent_name,
                    recommended_action="Investigate agent configuration and API connectivity"
                ))

        # Check handoff logs for routing loops
        handoff_logs = self.read_logs("handoffs", limit=100)
        if handoff_logs:
            # Count handoffs per conversation (simplified)
            handoff_count = len([h for h in handoff_logs if h.timestamp > datetime.now() - timedelta(minutes=10)])
            if handoff_count > self.thresholds["handoff_limit"]:
                anomalies.append(Anomaly(
                    type="routing_loop",
                    severity="medium",
                    description=f"High number of handoffs detected ({handoff_count} in 10 minutes)",
                    recommended_action="Review routing logic for potential loops"
                ))

        log_agent_action(
            agent_name="manager",
            action="anomalies_detected",
            details={"anomaly_count": len(anomalies)}
        )

        return anomalies

    async def get_supervisor_recommendations(self) -> List[Recommendation]:
        """
        Generate recommendations for the Supervisor based on log analysis.

        Returns:
            List of prioritized recommendations
        """
        self.logger.info("Generating supervisor recommendations")
        recommendations = []

        # Analyze current state
        metrics = await self.analyze_realtime_metrics()
        anomalies = await self.detect_anomalies()

        # Generate recommendations based on anomalies
        for anomaly in anomalies:
            priority = "high" if anomaly.severity in ["high", "critical"] else "medium"
            recommendations.append(Recommendation(
                priority=priority,
                category="error" if "error" in anomaly.type else "performance",
                message=f"{anomaly.description}. Action: {anomaly.recommended_action}",
                context={"anomaly_type": anomaly.type, "affected_agent": anomaly.affected_agent}
            ))

        # Add general recommendations based on metrics
        if metrics.health_score < 0.7:
            recommendations.append(Recommendation(
                priority="high",
                category="performance",
                message=f"System health is degraded ({metrics.health_score:.0%}). Consider reviewing agent configurations.",
                context={"health_score": metrics.health_score, "bottlenecks": metrics.bottlenecks}
            ))

        if metrics.avg_response_time > 3.0:
            recommendations.append(Recommendation(
                priority="medium",
                category="performance",
                message=f"Average response time is {metrics.avg_response_time:.2f}s. Consider prompt optimization.",
                context={"avg_response_time": metrics.avg_response_time}
            ))

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 2))

        log_agent_action(
            agent_name="manager",
            action="recommendations_generated",
            details={"recommendation_count": len(recommendations)}
        )

        return recommendations

    async def generate_summary_report(self) -> str:
        """
        Generate a human-readable summary report.

        Returns:
            Formatted summary string
        """
        await self.analyze_agent_performance()
        metrics = await self.analyze_realtime_metrics()
        anomalies = await self.detect_anomalies()
        recommendations = await self.get_supervisor_recommendations()

        report = f"""
=== MANAGER REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SYSTEM HEALTH: {metrics.health_score:.0%}
Active Agents: {', '.join(metrics.agents_active) or 'None'}
Total Requests (5min): {metrics.total_requests}
Total Errors (5min): {metrics.total_errors}
Avg Response Time: {metrics.avg_response_time:.2f}s

AGENT PERFORMANCE:
"""
        for agent, m in self._agent_metrics.items():
            report += f"  {agent}: {m.total_executions} calls, {m.error_rate:.1f}% errors, {m.avg_duration:.2f}s avg\n"

        if anomalies:
            report += f"\nANOMALIES DETECTED ({len(anomalies)}):\n"
            for a in anomalies[:5]:
                report += f"  [{a.severity.upper()}] {a.description}\n"

        if recommendations:
            report += f"\nRECOMMENDATIONS ({len(recommendations)}):\n"
            for r in recommendations[:5]:
                report += f"  [{r.priority.upper()}] {r.message}\n"

        return report


# Singleton instance
_manager: Optional[ManagerAgent] = None


def get_manager() -> ManagerAgent:
    """Get or create the global manager instance."""
    global _manager
    if _manager is None:
        _manager = ManagerAgent()
    return _manager
