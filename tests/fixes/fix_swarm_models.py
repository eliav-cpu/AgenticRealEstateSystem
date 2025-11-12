#!/usr/bin/env python3
"""
Script para corrigir modelos no swarm.py
"""

import re

def fix_swarm_models():
    """Corrige todas as referências aos modelos no swarm.py"""
    
    # Ler arquivo
    with open('app/orchestration/swarm.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir openai/gpt-4o-mini por meta-llama/llama-4-maverick:free
    new_content = re.sub(
        r'"openai/gpt-4o-mini",  # Modelo mais estável',
        '"meta-llama/llama-4-maverick:free",  # Modelo gratuito que funciona',
        content
    )
    
    # Verificar se houve mudanças
    if content != new_content:
        # Escrever arquivo corrigido
        with open('app/orchestration/swarm.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Modelos do Swarm atualizados:")
        print("   openai/gpt-4o-mini → meta-llama/llama-4-maverick:free")
        
        # Contar quantas substituições foram feitas
        count = content.count('"openai/gpt-4o-mini",  # Modelo mais estável')
        print(f"   {count} ocorrências corrigidas")
    else:
        print("✅ Nenhuma correção necessária - arquivo já atualizado")

if __name__ == "__main__":
    fix_swarm_models() 