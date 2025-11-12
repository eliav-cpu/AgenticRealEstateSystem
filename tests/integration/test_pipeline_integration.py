"""
Pipeline de Testes Integrado - Real Estate Assistant
Combina stress testing, hooks de conversa e validação de sistema agêntico
"""

import asyncio
import pytest
import json
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

# Importar nossos módulos de teste
from test_stress_testing_pydantic import RealEstateStressTester, VirtualUser
from test_conversation_hooks import (
    ConversationAnalyzer, ConversationSimulator, ConversationEvent,
    AgentType, ConversationPhase
)

from pydantic_ai import models
from pydantic_ai.models.test import TestModel

# Configurar para testes
models.ALLOW_MODEL_REQUESTS = False

@dataclass
class TestScenario:
    """Cenário de teste completo"""
    name: str
    description: str
    virtual_users: List[VirtualUser]
    conversation_scripts: List[List[Dict[str, Any]]]
    expected_outcomes: Dict[str, Any]
    performance_thresholds: Dict[str, float]

@dataclass
class TestResults:
    """Resultados consolidados de testes"""
    scenario_name: str
    stress_test_results: Dict[str, Any]
    conversation_analysis: Dict[str, Any]
    integration_metrics: Dict[str, Any]
    overall_grade: str
    recommendations: List[str]
    timestamp: datetime

