"""
JARVIS - Ponto de entrada principal
Execute este arquivo para iniciar o agente de voz
"""
import sys
from pathlib import Path

# Adiciona o diretório src ao path para imports funcionarem
sys.path.insert(0, str(Path(__file__).parent / "src"))

from livekit import agents
from jarvis.agent import entrypoint

if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )
