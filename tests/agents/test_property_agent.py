#!/usr/bin/env python3
"""Test script to validate property_agent specifically"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.orchestration.swarm import SwarmOrchestrator
from app.agents.property import property_agent_node

async def test_property_details_mock():
    """Test property_agent with mock data showing property details"""
    
    print("🧪 Testing property_agent with MOCK data...")
    
    # Mock property data
    mock_property = {
        'id': '1',
        'formattedAddress': '123 Main St, Miami, FL 33101',
        'price': 450000,
        'bedrooms': 3,
        'bathrooms': 2,
        'squareFootage': 1500,
        'yearBuilt': 2020,
        'propertyType': 'Condo',
        'city': 'Miami',
        'state': 'FL'
    }
    
    orchestrator = SwarmOrchestrator()
    
    # Message asking for property details (should trigger property_agent)
    message = {
        'messages': [{'role': 'user', 'content': 'Show me the details of this property'}],
        'context': {
            'property_context': mock_property,
            'data_mode': 'mock'
        }
    }
    
    try:
        result = await orchestrator.process_message(message)
        
        if result and 'messages' in result:
            last_message = result['messages'][-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            print(f"🎯 Property Details Response:\n{response_content}")
            
            # Check if all property details are present
            checks = {
                'Address': '123 Main St, Miami, FL 33101' in response_content,
                'Price': '$450,000' in response_content,
                'Bedrooms': '3' in response_content,
                'Bathrooms': '2' in response_content,
                'Square Footage': '1,500' in response_content,
                'Year Built': '2020' in response_content,
                'Property Type': 'Condo' in response_content,
                'City/State': 'Miami, FL' in response_content,
                'Data Mode': 'MOCK' in response_content
            }
            
            print("\n📊 Property Data Validation:")
            for check_name, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"{status} {check_name}: {passed}")
            
            all_passed = all(checks.values())
            if all_passed:
                print("\n🎉 SUCCESS: All property details are correctly displayed!")
            else:
                print("\n⚠️  Some property details are missing or incorrect")
                
        else:
            print("❌ No response received")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_property_details_real():
    """Test property_agent with real data showing property details"""
    
    print("\n" + "="*60)
    print("🧪 Testing property_agent with REAL data...")
    
    # Real property data
    real_property = {
        'id': '1050-Brickell-Ave,-Apt-3504,-Miami,-FL-33131',
        'formattedAddress': '1050 Brickell Ave, Apt 3504, Miami, FL 33131',
        'price': 850000,
        'bedrooms': 2,
        'bathrooms': 2,
        'squareFootage': 1200,
        'yearBuilt': 2018,
        'propertyType': 'Apartment',
        'city': 'Miami',
        'state': 'FL'
    }
    
    orchestrator = SwarmOrchestrator()
    
    # Message asking for property details
    message = {
        'messages': [{'role': 'user', 'content': 'What can you tell me about this property?'}],
        'context': {
            'property_context': real_property,
            'data_mode': 'real'
        }
    }
    
    try:
        result = await orchestrator.process_message(message)
        
        if result and 'messages' in result:
            last_message = result['messages'][-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            print(f"🎯 Property Details Response:\n{response_content}")
            
            # Check if all property details are present
            checks = {
                'Address': 'Brickell Ave' in response_content,
                'Price': '$850,000' in response_content,
                'Bedrooms': '2' in response_content,
                'Bathrooms': '2' in response_content,
                'Square Footage': '1,200' in response_content,
                'Year Built': '2018' in response_content,
                'Property Type': 'Apartment' in response_content,
                'City/State': 'Miami, FL' in response_content,
                'Data Mode': 'REAL' in response_content,
                'Price per sq ft': '$' in response_content and '708' in response_content  # 850000/1200 ≈ 708
            }
            
            print("\n📊 Property Data Validation:")
            for check_name, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"{status} {check_name}: {passed}")
            
            all_passed = all(checks.values())
            if all_passed:
                print("\n🎉 SUCCESS: All property details are correctly displayed!")
            else:
                print("\n⚠️  Some property details are missing or incorrect")
                
        else:
            print("❌ No response received")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_property_agent():
    """Teste básico do agente de propriedades."""
    
    # Teste 1: Estado vazio (primeira mensagem)
    print("🧪 Teste 1: Estado vazio")
    state = {"messages": []}
    result = await property_agent_node(state)
    print(f"Resultado: {result}")
    print()
    
    # Teste 2: Mensagem de usuário geral
    print("🧪 Teste 2: Mensagem geral do usuário")
    state = {
        "messages": [
            {"role": "user", "content": "Olá, gostaria de ajuda com propriedades"}
        ]
    }
    result = await property_agent_node(state)
    print(f"Resultado: {result}")
    print()
    
    # Teste 3: Pedido de agendamento (deve fazer handoff)
    print("🧪 Teste 3: Pedido de agendamento")
    state = {
        "messages": [
            {"role": "user", "content": "Gostaria de agendar uma visita"}
        ]
    }
    result = await property_agent_node(state)
    print(f"Resultado: {result}")
    print()
    
    # Teste 4: Pedido de busca (deve fazer handoff)
    print("🧪 Teste 4: Pedido de busca")
    state = {
        "messages": [
            {"role": "user", "content": "Quero buscar mais propriedades"}
        ]
    }
    result = await property_agent_node(state)
    print(f"Resultado: {result}")
    print()

async def main():
    """Run property agent tests"""
    await test_property_details_mock()
    await test_property_details_real()
    await test_property_agent()
    print("\n" + "="*60)
    print("🏁 Property agent tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 