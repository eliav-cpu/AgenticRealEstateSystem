#!/usr/bin/env python3
"""
Teste do sistema agêntico com ID de propriedade real
"""

import requests

def test_with_real_property_id():
    print('🧪 Testando com ID de propriedade real')
    print('=' * 50)
    
    # Use a real property ID from mock mode
    mock_property_id = "1050-Brickell-Ave,-Apt-3504,-Miami,-FL-33131"
    real_property_id = "1300-S-Miami-Ave,-Unit-3408,-Miami,-FL-33130"
    
    modes = [
        ("mock", mock_property_id),
        ("real", real_property_id)
    ]
    
    for mode, property_id in modes:
        print(f'\n--- Testando modo {mode.upper()} com property_id: {property_id} ---')
        
        # Start session
        session_resp = requests.post(f'http://localhost:8000/api/agent/session/start?mode={mode}', 
            json={'property_id': property_id, 'mode': 'details'})
        
        if not session_resp.ok:
            print(f'❌ Erro ao iniciar sessão: {session_resp.text}')
            continue
        
        session_data = session_resp.json()
        session_id = session_data['data']['session']['session_id']
        print(f'✅ Sessão criada: {session_id}')
        
        # Send message
        chat_resp = requests.post(f'http://localhost:8000/api/agent/chat?mode={mode}',
            json={'message': 'What are the exact monthly costs for this property?', 'session_id': session_id})
        
        if chat_resp.ok:
            chat_data = chat_resp.json()
            print(f'Agent: {chat_data["data"]["agent_name"]}')
            message = chat_data["data"]["message"]
            print(f'Response preview: {message[:200]}...')
            
            # Look for property-specific information
            if "1050 Brickell" in message:
                print('✅ Found Brickell property info (mock data)')
            elif "1300 S Miami" in message:
                print('✅ Found Miami Ave property info (real data)')
            elif "Copacabana" in message:
                print('❌ Still showing Brazilian data (incorrect)')
            else:
                print('? Unknown property data')
        else:
            print(f'❌ Erro no chat: {chat_resp.text}')

if __name__ == "__main__":
    test_with_real_property_id() 