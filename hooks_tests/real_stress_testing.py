#!/usr/bin/env python3
"""
Sistema de Stress Testing REAL - Real Estate Assistant
Integrado com OpenRouter/Ollama real e base de dados Mock
"""

import asyncio
import time
import random
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import sys
import os
from pathlib import Path
from langchain_core.messages import HumanMessage

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

# Importar componentes do sistema real
from app.orchestration.swarm import SwarmOrchestrator
from app.utils.logging import get_logger, log_agent_action, log_api_call, log_error
from config.settings import get_settings

@dataclass
class RealVirtualUser:
    """Usuário virtual para testes com sistema real"""
    name: str
    profile: str
    budget_min: int
    budget_max: int
    bedrooms: int
    location_preferences: List[str]
    personality_traits: List[str]
    conversation_style: str
    session_id: str
    
    def generate_realistic_questions(self) -> List[str]:
        """Gera perguntas realistas baseadas no perfil para sistema Mock"""
        base_questions = [
            f"Hi, I'm looking for a {self.bedrooms}-bedroom apartment in Miami",
            f"What properties do you have under ${self.budget_max:,}?",
            f"I need something with at least {self.bedrooms} bedrooms",
            "Can you tell me about the neighborhood?",
            "What's the square footage of available properties?",
            "When can I schedule a viewing?",
            "Are pets allowed in these properties?",
            "What's included in the rent?",
            "How's the parking situation?",
            "What are the nearby amenities?"
        ]
        
        # Perguntas específicas para dados Mock
        mock_specific = [
            "Tell me about the property at 501 Sw 6th Ct, Apt 215",
            "What properties do you have in Miami-Dade?",
            "Show me apartments with more than 600 sq ft",
            "I'm interested in properties built after 1920",
            "What's available in the $1600 price range?",
            "Do you have any 1-bedroom apartments available?",
            "Tell me about properties in Miami, FL"
        ]
        
        # Personalizar baseado no perfil
        if "family" in self.profile.lower():
            base_questions.extend([
                "Are there good schools nearby?",
                "Is it family-friendly?",
                "Are there parks for kids?"
            ])
        elif "professional" in self.profile.lower():
            base_questions.extend([
                "How's the commute to downtown Miami?",
                "Is there good internet connectivity?",
                "Any coworking spaces nearby?"
            ])
        elif "student" in self.profile.lower():
            base_questions.extend([
                "Is it close to the university?",
                "Are there study spaces?",
                "What's the public transportation like?"
            ])
        
        # Combinar perguntas gerais com específicas do Mock
        all_questions = base_questions + mock_specific
        return random.sample(all_questions, min(len(all_questions), 10))

