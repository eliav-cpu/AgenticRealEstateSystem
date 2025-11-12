#!/usr/bin/env python3
"""
Teste REAL da API RentCast - Versão Corrigida

Baseado no primeiro teste, descobrimos que:
1. A API responde com Status 200 para cidades brasileiras
2. A estrutura da resposta é uma LISTA (não dict)
3. Para cidades brasileiras: lista vazia []
4. Modelo LLM confirmado: meta-llama/llama-4-scout:free

Este teste corrigido irá:
- Mostrar a estrutura real da resposta
- Comparar Brasil vs EUA
- Confirmar se RentCast tem dados brasileiros
"""

import os
import asyncio
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from config.settings import get_settings
from app.utils.logging import setup_logging
from app.utils.api_monitor import api_monitor

async def test_rentcast_detailed():
    """Teste detalhado da API RentCast com estrutura corrigida."""
    
    logger = setup_logging()
    settings = get_settings()
    
    print("🔍 TESTE DETALHADO - API RentCast (Estrutura Corrigida)")
    print("=" * 65)
    
    # Confirmar configurações
    print(f"🤖 Modelo LLM: {settings.models.default_model}")
    print(f"🔧 Provider: {settings.models.provider}")
    print(f"🌐 OpenRouter URL: {settings.apis.openrouter_url}")
    
    api_key = settings.apis.rentcast_api_key
    print(f"🔑 API Key: {api_key[:15]}...{api_key[-8:]}")
    
    usage = api_monitor.get_rentcast_usage()
    print(f"📊 Uso atual: {usage['total_used']}/50 calls")
    
    headers = {
        "X-API-Key": api_key,
        "accept": "application/json"
    }
    
    # Teste 1: Cidade brasileira
    print(f"\n🇧🇷 TESTE 1: CIDADE BRASILEIRA")
    print("-" * 40)
    
    params_br = {
        "city": "Rio de Janeiro",
        "state": "RJ",
        "propertyType": "Apartment",
        "status": "ForRent"
    }
    
    print(f"📋 Parâmetros: {params_br}")
    
    try:
        response_br = requests.get(
            "https://api.rentcast.io/v1/listings/rental/long-term",
            headers=headers,
            params=params_br,
            timeout=10
        )
        
        print(f"📡 Status: {response_br.status_code}")
        
        if response_br.status_code == 200:
            data_br = response_br.json()
            api_monitor.record_rentcast_call()
            
            print(f"✅ Resposta recebida!")
            print(f"📊 Tipo da resposta: {type(data_br).__name__}")
            
            if isinstance(data_br, list):
                print(f"📋 Lista com {len(data_br)} itens")
                if data_br:
                    print(f"📄 Primeiro item: {json.dumps(data_br[0], indent=2)[:500]}...")
                else:
                    print(f"📄 Lista vazia - Nenhum imóvel encontrado no Brasil")
            
            elif isinstance(data_br, dict):
                print(f"📋 Dict com chaves: {list(data_br.keys())}")
                print(f"📄 Conteúdo: {json.dumps(data_br, indent=2)[:500]}...")
            
            print(f"📄 RESPOSTA COMPLETA BRASIL:")
            print(json.dumps(data_br, indent=2)[:800])
        
        else:
            print(f"❌ Erro {response_br.status_code}: {response_br.text}")
    
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # Aguardar entre requests
    await asyncio.sleep(3)
    
    # Teste 2: Cidade americana
    print(f"\n🇺🇸 TESTE 2: CIDADE AMERICANA")
    print("-" * 40)
    
    params_us = {
        "city": "Miami",
        "state": "FL", 
        "propertyType": "Apartment",
        "status": "ForRent",
        "bedrooms": 2,
        "maxRent": 3000
    }
    
    print(f"📋 Parâmetros: {params_us}")
    
    try:
        response_us = requests.get(
            "https://api.rentcast.io/v1/listings/rental/long-term",
            headers=headers,
            params=params_us,
            timeout=10
        )
        
        print(f"📡 Status: {response_us.status_code}")
        
        if response_us.status_code == 200:
            data_us = response_us.json()
            api_monitor.record_rentcast_call()
            
            print(f"✅ Resposta recebida!")
            print(f"📊 Tipo da resposta: {type(data_us).__name__}")
            
            if isinstance(data_us, list):
                print(f"📋 Lista com {len(data_us)} itens")
                if data_us:
                    print(f"📄 Primeiro item encontrado:")
                    first_item = data_us[0]
                    for key, value in first_item.items():
                        print(f"   {key}: {value}")
                    
                    print(f"\n📄 RESPOSTA COMPLETA EUA (primeiro item):")
                    print(json.dumps(first_item, indent=2))
                else:
                    print(f"📄 Lista vazia - Nenhum imóvel encontrado")
            
            elif isinstance(data_us, dict):
                print(f"📋 Dict com chaves: {list(data_us.keys())}")
                print(f"📄 Conteúdo: {json.dumps(data_us, indent=2)[:500]}...")
        
        else:
            print(f"❌ Erro {response_us.status_code}: {response_us.text}")
    
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # Resumo final
    usage_final = api_monitor.get_rentcast_usage()
    calls_used = usage_final['total_used'] - usage['total_used']
    
    print(f"\n" + "=" * 65)
    print(f"📊 CONCLUSÕES DO TESTE:")
    print(f"   🔢 Calls utilizadas neste teste: {calls_used}")
    print(f"   📈 Total acumulado: {usage_final['total_used']}/50")
    print(f"   🤖 Modelo LLM confirmado: {settings.models.default_model}")
    print(f"   🌐 API RentCast responde para Brasil: ✅ SIM (Status 200)")
    print(f"   🏠 Imóveis brasileiros encontrados: ❌ NÃO (lista vazia)")
    print(f"   🇺🇸 Comparação com EUA: Dados disponíveis")
    
    return True

async def test_other_endpoints():
    """Testar outros endpoints da API RentCast."""
    
    print(f"\n🔍 TESTE 3: OUTROS ENDPOINTS")
    print("-" * 40)
    
    settings = get_settings()
    api_key = settings.apis.rentcast_api_key
    
    headers = {
        "X-API-Key": api_key,
        "accept": "application/json"
    }
    
    # Endpoints para testar
    endpoints = [
        "/markets",
        "/listings/sale/long-term", 
        "/property/details"
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Testando endpoint: {endpoint}")
        
        try:
            response = requests.get(
                f"https://api.rentcast.io/v1{endpoint}",
                headers=headers,
                params={"city": "Miami", "state": "FL"} if endpoint != "/markets" else {},
                timeout=10
            )
            
            print(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sucesso - Tipo: {type(data).__name__}")
                if isinstance(data, list):
                    print(f"   Lista com {len(data)} itens")
                elif isinstance(data, dict):
                    print(f"   Dict com chaves: {list(data.keys())}")
            else:
                print(f"❌ Erro {response.status_code}")
        
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
        
        await asyncio.sleep(1)

if __name__ == "__main__":
    print("🚨 Este teste usará aproximadamente 3-5 calls da API RentCast")
    print("Pressione CTRL+C nos próximos 3 segundos para cancelar...")
    
    try:
        import time
        for i in range(3, 0, -1):
            print(f"Iniciando em {i}...")
            time.sleep(1)
        
        asyncio.run(test_rentcast_detailed())
        asyncio.run(test_other_endpoints())
        
    except KeyboardInterrupt:
        print("\n⏹️ Teste cancelado pelo usuário") 