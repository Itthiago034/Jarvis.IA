"""
JARVIS - Teste do CodeAgent
===========================
Script para testar as ferramentas do CodeAgent sem precisar do google-adk.
Simula o comportamento esperado do agente.
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_code_analysis():
    """Testa ferramentas de análise de código"""
    print("\n" + "="*60)
    print("🔍 TESTE: Análise de Código")
    print("="*60)
    
    from jarvis.tools.code_analysis import (
        get_syntax_errors,
        find_symbol_usages,
        count_code_metrics
    )
    
    # Testar em um arquivo do próprio projeto
    test_file = Path(__file__).parent.parent / "src" / "jarvis" / "tools" / "terminal.py"
    
    print(f"\n📄 Analisando: {test_file.name}")
    
    # Verificar erros de sintaxe
    errors = get_syntax_errors(str(test_file))
    if errors:
        print(f"❌ Erros encontrados: {len(errors)}")
        for err in errors:
            print(f"   Linha {err['line']}: {err['message']}")
    else:
        print("✅ Nenhum erro de sintaxe")
    
    # Métricas
    metrics = count_code_metrics(str(test_file))
    print(f"\n📊 Métricas:")
    print(f"   Total de linhas: {metrics.get('total_lines', 0)}")
    print(f"   Linhas de código: {metrics.get('code_lines', 0)}")
    print(f"   Funções: {metrics.get('functions', 0)}")
    print(f"   Classes: {metrics.get('classes', 0)}")
    
    # Buscar usos de uma função
    workspace = str(Path(__file__).parent.parent / "src")
    usages = find_symbol_usages("run_command", workspace, "**/*.py")
    print(f"\n🔗 Usos de 'run_command': {len(usages)} encontrados")
    for usage in usages[:5]:
        print(f"   {Path(usage['file_path']).name}:{usage['line']} - {usage['usage_type']}")
    
    return True


def test_git_tools():
    """Testa ferramentas Git"""
    print("\n" + "="*60)
    print("📊 TESTE: Git Tools")
    print("="*60)
    
    from jarvis.tools.git_tools import (
        is_git_repository,
        get_repository_status,
        get_current_branch,
        get_commit_history
    )
    
    workspace = str(Path(__file__).parent.parent)
    
    if not is_git_repository(workspace):
        print("⚠️ Não é um repositório Git")
        return False
    
    print("✅ Repositório Git detectado")
    
    # Branch atual
    branch = get_current_branch(workspace)
    print(f"🌿 Branch atual: {branch}")
    
    # Status
    status = get_repository_status(workspace)
    print(f"\n📋 Status:")
    print(f"   Arquivos staged: {status.get('staged_count', 0)}")
    print(f"   Arquivos modificados: {status.get('unstaged_count', 0)}")
    print(f"   Arquivos untracked: {status.get('untracked_count', 0)}")
    
    # Últimos commits
    commits = get_commit_history(workspace, max_commits=3)
    print(f"\n📜 Últimos commits:")
    for commit in commits:
        print(f"   {commit['hash']} - {commit['message'][:50]}...")
    
    return True


def test_refactoring():
    """Testa ferramentas de refatoração"""
    print("\n" + "="*60)
    print("🔧 TESTE: Refatoração")
    print("="*60)
    
    from jarvis.tools.refactoring import (
        organize_imports,
        generate_docstring,
        rename_symbol
    )
    
    # Código de exemplo para refatorar
    sample_code = '''
import os
import json
from pathlib import Path
import sys
from typing import List, Dict
import asyncio
from dataclasses import dataclass

def calculate_total(items, tax_rate):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total * (1 + tax_rate)

class OrderProcessor:
    def __init__(self):
        self.orders = []
    
    def add_order(self, order):
        self.orders.append(order)
    
    def process_all(self):
        for order in self.orders:
            self._process(order)
'''
    
    # Organizar imports
    print("\n📦 Organizando imports...")
    result = organize_imports(sample_code)
    if result['success']:
        print(f"   ✅ Imports organizados!")
        print(f"   stdlib: {result['stdlib_count']}, third-party: {result['thirdparty_count']}, local: {result['local_count']}")
    
    # Gerar docstring
    print("\n📝 Gerando docstring para 'calculate_total'...")
    result = generate_docstring(sample_code, "calculate_total", style="google")
    if result['success']:
        print("   ✅ Docstring gerada:")
        for line in result['docstring'].split('\n')[:5]:
            print(f"      {line}")
        print("      ...")
    
    # Renomear símbolo
    print("\n✏️ Renomeando 'calculate_total' -> 'compute_order_total'...")
    result = rename_symbol(sample_code, "calculate_total", "compute_order_total")
    if result['success']:
        print(f"   ✅ {result['occurrences_replaced']} ocorrências substituídas")
    
    return True


def test_diagram_generation():
    """Testa geração de diagramas"""
    print("\n" + "="*60)
    print("📐 TESTE: Geração de Diagramas")
    print("="*60)
    
    from jarvis.tools.diagram_tools import (
        generate_flowchart,
        add_flowchart_connections,
        generate_class_diagram_from_file,
        generate_architecture_diagram
    )
    
    # Gerar flowchart
    print("\n🔀 Gerando flowchart...")
    steps = [
        {"id": "A", "text": "Usuário fala", "type": "start"},
        {"id": "B", "text": "JARVIS processa", "type": "process"},
        {"id": "C", "text": "É programação?", "type": "decision"},
        {"id": "D", "text": "CodeAgent executa", "type": "process"},
        {"id": "E", "text": "Resposta direta", "type": "process"},
        {"id": "F", "text": "Retorna resultado", "type": "end"},
    ]
    
    flowchart = generate_flowchart("Fluxo JARVIS + CodeAgent", steps)
    connections = [
        ("A", "B"),
        ("B", "C"),
        ("C", "D", "Sim"),
        ("C", "E", "Não"),
        ("D", "F"),
        ("E", "F"),
    ]
    flowchart = add_flowchart_connections(flowchart, connections)
    
    print("   ✅ Flowchart gerado:")
    for line in flowchart.split('\n')[:8]:
        print(f"      {line}")
    print("      ...")
    
    # Gerar diagrama de arquitetura
    print("\n🏗️ Gerando diagrama de arquitetura...")
    components = [
        {"id": "user", "name": "Usuário", "type": "client"},
        {"id": "jarvis", "name": "JARVIS", "type": "service"},
        {"id": "code_agent", "name": "CodeAgent", "type": "service"},
        {"id": "gemini", "name": "Gemini API", "type": "external"},
        {"id": "mem0", "name": "Mem0", "type": "database"},
    ]
    flows = [
        {"from": "user", "to": "jarvis", "label": "Voz/Texto"},
        {"from": "jarvis", "to": "code_agent", "label": "Delega código"},
        {"from": "code_agent", "to": "gemini", "label": "LLM"},
        {"from": "jarvis", "to": "mem0", "label": "Memória"},
    ]
    
    arch_diagram = generate_architecture_diagram("Arquitetura JARVIS", components, flows)
    print("   ✅ Diagrama de arquitetura gerado!")
    
    # Gerar diagrama de classes de um arquivo real
    print("\n📊 Gerando diagrama de classes automaticamente...")
    test_file = Path(__file__).parent.parent / "src" / "jarvis" / "tools" / "git_tools.py"
    if test_file.exists():
        class_diagram = generate_class_diagram_from_file(str(test_file))
        if "Erro" not in class_diagram:
            print("   ✅ Diagrama de classes gerado do arquivo!")
        else:
            print(f"   ⚠️ {class_diagram}")
    
    return True


def test_complex_task():
    """
    🎯 TAREFA COMPLEXA: Simula o que o CodeAgent faria
    
    Tarefa: "Analise o arquivo agent.py, encontre problemas,
    sugira melhorias e gere um diagrama de classes"
    """
    print("\n" + "="*60)
    print("🎯 TAREFA COMPLEXA: Análise Completa de Arquivo")
    print("="*60)
    
    from jarvis.tools.code_analysis import get_python_errors, count_code_metrics, find_symbol_usages
    from jarvis.tools.diagram_tools import generate_class_diagram_from_file
    from jarvis.tools.refactoring import generate_docstring
    
    target_file = Path(__file__).parent.parent / "src" / "jarvis" / "agent.py"
    workspace = str(Path(__file__).parent.parent / "src")
    
    if not target_file.exists():
        print(f"⚠️ Arquivo {target_file} não encontrado")
        return False
    
    print(f"\n📄 Arquivo alvo: {target_file.name}")
    print("-" * 40)
    
    # PASSO 1: Métricas do código
    print("\n📊 PASSO 1: Coletando métricas...")
    metrics = count_code_metrics(str(target_file))
    print(f"   Linhas totais: {metrics.get('total_lines', 0)}")
    print(f"   Linhas de código: {metrics.get('code_lines', 0)}")
    print(f"   Comentários: {metrics.get('comment_lines', 0)}")
    print(f"   Funções: {metrics.get('functions', 0)}")
    print(f"   Classes: {metrics.get('classes', 0)}")
    print(f"   Docstrings: {metrics.get('docstrings', 0)}")
    
    # PASSO 2: Verificar erros
    print("\n🐛 PASSO 2: Verificando erros...")
    errors = get_python_errors(str(target_file), use_pylint=False)
    if errors:
        print(f"   ❌ {len(errors)} erros encontrados:")
        for err in errors[:5]:
            print(f"      Linha {err.get('line', '?')}: {err.get('message', '')[:60]}")
    else:
        print("   ✅ Nenhum erro de sintaxe!")
    
    # PASSO 3: Análise de símbolos
    print("\n🔗 PASSO 3: Analisando símbolos principais...")
    symbols_to_check = ["JarvisVoiceAgent", "run", "initialize"]
    for symbol in symbols_to_check:
        usages = find_symbol_usages(symbol, workspace, "**/*.py")
        if usages:
            defs = [u for u in usages if 'definition' in u.get('usage_type', '')]
            refs = [u for u in usages if 'reference' in u.get('usage_type', '')]
            print(f"   '{symbol}': {len(defs)} definições, {len(refs)} referências")
    
    # PASSO 4: Gerar diagrama
    print("\n📐 PASSO 4: Gerando diagrama de classes...")
    diagram = generate_class_diagram_from_file(str(target_file))
    if "Erro" not in diagram and "Nenhuma" not in diagram:
        print("   ✅ Diagrama gerado com sucesso!")
        print("\n   Preview do diagrama:")
        for line in diagram.split('\n')[:10]:
            print(f"   {line}")
    else:
        print(f"   ⚠️ {diagram[:100]}")
    
    # PASSO 5: Sugestões de melhoria
    print("\n💡 PASSO 5: Sugestões de melhoria...")
    suggestions = []
    
    # Análise baseada em métricas
    if metrics.get('total_lines', 0) > 500:
        suggestions.append("Considere dividir o arquivo em módulos menores")
    
    code_lines = metrics.get('code_lines', 0)
    comment_lines = metrics.get('comment_lines', 0)
    if code_lines > 0 and comment_lines / code_lines < 0.1:
        suggestions.append("Adicionar mais comentários/documentação")
    
    if metrics.get('docstrings', 0) < metrics.get('functions', 0):
        suggestions.append("Adicionar docstrings às funções")
    
    if not suggestions:
        suggestions.append("Código está bem estruturado!")
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    print("\n" + "="*60)
    print("✅ ANÁLISE COMPLETA FINALIZADA")
    print("="*60)
    
    return True


def main():
    """Executa todos os testes"""
    print("\n" + "🤖 "*20)
    print("   JARVIS CodeAgent - Suite de Testes")
    print("🤖 "*20)
    
    results = []
    
    try:
        results.append(("Análise de Código", test_code_analysis()))
    except Exception as e:
        print(f"❌ Erro em Análise de Código: {e}")
        results.append(("Análise de Código", False))
    
    try:
        results.append(("Git Tools", test_git_tools()))
    except Exception as e:
        print(f"❌ Erro em Git Tools: {e}")
        results.append(("Git Tools", False))
    
    try:
        results.append(("Refatoração", test_refactoring()))
    except Exception as e:
        print(f"❌ Erro em Refatoração: {e}")
        results.append(("Refatoração", False))
    
    try:
        results.append(("Diagramas", test_diagram_generation()))
    except Exception as e:
        print(f"❌ Erro em Diagramas: {e}")
        results.append(("Diagramas", False))
    
    try:
        results.append(("Tarefa Complexa", test_complex_task()))
    except Exception as e:
        print(f"❌ Erro em Tarefa Complexa: {e}")
        results.append(("Tarefa Complexa", False))
    
    # Resumo
    print("\n" + "="*60)
    print("📋 RESUMO DOS TESTES")
    print("="*60)
    
    passed = 0
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n   Total: {passed}/{len(results)} testes passaram")
    print("="*60)


if __name__ == "__main__":
    main()
