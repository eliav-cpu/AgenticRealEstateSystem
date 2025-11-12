#!/usr/bin/env python3
"""
Teste da funcionalidade de agendamento
"""

import asyncio
from app.orchestration.swarm import SwarmOrchestrator
from langchain_core.messages import HumanMessage

async def test_scheduling():
    orchestrator = SwarmOrchestrator()
    
    # Test scheduling intent
    message = {
        'messages': [HumanMessage(content='I would like to schedule a visit to this property')],
        'context': {
            'property_context': {
                'id': '1',
                'formattedAddress': '1050 Brickell Ave, Apt 3504, Miami, FL 33131',
                'price': 12000,
                'bedrooms': 3,
                'bathrooms': 3,
                'squareFootage': 2238,
                'city': 'Miami',
                'state': 'FL'
            },
            'data_mode': 'mock'
        }
    }
    
    try:
        result = await orchestrator.process_message(message)
        print('✅ Scheduling test successful!')
        print('Agent response:')
        if 'messages' in result and result['messages']:
            last_msg = result['messages'][-1]
            if hasattr(last_msg, 'content'):
                print(last_msg.content)
            else:
                print(str(last_msg))
        else:
            print('No response found')
    except Exception as e:
        print(f'❌ Scheduling test failed: {e}')

if __name__ == "__main__":
    asyncio.run(test_scheduling()) 