class RealSystemStressTester:
    """Sistema de stress testing integrado com sistema agêntico real"""
    
    def __init__(self):
        self.logger = get_logger("real_stress_tester")
        self.swarm = SwarmOrchestrator()
        self.virtual_users = self._create_real_virtual_users()
        self.mock_api_base = "http://localhost:8000"
        self.test_results = []
        
        # Verificar se sistema Mock está disponível
        self._verify_mock_system()
    
    def _verify_mock_system(self):
        """Verifica se o sistema Mock está rodando"""
        try:
            response = requests.get(f"{self.mock_api_base}/api/properties/search", timeout=5)
            if response.status_code == 200:
                data = response.json()
                properties_count = len(data.get("properties", []))
                self.logger.info(f"✅ Sistema Mock conectado - {properties_count} propriedades disponíveis")
            else:
                self.logger.warning(f"⚠️ Sistema Mock respondeu com status {response.status_code}")
        except Exception as e:
            self.logger.error(f"❌ Sistema Mock não está disponível: {e}")
            self.logger.info("💡 Para iniciar o sistema Mock, execute: python main.py")
    
    def _create_real_virtual_users(self) -> List[RealVirtualUser]:
        """Cria usuários virtuais para testes reais"""
        return [
            RealVirtualUser(
                name="Sarah Johnson",
                profile="Young Professional",
                budget_min=1500,
                budget_max=2500,
                bedrooms=1,
                location_preferences=["Miami", "Brickell", "Downtown"],
                personality_traits=["detail-oriented", "budget-conscious"],
                conversation_style="direct",
                session_id="stress_test_sarah"
            ),
            RealVirtualUser(
                name="Mike Rodriguez",
                profile="Family Man",
                budget_min=2500,
                budget_max=4000,
                bedrooms=3,
                location_preferences=["Coral Gables", "Aventura", "Doral"],
                personality_traits=["family-focused", "safety-conscious"],
                conversation_style="thorough",
                session_id="stress_test_mike"
            ),
            RealVirtualUser(
                name="Emily Chen",
                profile="Graduate Student",
                budget_min=800,
                budget_max=1500,
                bedrooms=1,
                location_preferences=["University Area", "Coconut Grove"],
                personality_traits=["budget-limited", "location-flexible"],
                conversation_style="casual",
                session_id="stress_test_emily"
            ),
            RealVirtualUser(
                name="David Thompson",
                profile="Executive",
                budget_min=4000,
                budget_max=8000,
                bedrooms=2,
                location_preferences=["South Beach", "Brickell", "Key Biscayne"],
                personality_traits=["luxury-seeking", "convenience-focused"],
                conversation_style="efficient",
                session_id="stress_test_david"
            ),
            RealVirtualUser(
                name="Lisa Martinez",
                profile="Retiree",
                budget_min=2000,
                budget_max=3500,
                bedrooms=2,
                location_preferences=["Aventura", "Bal Harbour", "Sunny Isles"],
                personality_traits=["comfort-focused", "community-oriented"],
                conversation_style="friendly",
                session_id="stress_test_lisa"
            )
        ]
    
    async def simulate_real_conversation(self, user: RealVirtualUser, num_questions: int = 5) -> Dict[str, Any]:
        """Simula conversa usando sistema agêntico REAL"""
        
        self.logger.info(f"🎭 Iniciando conversa real com {user.name} ({user.profile})")
        
        conversation_log = []
        start_time = time.time()
        
        # Gerar perguntas realistas
        questions = user.generate_realistic_questions()
        selected_questions = random.sample(questions, min(num_questions, len(questions)))
        
        # Configurar contexto inicial com dados Mock
        initial_context = {
            "data_mode": "mock",
            "property_context": {
                "formattedAddress": "501 Sw 6th Ct, Apt 215, Miami, FL 33130",
                "price": 1600,
                "bedrooms": 1,
                "bathrooms": 1,
                "squareFootage": 600,
                "propertyType": "Apartment",
                "yearBuilt": 1925,
                "city": "Miami",
                "state": "FL"
            }
        }
        
        for i, question in enumerate(selected_questions):
            question_start = time.time()
            
            try:
                # Simular delay humano
                if i > 0:
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                
                self.logger.info(f"   Q{i+1}: {question}")
                
                # Usar sistema agêntico REAL
                message_data = {
                    "messages": [HumanMessage(content=question)],
                    "session_id": user.session_id,
                    "current_agent": "property_agent",
                    "context": initial_context
                }
                
                # 🔥 NOVO: Config com thread_id para memória persistente
                config = {
                    "configurable": {
                        "thread_id": user.session_id,  # Usar session_id como thread_id
                        "user_id": user.name.replace(" ", "_").lower(),  # Para memória de longo prazo
                        "checkpoint_ns": "stress_test"  # Namespace para checkpoints
                    }
                }
                
                result = await self.swarm.process_message(message_data, config)  # 🔥 PASSAR CONFIG
                response_time = time.time() - question_start
                
                # Extrair resposta
                if "messages" in result and result["messages"]:
                    agent_response = result["messages"][-1].content
                    success = True
                    error = None
                else:
                    agent_response = "No response received"
                    success = False
                    error = "Empty response"
                
                conversation_log.append({
                    "question": question,
                    "response": agent_response,
                    "response_time": response_time,
                    "success": success,
                    "error": error,
                    "agent_info": result.get("current_agent", "unknown"),
                    "context": result.get("context", {})
                })
                
                self.logger.info(f"      ✅ Resposta ({response_time:.2f}s): {agent_response[:100]}...")
                
                # Log da interação
                log_agent_action(
                    agent_name="stress_test",
                    action="user_interaction",
                    details={
                        "user": user.name,
                        "question_number": i + 1,
                        "response_time": response_time,
                        "success": success
                    }
                )
                
            except Exception as e:
                response_time = time.time() - question_start
                error_msg = str(e)
                
                conversation_log.append({
                    "question": question,
                    "response": f"Error: {error_msg}",
                    "response_time": response_time,
                    "success": False,
                    "error": error_msg,
                    "agent_info": "error",
                    "context": {}
                })
                
                self.logger.error(f"      ❌ Erro ({response_time:.2f}s): {error_msg}")
                
                # Log do erro
                log_error(e, context={
                    "user": user.name,
                    "question": question,
                    "test_type": "stress_test"
                })
        
        total_time = time.time() - start_time
        successful_responses = sum(1 for log in conversation_log if log["success"])
        
        result = {
            "user": user,
            "conversation_log": conversation_log,
            "total_time": total_time,
            "questions_asked": len(selected_questions),
            "successful_responses": successful_responses,
            "success_rate": (successful_responses / len(selected_questions) * 100) if selected_questions else 0,
            "average_response_time": sum(log["response_time"] for log in conversation_log) / len(conversation_log) if conversation_log else 0
        }
        
        self.logger.info(f"✅ Conversa concluída - {user.name}: {successful_responses}/{len(selected_questions)} sucessos")
        return result
    
    async def run_real_stress_test(self, concurrent_users: int = 3, questions_per_user: int = 5) -> Dict[str, Any]:
        """Executa stress test com sistema agêntico REAL"""
        
        self.logger.info(f"🚀 INICIANDO STRESS TEST REAL")
        self.logger.info(f"   • Usuários simultâneos: {concurrent_users}")
        self.logger.info(f"   • Perguntas por usuário: {questions_per_user}")
        self.logger.info(f"   • Sistema: OpenRouter + Ollama + Mock Data")
        
        start_time = time.time()
        
        # Selecionar usuários para teste
        test_users = random.sample(self.virtual_users, min(concurrent_users, len(self.virtual_users)))
        
        self.logger.info(f"👥 Usuários selecionados: {[u.name for u in test_users]}")
        
        # Executar conversas em paralelo usando sistema real
        self.logger.info(f"💬 Executando conversas através do SwarmOrchestrator...")
        
        tasks = [
            self.simulate_real_conversation(user, questions_per_user) 
            for user in test_users
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Processar resultados
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        # Calcular estatísticas
        total_questions = sum(r["questions_asked"] for r in successful_results)
        total_successful = sum(r["successful_responses"] for r in successful_results)
        avg_response_time = sum(r["average_response_time"] for r in successful_results) / len(successful_results) if successful_results else 0
        overall_success_rate = (total_successful / total_questions * 100) if total_questions > 0 else 0
        
        # Calcular estatísticas por agente
        agent_stats = self._calculate_agent_statistics(successful_results)
        
        test_summary = {
            "test_config": {
                "concurrent_users": concurrent_users,
                "questions_per_user": questions_per_user,
                "total_users_tested": len(test_users),
                "system_type": "real_agentic_system",
                "data_source": "mock_api"
            },
            "execution_stats": {
                "total_time": total_time,
                "total_questions": total_questions,
                "successful_responses": total_successful,
                "failed_responses": total_questions - total_successful,
                "success_rate": overall_success_rate,
                "average_response_time": avg_response_time,
                "questions_per_second": total_questions / total_time if total_time > 0 else 0
            },
            "agent_statistics": agent_stats,
            "user_results": successful_results,
            "failures": failed_results,
            "performance_grade": self._calculate_performance_grade(total_successful, total_questions, avg_response_time),
            "system_health": self._assess_system_health(successful_results)
        }
        
        # Log do resultado final
        log_agent_action(
            agent_name="stress_test",
            action="test_completed",
            details={
                "success_rate": overall_success_rate,
                "total_questions": total_questions,
                "performance_grade": test_summary["performance_grade"],
                "concurrent_users": concurrent_users
            }
        )
        
        self.test_results.append(test_summary)
        return test_summary
    
    def _calculate_agent_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estatísticas por agente"""
        agent_interactions = {}
        
        for result in results:
            for log in result["conversation_log"]:
                agent = log.get("agent_info", "unknown")
                if agent not in agent_interactions:
                    agent_interactions[agent] = {
                        "total_interactions": 0,
                        "successful_interactions": 0,
                        "total_response_time": 0.0,
                        "errors": []
                    }
                
                agent_interactions[agent]["total_interactions"] += 1
                agent_interactions[agent]["total_response_time"] += log["response_time"]
                
                if log["success"]:
                    agent_interactions[agent]["successful_interactions"] += 1
                else:
                    agent_interactions[agent]["errors"].append(log.get("error", "Unknown error"))
        
        # Calcular métricas finais
        agent_stats = {}
        for agent, stats in agent_interactions.items():
            if stats["total_interactions"] > 0:
                agent_stats[agent] = {
                    "total_interactions": stats["total_interactions"],
                    "success_rate": (stats["successful_interactions"] / stats["total_interactions"]) * 100,
                    "average_response_time": stats["total_response_time"] / stats["total_interactions"],
                    "error_count": len(stats["errors"]),
                    "common_errors": list(set(stats["errors"]))[:3]  # Top 3 erros únicos
                }
        
        return agent_stats
    
    def _assess_system_health(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Avalia saúde geral do sistema"""
        total_conversations = len(results)
        if total_conversations == 0:
            return {"status": "critical", "issues": ["No successful conversations"]}
        
        # Calcular métricas de saúde
        avg_success_rate = sum(r["success_rate"] for r in results) / total_conversations
        avg_response_time = sum(r["average_response_time"] for r in results) / total_conversations
        
        issues = []
        if avg_success_rate < 80:
            issues.append(f"Low success rate: {avg_success_rate:.1f}%")
        if avg_response_time > 5.0:
            issues.append(f"High response time: {avg_response_time:.2f}s")
        
        # Determinar status
        if avg_success_rate >= 95 and avg_response_time <= 3.0:
            status = "excellent"
        elif avg_success_rate >= 85 and avg_response_time <= 5.0:
            status = "good"
        elif avg_success_rate >= 70 and avg_response_time <= 8.0:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "status": status,
            "average_success_rate": avg_success_rate,
            "average_response_time": avg_response_time,
            "total_conversations": total_conversations,
            "issues": issues
        }
    
    def _calculate_performance_grade(self, successful: int, total: int, avg_time: float) -> str:
        """Calcula nota de performance"""
        success_rate = (successful / total * 100) if total > 0 else 0
        
        if success_rate >= 95 and avg_time < 2.0:
            return "A+ (Excelente)"
        elif success_rate >= 90 and avg_time < 3.0:
            return "A (Muito Bom)"
        elif success_rate >= 80 and avg_time < 5.0:
            return "B (Bom)"
        elif success_rate >= 70 and avg_time < 8.0:
            return "C (Satisfatório)"
        else:
            return "D (Precisa Melhorar)"
    
    def generate_real_system_report(self, results: Dict[str, Any]) -> str:
        """Gera relatório detalhado do sistema real"""
        
        report = f"""
🔬 RELATÓRIO DE STRESS TEST - SISTEMA AGÊNTICO REAL
{'='*70}

🎯 CONFIGURAÇÃO DO TESTE:
• Usuários Simultâneos: {results['test_config']['concurrent_users']}
• Perguntas por Usuário: {results['test_config']['questions_per_user']}
• Sistema: {results['test_config']['system_type'].upper()}
• Fonte de Dados: {results['test_config']['data_source'].upper()}

⚡ ESTATÍSTICAS DE EXECUÇÃO:
• Tempo Total: {results['execution_stats']['total_time']:.2f}s
• Total de Perguntas: {results['execution_stats']['total_questions']}
• Respostas Bem-sucedidas: {results['execution_stats']['successful_responses']}
• Respostas com Falha: {results['execution_stats']['failed_responses']}
• Taxa de Sucesso: {results['execution_stats']['success_rate']:.1f}%
• Tempo Médio de Resposta: {results['execution_stats']['average_response_time']:.2f}s
• Perguntas por Segundo: {results['execution_stats']['questions_per_second']:.2f}

🎯 NOTA DE PERFORMANCE: {results['performance_grade']}

🤖 ESTATÍSTICAS POR AGENTE:
"""
        
        for agent, stats in results['agent_statistics'].items():
            report += f"""
• {agent.upper()}:
  - Interações: {stats['total_interactions']}
  - Taxa de Sucesso: {stats['success_rate']:.1f}%
  - Tempo Médio: {stats['average_response_time']:.2f}s
  - Erros: {stats['error_count']}
"""
        
        report += f"""
🏥 SAÚDE DO SISTEMA:
• Status: {results['system_health']['status'].upper()}
• Taxa de Sucesso Média: {results['system_health']['average_success_rate']:.1f}%
• Tempo de Resposta Médio: {results['system_health']['average_response_time']:.2f}s
• Conversas Totais: {results['system_health']['total_conversations']}
"""
        
        if results['system_health']['issues']:
            report += "\n⚠️ PROBLEMAS IDENTIFICADOS:\n"
            for issue in results['system_health']['issues']:
                report += f"• {issue}\n"
        
        report += f"\n👥 DETALHES POR USUÁRIO:\n"
        for i, user_result in enumerate(results['user_results'], 1):
            user = user_result['user']
            report += f"""
{i}. {user.name} ({user.profile})
   • Perguntas: {user_result['questions_asked']}
   • Sucessos: {user_result['successful_responses']}
   • Taxa de Sucesso: {user_result['success_rate']:.1f}%
   • Tempo Médio: {user_result['average_response_time']:.2f}s
   • Session ID: {user.session_id}
"""
        
        if results['failures']:
            report += f"\n❌ FALHAS DO SISTEMA: {len(results['failures'])}\n"
            for i, failure in enumerate(results['failures'], 1):
                report += f"   {i}. {str(failure)}\n"
        
        # Recomendações baseadas no sistema real
        report += "\n🔧 RECOMENDAÇÕES PARA SISTEMA REAL:\n"
        success_rate = results['execution_stats']['success_rate']
        avg_time = results['execution_stats']['average_response_time']
        
        if success_rate < 90:
            report += "• Melhorar tratamento de erros nos agentes\n"
            report += "• Verificar configuração do OpenRouter/Ollama\n"
        if avg_time > 5.0:
            report += "• Otimizar prompts dos agentes\n"
            report += "• Considerar cache para respostas frequentes\n"
        if results['system_health']['status'] in ['fair', 'poor']:
            report += "• Revisar transições entre agentes\n"
            report += "• Verificar logs de erro detalhados\n"
        if success_rate >= 95 and avg_time < 3.0:
            report += "• Sistema funcionando excelentemente!\n"
            report += "• Manter monitoramento contínuo\n"
        
        return report

