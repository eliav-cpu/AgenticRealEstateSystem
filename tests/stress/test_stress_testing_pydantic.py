"""
Sistema de Stress Testing para Real Estate Assistant
Usando PydanticAI TestModel e FunctionModel para simular usuários reais
"""

import asyncio
import pytest
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from pydantic_ai import Agent, RunContext, models
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel, AgentInfo
from pydantic_ai.messages import (
    ModelMessage, ModelResponse, TextPart, ToolCallPart, 
    SystemPromptPart, UserPromptPart
)
from pydantic_ai import capture_run_messages

# Configurar para não fazer chamadas reais durante testes
models.ALLOW_MODEL_REQUESTS = False

@dataclass
class VirtualUser:
    """Representa um usuário virtual com personalidade e necessidades específicas"""
    name: str
    profile: str
    budget_min: int
    budget_max: int
    bedrooms: int
    location_preferences: List[str]
    personality_traits: List[str]
    conversation_style: str
    questions: List[str]
    
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

class RealEstateStressTester:
    """Sistema de stress testing para o Real Estate Assistant"""
    
    def __init__(self):
        self.virtual_users = self._create_virtual_users()
        self.conversation_hooks = []
        self.test_results = []
        
    def _create_virtual_users(self) -> List[VirtualUser]:
        """Cria usuários virtuais diversos para testes"""
        users = [
            VirtualUser(
                name="Sarah Johnson",
                profile="Young Professional",
                budget_min=1500,
                budget_max=2500,
                bedrooms=1,
                location_preferences=["Miami", "Brickell", "Downtown"],
                personality_traits=["detail-oriented", "budget-conscious"],
                conversation_style="direct",
                questions=[]
            ),
            VirtualUser(
                name="Mike Rodriguez",
                profile="Family Man",
                budget_min=2500,
                budget_max=4000,
                bedrooms=3,
                location_preferences=["Coral Gables", "Aventura", "Doral"],
                personality_traits=["family-focused", "safety-conscious"],
                conversation_style="thorough",
                questions=[]
            ),
            VirtualUser(
                name="Emily Chen",
                profile="Graduate Student",
                budget_min=800,
                budget_max=1500,
                bedrooms=1,
                location_preferences=["University Area", "Coconut Grove"],
                personality_traits=["budget-limited", "location-flexible"],
                conversation_style="casual",
                questions=[]
            ),
            VirtualUser(
                name="David Thompson",
                profile="Executive",
                budget_min=4000,
                budget_max=8000,
                bedrooms=2,
                location_preferences=["South Beach", "Brickell", "Key Biscayne"],
                personality_traits=["luxury-seeking", "convenience-focused"],
                conversation_style="efficient",
                questions=[]
            ),
            VirtualUser(
                name="Lisa Martinez",
                profile="Retiree",
                budget_min=2000,
                budget_max=3500,
                bedrooms=2,
                location_preferences=["Aventura", "Bal Harbour", "Sunny Isles"],
                personality_traits=["comfort-focused", "community-oriented"],
                conversation_style="friendly",
                questions=[]
            )
        ]
        
        # Gerar perguntas para cada usuário
        for user in users:
            user.questions = user.generate_questions()
            
        return users
    
    def create_intelligent_test_model(self, user: VirtualUser) -> FunctionModel:
        """Cria um modelo de teste inteligente baseado no perfil do usuário"""
        
        def intelligent_response(messages: List[ModelMessage], info: AgentInfo) -> ModelResponse:
            """Gera respostas inteligentes baseadas no perfil do usuário"""
            
            # Obter a última mensagem do usuário
            last_message = messages[-1]
            if hasattr(last_message, 'parts') and last_message.parts:
                user_content = last_message.parts[-1].content
            else:
                user_content = "Hello"
            
            # Gerar resposta baseada no perfil do usuário
            if "budget" in user_content.lower() or "price" in user_content.lower():
                if user.budget_max > 3000:
                    response = f"I have several premium options in your ${user.budget_min:,}-${user.budget_max:,} range. Let me show you some luxury properties."
                else:
                    response = f"I understand you're looking for something affordable. Here are some great options under ${user.budget_max:,}."
            elif "bedroom" in user_content.lower():
                response = f"Perfect! I have several {user.bedrooms}-bedroom options that might interest you."
            elif "location" in user_content.lower() or any(loc in user_content for loc in user.location_preferences):
                preferred_location = random.choice(user.location_preferences)
                response = f"Great choice! {preferred_location} is a wonderful area. I have several properties there."
            elif "schedule" in user_content.lower() or "viewing" in user_content.lower():
                response = "I'd be happy to schedule a viewing for you. What days work best for you?"
            else:
                # Resposta genérica baseada no estilo de conversa
                if user.conversation_style == "direct":
                    response = "Let me get you the information you need quickly."
                elif user.conversation_style == "thorough":
                    response = "I'll provide you with comprehensive details about each property."
                elif user.conversation_style == "casual":
                    response = "Sure thing! Let me help you find something perfect."
                elif user.conversation_style == "efficient":
                    response = "I'll focus on the properties that best match your criteria."
                else:
                    response = "I'm here to help you find your perfect home!"
            
            return ModelResponse(parts=[TextPart(content=response)])
        
        return FunctionModel(intelligent_response)
    
    async def simulate_user_conversation(self, user: VirtualUser, num_questions: int = 5) -> Dict[str, Any]:
        """Simula uma conversa completa com um usuário virtual"""
        
        # Criar agente de teste
        test_model = self.create_intelligent_test_model(user)
        agent = Agent(test_model, deps_type=str)
        
        conversation_log = []
        start_time = time.time()
        
        # Simular conversa
        selected_questions = random.sample(user.questions, min(num_questions, len(user.questions)))
        
        for i, question in enumerate(selected_questions):
            question_start = time.time()
            
            with capture_run_messages() as messages:
                try:
                    # Simular delay humano entre perguntas
                    if i > 0:
                        await asyncio.sleep(random.uniform(0.5, 2.0))
                    
                    result = await agent.run(question)
                    response_time = time.time() - question_start
                    
                    conversation_log.append({
                        "question": question,
                        "response": str(result.data),
                        "response_time": response_time,
                        "success": True,
                        "messages": messages
                    })
                    
                except Exception as e:
                    conversation_log.append({
                        "question": question,
                        "response": f"Error: {str(e)}",
                        "response_time": time.time() - question_start,
                        "success": False,
                        "error": str(e)
                    })
        
        total_time = time.time() - start_time
        
        return {
            "user": user,
            "conversation_log": conversation_log,
            "total_time": total_time,
            "questions_asked": len(selected_questions),
            "successful_responses": sum(1 for log in conversation_log if log["success"]),
            "average_response_time": sum(log["response_time"] for log in conversation_log) / len(conversation_log) if conversation_log else 0
        }
    
    async def run_stress_test(self, concurrent_users: int = 3, questions_per_user: int = 5) -> Dict[str, Any]:
        """Executa stress test com múltiplos usuários simultâneos"""
        
        print(f"🚀 Iniciando stress test com {concurrent_users} usuários simultâneos")
        print(f"📝 {questions_per_user} perguntas por usuário")
        
        start_time = time.time()
        
        # Selecionar usuários para o teste
        test_users = random.sample(self.virtual_users, min(concurrent_users, len(self.virtual_users)))
        
        # Executar conversas em paralelo
        tasks = [
            self.simulate_user_conversation(user, questions_per_user) 
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
        
        test_summary = {
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
                "success_rate": (total_successful / total_questions * 100) if total_questions > 0 else 0,
                "average_response_time": avg_response_time,
                "questions_per_second": total_questions / total_time if total_time > 0 else 0
            },
            "user_results": successful_results,
            "failures": failed_results,
            "performance_grade": self._calculate_performance_grade(total_successful, total_questions, avg_response_time)
        }
        
        return test_summary
    
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
    
    def generate_test_report(self, test_results: Dict[str, Any]) -> str:
        """Gera relatório detalhado do teste"""
        
        report = f"""
🔬 RELATÓRIO DE STRESS TEST - REAL ESTATE ASSISTANT
{'='*60}

📊 CONFIGURAÇÃO DO TESTE:
• Usuários Simultâneos: {test_results['test_config']['concurrent_users']}
• Perguntas por Usuário: {test_results['test_config']['questions_per_user']}
• Total de Usuários: {test_results['test_config']['total_users_tested']}

⚡ ESTATÍSTICAS DE EXECUÇÃO:
• Tempo Total: {test_results['execution_stats']['total_time']:.2f}s
• Total de Perguntas: {test_results['execution_stats']['total_questions']}
• Respostas Bem-sucedidas: {test_results['execution_stats']['successful_responses']}
• Respostas com Falha: {test_results['execution_stats']['failed_responses']}
• Taxa de Sucesso: {test_results['execution_stats']['success_rate']:.1f}%
• Tempo Médio de Resposta: {test_results['execution_stats']['average_response_time']:.2f}s
• Perguntas por Segundo: {test_results['execution_stats']['questions_per_second']:.2f}

🎯 NOTA DE PERFORMANCE: {test_results['performance_grade']}

👥 DETALHES POR USUÁRIO:
"""
        
        for i, user_result in enumerate(test_results['user_results'], 1):
            user = user_result['user']
            report += f"""
{i}. {user.name} ({user.profile})
   • Perguntas: {user_result['questions_asked']}
   • Sucessos: {user_result['successful_responses']}
   • Tempo Médio: {user_result['average_response_time']:.2f}s
   • Taxa de Sucesso: {(user_result['successful_responses']/user_result['questions_asked']*100):.1f}%
"""
        
        if test_results['failures']:
            report += f"\n❌ FALHAS DETECTADAS: {len(test_results['failures'])}\n"
            for i, failure in enumerate(test_results['failures'], 1):
                report += f"   {i}. {str(failure)}\n"
        
        return report

