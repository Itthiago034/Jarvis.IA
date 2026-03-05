"""
JARVIS CLI - Configurações
==========================
Gerencia configurações do usuário e do CLI.
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# Diretório de dados do CLI
CLI_DATA_DIR = Path.home() / ".jarvis-code"
CONFIG_FILE = CLI_DATA_DIR / "config.json"
HISTORY_DIR = CLI_DATA_DIR / "history"


@dataclass
class CLIConfig:
    """Configuração do CLI"""
    # Modelo e API
    model: str = "gemini-2.5-flash"
    api_key_env: str = "GOOGLE_API_KEY"
    
    # Interface
    theme: str = "monokai"  # Tema para syntax highlighting
    show_tokens: bool = False  # Mostrar contagem de tokens
    stream_output: bool = True  # Streaming de resposta
    
    # Comportamento
    auto_context: bool = True  # Detectar contexto automaticamente
    max_context_files: int = 10  # Máximo de arquivos no contexto
    save_history: bool = True  # Salvar histórico de conversas
    
    # Agente padrão
    default_agent: str = "coder"
    
    # Atalhos personalizados
    aliases: dict = field(default_factory=lambda: {
        "r": "review",
        "d": "debug",
        "t": "test",
        "e": "explain"
    })
    
    @classmethod
    def load(cls) -> "CLIConfig":
        """Carrega configuração do arquivo"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**data)
            except Exception:
                pass
        return cls()
    
    def save(self):
        """Salva configuração no arquivo"""
        CLI_DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)
    
    def get_api_key(self) -> Optional[str]:
        """Obtém a API key do ambiente"""
        return os.getenv(self.api_key_env)


def ensure_dirs():
    """Garante que os diretórios necessários existem"""
    CLI_DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


# Configuração global
_config: Optional[CLIConfig] = None


def get_config() -> CLIConfig:
    """Obtém configuração global (singleton)"""
    global _config
    if _config is None:
        _config = CLIConfig.load()
    return _config