class RealEstateTestPipeline:
    """Pipeline integrado de testes para o sistema imobiliário"""
    
    def __init__(self):
        self.stress_tester = RealEstateStressTester()
        self.conversation_analyzer = ConversationAnalyzer()
        self.conversation_simulator = ConversationSimulator(self.conversation_analyzer)
        self.test_scenarios = self._create_test_scenarios()
        self.results_history: List[TestResults] = []
        
        # Configurar hooks padrão
        self.conversation_analyzer.create_standard_hooks()
    
    def _create_test_scenarios(self) -> List[TestScenario]:
        """Cria cenários de teste realistas"""
        
        scenarios = [
            TestScenario(
                name="basic_user_journey",
                description="Jornada básica do usuário: busca -> detalhes -> agendamento",
                virtual_users=self.stress_tester.virtual_users[:2],
                conversation_scripts=[
                    [
                        {"user_input": "Hi, I'm looking for an apartment", "agent_type": "search_agent", "phase": "greeting"},
                        {"user_input": "I need 1 bedroom under $2000", "agent_type": "search_agent", "phase": "search_criteria"},
                        {"user_input": "Tell me about the first property", "agent_type": "property_agent", "phase": "property_details"},
                        {"user_input": "Can I schedule a viewing?", "agent_type": "scheduling_agent", "phase": "scheduling"}
                    ]
                ],
                expected_outcomes={
                    "min_interactions": 4,
                    "agents_used": 3,
                    "phases_covered": 4
                },
                performance_thresholds={
                    "max_response_time": 5.0,
                    "min_success_rate": 90.0
                }
            ),
            
            TestScenario(
                name="complex_search_scenario",
                description="Busca complexa com múltiplos critérios e negociação",
                virtual_users=self.stress_tester.virtual_users[2:4],
                conversation_scripts=[
                    [
                        {"user_input": "Hello, I need help finding a family home", "agent_type": "search_agent", "phase": "greeting"},
                        {"user_input": "Looking for 3 bedrooms in a safe neighborhood", "agent_type": "search_agent", "phase": "search_criteria"},
                        {"user_input": "What's the price range for these properties?", "agent_type": "search_agent", "phase": "search_criteria"},
                        {"user_input": "Show me details for the best option", "agent_type": "property_agent", "phase": "property_details"},
                        {"user_input": "What about schools nearby?", "agent_type": "property_agent", "phase": "property_details"},
                        {"user_input": "Is the price negotiable?", "agent_type": "property_agent", "phase": "property_details"},
                        {"user_input": "Let's schedule a family viewing", "agent_type": "scheduling_agent", "phase": "scheduling"},
                        {"user_input": "What times are available this weekend?", "agent_type": "scheduling_agent", "phase": "scheduling"}
                    ]
                ],
                expected_outcomes={
                    "min_interactions": 8,
                    "agents_used": 3,
                    "phases_covered": 4
                },
                performance_thresholds={
                    "max_response_time": 6.0,
                    "min_success_rate": 85.0
                }
            ),
            
            TestScenario(
                name="high_volume_concurrent",
                description="Teste de volume alto com usuários simultâneos",
                virtual_users=self.stress_tester.virtual_users,
                conversation_scripts=[],  # Será gerado dinamicamente
                expected_outcomes={
                    "concurrent_users": 5,
                    "total_interactions": 25
                },
                performance_thresholds={
                    "max_response_time": 8.0,
                    "min_success_rate": 80.0
                }
            ),
            
            TestScenario(
                name="edge_cases_handling",
                description="Teste de casos extremos e tratamento de erros",
                virtual_users=self.stress_tester.virtual_users[:1],
                conversation_scripts=[
                    [
                        {"user_input": "", "agent_type": "search_agent", "phase": "greeting"},  # Input vazio
                        {"user_input": "I want a 50-bedroom mansion for $100", "agent_type": "search_agent", "phase": "search_criteria"},  # Critério impossível
                        {"user_input": "What's the weather like?", "agent_type": "search_agent", "phase": "search_criteria"},  # Pergunta fora do escopo
                        {"user_input": "Show me property ID 99999999", "agent_type": "property_agent", "phase": "property_details"},  # ID inexistente
                        {"user_input": "Schedule viewing for yesterday", "agent_type": "scheduling_agent", "phase": "scheduling"}  # Data inválida
                    ]
                ],
                expected_outcomes={
                    "error_handling": True,
                    "graceful_degradation": True
                },
                performance_thresholds={
                    "max_response_time": 10.0,
                    "min_success_rate": 60.0  # Menor devido aos casos de erro
                }
            )
        ]
        
        return scenarios
    
    async def run_scenario(self, scenario: TestScenario) -> TestResults:
        """Executa cenário de teste completo"""
        
        print(f"\n🎯 Executando cenário: {scenario.name}")
        print(f"📝 {scenario.description}")
        
        start_time = time.time()
        
        # 1. Executar stress test se aplicável
        stress_results = None
        if scenario.name == "high_volume_concurrent":
            print("   🚀 Executando stress test...")
            stress_results = await self.stress_tester.run_stress_test(
                concurrent_users=len(scenario.virtual_users),
                questions_per_user=5
            )
        else:
            print("   🔄 Executando teste de carga leve...")
            stress_results = await self.stress_tester.run_stress_test(
                concurrent_users=len(scenario.virtual_users),
                questions_per_user=3
            )
        
        # 2. Executar simulações de conversa
        print("   💬 Executando simulações de conversa...")
        for i, script in enumerate(scenario.conversation_scripts):
            await self.conversation_simulator.simulate_conversation(
                f"{scenario.name}_user_{i}",
                script
            )
        
        # 3. Analisar padrões de conversa
        conversation_analysis = self.conversation_analyzer.analyze_patterns()
        
        # 4. Calcular métricas de integração
        integration_metrics = self._calculate_integration_metrics(
            scenario, stress_results, conversation_analysis
        )
        
        # 5. Determinar nota geral
        overall_grade = self._calculate_overall_grade(
            scenario, stress_results, conversation_analysis, integration_metrics
        )
        
        # 6. Gerar recomendações
        recommendations = self._generate_recommendations(
            scenario, stress_results, conversation_analysis, integration_metrics
        )
        
        execution_time = time.time() - start_time
        print(f"   ✅ Cenário concluído em {execution_time:.2f}s")
        
        # Criar resultado
        result = TestResults(
            scenario_name=scenario.name,
            stress_test_results=stress_results,
            conversation_analysis=conversation_analysis,
            integration_metrics=integration_metrics,
            overall_grade=overall_grade,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
        
        self.results_history.append(result)
        return result
    
    def _calculate_integration_metrics(self, scenario: TestScenario, stress_results: Dict, conversation_analysis: Dict) -> Dict[str, Any]:
        """Calcula métricas de integração entre componentes"""
        
        metrics = {
            "system_coherence": 0.0,
            "agent_coordination": 0.0,
            "response_consistency": 0.0,
            "error_resilience": 0.0,
            "user_experience_score": 0.0
        }
        
        # Coerência do sistema (baseada na taxa de sucesso)
        if stress_results and "execution_stats" in stress_results:
            success_rate = stress_results["execution_stats"]["success_rate"]
            metrics["system_coherence"] = min(success_rate / 100.0, 1.0)
        
        # Coordenação entre agentes (baseada nas transições)
        if conversation_analysis and "common_agent_transitions" in conversation_analysis:
            transitions = conversation_analysis["common_agent_transitions"]
            expected_transitions = ["search_agent -> property_agent", "property_agent -> scheduling_agent"]
            found_transitions = sum(1 for trans in expected_transitions if any(trans in key for key in transitions.keys()))
            metrics["agent_coordination"] = found_transitions / len(expected_transitions)
        
        # Consistência de resposta (baseada no tempo médio)
        if stress_results and "execution_stats" in stress_results:
            avg_time = stress_results["execution_stats"]["average_response_time"]
            threshold = scenario.performance_thresholds.get("max_response_time", 5.0)
            metrics["response_consistency"] = max(0.0, 1.0 - (avg_time / threshold))
        
        # Resiliência a erros (baseada no cenário de edge cases)
        if scenario.name == "edge_cases_handling":
            # Para cenários de casos extremos, medir como o sistema lida com erros
            metrics["error_resilience"] = 0.8  # Valor base, seria calculado baseado em logs reais
        else:
            metrics["error_resilience"] = metrics["system_coherence"]  # Usar coerência como proxy
        
        # Score de experiência do usuário (média ponderada)
        weights = [0.3, 0.25, 0.25, 0.2]  # Pesos para cada métrica
        values = [metrics["system_coherence"], metrics["agent_coordination"], 
                 metrics["response_consistency"], metrics["error_resilience"]]
        metrics["user_experience_score"] = sum(w * v for w, v in zip(weights, values))
        
        return metrics
    
    def _calculate_overall_grade(self, scenario: TestScenario, stress_results: Dict, 
                                conversation_analysis: Dict, integration_metrics: Dict) -> str:
        """Calcula nota geral do cenário"""
        
        # Obter score de experiência do usuário
        ux_score = integration_metrics.get("user_experience_score", 0.0)
        
        # Verificar se atende aos thresholds
        threshold_compliance = 0.0
        if stress_results and "execution_stats" in stress_results:
            success_rate = stress_results["execution_stats"]["success_rate"]
            avg_response_time = stress_results["execution_stats"]["average_response_time"]
            
            min_success = scenario.performance_thresholds.get("min_success_rate", 80.0)
            max_time = scenario.performance_thresholds.get("max_response_time", 5.0)
            
            success_compliance = 1.0 if success_rate >= min_success else success_rate / min_success
            time_compliance = 1.0 if avg_response_time <= max_time else max_time / avg_response_time
            
            threshold_compliance = (success_compliance + time_compliance) / 2.0
        
        # Calcular nota final
        final_score = (ux_score * 0.6) + (threshold_compliance * 0.4)
        
        if final_score >= 0.9:
            return "A+ (Excelente)"
        elif final_score >= 0.8:
            return "A (Muito Bom)"
        elif final_score >= 0.7:
            return "B (Bom)"
        elif final_score >= 0.6:
            return "C (Satisfatório)"
        else:
            return "D (Precisa Melhorar)"
    
    def _generate_recommendations(self, scenario: TestScenario, stress_results: Dict,
                                 conversation_analysis: Dict, integration_metrics: Dict) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        
        recommendations = []
        
        # Analisar tempo de resposta
        if stress_results and "execution_stats" in stress_results:
            avg_time = stress_results["execution_stats"]["average_response_time"]
            if avg_time > 5.0:
                recommendations.append("⚡ Otimizar tempo de resposta - considerar cache ou otimização de prompts")
            
            success_rate = stress_results["execution_stats"]["success_rate"]
            if success_rate < 90.0:
                recommendations.append("🔧 Melhorar taxa de sucesso - revisar tratamento de erros e fallbacks")
        
        # Analisar coordenação entre agentes
        coordination_score = integration_metrics.get("agent_coordination", 0.0)
        if coordination_score < 0.8:
            recommendations.append("🤝 Melhorar coordenação entre agentes - implementar handoffs mais suaves")
        
        # Analisar experiência do usuário
        ux_score = integration_metrics.get("user_experience_score", 0.0)
        if ux_score < 0.7:
            recommendations.append("👤 Melhorar experiência do usuário - personalizar respostas e reduzir fricção")
        
        # Analisar padrões de conversa
        if conversation_analysis and "response_time_distribution" in conversation_analysis:
            p95_time = conversation_analysis["response_time_distribution"].get("p95", 0)
            if p95_time > 10.0:
                recommendations.append("📊 Reduzir variabilidade no tempo de resposta - investigar outliers")
        
        # Recomendações específicas por cenário
        if scenario.name == "edge_cases_handling":
            recommendations.append("🛡️ Implementar validação mais robusta de entrada do usuário")
            recommendations.append("🔄 Melhorar mensagens de erro para serem mais úteis ao usuário")
        
        if not recommendations:
            recommendations.append("✅ Sistema funcionando bem - manter monitoramento contínuo")
        
        return recommendations
    
    def generate_pipeline_report(self, results: List[TestResults]) -> str:
        """Gera relatório consolidado do pipeline"""
        
        if not results:
            return "❌ Nenhum resultado disponível para relatório"
        
        report = f"""
🏠 RELATÓRIO DO PIPELINE DE TESTES - REAL ESTATE ASSISTANT
{'='*70}

📊 RESUMO EXECUTIVO:
• Total de Cenários Testados: {len(results)}
• Data da Execução: {results[-1].timestamp.strftime('%Y-%m-%d %H:%M:%S')}
• Duração Total: {sum((r.timestamp - results[0].timestamp).total_seconds() for r in results[1:]):.1f}s

🎯 RESULTADOS POR CENÁRIO:
"""
        
        for result in results:
            report += f"""
📋 {result.scenario_name.upper()}:
   • Nota Geral: {result.overall_grade}
   • Score UX: {result.integration_metrics.get('user_experience_score', 0):.2f}
   • Taxa de Sucesso: {result.stress_test_results.get('execution_stats', {}).get('success_rate', 0):.1f}%
   • Tempo Médio: {result.stress_test_results.get('execution_stats', {}).get('average_response_time', 0):.2f}s
"""
        
        # Calcular métricas agregadas
        avg_ux_score = sum(r.integration_metrics.get('user_experience_score', 0) for r in results) / len(results)
        avg_success_rate = sum(r.stress_test_results.get('execution_stats', {}).get('success_rate', 0) for r in results) / len(results)
        
        report += f"""
📈 MÉTRICAS AGREGADAS:
• Score UX Médio: {avg_ux_score:.2f}
• Taxa de Sucesso Média: {avg_success_rate:.1f}%
• Cenários com Nota A+/A: {sum(1 for r in results if r.overall_grade.startswith('A'))}/{len(results)}

🔧 PRINCIPAIS RECOMENDAÇÕES:
"""
        
        # Compilar todas as recomendações
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)
        
        # Contar recomendações mais comuns
        rec_counts = {}
        for rec in all_recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        # Mostrar top 5 recomendações
        top_recommendations = sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for rec, count in top_recommendations:
            report += f"• {rec} (mencionado {count}x)\n"
        
        # Determinar status geral
        if avg_ux_score >= 0.8 and avg_success_rate >= 90:
            status = "🟢 SISTEMA EM EXCELENTE ESTADO"
        elif avg_ux_score >= 0.7 and avg_success_rate >= 80:
            status = "🟡 SISTEMA EM BOM ESTADO - MELHORIAS RECOMENDADAS"
        else:
            status = "🔴 SISTEMA PRECISA DE ATENÇÃO URGENTE"
        
        report += f"\n{status}\n"
        
        return report
    
    async def run_full_pipeline(self) -> List[TestResults]:
        """Executa pipeline completo de testes"""
        
        print("🚀 INICIANDO PIPELINE COMPLETO DE TESTES")
        print("="*50)
        
        results = []
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"\n📋 Cenário {i}/{len(self.test_scenarios)}")
            try:
                result = await self.run_scenario(scenario)
                results.append(result)
                print(f"   ✅ {scenario.name}: {result.overall_grade}")
            except Exception as e:
                print(f"   ❌ Erro no cenário {scenario.name}: {str(e)}")
                continue
        
        # Gerar relatório final
        print("\n" + "="*50)
        print("📊 GERANDO RELATÓRIO FINAL...")
        final_report = self.generate_pipeline_report(results)
        print(final_report)
        
        return results