async def main():
    """Função principal para executar stress test real"""
    
    print("🏠 SISTEMA DE STRESS TESTING REAL - REAL ESTATE ASSISTANT")
    print("="*70)
    print("🎯 Testando sistema agêntico REAL com OpenRouter/Ollama + Mock Data")
    
    # Verificar se estamos no ambiente correto
    try:
        settings = get_settings()
        print(f"✅ Configurações carregadas")
        print(f"🔑 OpenRouter configurado: {'Sim' if settings.apis.openrouter_key else 'Não'}")
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        return
    
    tester = RealSystemStressTester()
    
    # Mostrar usuários disponíveis
    print(f"\n👥 USUÁRIOS VIRTUAIS PARA TESTE REAL:")
    for i, user in enumerate(tester.virtual_users, 1):
        print(f"   {i}. {user.name} - {user.profile}")
        print(f"      Budget: ${user.budget_min:,}-${user.budget_max:,}, {user.bedrooms}BR")
        print(f"      Session: {user.session_id}")
    
    # Executar testes reais
    print(f"\n🚀 EXECUTANDO TESTES COM SISTEMA REAL...")
    
    # Teste 1: Básico com sistema real
    print(f"\n1️⃣ TESTE BÁSICO REAL (2 usuários, 3 perguntas cada)")
    basic_results = await tester.run_real_stress_test(concurrent_users=2, questions_per_user=3)
    print(tester.generate_real_system_report(basic_results))
    
    # Teste 2: Médio com sistema real
    print(f"\n2️⃣ TESTE MÉDIO REAL (3 usuários, 5 perguntas cada)")
    medium_results = await tester.run_real_stress_test(concurrent_users=3, questions_per_user=5)
    print(tester.generate_real_system_report(medium_results))
    
    # Resumo final
    print(f"\n📊 RESUMO FINAL DO SISTEMA REAL:")
    print(f"="*50)
    
    basic_grade = basic_results['performance_grade']
    medium_grade = medium_results['performance_grade']
    
    print(f"🎯 Teste Básico Real: {basic_grade}")
    print(f"🎯 Teste Médio Real: {medium_grade}")
    
    # Status do sistema real
    basic_health = basic_results['system_health']['status']
    medium_health = medium_results['system_health']['status']
    
    print(f"🏥 Saúde do Sistema:")
    print(f"   • Teste Básico: {basic_health.upper()}")
    print(f"   • Teste Médio: {medium_health.upper()}")
    
    # Determinar status geral
    basic_success = basic_results['execution_stats']['success_rate']
    medium_success = medium_results['execution_stats']['success_rate']
    avg_success = (basic_success + medium_success) / 2
    
    if avg_success >= 90:
        print(f"🟢 STATUS GERAL: Sistema agêntico funcionando bem! ({avg_success:.1f}% sucesso)")
    elif avg_success >= 70:
        print(f"🟡 STATUS GERAL: Sistema estável, melhorias recomendadas ({avg_success:.1f}% sucesso)")
    else:
        print(f"🔴 STATUS GERAL: Sistema precisa de atenção urgente ({avg_success:.1f}% sucesso)")
    
    print(f"\n✅ STRESS TEST REAL CONCLUÍDO!")
    print(f"📊 Sistema testado com OpenRouter/Ollama real + dados Mock")
    print(f"🔄 Logs detalhados disponíveis em logs/")

if __name__ == "__main__":
    # Configurar event loop para Windows
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main()) 