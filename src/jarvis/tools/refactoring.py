"""
JARVIS - Refactoring Tools
==========================
Ferramentas para refatoração de código Python.
Inclui: extract function, rename, organize imports, generate docstrings.
"""

import ast
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
import textwrap

logger = logging.getLogger(__name__)


@dataclass
class RefactoringResult:
    """Resultado de uma refatoração"""
    success: bool
    original_code: str
    refactored_code: str
    changes_made: List[str]
    message: str


def extract_function(
    source_code: str,
    start_line: int,
    end_line: int,
    function_name: str,
    parameters: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Extrai um trecho de código para uma nova função.
    
    Args:
        source_code: Código fonte original
        start_line: Linha inicial (1-based)
        end_line: Linha final (1-based)
        function_name: Nome da nova função
        parameters: Parâmetros opcionais
        
    Returns:
        Dicionário com código refatorado e nova função
    """
    lines = source_code.splitlines()
    
    if start_line < 1 or end_line > len(lines):
        return {
            "success": False,
            "error": f"Linhas inválidas. Arquivo tem {len(lines)} linhas."
        }
    
    # Extrair código
    extracted_lines = lines[start_line - 1:end_line]
    extracted_code = "\n".join(extracted_lines)
    
    # Detectar indentação base
    base_indent = len(extracted_lines[0]) - len(extracted_lines[0].lstrip())
    
    # Remover indentação base
    dedented_lines = []
    for line in extracted_lines:
        if line.strip():
            dedented_lines.append(line[base_indent:] if len(line) > base_indent else line)
        else:
            dedented_lines.append("")
    
    # Detectar variáveis usadas (análise simplificada)
    if parameters is None:
        parameters = _detect_variables(extracted_code)
    
    # Gerar nova função
    params_str = ", ".join(parameters) if parameters else ""
    new_function = [
        f"def {function_name}({params_str}):",
        f'    """TODO: Add docstring."""'
    ]
    
    for line in dedented_lines:
        new_function.append(f"    {line}" if line.strip() else "")
    
    new_function_code = "\n".join(new_function)
    
    # Gerar chamada da função
    indent = " " * base_indent
    call_code = f"{indent}{function_name}({params_str})"
    
    # Substituir no código original
    new_lines = lines[:start_line - 1] + [call_code] + lines[end_line:]
    
    return {
        "success": True,
        "new_function": new_function_code,
        "function_call": call_code,
        "refactored_code": "\n".join(new_lines),
        "extracted_lines": (start_line, end_line),
        "detected_parameters": parameters
    }


def rename_symbol(
    source_code: str,
    old_name: str,
    new_name: str,
    scope: str = "all"
) -> Dict[str, Any]:
    """
    Renomeia um símbolo (variável, função, classe) no código.
    
    Args:
        source_code: Código fonte
        old_name: Nome atual
        new_name: Novo nome
        scope: 'all', 'local', 'global'
        
    Returns:
        Dicionário com código refatorado
    """
    # Validar novo nome
    if not new_name.isidentifier():
        return {
            "success": False,
            "error": f"'{new_name}' não é um identificador Python válido"
        }
    
    # Verificar se novo nome já existe
    if re.search(rf'\b{new_name}\b', source_code):
        return {
            "success": False,
            "error": f"'{new_name}' já existe no código",
            "warning": "Renomear pode causar conflitos"
        }
    
    # Usar regex com word boundaries para evitar substituições parciais
    pattern = rf'\b{re.escape(old_name)}\b'
    
    # Contar ocorrências
    occurrences = len(re.findall(pattern, source_code))
    
    if occurrences == 0:
        return {
            "success": False,
            "error": f"'{old_name}' não encontrado no código"
        }
    
    # Substituir
    refactored_code = re.sub(pattern, new_name, source_code)
    
    return {
        "success": True,
        "refactored_code": refactored_code,
        "occurrences_replaced": occurrences,
        "old_name": old_name,
        "new_name": new_name
    }


def organize_imports(source_code: str) -> Dict[str, Any]:
    """
    Organiza imports no estilo PEP8.
    
    Ordem:
    1. Imports da biblioteca padrão
    2. Imports de terceiros
    3. Imports locais
    
    Args:
        source_code: Código fonte
        
    Returns:
        Código com imports organizados
    """
    # Biblioteca padrão Python comum
    STDLIB_MODULES = {
        'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections',
        'concurrent', 'contextlib', 'copy', 'dataclasses', 'datetime',
        'decimal', 'enum', 'functools', 'glob', 'hashlib', 'http',
        'io', 'itertools', 'json', 'logging', 'math', 'multiprocessing',
        'os', 'pathlib', 'pickle', 'platform', 'queue', 're', 'shutil',
        'socket', 'sqlite3', 'string', 'subprocess', 'sys', 'tempfile',
        'threading', 'time', 'traceback', 'typing', 'unittest', 'urllib',
        'uuid', 'warnings', 'weakref', 'xml', 'zipfile'
    }
    
    lines = source_code.splitlines()
    
    # Separar imports do resto do código
    imports = []
    from_imports = []
    other_code = []
    import_section_ended = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if not import_section_ended:
            if stripped.startswith('import '):
                imports.append(stripped)
            elif stripped.startswith('from '):
                from_imports.append(stripped)
            elif stripped.startswith('#') or stripped == '' or stripped.startswith('"""') or stripped.startswith("'''"):
                # Docstrings e comentários no início
                if not imports and not from_imports:
                    other_code.append(line)
                elif stripped == '':
                    continue  # Ignorar linhas vazias entre imports
                else:
                    import_section_ended = True
                    other_code.append(line)
            else:
                import_section_ended = True
                other_code.append(line)
        else:
            other_code.append(line)
    
    # Classificar imports
    stdlib_imports = []
    thirdparty_imports = []
    local_imports = []
    
    stdlib_from = []
    thirdparty_from = []
    local_from = []
    
    for imp in imports:
        module = imp.replace('import ', '').split('.')[0].split(' ')[0]
        if module in STDLIB_MODULES:
            stdlib_imports.append(imp)
        elif module.startswith('.'):
            local_imports.append(imp)
        else:
            thirdparty_imports.append(imp)
    
    for imp in from_imports:
        match = re.match(r'from\s+([.\w]+)', imp)
        if match:
            module = match.group(1).split('.')[0]
            if module.startswith('.'):
                local_from.append(imp)
            elif module in STDLIB_MODULES:
                stdlib_from.append(imp)
            else:
                thirdparty_from.append(imp)
    
    # Ordenar cada grupo
    stdlib_imports.sort()
    thirdparty_imports.sort()
    local_imports.sort()
    stdlib_from.sort()
    thirdparty_from.sort()
    local_from.sort()
    
    # Reconstruir
    new_code = []
    
    # Docstring ou comentários iniciais
    for line in other_code[:]:
        if line.strip() and not line.strip().startswith('#') and not line.strip().startswith(('"""', "'''")):
            break
        new_code.append(line)
        other_code.remove(line)
    
    # Imports stdlib
    if stdlib_imports or stdlib_from:
        for imp in stdlib_imports:
            new_code.append(imp)
        for imp in stdlib_from:
            new_code.append(imp)
        new_code.append("")
    
    # Imports terceiros
    if thirdparty_imports or thirdparty_from:
        for imp in thirdparty_imports:
            new_code.append(imp)
        for imp in thirdparty_from:
            new_code.append(imp)
        new_code.append("")
    
    # Imports locais
    if local_imports or local_from:
        for imp in local_imports:
            new_code.append(imp)
        for imp in local_from:
            new_code.append(imp)
        new_code.append("")
    
    # Garantir linha em branco antes do código
    if new_code and new_code[-1] != "":
        new_code.append("")
    
    # Resto do código
    new_code.extend(other_code)
    
    return {
        "success": True,
        "refactored_code": "\n".join(new_code),
        "stdlib_count": len(stdlib_imports) + len(stdlib_from),
        "thirdparty_count": len(thirdparty_imports) + len(thirdparty_from),
        "local_count": len(local_imports) + len(local_from)
    }


def generate_docstring(
    source_code: str,
    function_name: str,
    style: str = "google"
) -> Dict[str, Any]:
    """
    Gera docstring para uma função.
    
    Args:
        source_code: Código fonte
        function_name: Nome da função
        style: Estilo (google, numpy, sphinx)
        
    Returns:
        Docstring gerada
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {"success": False, "error": f"Erro de sintaxe: {e}"}
    
    # Encontrar a função
    func_def = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            func_def = node
            break
    
    if not func_def:
        return {
            "success": False,
            "error": f"Função '{function_name}' não encontrada"
        }
    
    # Extrair informações
    args = []
    for arg in func_def.args.args:
        arg_info = {"name": arg.arg}
        
        # Tentar extrair tipo da anotação
        if arg.annotation:
            arg_info["type"] = ast.unparse(arg.annotation)
        else:
            arg_info["type"] = "Any"
        
        args.append(arg_info)
    
    # Extrair retorno
    returns = None
    if func_def.returns:
        returns = ast.unparse(func_def.returns)
    else:
        # Tentar detectar return statements
        for node in ast.walk(func_def):
            if isinstance(node, ast.Return) and node.value:
                returns = "Unknown"
                break
    
    # Detectar raises
    raises = set()
    for node in ast.walk(func_def):
        if isinstance(node, ast.Raise):
            if node.exc:
                if isinstance(node.exc, ast.Name):
                    raises.add(node.exc.id)
                elif isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                    raises.add(node.exc.func.id)
    
    # Gerar docstring baseado no estilo
    if style == "google":
        docstring = _generate_google_docstring(function_name, args, returns, raises)
    elif style == "numpy":
        docstring = _generate_numpy_docstring(function_name, args, returns, raises)
    else:  # sphinx
        docstring = _generate_sphinx_docstring(function_name, args, returns, raises)
    
    return {
        "success": True,
        "function_name": function_name,
        "style": style,
        "docstring": docstring,
        "args_found": len(args),
        "has_return": returns is not None
    }


def add_type_hints(source_code: str) -> Dict[str, Any]:
    """
    Adiciona type hints básicos ao código.
    
    Args:
        source_code: Código fonte
        
    Returns:
        Código com type hints
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {"success": False, "error": str(e)}
    
    changes = []
    
    class TypeHintAdder(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            # Adicionar tipo de retorno se não existir
            if node.returns is None:
                # Tentar inferir do return
                for child in ast.walk(node):
                    if isinstance(child, ast.Return) and child.value:
                        if isinstance(child.value, ast.Constant):
                            if isinstance(child.value.value, str):
                                node.returns = ast.Name(id='str', ctx=ast.Load())
                            elif isinstance(child.value.value, int):
                                node.returns = ast.Name(id='int', ctx=ast.Load())
                            elif isinstance(child.value.value, float):
                                node.returns = ast.Name(id='float', ctx=ast.Load())
                            elif isinstance(child.value.value, bool):
                                node.returns = ast.Name(id='bool', ctx=ast.Load())
                        elif isinstance(child.value, ast.List):
                            node.returns = ast.Subscript(
                                value=ast.Name(id='List', ctx=ast.Load()),
                                slice=ast.Name(id='Any', ctx=ast.Load()),
                                ctx=ast.Load()
                            )
                        elif isinstance(child.value, ast.Dict):
                            node.returns = ast.Subscript(
                                value=ast.Name(id='Dict', ctx=ast.Load()),
                                slice=ast.Tuple(elts=[
                                    ast.Name(id='str', ctx=ast.Load()),
                                    ast.Name(id='Any', ctx=ast.Load())
                                ], ctx=ast.Load()),
                                ctx=ast.Load()
                            )
                        break
                
                if node.returns is None:
                    node.returns = ast.Name(id='None', ctx=ast.Load())
                
                changes.append(f"Added return type to {node.name}")
            
            return self.generic_visit(node)
    
    transformer = TypeHintAdder()
    new_tree = transformer.visit(tree)
    
    # Adicionar import typing se necessário
    new_code = ast.unparse(new_tree)
    
    if 'List[' in new_code or 'Dict[' in new_code:
        if 'from typing import' not in new_code and 'import typing' not in new_code:
            new_code = "from typing import Any, List, Dict\n\n" + new_code
            changes.append("Added typing imports")
    
    return {
        "success": True,
        "refactored_code": new_code,
        "changes": changes
    }


def extract_constant(
    source_code: str,
    value: str,
    constant_name: str
) -> Dict[str, Any]:
    """
    Extrai um valor literal para uma constante.
    
    Args:
        source_code: Código fonte
        value: Valor a extrair (ex: '"api/v1"', '42')
        constant_name: Nome da constante (ex: 'API_BASE_URL')
        
    Returns:
        Código refatorado
    """
    # Verificar se valor existe
    if value not in source_code:
        return {
            "success": False,
            "error": f"Valor '{value}' não encontrado no código"
        }
    
    # Contar ocorrências
    occurrences = source_code.count(value)
    
    # Substituir
    refactored = source_code.replace(value, constant_name)
    
    # Adicionar definição da constante no início (após imports)
    lines = refactored.splitlines()
    insert_pos = 0
    
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith(('import ', 'from ', '#', '"""', "'''")):
            if line.strip() and not line.startswith(' '):  # Primeira linha de código
                insert_pos = i
                break
    
    constant_def = f"{constant_name} = {value}"
    lines.insert(insert_pos, "")
    lines.insert(insert_pos, constant_def)
    
    return {
        "success": True,
        "refactored_code": "\n".join(lines),
        "constant_name": constant_name,
        "constant_value": value,
        "occurrences_replaced": occurrences
    }


def _detect_variables(code: str) -> List[str]:
    """Detecta variáveis usadas mas não definidas no código"""
    try:
        tree = ast.parse(code)
    except:
        return []
    
    assigned = set()
    used = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                assigned.add(node.id)
            elif isinstance(node.ctx, ast.Load):
                used.add(node.id)
    
    # Variáveis usadas mas não definidas localmente
    external = used - assigned
    
    # Filtrar builtins
    builtins_names = {'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict',
                      'set', 'tuple', 'bool', 'None', 'True', 'False', 'open', 'input',
                      'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'sum',
                      'min', 'max', 'abs', 'round', 'type', 'isinstance', 'hasattr',
                      'getattr', 'setattr', 'super', 'object', 'Exception'}
    
    return list(external - builtins_names)


def _generate_google_docstring(name: str, args: List[Dict], returns: Optional[str], raises: Set[str]) -> str:
    """Gera docstring estilo Google"""
    lines = ['"""Short description.', '', 'Long description if needed.', '']
    
    if args:
        lines.append('Args:')
        for arg in args:
            if arg['name'] != 'self':
                lines.append(f"    {arg['name']} ({arg['type']}): Description.")
        lines.append('')
    
    if returns:
        lines.append('Returns:')
        lines.append(f'    {returns}: Description.')
        lines.append('')
    
    if raises:
        lines.append('Raises:')
        for exc in raises:
            lines.append(f'    {exc}: When it happens.')
        lines.append('')
    
    lines.append('"""')
    return '\n'.join(lines)


def _generate_numpy_docstring(name: str, args: List[Dict], returns: Optional[str], raises: Set[str]) -> str:
    """Gera docstring estilo NumPy"""
    lines = ['"""Short description.', '', 'Long description if needed.', '']
    
    if args:
        lines.append('Parameters')
        lines.append('----------')
        for arg in args:
            if arg['name'] != 'self':
                lines.append(f"{arg['name']} : {arg['type']}")
                lines.append('    Description.')
        lines.append('')
    
    if returns:
        lines.append('Returns')
        lines.append('-------')
        lines.append(returns)
        lines.append('    Description.')
        lines.append('')
    
    if raises:
        lines.append('Raises')
        lines.append('------')
        for exc in raises:
            lines.append(exc)
            lines.append('    When it happens.')
        lines.append('')
    
    lines.append('"""')
    return '\n'.join(lines)


def _generate_sphinx_docstring(name: str, args: List[Dict], returns: Optional[str], raises: Set[str]) -> str:
    """Gera docstring estilo Sphinx"""
    lines = ['"""Short description.', '', 'Long description if needed.', '']
    
    for arg in args:
        if arg['name'] != 'self':
            lines.append(f":param {arg['name']}: Description.")
            lines.append(f":type {arg['name']}: {arg['type']}")
    
    if returns:
        lines.append(f':returns: Description.')
        lines.append(f':rtype: {returns}')
    
    for exc in raises:
        lines.append(f':raises {exc}: When it happens.')
    
    lines.append('"""')
    return '\n'.join(lines)
