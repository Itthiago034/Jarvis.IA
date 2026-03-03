"""
JARVIS - Code Analysis Tools
============================
Ferramentas para análise estática de código.
Equivalente às funcionalidades get_errors, list_code_usages, test_failure.
"""

import ast
import re
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CodeError:
    """Representa um erro de código"""
    file_path: str
    line: int
    column: int
    message: str
    severity: str  # error, warning, info
    source: str  # pylint, mypy, syntax, etc.


@dataclass
class CodeUsage:
    """Representa um uso de símbolo"""
    file_path: str
    line: int
    column: int
    context: str  # linha de código
    usage_type: str  # definition, reference, import


def get_syntax_errors(file_path: str) -> List[Dict[str, Any]]:
    """
    Verifica erros de sintaxe em um arquivo Python.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Lista de erros com file_path, line, column, message
    """
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        try:
            ast.parse(source)
        except SyntaxError as e:
            errors.append({
                "file_path": file_path,
                "line": e.lineno or 1,
                "column": e.offset or 0,
                "message": str(e.msg),
                "severity": "error",
                "source": "syntax"
            })
            
    except FileNotFoundError:
        errors.append({
            "file_path": file_path,
            "line": 0,
            "column": 0,
            "message": f"Arquivo não encontrado: {file_path}",
            "severity": "error",
            "source": "filesystem"
        })
    except Exception as e:
        errors.append({
            "file_path": file_path,
            "line": 0,
            "column": 0,
            "message": str(e),
            "severity": "error",
            "source": "unknown"
        })
    
    return errors


