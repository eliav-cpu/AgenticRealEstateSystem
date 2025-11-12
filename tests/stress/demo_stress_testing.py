#!/usr/bin/env python3
"""
Demonstração do Sistema de Stress Testing - Real Estate Assistant
Versão simplificada para demonstrar o funcionamento do sistema agêntico
"""

import asyncio
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import json

@dataclass
class VirtualUser:
    """Representa um usuário virtual com personalidade específica"""
    name: str
    profile: str
    budget_min: int
    budget_max: int
    bedrooms: int
    location_preferences: List[str]
    personality_traits: List[str]
    conversation_style: str
    
    def generate_questions(self) -> List[str]:
        """Gera perguntas baseadas no perfil do usuário"""
        base_questions = [
            f"Hi, I'm looking for a {self.bedrooms}-bedroom apartment in {random.choice(self.location_preferences)}",
            f"What properties do you have under ${self.budget_max:,}?",
            f"I need something with at least {self.bedrooms} bedrooms",
            "Can you tell me about the neighborhood?",
            "What's the square footage?",
            "When can I schedule a viewing?",
            "Are pets allowed?",
            "What's included in the rent?",
            "How's the parking situation?",
            "What are the nearby amenities?"
        ]
        
        # Personalizar perguntas baseadas no perfil
        if "family" in self.profile.lower():
            base_questions.extend([
                "Are there good schools nearby?",
                "Is it family-friendly?",
                "Are there parks for kids?"
            ])
        elif "professional" in self.profile.lower():
            base_questions.extend([
                "How's the commute to downtown?",
                "Is there good internet connectivity?",
                "Any coworking spaces nearby?"
            ])
        elif "student" in self.profile.lower():
            base_questions.extend([
                "Is it close to the university?",
                "Are there study spaces?",
                "What's the public transportation like?"
            ])
            
        return random.sample(base_questions, min(len(base_questions), 8))

class MockAgent:
    """Agente simulado para testes"""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.response_templates = {
            "search_agent": [
                "I found several properties that match your criteria. Let me show you the best options.",
                "Based on your budget and preferences, I have {count} properties to show you.",
                "Great! I can help you find the perfect property. Here are some excellent options."
            ],
            "property_agent": [
                "This property is excellent! It features {bedrooms} bedrooms and {bathrooms} bathrooms.",
                "Let me tell you about this amazing property - it's {sqft} sq ft with great amenities.",
                "This is a fantastic choice! The property offers great value at ${price}/month."
            ],
            "scheduling_agent": [
                "I'd be happy to schedule a viewing for you. What days work best?",
                "Let's set up a tour! I have availability this week and next.",
                "Perfect! I can schedule your property viewing. When would you prefer to visit?"
            ]
        }
    
    async def generate_response(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Gera resposta simulada baseada no tipo de agente"""
        
        # Simular tempo de processamento
        await asyncio.sleep(random.uniform(0.5, 3.0))
        
        # Escolher template baseado no tipo de agente
        templates = self.response_templates.get(self.agent_type, ["I'm here to help you!"])
        response = random.choice(templates)
        
        # Personalizar resposta baseada no contexto
        if context:
            if "bedrooms" in context:
                response = response.replace("{bedrooms}", str(context["bedrooms"]))
            if "bathrooms" in context:
                response = response.replace("{bathrooms}", str(context["bathrooms"]))
            if "sqft" in context:
                response = response.replace("{sqft}", f"{context['sqft']:,}")
            if "price" in context:
                response = response.replace("{price}", f"{context['price']:,}")
            if "count" in context:
                response = response.replace("{count}", str(context["count"]))
        
        return response

class ConversationSimulator:
    """Simulador de conversas para stress testing"""
    
    def __init__(self):
        self.agents = {
            "search_agent": MockAgent("search_agent"),
            "property_agent": MockAgent("property_agent"),
            "scheduling_agent": MockAgent("scheduling_agent")
        }
        self.conversation_log = []
    
    async def simulate_user_conversation(self, user: VirtualUser, num_questions: int = 5) -> Dict[str, Any]:
        """Simula uma conversa completa com um usuário virtual"""
        
        print(f"   👤 Simulando conversa com {user.name} ({user.profile})")
        
        conversation_log = []
        start_time = time.time()
        
        # Gerar perguntas para o usuário
        questions = user.generate_questions()
        selected_questions = random.sample(questions, min(num_questions, len(questions)))
        
        # Simular fluxo de conversa
        agent_sequence = ["search_agent", "property_agent", "scheduling_agent"]
        
        for i, question in enumerate(selected_questions):
            question_start = time.time()
            
            # Determinar qual agente responder
            agent_type = agent_sequence[i % len(agent_sequence)]
            agent = self.agents[agent_type]
            
            # Criar contexto para a resposta
            context = {
                "bedrooms": user.bedrooms,
                "bathrooms": random.randint(1, 3),
                "sqft": random.randint(500, 2000),
                "price": random.randint(user.budget_min, user.budget_max),
                "count": random.randint(3, 8)
            }
            
            try:
                # Simular delay humano entre perguntas
                if i > 0:
                    await asyncio.sleep(random.uniform(0.2, 1.0))
                
                # Gerar resposta
                response = await agent.generate_response(question, context)
                response_time = time.time() - question_start
                
                conversation_log.append({
                    "question": question,
                    "agent_type": agent_type,
                    "response": response,
                    "response_time": response_time,
                    "success": True,
                    "context": context
                })
                
                print(f"      Q{i+1}: {question[:50]}... → {agent_type} ({response_time:.2f}s)")
                
            except Exception as e:
                conversation_log.append({
                    "question": question,
                    "agent_type": agent_type,
                    "response": f"Error: {str(e)}",
                    "response_time": time.time() - question_start,
                    "success": False,
                    "error": str(e)
                })
        
        total_time = time.time() - start_time
        successful_responses = sum(1 for log in conversation_log if log["success"])
        
        return {
            "user": user,
            "conversation_log": conversation_log,
            "total_time": total_time,
            "questions_asked": len(selected_questions),
            "successful_responses": successful_responses,
            "success_rate": (successful_responses / len(selected_questions) * 100) if selected_questions else 0,
            "average_response_time": sum(log["response_time"] for log in conversation_log) / len(conversation_log) if conversation_log else 0
        }

class StressTester:
    """Sistema de stress testing simplificado"""
    
    def __init__(self):
        self.virtual_users = self._create_virtual_users()
        self.simulator = ConversationSimulator()
    
    def _create_virtual_users(self) -> List[VirtualUser]:
        """Cria usuários virtuais diversos"""
        return [
            VirtualUser(
                name="Sarah Johnson",
                profile="Young Professional",
                budget_min=1500,
                budget_max=2500,
                bedrooms=1,
                location_preferences=["Miami", "Brickell", "Downtown"],
                personality_traits=["detail-oriented", "budget-conscious"],
                conversation_style="direct"
            ),
            VirtualUser(
                name="Mike Rodriguez",
                profile="Family Man",
                budget_min=2500,
                budget_max=4000,
                bedrooms=3,
                location_preferences=["Coral Gables", "Aventura", "Doral"],
                personality_traits=["family-focused", "safety-conscious"],
                conversation_style="thorough"
            ),
            VirtualUser(
                name="Emily Chen",
                profile="Graduate Student",
                budget_min=800,
                budget_max=1500,
                bedrooms=1,
                location_preferences=["University Area", "Coconut Grove"],
                personality_traits=["budget-limited", "location-flexible"],
                conversation_style="casual"
            ),
            VirtualUser(
                name="David Thompson",
                profile="Executive",
                budget_min=4000,
                budget_max=8000,
                bedrooms=2,
                location_preferences=["South Beach", "Brickell", "Key Biscayne"],
                personality_traits=["luxury-seeking", "convenience-focused"],
                conversation_style="efficient"
            )
        ]
    
    async def run_stress_test(self, concurrent_users: int = 3, questions_per_user: int = 5) -> Dict[str, Any]:
        """Executa stress test com múltiplos usuários simultâneos"""
        
        print(f"🚀 Iniciando stress test:")
        print(f"   • Usuários simultâneos: {concurrent_users}")
        print(f"   • Perguntas por usuário: {questions_per_user}")
        print(f"   • Total de usuários disponíveis: {len(self.virtual_users)}")
        
        start_time = time.time()
        
        # Selecionar usuários para o teste
        test_users = random.sample(self.virtual_users, min(concurrent_users, len(self.virtual_users)))
        
        # Executar conversas em paralelo
        print(f"\n💬 Executando conversas em paralelo...")
        tasks = [
            self.simulator.simulate_user_conversation(user, questions_per_user) 
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
        
        return {
            "test_config": {
                "concurrent_users": concurrent_users,
                "questions_per_user": questions_per_user,
                "total_users_tested": len(test_users)
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
            "user_results": successful_results,
            "failures": failed_results,
            "performance_grade": self._calculate_performance_grade(total_successful, total_questions, avg_response_time)
        }
    
    def _calculate_performance_grade(self, successful: int, total: int, avg_time: float) -> str:
        """Calcula nota de performance do sistema"""
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
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Gera relatório detalhado do teste"""
        
        report = f"""
🔬 RELATÓRIO DE STRESS TEST - REAL ESTATE ASSISTANT
{'='*60}

📊 CONFIGURAÇÃO DO TESTE:
• Usuários Simultâneos: {results['test_config']['concurrent_users']}
• Perguntas por Usuário: {results['test_config']['questions_per_user']}
• Total de Usuários: {results['test_config']['total_users_tested']}

⚡ ESTATÍSTICAS DE EXECUÇÃO:
• Tempo Total: {results['execution_stats']['total_time']:.2f}s
• Total de Perguntas: {results['execution_stats']['total_questions']}
• Respostas Bem-sucedidas: {results['execution_stats']['successful_responses']}
• Respostas com Falha: {results['execution_stats']['failed_responses']}
• Taxa de Sucesso: {results['execution_stats']['success_rate']:.1f}%
• Tempo Médio de Resposta: {results['execution_stats']['average_response_time']:.2f}s
• Perguntas por Segundo: {results['execution_stats']['questions_per_second']:.2f}

🎯 NOTA DE PERFORMANCE: {results['performance_grade']}

👥 DETALHES POR USUÁRIO:
"""
        
        for i, user_result in enumerate(results['user_results'], 1):
            user = user_result['user']
            report += f"""
{i}. {user.name} ({user.profile})
   • Perguntas: {user_result['questions_asked']}
   • Sucessos: {user_result['successful_responses']}
   • Taxa de Sucesso: {user_result['success_rate']:.1f}%
   • Tempo Médio: {user_result['average_response_time']:.2f}s
"""
        
        if results['failures']:
            report += f"\n❌ FALHAS DETECTADAS: {len(results['failures'])}\n"
            for i, failure in enumerate(results['failures'], 1):
                report += f"   {i}. {str(failure)}\n"
        
        # Recomendações
        report += "\n🔧 RECOMENDAÇÕES:\n"
        success_rate = results['execution_stats']['success_rate']
        avg_time = results['execution_stats']['average_response_time']
        
        if success_rate < 90:
            report += "• Melhorar taxa de sucesso - revisar tratamento de erros\n"
        if avg_time > 5.0:
            report += "• Otimizar tempo de resposta - considerar cache ou otimização\n"
        if success_rate >= 95 and avg_time < 2.0:
            report += "• Sistema funcionando excelentemente - manter monitoramento\n"
        
        return report

async def main():
    """Função principal para demonstração"""
    
    print("🏠 SISTEMA DE STRESS TESTING - REAL ESTATE ASSISTANT")
    print("="*60)
    print("🎯 Demonstração do sistema de testes agênticos")
    print("💡 Simulando usuários reais com diferentes perfis e necessidades")
    
    tester = StressTester()
    
    # Mostrar usuários disponíveis
    print(f"\n👥 USUÁRIOS VIRTUAIS DISPONÍVEIS:")
    for i, user in enumerate(tester.virtual_users, 1):
        print(f"   {i}. {user.name} - {user.profile}")
        print(f"      Budget: ${user.budget_min:,}-${user.budget_max:,}, {user.bedrooms}BR")
        print(f"      Estilo: {user.conversation_style}, Locais: {', '.join(user.location_preferences[:2])}")
    
    # Executar testes
    print(f"\n🚀 EXECUTANDO TESTES...")
    
    # Teste 1: Básico
    print(f"\n1️⃣ TESTE BÁSICO (2 usuários, 3 perguntas cada)")
    basic_results = await tester.run_stress_test(concurrent_users=2, questions_per_user=3)
    print(tester.generate_report(basic_results))
    
    # Teste 2: Médio
    print(f"\n2️⃣ TESTE MÉDIO (3 usuários, 5 perguntas cada)")
    medium_results = await tester.run_stress_test(concurrent_users=3, questions_per_user=5)
    print(tester.generate_report(medium_results))
    
    # Resumo final
    print(f"\n📊 RESUMO FINAL:")
    print(f"="*40)
    
    basic_grade = basic_results['performance_grade']
    medium_grade = medium_results['performance_grade']
    
    print(f"🎯 Teste Básico: {basic_grade}")
    print(f"🎯 Teste Médio: {medium_grade}")
    
    # Determinar status geral
    basic_success = basic_results['execution_stats']['success_rate']
    medium_success = medium_results['execution_stats']['success_rate']
    avg_success = (basic_success + medium_success) / 2
    
    if avg_success >= 90:
        print(f"🟢 STATUS GERAL: Sistema funcionando bem! ({avg_success:.1f}% sucesso)")
    elif avg_success >= 70:
        print(f"🟡 STATUS GERAL: Sistema estável, melhorias recomendadas ({avg_success:.1f}% sucesso)")
    else:
        print(f"🔴 STATUS GERAL: Sistema precisa de atenção ({avg_success:.1f}% sucesso)")
    
    print(f"\n✅ DEMONSTRAÇÃO CONCLUÍDA!")
    print(f"💡 Este sistema pode ser integrado com PydanticAI para testes mais avançados")
    print(f"🔄 Próximos passos: Integrar com o sistema agêntico real")

if __name__ == "__main__":
    # Configurar event loop para Windows se necessário
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main()) 