# Testes pytest
class TestPipelineIntegration:
    """Testes para o pipeline integrado"""
    
    @pytest.fixture
    def pipeline(self):
        return RealEstateTestPipeline()
    
    @pytest.mark.asyncio
    async def test_basic_scenario_execution(self, pipeline):
        """Testa execução de cenário básico"""
        scenario = pipeline.test_scenarios[0]  # basic_user_journey
        result = await pipeline.run_scenario(scenario)
        
        assert result.scenario_name == "basic_user_journey"
        assert result.stress_test_results is not None
        assert result.conversation_analysis is not None
        assert result.overall_grade in ["A+", "A", "B", "C", "D"]
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_integration_metrics_calculation(self, pipeline):
        """Testa cálculo de métricas de integração"""
        scenario = pipeline.test_scenarios[0]
        
        # Mock de resultados
        stress_results = {
            "execution_stats": {
                "success_rate": 95.0,
                "average_response_time": 2.5
            }
        }
        
        conversation_analysis = {
            "common_agent_transitions": {
                "search_agent -> property_agent": 5,
                "property_agent -> scheduling_agent": 3
            }
        }
        
        metrics = pipeline._calculate_integration_metrics(
            scenario, stress_results, conversation_analysis
        )
        
        assert "system_coherence" in metrics
        assert "agent_coordination" in metrics
        assert "user_experience_score" in metrics
        assert 0.0 <= metrics["user_experience_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_pipeline_report_generation(self, pipeline):
        """Testa geração de relatório do pipeline"""
        # Criar resultados mock
        mock_results = [
            TestResults(
                scenario_name="test_scenario",
                stress_test_results={"execution_stats": {"success_rate": 90.0, "average_response_time": 3.0}},
                conversation_analysis={},
                integration_metrics={"user_experience_score": 0.8},
                overall_grade="A (Muito Bom)",
                recommendations=["Teste recomendação"],
                timestamp=datetime.now()
            )
        ]
        
        report = pipeline.generate_pipeline_report(mock_results)
        
        assert "RELATÓRIO DO PIPELINE DE TESTES" in report
        assert "test_scenario" in report
        assert "A (Muito Bom)" in report
        assert "Teste recomendação" in report

# Função principal
async def main():
    """Executa pipeline completo"""
    
    pipeline = RealEstateTestPipeline()
    results = await pipeline.run_full_pipeline()
    
    # Salvar resultados em arquivo
    results_data = []
    for result in results:
        results_data.append({
            "scenario_name": result.scenario_name,
            "overall_grade": result.overall_grade,
            "integration_metrics": result.integration_metrics,
            "recommendations": result.recommendations,
            "timestamp": result.timestamp.isoformat()
        })
    
    # Salvar em arquivo JSON
    output_file = Path("test_results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    print("✅ Pipeline de testes concluído com sucesso!")

if __name__ == "__main__":
    asyncio.run(main()) 