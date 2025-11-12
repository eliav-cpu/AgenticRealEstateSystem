"""
Real-time Observability Dashboard for Agentic Real Estate System.

Provides comprehensive monitoring and observability features:
- System health and status
- Agent performance metrics
- API call statistics
- Error tracking and analysis
- Real-time conversation flows
- Resource utilization
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List, Any, Optional
import asyncio
import json
import time
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque

from config.settings import get_settings
from ..utils.logging import get_logger

# Global metrics storage (in production, use Redis or dedicated metrics store)
class MetricsCollector:
    def __init__(self):
        self.agent_calls = defaultdict(int)
        self.agent_durations = defaultdict(list)
        self.api_calls = defaultdict(int)
        self.api_errors = defaultdict(int)
        self.handoffs = deque(maxlen=100)  # Last 100 handoffs
        self.recent_logs = deque(maxlen=200)  # Last 200 log entries
        self.active_sessions = set()
        self.system_start_time = time.time()
        
    def record_agent_call(self, agent_name: str, duration: float, success: bool):
        """Record agent execution metrics."""
        self.agent_calls[agent_name] += 1
        self.agent_durations[agent_name].append({
            'duration': duration,
            'success': success,
            'timestamp': time.time()
        })
        # Keep only last 50 calls per agent
        if len(self.agent_durations[agent_name]) > 50:
            self.agent_durations[agent_name] = self.agent_durations[agent_name][-50:]
    
    def record_api_call(self, api_name: str, success: bool, duration: Optional[float] = None):
        """Record API call metrics."""
        self.api_calls[api_name] += 1
        if not success:
            self.api_errors[api_name] += 1
    
    def record_handoff(self, from_agent: str, to_agent: str, reason: str):
        """Record agent handoff."""
        self.handoffs.append({
            'from_agent': from_agent,
            'to_agent': to_agent,
            'reason': reason,
            'timestamp': time.time()
        })
    
    def record_log(self, level: str, message: str, component: str):
        """Record log entry."""
        self.recent_logs.append({
            'level': level,
            'message': message,
            'component': component,
            'timestamp': time.time()
        })
    
    def add_session(self, session_id: str):
        """Track active session."""
        self.active_sessions.add(session_id)
    
    def remove_session(self, session_id: str):
        """Remove session when completed."""
        self.active_sessions.discard(session_id)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        current_time = time.time()
        uptime = current_time - self.system_start_time
        
        # Calculate agent performance
        agent_performance = {}
        for agent, durations in self.agent_durations.items():
            recent_calls = [d for d in durations if current_time - d['timestamp'] < 300]  # Last 5 minutes
            if recent_calls:
                avg_duration = sum(d['duration'] for d in recent_calls) / len(recent_calls)
                success_rate = sum(1 for d in recent_calls if d['success']) / len(recent_calls)
            else:
                avg_duration = 0
                success_rate = 1.0
            
            agent_performance[agent] = {
                'total_calls': self.agent_calls[agent],
                'recent_calls': len(recent_calls),
                'avg_duration': round(avg_duration, 2),
                'success_rate': round(success_rate * 100, 1)
            }
        
        # Calculate API performance
        api_performance = {}
        for api_name in self.api_calls:
            total_calls = self.api_calls[api_name]
            error_count = self.api_errors[api_name]
            success_rate = ((total_calls - error_count) / total_calls) * 100 if total_calls > 0 else 100
            
            api_performance[api_name] = {
                'total_calls': total_calls,
                'error_count': error_count,
                'success_rate': round(success_rate, 1)
            }
        
        # Recent activity
        recent_handoffs = [h for h in self.handoffs if current_time - h['timestamp'] < 300]
        recent_errors = [log for log in self.recent_logs if log['level'] == 'ERROR' and current_time - log['timestamp'] < 300]
        
        return {
            'system': {
                'uptime_seconds': round(uptime, 1),
                'uptime_formatted': self._format_duration(uptime),
                'active_sessions': len(self.active_sessions),
                'total_agent_calls': sum(self.agent_calls.values()),
                'total_api_calls': sum(self.api_calls.values()),
                'recent_errors': len(recent_errors)
            },
            'agents': agent_performance,
            'apis': api_performance,
            'recent_activity': {
                'handoffs': list(recent_handoffs),
                'errors': list(recent_errors)[-10:],  # Last 10 errors
                'logs': list(self.recent_logs)[-20:]  # Last 20 logs
            }
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"

# Global metrics collector instance
metrics = MetricsCollector()

# Dashboard router
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# WebSocket connections for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast data to all connected clients."""
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(json.dumps(data))
            except Exception:
                self.active_connections.remove(connection)

manager = ConnectionManager()

