"""Teste rápido da tarefa complexa"""
import sys
sys.path.insert(0, 'src')
from pathlib import Path
from jarvis.tools.code_analysis import get_python_errors, count_code_metrics, find_symbol_usages  # type: ignore
from jarvis.tools.diagram_tools import generate_class_diagram_from_file  # type: ignore

target_file = 'src/jarvis/agent.py'
workspace = 'src'

print('='*60)
print('🎯 TAREFA COMPLEXA: Análise do agent.py')
print('='*60)

# Métricas
metrics = count_code_metrics(target_file)
print(f"""
📊 MÉTRICAS DO CÓDIGO:
   Linhas totais: {metrics.get('total_lines', 0)}
   Linhas de código: {metrics.get('code_lines', 0)}
   Comentários: {metrics.get('comment_lines', 0)}
   Funções: {metrics.get('functions', 0)}
   Classes: {metrics.get('classes', 0)}
   Docstrings: {metrics.get('docstrings', 0)}
   Imports: {metrics.get('imports', 0)}
""")

# Erros
errors = get_python_errors(target_file, use_pylint=False)
if errors:
    print(f'🐛 ERROS ENCONTRADOS: {len(errors)}')
    for err in errors[:3]:
        msg = str(err.get('message', ''))[:60]
        print(f"   Linha {err.get('line', '?')}: {msg}")
else:
    print('✅ Nenhum erro de sintaxe!')

# Usos de símbolos
print()
print('🔗 ANÁLISE DE SÍMBOLOS:')
for symbol in ['JarvisVoiceAgent', 'handle_message', 'connect']:
    usages = find_symbol_usages(symbol, workspace, '**/*.py')
    defs = len([u for u in usages if 'definition' in u.get('usage_type', '')])
    refs = len([u for u in usages if 'reference' in u.get('usage_type', '')])
    print(f'   {symbol}: {defs} definição(ões), {refs} referência(s)')

# Diagrama de classes
print()
print('📐 DIAGRAMA DE CLASSES (Mermaid):')
diagram = generate_class_diagram_from_file(target_file)
for line in diagram.split('\n')[:12]:
    print(f'   {line}')
print('   ...')

# Sugestões
print()
print('💡 SUGESTÕES DE MELHORIA:')
suggestions = []
if metrics.get('total_lines', 0) > 300:
    suggestions.append('Arquivo grande - considere modularizar')
if metrics.get('docstrings', 0) < metrics.get('functions', 0) // 2:
    suggestions.append('Adicione mais docstrings às funções')
if metrics.get('comment_lines', 0) < metrics.get('code_lines', 0) * 0.05:
    suggestions.append('Adicione mais comentários explicativos')
ratio = metrics.get('docstrings', 0) / max(metrics.get('functions', 0), 1)
if ratio > 0.7:
    suggestions.append('✅ Boa cobertura de docstrings!')
if not suggestions:
    suggestions.append('Código bem estruturado!')

for i, s in enumerate(suggestions, 1):
    print(f'   {i}. {s}')

print()
print('='*60)
print('✅ ANÁLISE COMPLETA!')
print('='*60)
