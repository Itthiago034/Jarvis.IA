"""
Classe principal da JARVIS — orquestra personalidade, memória e chamadas à API.
"""

from openai import OpenAI

from .memory import ConversationMemory
from .personality import SYSTEM_PROMPT


class Jarvis:
    """Assistente pessoal JARVIS."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._memory = ConversationMemory()

    def chat(self, user_message: str) -> str:
        """Envia uma mensagem e retorna a resposta da JARVIS."""
        self._memory.add_user(user_message)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self._memory.get_messages()

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.8,
        )

        reply = response.choices[0].message.content.strip()
        self._memory.add_assistant(reply)
        return reply

    def clear_memory(self) -> None:
        """Limpa o histórico de conversação."""
        self._memory.clear()
