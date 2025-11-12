"""
Monitor de uso da API RentCast para controlar limite de calls.

Garante que não ultrapassemos o limite de 50 calls da API.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

class APIUsageMonitor:
    """Monitor de uso das APIs externas."""
    
    def __init__(self, usage_file: str = ".api_usage.json"):
        self.usage_file = Path(usage_file)
        self.usage_data = self._load_usage()
    
    def _load_usage(self) -> Dict[str, Any]:
        """Carrega dados de uso existentes."""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "rentcast": {
                "total_calls": 0,
                "daily_calls": {},
                "last_reset": datetime.now().date().isoformat()
            },
            "openrouter": {
                "total_calls": 0,
                "daily_calls": {}
            }
        }
    
    def _save_usage(self):
        """Salva dados de uso atualizados."""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
    
    def can_use_rentcast(self) -> bool:
        """Verifica se ainda pode usar a API RentCast."""
        total_calls = self.usage_data["rentcast"]["total_calls"]
        return total_calls < 50
    
    def get_rentcast_usage(self) -> Dict[str, int]:
        """Retorna estatísticas de uso da RentCast."""
        total = self.usage_data["rentcast"]["total_calls"]
        remaining = max(0, 50 - total)
        
        return {
            "total_used": total,
            "remaining": remaining,
            "limit": 50,
            "percentage_used": (total / 50) * 100
        }
    
    def record_rentcast_call(self) -> bool:
        """Registra uma chamada para a RentCast API."""
        if not self.can_use_rentcast():
            return False
        
        today = datetime.now().date().isoformat()
        
        # Incrementar contador total
        self.usage_data["rentcast"]["total_calls"] += 1
        
        # Incrementar contador diário
        daily = self.usage_data["rentcast"]["daily_calls"]
        daily[today] = daily.get(today, 0) + 1
        
        self._save_usage()
        return True
    
    def get_warning_message(self) -> str:
        """Retorna mensagem de aviso baseada no uso atual."""
        usage = self.get_rentcast_usage()
        total = usage["total_used"]
        
        if total >= 45:
            return f"🚨 CRÍTICO: {total}/50 calls usadas! Usar apenas para testes finais!"
        elif total >= 25:
            return f"⚠️ ATENÇÃO: {total}/50 calls usadas! Sistema deve estar pronto!"
        elif total >= 10:
            return f"📊 INFO: {total}/50 calls usadas. Usar com moderação."
        else:
            return f"✅ OK: {total}/50 calls usadas. Uso normal permitido."

# Instância global do monitor
api_monitor = APIUsageMonitor() 