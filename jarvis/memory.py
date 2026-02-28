"""
Gerenciamento de memória de conversação da JARVIS.
Mantém o histórico de mensagens para context window da API.
"""

from typing import List, Dict


class ConversationMemory:
    """Armazena o histórico de mensagens da conversa."""

    def __init__(self, max_messages: int = 20):
        self._history: List[Dict[str, str]] = []
        self.max_messages = max_messages

    def add_user(self, content: str) -> None:
        self._history.append({"role": "user", "content": content})
        self._trim()

    def add_assistant(self, content: str) -> None:
        self._history.append({"role": "assistant", "content": content})
        self._trim()

    def get_messages(self) -> List[Dict[str, str]]:
        return list(self._history)

    def clear(self) -> None:
        self._history.clear()

    def _trim(self) -> None:
        """Remove as mensagens mais antigas quando o limite é ultrapassado."""
        if len(self._history) > self.max_messages:
            self._history = self._history[-self.max_messages :]
