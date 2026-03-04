"""Configuração do pytest para os testes do JARVIS"""
import sys
from pathlib import Path

# Adiciona src ao PYTHONPATH para imports funcionarem corretamente
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
