"""
Configuração do LangSmith para tracing de operações LangGraph.

Integra o LangSmith para rastreamento completo de:
- Execuções de grafos LangGraph
- Fluxos de handoff entre agentes
- Performance de nós individuais
- Debugging de rotas e decisões
- Métricas de throughput e latência
"""

import os
import logging
from typing import Optional, Dict, Any
from functools import lru_cache
from pathlib import Path

try:
    from langsmith import Client
    from langsmith.utils import tracing_context
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    Client = None
    tracing_context = None

from config.settings import get_settings


class LangSmithConfig:
    """Configuração centralizada do LangSmith."""
    
    def __init__(self):
        self.settings = get_settings()
        self.configured = False
        self.client = None
        self.logger = logging.getLogger(__name__)
        
    def is_available(self) -> bool:
        """Verificar se LangSmith está disponível."""
        return LANGSMITH_AVAILABLE
    
    def configure_langsmith(self) -> bool:
        """
        Configurar LangSmith para tracing de LangGraph.
        
        Returns:
            bool: True se configurado com sucesso
        """
        if not self.is_available():
            self.logger.warning("LANGSMITH não disponível - install com: uv add langsmith")
            return False
            
        try:
            # Verificar configuração no .env
            api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGFUSE_SECRET_KEY")
            project_name = os.getenv("LANGSMITH_PROJECT") or "agentic-real-estate"
            endpoint = os.getenv("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com"
            
            if not api_key:
                self.logger.info("LANGSMITH API key não configurado - usando modo local")
                # Usar Logfire como fallback quando LangSmith não disponível
                return False
                
            # Configurar cliente LangSmith
            self.client = Client(
                api_url=endpoint,
                api_key=api_key
            )
            
            # Verificar conectividade
            try:
                self.client.list_datasets(limit=1)
                self.logger.info(f"SUCCESS: LangSmith configurado - projeto: {project_name}")
            except Exception as e:
                self.logger.warning(f"WARNING: LangSmith conectividade falhou: {e}")
                return False
            
            # Configurar variáveis de ambiente para tracing automático
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = project_name
            os.environ["LANGCHAIN_API_KEY"] = api_key
            os.environ["LANGCHAIN_ENDPOINT"] = endpoint
            
            self.configured = True
            self.logger.info("SUCCESS: LangSmith tracing ativado para LangGraph")
            return True
            
        except Exception as e:
            self.logger.error(f"ERROR: Erro ao configurar LangSmith: {e}")
            return False
    
    def create_run_context(
        self,
        name: str,
        run_type: str = "chain",
        inputs: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Criar contexto de execução para tracing manual.
        
        Args:
            name: Nome da execução
            run_type: Tipo de execução (chain, llm, tool, etc.)
            inputs: Inputs da execução
            metadata: Metadados adicionais
            
        Returns:
            Context manager para tracing ou None se não configurado
        """
        if not self.is_available() or not self.configured or not self.client:
            return None
            
        try:
            return tracing_context(
                name=name,
                run_type=run_type,
                inputs=inputs or {},
                metadata=metadata or {}
            )
        except Exception as e:
            self.logger.warning(f"WARNING: Falha ao criar contexto LangSmith: {e}")
            return None
    
    def log_langgraph_execution(
        self,
        graph_name: str,
        state: Dict[str, Any],
        node_name: str,
        execution_time: float,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Log específico para execuções de nós LangGraph.
        
        Args:
            graph_name: Nome do grafo
            state: Estado atual do grafo
            node_name: Nome do nó executado
            execution_time: Tempo de execução em segundos
            success: Se a execução foi bem-sucedida
            error: Mensagem de erro se houver
        """
        if not self.is_available() or not self.configured:
            return
            
        try:
            metadata = {
                "graph_name": graph_name,
                "node_name": node_name,
                "execution_time": execution_time,
                "success": success,
                "state_keys": list(state.keys()) if state else [],
                "environment": self.settings.environment
            }
            
            if error:
                metadata["error"] = error
            
            # LangSmith irá capturar automaticamente via environment variables
            # Este método fornece contexto adicional para debugging
            
        except Exception as e:
            self.logger.warning(f"WARNING: Falha ao logar execução LangGraph: {e}")
    
    def log_handoff_trace(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        state: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log de handoffs entre agentes com contexto LangGraph.
        
        Args:
            from_agent: Agente de origem
            to_agent: Agente de destino
            reason: Razão do handoff
            state: Estado atual do LangGraph
            context: Contexto adicional
        """
        if not self.is_available() or not self.configured:
            return
            
        try:
            metadata = {
                "handoff_type": "langgraph_agent_transition",
                "from_agent": from_agent,
                "to_agent": to_agent,
                "reason": reason,
                "state_size": len(str(state)) if state else 0,
                "message_count": len(state.get("messages", [])) if state else 0
            }
            
            if context:
                metadata.update({f"context_{k}": v for k, v in context.items()})
            
            # Context será capturado pelo tracing automático do LangSmith
            
        except Exception as e:
            self.logger.warning(f"WARNING: Falha ao logar handoff: {e}")
    
    def annotate_with_feedback(
        self,
        run_id: str,
        score: float,
        feedback_type: str = "user_rating",
        comment: Optional[str] = None
    ):
        """
        Adicionar feedback a uma execução específica.
        
        Args:
            run_id: ID da execução
            score: Score do feedback (0.0 - 1.0)
            feedback_type: Tipo de feedback
            comment: Comentário opcional
        """
        if not self.is_available() or not self.configured or not self.client:
            return
            
        try:
            self.client.create_feedback(
                run_id=run_id,
                key=feedback_type,
                score=score,
                comment=comment
            )
            self.logger.info(f"SUCCESS: Feedback adicionado ao run {run_id}")
            
        except Exception as e:
            self.logger.warning(f"WARNING: Falha ao adicionar feedback: {e}")


@lru_cache()
def get_langsmith_config() -> LangSmithConfig:
    """Obter instância singleton da configuração LangSmith."""
    return LangSmithConfig()


def setup_langsmith() -> bool:
    """
    Configurar LangSmith para o sistema.
    
    Returns:
        bool: True se configurado com sucesso
    """
    config = get_langsmith_config()
    return config.configure_langsmith()


def create_langgraph_tracer(graph_name: str):
    """
    Decorador para instrumentar grafos LangGraph com LangSmith.
    
    Args:
        graph_name: Nome do grafo
        
    Returns:
        Decorador ou função identidade se LangSmith não disponível
    """
    def decorator(func):
        if not LANGSMITH_AVAILABLE:
            return func
            
        def wrapper(*args, **kwargs):
            config = get_langsmith_config()
            
            if config.configured:
                with config.create_run_context(
                    name=f"langgraph_{graph_name}",
                    run_type="chain",
                    inputs={"args": args, "kwargs": kwargs},
                    metadata={"graph_name": graph_name}
                ):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
                
        return wrapper
    return decorator


# Context managers para tracing manual
class LangGraphExecutionContext:
    """Context manager para tracing de execuções LangGraph."""
    
    def __init__(self, graph_name: str, node_name: str, state: Dict[str, Any]):
        self.graph_name = graph_name
        self.node_name = node_name
        self.state = state
        self.config = get_langsmith_config()
        self.context = None
        self.start_time = None
        
    def __enter__(self):
        if self.config.is_available() and self.config.configured:
            import time
            self.start_time = time.time()
            
            self.context = self.config.create_run_context(
                name=f"{self.graph_name}.{self.node_name}",
                run_type="chain",
                inputs={"state": self.state},
                metadata={
                    "graph_name": self.graph_name,
                    "node_name": self.node_name,
                    "message_count": len(self.state.get("messages", []))
                }
            )
            
            if self.context:
                return self.context.__enter__()
        return None
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context and self.start_time:
            execution_time = time.time() - self.start_time
            
            # Log execution details
            self.config.log_langgraph_execution(
                graph_name=self.graph_name,
                state=self.state,
                node_name=self.node_name,
                execution_time=execution_time,
                success=exc_type is None,
                error=str(exc_val) if exc_val else None
            )
            
            return self.context.__exit__(exc_type, exc_val, exc_tb)


# Funções utilitárias
def log_graph_startup(graph_name: str, config: Dict[str, Any]):
    """Log de inicialização de grafo LangGraph."""
    if LANGSMITH_AVAILABLE:
        langsmith_config = get_langsmith_config()
        
        if langsmith_config.configured:
            with langsmith_config.create_run_context(
                name=f"graph_startup_{graph_name}",
                run_type="chain",
                inputs=config,
                metadata={"event": "graph_startup", "graph_name": graph_name}
            ):
                pass


def log_graph_completion(graph_name: str, final_state: Dict[str, Any], success: bool):
    """Log de finalização de grafo LangGraph."""
    if LANGSMITH_AVAILABLE:
        langsmith_config = get_langsmith_config()
        
        if langsmith_config.configured:
            with langsmith_config.create_run_context(
                name=f"graph_completion_{graph_name}",
                run_type="chain",
                inputs=final_state,
                metadata={
                    "event": "graph_completion",
                    "graph_name": graph_name,
                    "success": success,
                    "final_message_count": len(final_state.get("messages", []))
                }
            ):
                pass


def create_performance_tracer():
    """Criar tracer específico para métricas de performance LangGraph."""
    return logging.getLogger("langsmith_performance")