#!/usr/bin/env python3
"""
Ponto de entrada CLI da JARVIS.
Execute com: python jarvis.py
"""

import os
import sys

from dotenv import load_dotenv

from jarvis import Jarvis

load_dotenv()

_EXIT_COMMANDS = {"sair", "exit", "quit"}

_BANNER = """
╔══════════════════════════════════════════════╗
║              J  A  R  V  I  S                ║
║      Sua aliada pessoal de inteligência      ║
╚══════════════════════════════════════════════╝
  Digite sua mensagem e pressione Enter.
  Para encerrar: sair / exit / quit
"""


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Erro: variável de ambiente OPENAI_API_KEY não encontrada.")
        print("Copie .env.example para .env e adicione sua chave de API.")
        sys.exit(1)

    model = os.getenv("JARVIS_MODEL", "gpt-4o")
    jarvis = Jarvis(api_key=api_key, model=model)

    print(_BANNER)

    while True:
        try:
            user_input = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nJARVIS: Até logo, Chefe.")
            break

        if not user_input:
            continue

        if user_input.lower() in _EXIT_COMMANDS:
            print("JARVIS: Até logo, Chefe.")
            break

        try:
            reply = jarvis.chat(user_input)
            print(f"JARVIS: {reply}\n")
        except Exception as exc:  # pragma: no cover
            print(f"JARVIS: Encontrei um problema — {exc}\n")


if __name__ == "__main__":
    main()
