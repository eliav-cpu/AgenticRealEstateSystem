#!/usr/bin/env python3
"""
Teste do API server com agente real
"""

import requests
import json

def test_api_server():
    """Testa se o API server está funcionando com agente real"""
    
    print("🧪 TESTE DO API SERVER COM AGENTE REAL")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    
    try:
        # 1. Testar health check
        print("⏳ 1. Testando health check...")
        health_response = requests.get(f"{base_url}/health?mode=real", timeout=10)
        print(f"   Status: {health_response.status_code}")
        print(f"   Response: {health_response.json()}")
        
        # 2. Criar sessão de agente
        print("\n⏳ 2. Criando sessão de agente...")
        session_data = {
            "property_id": "1",
            "agent_mode": "details",
            "user_preferences": {"name": "Test User"},
            "language": "en"
        }
        
        session_response = requests.post(
            f"{base_url}/agent/session/start?mode=real",
            json=session_data,
            timeout=30
        )
        print(f"   Status: {session_response.status_code}")
        session_result = session_response.json()
        print(f"   Response: {json.dumps(session_result, indent=2)}")
        
        if not session_result.get("success"):
            print("❌ Falha ao criar sessão")
            return False
            
        session_id = session_result["data"]["session"]["session_id"]
        print(f"✅ Sessão criada: {session_id}")
        
        # 3. Enviar mensagem para o agente
        print("\n⏳ 3. Enviando mensagem para o agente...")
        message_data = {
            "message": "hello Emma",
            "session_id": session_id
        }
        
        message_response = requests.post(
            f"{base_url}/agent/chat?mode=real",
            json=message_data,
            timeout=30
        )
        print(f"   Status: {message_response.status_code}")
        message_result = message_response.json()
        print(f"   Response: {json.dumps(message_result, indent=2)}")
        
        if message_result.get("success"):
            agent_response = message_result["data"]
            print(f"\n✅ RESPOSTA DO AGENTE:")
            print(f"   Agente: {agent_response['agent_name']}")
            print(f"   Mensagem: {agent_response['message'][:200]}...")
            print(f"   Confiança: {agent_response['confidence']}")
            
            # Verificar se é resposta real
            if "Emma" in agent_response["message"] and agent_response["confidence"] > 0.8:
                print("🎯 SUCESSO: Resposta do agente real!")
                return True
            else:
                print("⚠️ Possível fallback ou problema")
                return False
        else:
            print("❌ Falha ao enviar mensagem")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando")
        print("   Execute: python api_server.py")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_api_server()
    if success:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n💥 TESTE FALHOU!") 