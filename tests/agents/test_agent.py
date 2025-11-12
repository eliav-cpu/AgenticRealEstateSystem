#!/usr/bin/env python3
"""
Teste do sistema agêntico real
"""

import requests
import json

def test_agentic_system():
    """Testa o sistema agêntico real"""
    
    print("🚀 Testando Sistema Agêntico Real")
    print("=" * 50)
    
    # 1. Start agent session
    print("\n1. Iniciando sessão do agente...")
    session_resp = requests.post('http://localhost:8000/api/agent/session/start?mode=real', 
        json={'property_id': '1', 'mode': 'details'})
    
    if not session_resp.ok:
        print(f"❌ Erro ao iniciar sessão: {session_resp.text}")
        return
    
    session_data = session_resp.json()
    print(f"✅ Sessão criada: {session_data}")
    
    session_id = session_data['data']['session']['session_id']
    
    # 2. Send message to agent
    print(f"\n2. Enviando mensagem para o agente (session: {session_id})...")
    chat_resp = requests.post('http://localhost:8000/api/agent/chat?mode=real',
        json={'message': 'What are the exact monthly costs?', 'session_id': session_id})
    
    if not chat_resp.ok:
        print(f"❌ Erro no chat: {chat_resp.text}")
        return
    
    chat_data = chat_resp.json()
    print(f"✅ Resposta do agente:")
    print(f"Agent: {chat_data['data']['agent_name']}")
    print(f"Message: {chat_data['data']['message'][:200]}...")
    
    # 3. Test scheduling
    print(f"\n3. Testando agendamento...")
    schedule_resp = requests.post('http://localhost:8000/api/agent/chat?mode=real',
        json={'message': 'I want to schedule a visit', 'session_id': session_id})
    
    if schedule_resp.ok:
        schedule_data = schedule_resp.json()
        print(f"✅ Resposta de agendamento:")
        print(f"Agent: {schedule_data['data']['agent_name']}")
        print(f"Message: {schedule_data['data']['message'][:200]}...")
    
    print("\n🎉 Teste concluído!")

if __name__ == "__main__":
    test_agentic_system() 