#!/usr/bin/env python3
"""
TESTE ESPECÍFICO: llama-3.1-8b-instant (Groq) para Acesso aos Logs NLL

MODELO ALVO: llama-3.1-8b-instant
OBJETIVO: Verificar se este modelo específico suporta logprobs para calcular NLL
"""

import os
import json
import math
import asyncio
import traceback
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class LlamaMInstantNLLTester:
    """Testador específico para llama-3.1-8b-instant"""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.model_name = "llama-3.1-8b-instant"
        
        # Prompts de teste variados
        self.test_prompts = [
            "Explain artificial intelligence in simple terms.",
            "What is machine learning?",
            "Define neural networks briefly.",
            "How does deep learning work?"
        ]
        
        # Configurar cliente
        if self.groq_api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.groq_api_key)
                print(f"✅ Cliente Groq configurado para {self.model_name}")
            except ImportError:
                print("❌ Biblioteca Groq não disponível")
                self.client = None
        else:
            print("❌ GROQ_API_KEY não encontrada")
            self.client = None
    
    def print_section(self, title: str):
        """Imprimir seção formatada"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    async def test_basic_functionality(self) -> Dict[str, Any]:
        """Teste básico de funcionalidade"""
        
        print("🔍 TESTE 1: Funcionalidade Básica")
        print("-" * 40)
        
        if not self.client:
            return {"error": "Cliente não disponível"}
        
        try:
            prompt = self.test_prompts[0]
            print(f"📝 Prompt: {prompt}")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            
            response_text = response.choices[0].message.content
            print(f"✅ Resposta recebida ({len(response_text)} chars)")
            print(f"📤 Resposta: {response_text[:150]}...")
            
            return {
                "status": "success",
                "prompt": prompt,
                "response": response_text,
                "response_length": len(response_text)
            }
            
        except Exception as e:
            print(f"❌ Erro na funcionalidade básica: {e}")
            return {"error": str(e)}
    
    async def test_logprobs_comprehensive(self) -> Dict[str, Any]:
        """Teste abrangente de logprobs"""
        
        print("\n🔍 TESTE 2: Logprobs Detalhado")
        print("-" * 40)
        
        if not self.client:
            return {"error": "Cliente não disponível"}
        
        prompt = self.test_prompts[1]
        print(f"📝 Prompt: {prompt}")
        
        # Teste 1: Logprobs básico
        print("\n🎯 Subteste 2A: Logprobs Básico")
        try:
            response_basic = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50,
                logprobs=True
            )
            
            print("✅ Logprobs básico aceito!")
            
        except Exception as e:
            print(f"❌ Logprobs básico rejeitado: {e}")
            return {"error": f"logprobs_basic_failed: {e}"}
        
        # Teste 2: Logprobs com top_logprobs
        print("\n🎯 Subteste 2B: Logprobs com Top Alternatives")
        try:
            response_top = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50,
                logprobs=True,
                top_logprobs=5
            )
            
            print("✅ Top logprobs aceito!")
            
            # Analisar estrutura da resposta
            choice = response_top.choices[0]
            response_text = choice.message.content
            
            print(f"📤 Resposta: {response_text[:100]}...")
            
            result = {
                "status": "success",
                "model": self.model_name,
                "prompt": prompt,
                "response_text": response_text,
                "logprobs_available": False,
                "nll_calculable": False
            }
            
            # Verificar se logprobs estão presentes
            if hasattr(choice, 'logprobs') and choice.logprobs:
                print("🎯 ANALISANDO LOGPROBS:")
                logprobs = choice.logprobs
                
                print(f"   Tipo logprobs: {type(logprobs)}")
                
                # Verificar atributos
                attrs = [attr for attr in dir(logprobs) if not attr.startswith('_')]
                print(f"   Atributos: {attrs}")
                
                # Verificar content
                if hasattr(logprobs, 'content') and logprobs.content:
                    content_len = len(logprobs.content)
                    print(f"   📊 Content tokens: {content_len}")
                    
                    if content_len > 0:
                        result["logprobs_available"] = True
                        
                        # Analisar primeiros tokens
                        print(f"\n   🔍 ANÁLISE DOS PRIMEIROS TOKENS:")
                        
                        total_logprob = 0.0
                        token_details = []
                        
                        for i, token_data in enumerate(logprobs.content[:5]):  # Primeiros 5 tokens
                            try:
                                token = getattr(token_data, 'token', 'N/A')
                                logprob = getattr(token_data, 'logprob', 0.0)
                                
                                print(f"      Token {i}: '{token}' -> logprob: {logprob:.4f}")
                                
                                total_logprob += logprob
                                token_details.append({
                                    "token": token,
                                    "logprob": logprob
                                })
                                
                                # Verificar top alternatives
                                if hasattr(token_data, 'top_logprobs') and token_data.top_logprobs:
                                    print(f"         Alternativas top:")
                                    for j, alt in enumerate(token_data.top_logprobs[:3]):
                                        alt_token = getattr(alt, 'token', 'N/A')
                                        alt_logprob = getattr(alt, 'logprob', 0.0)
                                        print(f"           {j+1}. '{alt_token}': {alt_logprob:.4f}")
                                
                            except Exception as token_error:
                                print(f"      ⚠️ Erro no token {i}: {token_error}")
                        
                        # Calcular NLL se temos dados suficientes
                        if token_details and len(token_details) > 0:
                            nll = -total_logprob
                            perplexity = math.exp(nll / len(token_details))
                            
                            result.update({
                                "nll_calculable": True,
                                "nll_value": nll,
                                "perplexity": perplexity,
                                "total_logprob": total_logprob,
                                "token_count": len(logprobs.content),
                                "analyzed_tokens": len(token_details),
                                "token_details": token_details
                            })
                            
                            print(f"\n   📊 MÉTRICAS CALCULADAS:")
                            print(f"      ✅ NLL: {nll:.4f}")
                            print(f"      ✅ Perplexity: {perplexity:.4f}")
                            print(f"      ✅ Total tokens: {len(logprobs.content)}")
                            print(f"      ✅ Total logprob: {total_logprob:.4f}")
                        
                        else:
                            print("   ⚠️ Não foi possível extrair dados dos tokens")
                    
                    else:
                        print("   ❌ Content está vazio")
                
                else:
                    print("   ❌ Logprobs.content não disponível")
            
            else:
                print("❌ Logprobs não encontrados na resposta")
            
            return result
            
        except Exception as e:
            print(f"❌ Top logprobs rejeitado: {e}")
            return {"error": f"top_logprobs_failed: {e}"}
    
    async def test_multiple_prompts(self) -> List[Dict[str, Any]]:
        """Testar múltiplos prompts para verificar consistência"""
        
        print("\n🔍 TESTE 3: Múltiplos Prompts")
        print("-" * 40)
        
        if not self.client:
            return [{"error": "Cliente não disponível"}]
        
        results = []
        
        for i, prompt in enumerate(self.test_prompts[2:], 3):  # Usar prompts restantes
            print(f"\n🎯 Subteste 3.{i-2}: {prompt}")
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=30,
                    logprobs=True,
                    top_logprobs=3
                )
                
                choice = response.choices[0]
                response_text = choice.message.content
                
                result = {
                    "prompt": prompt,
                    "response": response_text,
                    "has_logprobs": hasattr(choice, 'logprobs') and choice.logprobs is not None
                }
                
                if result["has_logprobs"]:
                    logprobs = choice.logprobs
                    if hasattr(logprobs, 'content') and logprobs.content:
                        # Calcular NLL rápido
                        total_logprob = sum(
                            getattr(token, 'logprob', 0.0) 
                            for token in logprobs.content
                        )
                        nll = -total_logprob
                        
                        result.update({
                            "token_count": len(logprobs.content),
                            "nll_value": nll,
                            "logprobs_success": True
                        })
                        
                        print(f"   ✅ NLL: {nll:.4f} ({len(logprobs.content)} tokens)")
                    else:
                        result["logprobs_success"] = False
                        print(f"   ⚠️ Logprobs sem content")
                else:
                    result["logprobs_success"] = False
                    print(f"   ❌ Sem logprobs")
                
                results.append(result)
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                results.append({"prompt": prompt, "error": str(e)})
        
        return results
    
    def analyze_final_results(self, basic_result: Dict, logprobs_result: Dict, multiple_results: List[Dict]):
        """Análise final de todos os resultados"""
        
        self.print_section("ANÁLISE FINAL - llama-3.1-8b-instant")
        
        print(f"🤖 MODELO TESTADO: {self.model_name}")
        print(f"🔑 API: Groq")
        
        # Status geral
        basic_ok = basic_result.get("status") == "success"
        logprobs_ok = logprobs_result.get("status") == "success"
        nll_ok = logprobs_result.get("nll_calculable", False)
        
        print(f"\n📊 RESUMO DOS TESTES:")
        print(f"   ✅ Funcionalidade básica: {'SIM' if basic_ok else 'NÃO'}")
        print(f"   📊 Logprobs disponíveis: {'SIM' if logprobs_ok else 'NÃO'}")
        print(f"   🎯 NLL calculável: {'SIM' if nll_ok else 'NÃO'}")
        
        if nll_ok:
            nll_value = logprobs_result.get("nll_value", 0)
            perplexity = logprobs_result.get("perplexity", 0)
            token_count = logprobs_result.get("token_count", 0)
            
            print(f"\n🎉 SUCESSO - NLL CALCULÁVEL!")
            print(f"   📈 NLL: {nll_value:.4f}")
            print(f"   📈 Perplexity: {perplexity:.4f}")
            print(f"   🔢 Tokens analisados: {token_count}")
            
            # Verificar consistência com múltiplos prompts
            successful_multiples = [r for r in multiple_results if r.get("logprobs_success")]
            if successful_multiples:
                avg_nll = sum(r["nll_value"] for r in successful_multiples) / len(successful_multiples)
                print(f"   📊 NLL médio (múltiplos prompts): {avg_nll:.4f}")
                print(f"   ✅ Consistência: {len(successful_multiples)}/{len(multiple_results)} prompts")
        
        else:
            print(f"\n❌ LIMITAÇÕES ENCONTRADAS:")
            
            if not basic_ok:
                print(f"   🚫 Funcionalidade básica falhou")
                print(f"   🚫 Erro: {basic_result.get('error', 'Desconhecido')}")
            
            elif not logprobs_ok:
                print(f"   🚫 Logprobs não suportados")
                print(f"   🚫 Erro: {logprobs_result.get('error', 'Desconhecido')}")
            
            else:
                print(f"   🚫 Dados de logprobs insuficientes para calcular NLL")
        
        # Comparação com outros modelos
        print(f"\n🔄 COMPARAÇÃO COM OUTROS RESULTADOS:")
        print(f"   🔵 Google Gemini: ✅ NLL via sampling (~0.3-1.2)")
        print(f"   🟢 llama-3.1-8b-instant: {'✅' if nll_ok else '❌'} NLL {'direto' if nll_ok else 'não disponível'}")
        
        # Recomendação final
        print(f"\n💡 RECOMENDAÇÃO PARA llama-3.1-8b-instant:")
        
        if nll_ok:
            print(f"   🏆 EXCELENTE! Use este modelo para:")
            print(f"      • Cálculo direto de NLL")
            print(f"      • Análise de perplexidade")
            print(f"      • Avaliação de modelos")
            print(f"   📝 Script: Já implementado neste teste")
        else:
            print(f"   ⚠️ Use apenas para geração de texto básica")
            print(f"   🔄 Para NLL, continue usando Google Gemini")
        
        return {
            "model": self.model_name,
            "basic_functionality": basic_ok,
            "logprobs_available": logprobs_ok,
            "nll_calculable": nll_ok,
            "nll_value": logprobs_result.get("nll_value") if nll_ok else None,
            "recommendation": "use_for_nll" if nll_ok else "use_basic_only"
        }
    
    async def run_comprehensive_test(self):
        """Executar teste completo do llama-3.1-8b-instant"""
        
        self.print_section(f"TESTE ABRANGENTE: {self.model_name}")
        
        print("🎯 OBJETIVO: Verificar se llama-3.1-8b-instant suporta logprobs para NLL")
        
        # Executar testes
        basic_result = await self.test_basic_functionality()
        logprobs_result = await self.test_logprobs_comprehensive()
        multiple_results = await self.test_multiple_prompts()
        
        # Análise final
        summary = self.analyze_final_results(basic_result, logprobs_result, multiple_results)
        
        # Salvar resultados
        output_data = {
            "model": self.model_name,
            "test_timestamp": "2024-12-19",
            "basic_test": basic_result,
            "logprobs_test": logprobs_result,
            "multiple_prompts_test": multiple_results,
            "summary": summary
        }
        
        try:
            filename = f"llama_3_1_8b_instant_nll_test.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n💾 Resultados salvos em: {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
        
        return summary

async def main():
    """Função principal"""
    
    print("🧪 TESTE ESPECÍFICO: llama-3.1-8b-instant para NLL")
    print("=" * 60)
    
    tester = LlamaMInstantNLLTester()
    summary = await tester.run_comprehensive_test()
    
    print(f"\n🏁 Teste do llama-3.1-8b-instant concluído!")
    
    if summary.get("nll_calculable"):
        print(f"🎉 RESULTADO: ✅ MODELO SUPORTA NLL!")
        print(f"📊 NLL obtido: {summary.get('nll_value', 'N/A')}")
    else:
        print(f"😔 RESULTADO: ❌ Modelo não suporta NLL")
        print(f"💡 Continue usando Google Gemini para NLL")

if __name__ == "__main__":
    asyncio.run(main()) 