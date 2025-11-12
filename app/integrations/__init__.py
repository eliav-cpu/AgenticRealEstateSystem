"""
Integrações externas do sistema.
"""

from .mcp import MCPPropertyServer, mcp_server

__all__ = [
    "MCPPropertyServer",
    "mcp_server"
] 