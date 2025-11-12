"""
Container de Injeção de Dependências

Sistema thread-safe de DI para o sistema agêntico.
"""

import asyncio
import inspect
import threading
from typing import Any, Dict, Type, TypeVar, Callable, Optional, Union
from functools import wraps
from contextlib import asynccontextmanager, contextmanager

from .logging import get_logger
from config.settings import Settings


T = TypeVar('T')


class DIScope:
    """Escopos de injeção de dependências."""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class DIContainer:
    """Container thread-safe de injeção de dependências."""
    
    def __init__(self):
        self._services: Dict[Type, Dict[str, Any]] = {}
        self._instances: Dict[Type, Any] = {}
        self._scoped_instances: Dict[str, Dict[Type, Any]] = {}
        self._lock = threading.RLock()
        self._logger = get_logger("container")
        self._scope_counter = 0
    
    def register(
        self,
        interface: Type[T],
        implementation: Union[Type[T], Callable[..., T], T],
        scope: str = DIScope.SINGLETON,
        name: Optional[str] = None
    ) -> 'DIContainer':
        """Registrar um serviço no container."""
        with self._lock:
            if interface not in self._services:
                self._services[interface] = {}
            
            service_key = name or "default"
            self._services[interface][service_key] = {
                "implementation": implementation,
                "scope": scope,
                "name": name
            }
            
            self._logger.debug(f"Registered {interface.__name__} with scope {scope}")
            return self
    
    def get(self, interface: Type[T], name: Optional[str] = None) -> T:
        """Resolver e obter instância do serviço."""
        with self._lock:
            service_key = name or "default"
            
            if interface not in self._services or service_key not in self._services[interface]:
                raise ValueError(f"Service {interface.__name__} not registered")
            
            service_info = self._services[interface][service_key]
            scope = service_info["scope"]
            implementation = service_info["implementation"]
            
            if scope == DIScope.SINGLETON:
                cache_key = (interface, service_key)
                if cache_key not in self._instances:
                    self._instances[cache_key] = self._create_instance(implementation)
                return self._instances[cache_key]
            else:
                return self._create_instance(implementation)
    
    def _create_instance(self, implementation: Union[Type[T], Callable[..., T], T]) -> T:
        """Criar instância resolvendo dependências."""
        if not (inspect.isclass(implementation) or inspect.isfunction(implementation)):
            return implementation
        
        if inspect.isfunction(implementation) or inspect.isclass(implementation):
            return self._call_with_injection(implementation)
        
        raise ValueError(f"Cannot create instance of {implementation}")
    
    def _call_with_injection(self, func_or_class: Callable) -> Any:
        """Chamar função/construtor injetando dependências."""
        sig = inspect.signature(func_or_class)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                annotation = param.annotation
                if annotation in self._services:
                    kwargs[param_name] = self.get(annotation)
        
        return func_or_class(**kwargs)
    
    async def setup(self, settings: Settings) -> None:
        """Configurar container com serviços padrão."""
        self._logger.info("Setting up DI container")
        
        # Registrar configurações
        self.register(Settings, settings, DIScope.SINGLETON)
        
        # Registrar orquestrador swarm
        from ..orchestration.swarm import SwarmOrchestrator
        self.register(SwarmOrchestrator, SwarmOrchestrator, DIScope.SINGLETON)
        
        self._logger.info("DI container setup completed")
    
    async def cleanup(self) -> None:
        """Limpar recursos do container."""
        self._logger.info("Cleaning up DI container")
        with self._lock:
            self._instances.clear()
            self._scoped_instances.clear()
        self._logger.info("DI container cleanup completed")


# Instância global do container
container = DIContainer() 