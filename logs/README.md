# Sistema de Logs - Agentic Real Estate

## Estrutura de Logs

Esta pasta contém os logs estruturados do sistema agêntico, organizados por categoria:

### Arquivos de Log

- **`app.log`** - Logs gerais da aplicação e sistema
- **`agents.log`** - Logs específicos dos agentes (search, property, scheduling)
- **`handoffs.log`** - Logs de transferências e comunicação entre agentes
- **`performance.log`** - Métricas de performance e tempo de resposta
- **`api.log`** - Chamadas para APIs externas (OpenRouter, RentCast)
- **`errors.log`** - Erros, exceções e problemas do sistema

### Integração com Logfire

O sistema usa **Logfire** (nativo do PydanticAI) para observabilidade avançada:

- **Rastreamento de Agentes**: Cada execução de agente é rastreada
- **Métricas de Performance**: Tempo de resposta, tokens usados, custos
- **Fluxo de Dados**: Visualização do fluxo entre agentes
- **Debugging**: Logs detalhados para debug e troubleshooting

### Configuração

Os logs são configurados via:
- `config/settings.py` - Configurações de observabilidade
- `app/utils/logging.py` - Sistema de logging estruturado
- `app/utils/logfire_config.py` - Configuração específica do Logfire

### Visualização

- **Local**: Arquivos de log nesta pasta
- **Logfire Dashboard**: https://logfire.pydantic.dev (requer configuração)
- **Console**: Logs em tempo real durante desenvolvimento 