# Testes pytest
class TestRealEstateStressTesting:
    """Testes automatizados para o sistema de stress testing"""
    
    @pytest.fixture
    def stress_tester(self):
        return RealEstateStressTester()
    
    @pytest.mark.asyncio
    async def test_single_user_conversation(self, stress_tester):
        """Testa conversa com um único usuário"""
        user = stress_tester.virtual_users[0]
        result = await stress_tester.simulate_user_conversation(user, 3)
        
        assert result["user"] == user
        assert result["questions_asked"] == 3
        assert result["successful_responses"] >= 0
        assert result["total_time"] > 0
        assert result["average_response_time"] > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_users(self, stress_tester):
        """Testa múltiplos usuários simultâneos"""
        test_results = await stress_tester.run_stress_test(concurrent_users=2, questions_per_user=3)
        
        assert test_results["test_config"]["concurrent_users"] == 2
        assert test_results["test_config"]["questions_per_user"] == 3
        assert test_results["execution_stats"]["total_questions"] == 6
        assert test_results["execution_stats"]["success_rate"] >= 0
        assert test_results["performance_grade"] in ["A+", "A", "B", "C", "D"]
    
    @pytest.mark.asyncio
    async def test_user_profiles_diversity(self, stress_tester):
        """Testa diversidade de perfis de usuários"""
        profiles = [user.profile for user in stress_tester.virtual_users]
        
        assert "Young Professional" in profiles
        assert "Family Man" in profiles
        assert "Graduate Student" in profiles
        assert "Executive" in profiles
        assert "Retiree" in profiles
        
        # Verificar que cada usuário tem perguntas únicas
        for user in stress_tester.virtual_users:
            assert len(user.questions) > 0
            assert user.budget_min < user.budget_max
            assert user.bedrooms > 0
    
    @pytest.mark.asyncio
    async def test_performance_grading(self, stress_tester):
        """Testa sistema de avaliação de performance"""
        # Teste com performance perfeita
        grade_a = stress_tester._calculate_performance_grade(100, 100, 1.5)
        assert grade_a == "A+ (Excelente)"
        
        # Teste com performance média
        grade_b = stress_tester._calculate_performance_grade(80, 100, 4.0)
        assert grade_b == "B (Bom)"
        
        # Teste com performance ruim
        grade_d = stress_tester._calculate_performance_grade(50, 100, 10.0)
        assert grade_d == "D (Precisa Melhorar)"

# Função principal para executar testes
async def main():
    """Função principal para executar stress test completo"""
    
    print("🏠 SISTEMA DE STRESS TESTING - REAL ESTATE ASSISTANT")
    print("="*60)
    
    tester = RealEstateStressTester()
    
    # Teste básico
    print("\n1️⃣ TESTE BÁSICO (2 usuários, 3 perguntas cada)")
    basic_results = await tester.run_stress_test(concurrent_users=2, questions_per_user=3)
    print(tester.generate_test_report(basic_results))
    
    # Teste médio
    print("\n2️⃣ TESTE MÉDIO (3 usuários, 5 perguntas cada)")
    medium_results = await tester.run_stress_test(concurrent_users=3, questions_per_user=5)
    print(tester.generate_test_report(medium_results))
    
    # Teste intensivo
    print("\n3️⃣ TESTE INTENSIVO (5 usuários, 8 perguntas cada)")
    intensive_results = await tester.run_stress_test(concurrent_users=5, questions_per_user=8)
    print(tester.generate_test_report(intensive_results))
    
    print("\n✅ STRESS TESTING COMPLETO!")
    print("📊 Relatórios gerados com sucesso")

if __name__ == "__main__":
    asyncio.run(main()) 