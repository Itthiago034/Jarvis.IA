"""
JARVIS - Agents Module
======================
Módulo de agentes especializados do JARVIS.

SubAgents disponíveis:
- CodeAgent: Engenheiro de Software Sênior para análise e criação de código
"""

from .code_agent import CodeAgent, CodeTaskResult, TaskType

__all__ = [
    "CodeAgent",
    "CodeTaskResult", 
    "TaskType",
]
