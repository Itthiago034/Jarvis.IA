"""Teste de acesso a pastas externas"""
import sys
sys.path.insert(0, 'c:/Users/Thiago/OneDrive/Documentos/JARVIS/Jarvis.IA/src')

from jarvis.tools.code_analysis import count_code_metrics
from jarvis.tools.search import list_directory

print("="*60)
print("🌍 TESTE: CodeAgent acessando OUTRAS PASTAS")
print("="*60)

# 1. Listar Documentos
print("\n📁 Listando C:/Users/Thiago/OneDrive/Documentos/")
dirs = list_directory('C:/Users/Thiago/OneDrive/Documentos')
for item in dirs[:8]:
    name = item.get('name', '')
    tipo = '📂' if item.get('type') == 'directory' else '📄'
    print(f"   {tipo} {name}")
print(f"   ... total: {len(dirs)} itens")

# 2. Analisar arquivo de OUTRO projeto
external_file = 'C:/Users/Thiago/OneDrive/Documentos/LLMs-from-scratch-main/conftest.py'
print(f"\n📊 Analisando arquivo EXTERNO:")
print(f"   {external_file}")

metrics = count_code_metrics(external_file)
if 'error' not in metrics or not metrics.get('error'):
    print(f"   ✅ Linhas totais: {metrics['total_lines']}")
    print(f"   ✅ Funções: {metrics['functions']}")
    print(f"   ✅ Classes: {metrics['classes']}")
else:
    print(f"   ⚠️ {metrics.get('error', 'Arquivo não encontrado')}")

# 3. Tentar Desktop
print("\n📁 Listando Desktop:")
desktop = list_directory('C:/Users/Thiago/Desktop')
for item in desktop[:5]:
    name = item.get('name', '')
    tipo = '📂' if item.get('type') == 'directory' else '📄'
    print(f"   {tipo} {name}")

print("\n" + "="*60)
print("✅ CodeAgent TEM ACESSO a qualquer pasta do sistema!")
print("="*60)
