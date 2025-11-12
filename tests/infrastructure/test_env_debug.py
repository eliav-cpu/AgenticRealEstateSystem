#!/usr/bin/env python3
"""
Script de debug para testar carregamento do .env
"""

import os
from dotenv import load_dotenv

print("=== DEBUG .ENV LOADING ===")

# 1. Verificar se arquivo existe
env_exists = os.path.exists('.env')
print(f"1. .env file exists: {env_exists}")

if env_exists:
    with open('.env', 'r') as f:
        content = f.read()
    print(f"2. .env content length: {len(content)} chars")
    print(f"3. .env first line: {content.split()[0] if content.strip() else 'EMPTY'}")

# 2. Carregar .env
load_result = load_dotenv()
print(f"4. load_dotenv() result: {load_result}")

# 3. Verificar chave
key = os.getenv('OPENROUTER_API_KEY', 'NOT_FOUND')
print(f"5. OPENROUTER_API_KEY found: {key != 'NOT_FOUND'}")
if key != 'NOT_FOUND':
    print(f"6. Key starts with: {key[:20]}...")
    print(f"7. Key length: {len(key)}")

# 4. Testar configurações
try:
    from config.settings import get_settings
    settings = get_settings()
    settings_key = settings.apis.openrouter_key
    print(f"8. Settings key found: {bool(settings_key)}")
    if settings_key:
        print(f"9. Settings key starts with: {settings_key[:20]}...")
        print(f"10. Settings key length: {len(settings_key)}")
        print(f"11. Keys match: {key == settings_key}")
    else:
        print(f"9. Settings key is empty or None")
except Exception as e:
    print(f"8. Error loading settings: {e}")

print("=== END DEBUG ===") 