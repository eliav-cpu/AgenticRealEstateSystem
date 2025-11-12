#!/usr/bin/env python3
"""
Debug script para verificar carregamento da chave OpenRouter
"""

import os
from dotenv import load_dotenv

print("=== DEBUG OPENROUTER KEY ===")

# 1. Verificar arquivo .env
print(f"1. .env exists: {os.path.exists('.env')}")

# 2. Carregar .env
load_result = load_dotenv()
print(f"2. load_dotenv result: {load_result}")

# 3. Verificar variável de ambiente
env_key = os.getenv('OPENROUTER_API_KEY', 'NOT_FOUND')
print(f"3. Env key found: {env_key != 'NOT_FOUND'}")
if env_key != 'NOT_FOUND':
    print(f"4. Env key length: {len(env_key)}")
    print(f"5. Env key starts: {env_key[:20]}...")

# 4. Testar configurações
try:
    from config.settings import get_settings
    settings = get_settings()
    settings_key = settings.apis.openrouter_key
    print(f"6. Settings key found: {bool(settings_key)}")
    if settings_key:
        print(f"7. Settings key length: {len(settings_key)}")
        print(f"8. Settings key starts: {settings_key[:20]}...")
        print(f"9. Keys match: {env_key == settings_key}")
    else:
        print(f"7. Settings key is EMPTY")
except Exception as e:
    print(f"6. Error loading settings: {e}")

print("=== END DEBUG ===") 