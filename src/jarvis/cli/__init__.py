"""
JARVIS CodeAgent CLI
====================
Interface de linha de comando para o CodeAgent.
Permite interação direta via terminal sem necessidade de voz.
"""

from .main import app, main_entrypoint
from .agents import AgentType, get_agent_instruction, get_agent_profile
from .context import ProjectContext, ContextDetector
from .history import ChatHistory, ChatSession
from .config import get_config, CLIConfig

__version__ = "0.1.0"
__all__ = [
    "app", 
    "main_entrypoint",
    "AgentType", 
    "get_agent_instruction",
    "get_agent_profile",
    "ProjectContext",
    "ContextDetector", 
    "ChatHistory",
    "ChatSession",
    "get_config",
    "CLIConfig",
]