@dashboard_router.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve the main dashboard page."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agentic Real Estate - Observability Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: #f5f5f5; 
                color: #333; 
                line-height: 1.6;
            }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 1rem 2rem; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header h1 { font-size: 1.8rem; font-weight: 300; }
            .header .subtitle { opacity: 0.9; font-size: 0.9rem; }
            .container { 
                max-width: 1400px; 
                margin: 0 auto; 
                padding: 2rem; 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 1.5rem; 
            }
            .card { 
                background: white; 
                border-radius: 8px; 
                padding: 1.5rem; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                transition: transform 0.2s;
            }
            .card:hover { transform: translateY(-2px); }
            .card h3 { 
                color: #4a5568; 
                margin-bottom: 1rem; 
                font-size: 1.1rem; 
                font-weight: 600; 
                border-bottom: 2px solid #e2e8f0; 
                padding-bottom: 0.5rem; 
            }
            .metric { 
                display: flex; 
                justify-content: space-between; 
                margin: 0.8rem 0; 
                padding: 0.5rem; 
                border-radius: 4px; 
                background: #f8fafc; 
            }
            .metric-label { font-weight: 500; }
            .metric-value { 
                font-weight: 600; 
                color: #2d3748; 
            }
            .status-good { color: #38a169; }
            .status-warning { color: #d69e2e; }
            .status-error { color: #e53e3e; }
            .log-entry { 
                padding: 0.5rem; 
                border-left: 3px solid #e2e8f0; 
                margin: 0.5rem 0; 
                font-size: 0.85rem; 
                background: #f8fafc; 
            }
            .log-error { border-left-color: #e53e3e; background: #fed7d7; }
            .log-warning { border-left-color: #d69e2e; background: #fef5e7; }
            .log-info { border-left-color: #3182ce; background: #e6f3ff; }
            .timestamp { color: #718096; font-size: 0.75rem; }
            .loading { text-align: center; color: #718096; padding: 2rem; }
            .grid-wide { grid-column: span 2; }
            @media (max-width: 768px) { 
                .container { grid-template-columns: 1fr; }
                .grid-wide { grid-column: span 1; }
                .header { padding: 1rem; }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏠 Agentic Real Estate Dashboard</h1>
            <div class="subtitle">Real-time System Observability & Performance Monitoring</div>
        </div>
        
        <div class="container">
            <div class="card">
                <h3>🚀 System Status</h3>
                <div id="system-metrics" class="loading">Connecting...</div>
            </div>
            
            <div class="card">
                <h3>🤖 Agent Performance</h3>
                <div id="agent-metrics" class="loading">Loading...</div>
            </div>
            
            <div class="card">
                <h3>🌐 API Performance</h3>
                <div id="api-metrics" class="loading">Loading...</div>
            </div>
            
            <div class="card">
                <h3>🔄 Recent Handoffs</h3>
                <div id="handoff-activity" class="loading">Loading...</div>
            </div>
            
            <div class="card grid-wide">
                <h3>📋 Recent System Logs</h3>
                <div id="recent-logs" class="loading">Loading...</div>
            </div>
        </div>

        <script>
            let ws;
            let reconnectInterval = 5000;
            
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/dashboard/ws`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function() {
                    console.log('WebSocket connected');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                };
                
                ws.onclose = function() {
                    console.log('WebSocket disconnected, reconnecting...');
                    setTimeout(connectWebSocket, reconnectInterval);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                };
            }
            
            function updateDashboard(data) {
                updateSystemMetrics(data.system);
                updateAgentMetrics(data.agents);
                updateApiMetrics(data.apis);
                updateRecentActivity(data.recent_activity);
            }
            
            function updateSystemMetrics(system) {
                const html = `
                    <div class="metric">
                        <span class="metric-label">Uptime</span>
                        <span class="metric-value status-good">${system.uptime_formatted}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Active Sessions</span>
                        <span class="metric-value">${system.active_sessions}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Agent Calls</span>
                        <span class="metric-value">${system.total_agent_calls}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total API Calls</span>
                        <span class="metric-value">${system.total_api_calls}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Recent Errors</span>
                        <span class="metric-value ${system.recent_errors > 0 ? 'status-error' : 'status-good'}">${system.recent_errors}</span>
                    </div>
                `;
                document.getElementById('system-metrics').innerHTML = html;
            }
            
            function updateAgentMetrics(agents) {
                let html = '';
                for (const [agent, metrics] of Object.entries(agents)) {
                    const statusClass = metrics.success_rate >= 95 ? 'status-good' : 
                                      metrics.success_rate >= 80 ? 'status-warning' : 'status-error';
                    html += `
                        <div class="metric">
                            <span class="metric-label">${agent}</span>
                            <span class="metric-value">
                                ${metrics.total_calls} calls | 
                                <span class="${statusClass}">${metrics.success_rate}%</span> | 
                                ${metrics.avg_duration}s avg
                            </span>
                        </div>
                    `;
                }
                document.getElementById('agent-metrics').innerHTML = html || '<div class="loading">No agent data yet</div>';
            }
            
            function updateApiMetrics(apis) {
                let html = '';
                for (const [api, metrics] of Object.entries(apis)) {
                    const statusClass = metrics.success_rate >= 95 ? 'status-good' : 
                                      metrics.success_rate >= 80 ? 'status-warning' : 'status-error';
                    html += `
                        <div class="metric">
                            <span class="metric-label">${api}</span>
                            <span class="metric-value">
                                ${metrics.total_calls} calls | 
                                <span class="${statusClass}">${metrics.success_rate}%</span>
                                ${metrics.error_count > 0 ? ` | ${metrics.error_count} errors` : ''}
                            </span>
                        </div>
                    `;
                }
                document.getElementById('api-metrics').innerHTML = html || '<div class="loading">No API data yet</div>';
            }
            
            function updateRecentActivity(activity) {
                // Update handoffs
                let handoffHtml = '';
                activity.handoffs.slice(-5).forEach(handoff => {
                    const time = new Date(handoff.timestamp * 1000).toLocaleTimeString();
                    handoffHtml += `
                        <div class="log-entry log-info">
                            <div>${handoff.from_agent} → ${handoff.to_agent}</div>
                            <div class="timestamp">${time} | ${handoff.reason}</div>
                        </div>
                    `;
                });
                document.getElementById('handoff-activity').innerHTML = handoffHtml || '<div class="loading">No recent handoffs</div>';
                
                // Update logs
                let logHtml = '';
                activity.logs.slice(-10).forEach(log => {
                    const time = new Date(log.timestamp * 1000).toLocaleTimeString();
                    const logClass = log.level === 'ERROR' ? 'log-error' : 
                                   log.level === 'WARNING' ? 'log-warning' : 'log-info';
                    logHtml += `
                        <div class="log-entry ${logClass}">
                            <div>[${log.level}] ${log.component}: ${log.message}</div>
                            <div class="timestamp">${time}</div>
                        </div>
                    `;
                });
                document.getElementById('recent-logs').innerHTML = logHtml || '<div class="loading">No recent logs</div>';
            }
            
            // Initialize connection
            connectWebSocket();
            
            // Refresh data every 5 seconds as fallback
            setInterval(() => {
                if (ws.readyState !== WebSocket.OPEN) {
                    fetch('/dashboard/api/metrics')
                        .then(response => response.json())
                        .then(data => updateDashboard(data))
                        .catch(console.error);
                }
            }, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@dashboard_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Send metrics every 3 seconds
            metrics_data = metrics.get_metrics_summary()
            await websocket.send_text(json.dumps(metrics_data))
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@dashboard_router.get("/api/metrics")
async def get_metrics():
    """REST API endpoint for metrics (fallback for WebSocket)."""
    return metrics.get_metrics_summary()

@dashboard_router.post("/api/record/agent")
async def record_agent_call(data: Dict[str, Any]):
    """Record agent execution data."""
    metrics.record_agent_call(
        data.get('agent_name'),
        data.get('duration', 0),
        data.get('success', True)
    )
    
    # Broadcast update to connected clients
    await manager.broadcast(metrics.get_metrics_summary())
    return {"status": "recorded"}

@dashboard_router.post("/api/record/api")
async def record_api_call(data: Dict[str, Any]):
    """Record API call data."""
    metrics.record_api_call(
        data.get('api_name'),
        data.get('success', True),
        data.get('duration')
    )
    return {"status": "recorded"}

@dashboard_router.post("/api/record/handoff")
async def record_handoff(data: Dict[str, Any]):
    """Record agent handoff."""
    metrics.record_handoff(
        data.get('from_agent'),
        data.get('to_agent'),
        data.get('reason', 'Unknown')
    )
    
    # Broadcast update to connected clients
    await manager.broadcast(metrics.get_metrics_summary())
    return {"status": "recorded"}

@dashboard_router.post("/api/record/log")
async def record_log(data: Dict[str, Any]):
    """Record log entry."""
    metrics.record_log(
        data.get('level', 'INFO'),
        data.get('message', ''),
        data.get('component', 'System')
    )
    return {"status": "recorded"}

# Utility functions for integration with the main system
def get_dashboard_metrics():
    """Get current metrics collector instance."""
    return metrics

async def broadcast_metrics_update():
    """Broadcast metrics update to all connected dashboard clients."""
    if manager.active_connections:
        await manager.broadcast(metrics.get_metrics_summary())