#!/usr/bin/env python3
"""
Teste direto do SwarmOrchestrator
"""

import asyncio
import traceback

async def test_swarm_orchestrator():
    """Testa o SwarmOrchestrator diretamente"""
    
    print("🧪 TESTE DIRETO DO SWARM ORCHESTRATOR")
    print("=" * 50)
    
    try:
        # 1. Importar SwarmOrchestrator
        print("⏳ 1. Importando SwarmOrchestrator...")
        from app.orchestration.swarm import SwarmOrchestrator
        print("✅ 1. SwarmOrchestrator importado com sucesso")
        
        # 2. Criar instância
        print("⏳ 2. Criando instância do SwarmOrchestrator...")
        orchestrator = SwarmOrchestrator()
        print("✅ 2. SwarmOrchestrator criado com sucesso")
        
        # 3. Criar mensagem de teste
        message = {
            "messages": [{"role": "user", "content": "hello Emma"}],
            "session_id": "test-session",
            "current_agent": "property_agent",
            "context": {
                "property_context": {
                    "formattedAddress": "123 Test St, Miami, FL",
                    "price": 2500,
                    "bedrooms": 2,
                    "bathrooms": 1,
                    "squareFootage": 1000
                }
            }
        }
        print("✅ 3. Mensagem de teste criada")
        
        # 4. Processar mensagem
        print("⏳ 4. Processando mensagem com SwarmOrchestrator...")
        result = await orchestrator.process_message(message)
        print("✅ 4. Mensagem processada com sucesso")
        
        # 5. Analisar resultado
        print(f"✅ 5. Tipo do resultado: {type(result)}")
        print(f"✅ 6. Chaves do resultado: {list(result.keys()) if hasattr(result, 'keys') else 'Não é dict'}")
        
        if result and hasattr(result, 'get') and result.get("messages"):
            messages = result["messages"]
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    content = last_message.content
                    print(f"✅ 7. Resposta extraída: {content[:100]}...")
                    print(f"✅ 8. Tamanho da resposta: {len(content)} chars")
                    
                    # Verificar se é resposta real ou fallback
                    if "I'm Emma" in content or "Emma" in content:
                        print("✅ 9. Resposta parece ser do agente real!")
                    else:
                        print("⚠️ 9. Resposta pode ser fallback")
                else:
                    print("⚠️ 7. Mensagem não tem atributo content")
            else:
                print("⚠️ 6. Lista de mensagens está vazia")
        else:
            print("⚠️ 5. Resultado não tem mensagens")
            print(f"   Resultado completo: {result}")
        
        print("\n🎯 TESTE CONCLUÍDO COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste: {e}")
        print(f"❌ Traceback completo:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_swarm_orchestrator()) 