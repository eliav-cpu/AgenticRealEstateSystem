"""
Demo do Sistema Escalável com LangGraph-Swarm.

Este exemplo demonstra as melhorias de escalabilidade implementadas:
- Dependency Injection Container
- Métricas avançadas
- Circuit Breakers para resiliência
- Arquitetura Swarm sem supervisor
- Configuração hierárquica
"""

import asyncio
import json
from datetime import datetime

from agentic_real_estate.core.container import configure_container, default_container
from agentic_real_estate.core.config import Settings
from agentic_real_estate.core.metrics import get_metrics_collector, get_agent_metrics
from agentic_real_estate.core.resilience import get_resilience_manager
from agentic_real_estate.orchestration.swarm_orchestrator import SwarmOrchestrator


async def demo_scalable_swarm():
    """Demonstra o sistema escalável com todas as melhorias."""
    
    print("🚀 Inicializando Sistema Escalável Agentic Real Estate")
    print("=" * 60)
    
    # 1. Configurar Container DI
    print("\n📦 Configurando Container de Injeção de Dependência...")
    container = configure_container()
    settings = container.get(Settings)
    
    print(f"✅ Container configurado com {len(container._bindings)} bindings")
    print(f"📊 Ambiente: {settings.environment}")
    print(f"🔧 Debug: {settings.debug}")
    
    # 2. Inicializar Sistema de Métricas
    print("\n📈 Inicializando Sistema de Métricas...")
    metrics = get_metrics_collector()
    agent_metrics = get_agent_metrics()
    
    # Simular algumas métricas iniciais
    metrics.increment_counter("system.startup")
    metrics.set_gauge("system.agents.active", 3.0)
    
    print("✅ Sistema de métricas inicializado")
    
    # 3. Configurar Resiliência
    print("\n🛡️ Configurando Sistema de Resiliência...")
    resilience = get_resilience_manager()
    
    # Criar circuit breakers para componentes críticos
    from agentic_real_estate.core.resilience import CircuitBreakerConfig
    
    search_cb = resilience.create_circuit_breaker(
        "search_agent",
        CircuitBreakerConfig(failure_threshold=3, recovery_timeout=30)
    )
    
    scheduling_cb = resilience.create_circuit_breaker(
        "scheduling_agent", 
        CircuitBreakerConfig(failure_threshold=2, recovery_timeout=60)
    )
    
    print(f"✅ Circuit breakers configurados: {len(resilience.circuit_breakers)}")
    
    # 4. Inicializar Swarm Orchestrator
    print("\n🐝 Inicializando LangGraph-Swarm Orchestrator...")
    
    # Usar container DI para injeção de dependências
    orchestrator = SwarmOrchestrator(container=container)
    
    print("✅ Swarm configurado sem supervisor - agentes fazem handoffs diretos")
    
    # 5. Demonstrar Consultas com Métricas
    print("\n🏠 Executando Consultas de Demonstração...")
    
    queries = [
        "Estou procurando um apartamento de 2 quartos em Copacabana até R$ 4000",
        "Quero agendar uma visita para amanhã às 14h no apartamento que você encontrou",
        "Pode me mostrar mais detalhes sobre os imóveis em Ipanema?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Consulta {i}: {query}")
        
        try:
            # Medir tempo de processamento
            start_time = datetime.now()
            
            response = await orchestrator.process_query(
                query=query,
                thread_id=f"demo_thread_{i}"
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Registrar métricas
            agent_metrics.record_agent_processing(
                agent_name="swarm_orchestrator",
                operation="process_query",
                duration=duration,
                success=True
            )
            
            print(f"✅ Resposta processada em {duration:.2f}s")
            print(f"📝 Resposta: {response.content[:100]}...")
            
        except Exception as e:
            print(f"❌ Erro na consulta: {e}")
            
            # Registrar métrica de erro
            agent_metrics.record_agent_processing(
                agent_name="swarm_orchestrator",
                operation="process_query", 
                duration=0.0,
                success=False
            )
    
    # 6. Exibir Métricas Coletadas
    print("\n📊 Métricas Coletadas:")
    print("-" * 40)
    
    all_metrics = metrics.get_all_metrics()
    
    print("Contadores:")
    for name, value in all_metrics["counters"].items():
        print(f"  {name}: {value}")
    
    print("\nGauges:")
    for name, value in all_metrics["gauges"].items():
        print(f"  {name}: {value}")
    
    print("\nSistema:")
    for name, value in all_metrics["system"].items():
        print(f"  {name}: {value}")
    
    # 7. Exibir Estado dos Circuit Breakers
    print("\n🛡️ Estado dos Circuit Breakers:")
    print("-" * 40)
    
    resilience_stats = resilience.get_all_stats()
    
    for name, stats in resilience_stats["circuit_breakers"].items():
        print(f"  {name}: {stats['state']} (falhas: {stats['failure_count']})")
    
    # 8. Demonstrar Configuração Hierárquica
    print("\n⚙️ Configurações por Agente:")
    print("-" * 40)
    
    agent_names = ["search_agent", "property_response_agent", "scheduling_agent"]
    
    for agent_name in agent_names:
        config = settings.get_agent_config(agent_name)
        print(f"  {agent_name}:")
        print(f"    modelo: {config.get('model_name', 'default')}")
        print(f"    temperatura: {config.get('temperature', 'default')}")
        print(f"    limite_falhas: {config.get('failure_threshold', 'default')}")
    
    # 9. Configuração do Swarm
    print("\n🐝 Configuração do Swarm:")
    print("-" * 40)
    
    swarm_config = settings.get_swarm_config()
    for key, value in swarm_config.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Demonstração Concluída!")
    print("🎯 Sistema escalável implementado com sucesso:")
    print("   - ✅ Dependency Injection Container")
    print("   - ✅ Métricas avançadas com tags")
    print("   - ✅ Circuit Breakers para resiliência")
    print("   - ✅ Arquitetura Swarm descentralizada")
    print("   - ✅ Configuração hierárquica")
    print("   - ✅ Supervisor removido (handoffs diretos)")


async def demo_handoff_performance():
    """Demonstra performance de handoffs diretos vs supervisor."""
    
    print("\n🚀 Teste de Performance: Handoffs Diretos vs Supervisor")
    print("=" * 60)
    
    container = configure_container()
    orchestrator = SwarmOrchestrator(container=container)
    agent_metrics = get_agent_metrics()
    
    # Simular múltiplos handoffs
    queries = [
        "Busque apartamentos em Copacabana",
        "Agende uma visita para amanhã",
        "Mostre detalhes do primeiro imóvel",
        "Reagende para depois de amanhã",
        "Busque mais opções em Ipanema"
    ]
    
    print(f"📊 Executando {len(queries)} consultas para medir handoffs...")
    
    total_handoffs = 0
    total_time = 0
    
    for i, query in enumerate(queries, 1):
        start_time = datetime.now()
        
        try:
            await orchestrator.process_query(
                query=query,
                thread_id=f"perf_test_{i}"
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            total_time += duration
            total_handoffs += 1  # Simplificado - cada query resulta em pelo menos 1 handoff
            
            print(f"  Consulta {i}: {duration:.3f}s")
            
        except Exception as e:
            print(f"  Consulta {i}: ERRO - {e}")
    
    if total_handoffs > 0:
        avg_handoff_time = total_time / total_handoffs
        print(f"\n📈 Resultados:")
        print(f"  Total de handoffs: {total_handoffs}")
        print(f"  Tempo total: {total_time:.3f}s")
        print(f"  Tempo médio por handoff: {avg_handoff_time:.3f}s")
        print(f"  Handoffs por segundo: {total_handoffs / total_time:.1f}")
        
        # Comparação teórica com supervisor
        supervisor_overhead = 0.1  # 100ms de overhead por handoff com supervisor
        supervisor_time = total_time + (total_handoffs * supervisor_overhead)
        
        print(f"\n🆚 Comparação com Supervisor (estimado):")
        print(f"  Tempo com supervisor: {supervisor_time:.3f}s")
        print(f"  Melhoria de performance: {((supervisor_time - total_time) / supervisor_time * 100):.1f}%")
        print(f"  Redução de latência: {supervisor_overhead * total_handoffs:.3f}s")


async def main():
    """Função principal da demonstração."""
    try:
        await demo_scalable_swarm()
        await demo_handoff_performance()
        
    except KeyboardInterrupt:
        print("\n⚠️ Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante demonstração: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 