def get_python_errors(
    file_path: str,
    use_pylint: bool = True,
    use_mypy: bool = False
) -> List[Dict[str, Any]]:
    """
    Obtém erros de linting de um arquivo Python.
    
    Args:
        file_path: Caminho do arquivo
        use_pylint: Usar pylint para análise
        use_mypy: Usar mypy para type checking
        
    Returns:
        Lista de erros encontrados
    """
    errors = []
    
    # Sempre verificar sintaxe
    syntax_errors = get_syntax_errors(file_path)
    errors.extend(syntax_errors)
    
    # Se tem erro de sintaxe, não precisa continuar
    if syntax_errors:
        return errors
    
    # Pylint analysis
    if use_pylint:
        try:
            import subprocess
            result = subprocess.run(
                ['python', '-m', 'pylint', '--output-format=json', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                pylint_results = json.loads(result.stdout)
                for item in pylint_results:
                    errors.append({
                        "file_path": item.get('path', file_path),
                        "line": item.get('line', 0),
                        "column": item.get('column', 0),
                        "message": item.get('message', ''),
                        "severity": _map_pylint_type(item.get('type', '')),
                        "source": "pylint",
                        "symbol": item.get('symbol', '')
                    })
        except FileNotFoundError:
            logger.debug("pylint não instalado")
        except subprocess.TimeoutExpired:
            logger.warning("pylint timeout")
        except Exception as e:
            logger.debug(f"Erro ao executar pylint: {e}")
    
    # Mypy analysis
    if use_mypy:
        try:
            import subprocess
            result = subprocess.run(
                ['python', '-m', 'mypy', '--no-error-summary', file_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            for line in result.stdout.splitlines():
                match = re.match(r'(.+):(\d+): (\w+): (.+)', line)
                if match:
                    errors.append({
                        "file_path": match.group(1),
                        "line": int(match.group(2)),
                        "column": 0,
                        "message": match.group(4),
                        "severity": match.group(3).lower(),
                        "source": "mypy"
                    })
        except FileNotFoundError:
            logger.debug("mypy não instalado")
        except subprocess.TimeoutExpired:
            logger.warning("mypy timeout")
        except Exception as e:
            logger.debug(f"Erro ao executar mypy: {e}")
    
    return errors


def get_all_errors(
    root_path: str,
    file_patterns: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Obtém erros de todos os arquivos em um diretório.
    
    Args:
        root_path: Diretório raiz
        file_patterns: Padrões de arquivo (ex: ["*.py", "*.js"])
        
    Returns:
        Lista consolidada de erros
    """
    if file_patterns is None:
        file_patterns = ["**/*.py"]
    
    all_errors = []
    root = Path(root_path)
    
    for pattern in file_patterns:
        for file_path in root.glob(pattern):
            if file_path.is_file():
                # Ignorar __pycache__ e similares
                if '__pycache__' in str(file_path):
                    continue
                if file_path.suffix == '.py':
                    errors = get_python_errors(str(file_path))
                    all_errors.extend(errors)
    
    return all_errors


def find_symbol_usages(
    symbol_name: str,
    root_path: str,
    file_pattern: str = "**/*.py"
) -> List[Dict[str, Any]]:
    """
    Encontra todos os usos de um símbolo (função, classe, variável).
    
    Args:
        symbol_name: Nome do símbolo a buscar
        root_path: Diretório raiz
        file_pattern: Padrão de arquivos
        
    Returns:
        Lista de usos com file_path, line, context, usage_type
    """
    usages = []
    root = Path(root_path)
    
    # Padrões regex para diferentes tipos de uso
    patterns = {
        'definition_function': rf'^(\s*)def\s+{re.escape(symbol_name)}\s*\(',
        'definition_class': rf'^(\s*)class\s+{re.escape(symbol_name)}\s*[:\(]',
        'definition_variable': rf'^(\s*){re.escape(symbol_name)}\s*=',
        'import': rf'from\s+\S+\s+import\s+.*\b{re.escape(symbol_name)}\b|import\s+.*\b{re.escape(symbol_name)}\b',
        'reference': rf'\b{re.escape(symbol_name)}\b',
    }
    
    for file_path in root.glob(file_pattern):
        if not file_path.is_file() or '__pycache__' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Verificar cada tipo de padrão
                for usage_type, pattern in patterns.items():
                    if re.search(pattern, line):
                        # Evitar duplicatas (reference vai pegar tudo)
                        if usage_type == 'reference':
                            # Só adicionar se não for outro tipo
                            is_other = any(
                                re.search(p, line) 
                                for t, p in patterns.items() 
                                if t != 'reference'
                            )
                            if is_other:
                                continue
                        
                        usages.append({
                            "file_path": str(file_path),
                            "line": line_num,
                            "column": line.find(symbol_name),
                            "context": line.strip()[:200],
                            "usage_type": usage_type.replace('_', ' ')
                        })
                        break  # Só adicionar uma vez por linha
                        
        except Exception as e:
            logger.debug(f"Erro ao ler {file_path}: {e}")
    
    return usages


def analyze_test_failure(
    error_output: str,
    test_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analisa uma falha de teste e extrai informações úteis.
    
    Args:
        error_output: Output do teste que falhou
        test_file: Arquivo de teste (opcional)
        
    Returns:
        Dicionário com análise da falha
    """
    analysis = {
        "test_framework": "unknown",
        "failed_tests": [],
        "error_type": "unknown",
        "error_message": "",
        "traceback": [],
        "suggestions": []
    }
    
    # Detectar framework
    if 'pytest' in error_output.lower() or 'FAILED' in error_output:
        analysis["test_framework"] = "pytest"
    elif 'unittest' in error_output.lower() or 'FAIL:' in error_output:
        analysis["test_framework"] = "unittest"
    elif 'jest' in error_output.lower() or 'FAIL' in error_output:
        analysis["test_framework"] = "jest"
    
    # Extrair testes que falharam
    failed_pattern = r'(?:FAILED|FAIL:?|✕)\s*([^\s]+(?:\.py)?::[^\s]+|[^\s]+)'
    failed_matches = re.findall(failed_pattern, error_output)
    analysis["failed_tests"] = failed_matches[:10]
    
    # Extrair tipo de erro
    error_types = [
        'AssertionError', 'TypeError', 'ValueError', 'KeyError',
        'AttributeError', 'NameError', 'ImportError', 'FileNotFoundError',
        'ZeroDivisionError', 'IndexError', 'RuntimeError', 'Exception'
    ]
    for error_type in error_types:
        if error_type in error_output:
            analysis["error_type"] = error_type
            break
    
    # Extrair mensagem de erro
    error_msg_patterns = [
        rf'{analysis["error_type"]}:\s*(.+?)(?:\n|$)',
        r'AssertionError:\s*(.+?)(?:\n|$)',
        r'Error:\s*(.+?)(?:\n|$)',
    ]
    for pattern in error_msg_patterns:
        match = re.search(pattern, error_output)
        if match:
            analysis["error_message"] = match.group(1).strip()[:500]
            break
    
    # Extrair traceback
    traceback_lines = []
    for line in error_output.splitlines():
        if 'File "' in line or 'at ' in line:
            traceback_lines.append(line.strip())
    analysis["traceback"] = traceback_lines[:10]
    
    # Sugestões baseadas no tipo de erro
    suggestions = {
        'AssertionError': [
            "Verifique se o valor esperado está correto",
            "Confirme que a lógica do teste corresponde ao comportamento esperado",
            "Pode ser necessário atualizar o valor esperado se o comportamento mudou"
        ],
        'TypeError': [
            "Verifique os tipos dos argumentos passados",
            "Confirme que a função está recebendo os parâmetros corretos",
            "Pode haver um None onde não deveria"
        ],
        'AttributeError': [
            "O objeto pode não ter o atributo esperado",
            "Verifique se o mock está configurado corretamente",
            "O objeto pode ser None"
        ],
        'ImportError': [
            "Verifique se o módulo está instalado",
            "Confirme o caminho do import",
            "Pode haver dependência circular"
        ],
        'KeyError': [
            "A chave não existe no dicionário",
            "Verifique se os dados de teste estão corretos",
            "Use .get() para valores opcionais"
        ]
    }
    analysis["suggestions"] = suggestions.get(
        analysis["error_type"], 
        ["Analise a mensagem de erro e o traceback para mais detalhes"]
    )
    
    return analysis


def count_code_metrics(file_path: str) -> Dict[str, Any]:
    """
    Conta métricas básicas de código.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Dicionário com métricas (lines, functions, classes, etc.)
    """
    metrics = {
        "file_path": file_path,
        "total_lines": 0,
        "code_lines": 0,
        "comment_lines": 0,
        "blank_lines": 0,
        "functions": 0,
        "classes": 0,
        "imports": 0,
        "docstrings": 0
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        metrics["total_lines"] = len(lines)
        
        in_docstring = False
        docstring_char = None
        
        for line in lines:
            stripped = line.strip()
            
            # Linha em branco
            if not stripped:
                metrics["blank_lines"] += 1
                continue
            
            # Docstring multiline
            if in_docstring:
                metrics["comment_lines"] += 1
                if docstring_char in stripped:
                    in_docstring = False
                continue
            
            # Início de docstring
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                metrics["docstrings"] += 1
                metrics["comment_lines"] += 1
                if stripped.count(docstring_char) == 1:
                    in_docstring = True
                continue
            
            # Comentário
            if stripped.startswith('#'):
                metrics["comment_lines"] += 1
                continue
            
            # Código
            metrics["code_lines"] += 1
            
            # Definições
            if stripped.startswith('def '):
                metrics["functions"] += 1
            elif stripped.startswith('class '):
                metrics["classes"] += 1
            elif stripped.startswith('import ') or stripped.startswith('from '):
                metrics["imports"] += 1
                
    except Exception as e:
        metrics["error"] = str(e)
    
    return metrics


def _map_pylint_type(pylint_type: str) -> str:
    """Mapeia tipo do pylint para severity padrão"""
    mapping = {
        'convention': 'info',
        'refactor': 'info',
        'warning': 'warning',
        'error': 'error',
        'fatal': 'error'
    }
    return mapping.get(pylint_type.lower(), 'warning')
