#!/usr/bin/env python3
"""
Script de Cadastro de Voz - JARVIS
==================================
Execute este script para cadastrar sua voz no JARVIS.

Uso:
    python enroll_voice.py           # Cadastra usuário "Thiago"
    python enroll_voice.py --name Maria   # Cadastra usuário "Maria"
    python enroll_voice.py --test    # Testa verificação
    python enroll_voice.py --list    # Lista usuários cadastrados
"""

import sys
import argparse
from pathlib import Path

# Adiciona o src ao path para importação em runtime
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.jarvis.voice_verification import (  # noqa: E402
    interactive_enrollment,
    test_verification,
    get_verifier
)


def main():
    parser = argparse.ArgumentParser(
        description="Cadastro de Voz do JARVIS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python enroll_voice.py               # Cadastra voz do Thiago
  python enroll_voice.py --name Maria  # Cadastra voz da Maria
  python enroll_voice.py --test        # Testa se reconhece sua voz
  python enroll_voice.py --list        # Lista usuários cadastrados
  python enroll_voice.py --remove Ana  # Remove cadastro da Ana
        """
    )
    
    parser.add_argument(
        "--name", "-n",
        type=str,
        default="Thiago",
        help="Nome do usuário a cadastrar (padrão: Thiago)"
    )
    
    parser.add_argument(
        "--samples", "-s",
        type=int,
        default=5,
        help="Número de amostras de áudio (padrão: 5)"
    )
    
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Modo de teste: verifica se reconhece sua voz"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Lista usuários cadastrados"
    )
    
    parser.add_argument(
        "--remove", "-r",
        type=str,
        metavar="NOME",
        help="Remove cadastro de um usuário"
    )
    
    parser.add_argument(
        "--threshold",
        type=float,
        help="Ajusta threshold de similaridade (0.6-0.95)"
    )
    
    args = parser.parse_args()
    
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║     JARVIS - Sistema de Verificação de Voz        ║
    ║              Powered by Resemblyzer               ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # Lista usuários
    if args.list:
        verifier = get_verifier()
        users = verifier.list_enrolled_users()
        print("\n📋 Usuários cadastrados:")
        if users:
            for user in users:
                print(f"   ✓ {user}")
        else:
            print("   (nenhum usuário cadastrado)")
        return
    
    # Remove usuário
    if args.remove:
        verifier = get_verifier()
        if verifier.remove_user(args.remove):
            print(f"\n✅ Usuário '{args.remove}' removido com sucesso!")
        else:
            print(f"\n❌ Erro ao remover '{args.remove}'")
        return
    
    # Ajusta threshold
    if args.threshold:
        verifier = get_verifier()
        verifier.adjust_threshold(args.threshold)
        print(f"\n✅ Threshold ajustado para {args.threshold}")
        return
    
    # Modo de teste
    if args.test:
        test_verification()
        return
    
    # Cadastro padrão
    print(f"\n🎤 Modo: Cadastro de voz para '{args.name}'")
    print(f"   Amostras a gravar: {args.samples}")
    interactive_enrollment(args.name, args.samples)
    
    print("\n" + "="*50)
    print("PRÓXIMOS PASSOS:")
    print("="*50)
    print("1. Teste com: python enroll_voice.py --test")
    print("2. O JARVIS agora pode verificar se é você falando")
    print("="*50)


if __name__ == "__main__":
    main()
