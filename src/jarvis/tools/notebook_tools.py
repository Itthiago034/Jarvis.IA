"""
JARVIS - Notebook Tools
=======================
Ferramentas para trabalhar com Jupyter Notebooks.
Equivalente às funcionalidades run_notebook_cell, edit_notebook_file, copilot_getNotebookSummary.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NotebookCell:
    """Representa uma célula de notebook"""
    cell_id: str
    cell_type: str  # code, markdown
    source: str
    outputs: List[Any]
    execution_count: Optional[int] = None


def read_notebook(file_path: str) -> Dict[str, Any]:
    """
    Lê um arquivo Jupyter Notebook.
    
    Args:
        file_path: Caminho do arquivo .ipynb
        
    Returns:
        Dicionário com metadados e células do notebook
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        return {
            "success": True,
            "file_path": file_path,
            "kernel": notebook.get('metadata', {}).get('kernelspec', {}).get('display_name', 'Unknown'),
            "language": notebook.get('metadata', {}).get('language_info', {}).get('name', 'python'),
            "cell_count": len(notebook.get('cells', [])),
            "cells": notebook.get('cells', []),
            "metadata": notebook.get('metadata', {})
        }
    except FileNotFoundError:
        return {"success": False, "error": f"Arquivo não encontrado: {file_path}"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Erro ao ler notebook: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_notebook_summary(file_path: str) -> Dict[str, Any]:
    """
    Obtém um resumo do notebook.
    
    Args:
        file_path: Caminho do arquivo .ipynb
        
    Returns:
        Resumo com informações das células
    """
    notebook = read_notebook(file_path)
    
    if not notebook.get('success'):
        return notebook
    
    cells_summary = []
    code_cells = 0
    markdown_cells = 0
    total_code_lines = 0
    
    for i, cell in enumerate(notebook.get('cells', [])):
        cell_type = cell.get('cell_type', 'unknown')
        source = ''.join(cell.get('source', []))
        
        if cell_type == 'code':
            code_cells += 1
            total_code_lines += source.count('\n') + 1
        else:
            markdown_cells += 1
        
        # Extrair outputs
        outputs = cell.get('outputs', [])
        output_types = []
        for output in outputs:
            if 'text' in output:
                output_types.append('text')
            elif 'image/png' in output.get('data', {}):
                output_types.append('image')
            elif 'text/html' in output.get('data', {}):
                output_types.append('html')
            elif output.get('output_type') == 'error':
                output_types.append('error')
        
        cells_summary.append({
            "cell_number": i + 1,
            "cell_id": cell.get('id', f'cell_{i}'),
            "cell_type": cell_type,
            "source_preview": source[:100] + '...' if len(source) > 100 else source,
            "line_count": source.count('\n') + 1,
            "execution_count": cell.get('execution_count'),
            "has_output": len(outputs) > 0,
            "output_types": list(set(output_types))
        })
    
    return {
        "success": True,
        "file_path": file_path,
        "kernel": notebook.get('kernel'),
        "language": notebook.get('language'),
        "total_cells": len(cells_summary),
        "code_cells": code_cells,
        "markdown_cells": markdown_cells,
        "total_code_lines": total_code_lines,
        "cells": cells_summary
    }


def get_cell_content(
    file_path: str,
    cell_number: int
) -> Dict[str, Any]:
    """
    Obtém conteúdo de uma célula específica.
    
    Args:
        file_path: Caminho do notebook
        cell_number: Número da célula (1-based)
        
    Returns:
        Conteúdo da célula
    """
    notebook = read_notebook(file_path)
    
    if not notebook.get('success'):
        return notebook
    
    cells = notebook.get('cells', [])
    index = cell_number - 1
    
    if index < 0 or index >= len(cells):
        return {
            "success": False,
            "error": f"Célula {cell_number} não existe. Notebook tem {len(cells)} células."
        }
    
    cell = cells[index]
    source = ''.join(cell.get('source', []))
    
    # Processar outputs
    outputs_text = []
    for output in cell.get('outputs', []):
        if 'text' in output:
            outputs_text.append(''.join(output['text']))
        elif 'data' in output:
            if 'text/plain' in output['data']:
                outputs_text.append(''.join(output['data']['text/plain']))
        elif output.get('output_type') == 'error':
            outputs_text.append(f"Error: {output.get('ename', '')}: {output.get('evalue', '')}")
    
    return {
        "success": True,
        "cell_number": cell_number,
        "cell_type": cell.get('cell_type'),
        "source": source,
        "execution_count": cell.get('execution_count'),
        "outputs": outputs_text
    }


def edit_cell(
    file_path: str,
    cell_number: int,
    new_source: str,
    save: bool = True
) -> Dict[str, Any]:
    """
    Edita o conteúdo de uma célula.
    
    Args:
        file_path: Caminho do notebook
        cell_number: Número da célula (1-based)
        new_source: Novo conteúdo da célula
        save: Se True, salva o notebook
        
    Returns:
        Resultado da operação
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        cells = notebook.get('cells', [])
        index = cell_number - 1
        
        if index < 0 or index >= len(cells):
            return {
                "success": False,
                "error": f"Célula {cell_number} não existe"
            }
        
        # Atualizar source (como lista de linhas)
        lines = new_source.split('\n')
        notebook['cells'][index]['source'] = [
            line + '\n' if i < len(lines) - 1 else line
            for i, line in enumerate(lines)
        ]
        
        # Limpar outputs ao editar código
        if notebook['cells'][index].get('cell_type') == 'code':
            notebook['cells'][index]['outputs'] = []
            notebook['cells'][index]['execution_count'] = None
        
        if save:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1)
        
        return {
            "success": True,
            "message": f"Célula {cell_number} atualizada",
            "cell_number": cell_number,
            "new_source": new_source
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def add_cell(
    file_path: str,
    source: str,
    cell_type: str = "code",
    position: Optional[int] = None
) -> Dict[str, Any]:
    """
    Adiciona uma nova célula ao notebook.
    
    Args:
        file_path: Caminho do notebook
        source: Conteúdo da célula
        cell_type: Tipo (code ou markdown)
        position: Posição para inserir (None = final)
        
    Returns:
        Resultado da operação
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        # Criar nova célula
        lines = source.split('\n')
        new_cell = {
            "cell_type": cell_type,
            "source": [
                line + '\n' if i < len(lines) - 1 else line
                for i, line in enumerate(lines)
            ],
            "metadata": {},
        }
        
        if cell_type == "code":
            new_cell["outputs"] = []
            new_cell["execution_count"] = None
        
        # Inserir na posição
        if position is None:
            notebook['cells'].append(new_cell)
            position = len(notebook['cells'])
        else:
            notebook['cells'].insert(position - 1, new_cell)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1)
        
        return {
            "success": True,
            "message": f"Célula adicionada na posição {position}",
            "cell_number": position,
            "cell_type": cell_type
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_cell(
    file_path: str,
    cell_number: int
) -> Dict[str, Any]:
    """
    Remove uma célula do notebook.
    
    Args:
        file_path: Caminho do notebook
        cell_number: Número da célula (1-based)
        
    Returns:
        Resultado da operação
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        index = cell_number - 1
        if index < 0 or index >= len(notebook['cells']):
            return {
                "success": False,
                "error": f"Célula {cell_number} não existe"
            }
        
        deleted = notebook['cells'].pop(index)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1)
        
        return {
            "success": True,
            "message": f"Célula {cell_number} removida",
            "deleted_type": deleted.get('cell_type')
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_notebook(
    file_path: str,
    output_path: Optional[str] = None,
    timeout: int = 600
) -> Dict[str, Any]:
    """
    Executa todas as células de um notebook.
    Requer: pip install nbconvert jupyter
    
    Args:
        file_path: Caminho do notebook
        output_path: Caminho para salvar resultado (opcional)
        timeout: Timeout em segundos
        
    Returns:
        Resultado da execução
    """
    if output_path is None:
        output_path = file_path
    
    try:
        result = subprocess.run(
            [
                'jupyter', 'nbconvert',
                '--to', 'notebook',
                '--execute',
                f'--ExecutePreprocessor.timeout={timeout}',
                '--output', Path(output_path).name,
                file_path
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 60,
            cwd=Path(output_path).parent if output_path else None
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": "Notebook executado com sucesso",
                "output_file": output_path
            }
        else:
            return {
                "success": False,
                "error": result.stderr or result.stdout
            }
            
    except FileNotFoundError:
        return {
            "success": False,
            "error": "jupyter não está instalado. Execute: pip install jupyter nbconvert"
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Execução excedeu o timeout de {timeout} segundos"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_notebook(
    file_path: str,
    kernel: str = "python3",
    initial_cells: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Cria um novo notebook Jupyter.
    
    Args:
        file_path: Caminho do arquivo
        kernel: Kernel a usar (python3, ir, julia, etc.)
        initial_cells: Lista de células iniciais [{"type": "code/markdown", "source": "..."}]
        
    Returns:
        Resultado da criação
    """
    notebook = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": kernel.title(),
                "language": "python" if "python" in kernel else kernel,
                "name": kernel
            },
            "language_info": {
                "name": "python" if "python" in kernel else kernel,
                "version": "3.10"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    
    # Adicionar células iniciais
    if initial_cells:
        for cell_info in initial_cells:
            cell_type = cell_info.get('type', 'code')
            source = cell_info.get('source', '')
            lines = source.split('\n')
            
            cell = {
                "cell_type": cell_type,
                "source": [
                    line + '\n' if i < len(lines) - 1 else line
                    for i, line in enumerate(lines)
                ],
                "metadata": {}
            }
            
            if cell_type == "code":
                cell["outputs"] = []
                cell["execution_count"] = None
            
            notebook['cells'].append(cell)
    
    try:
        # Criar diretório se necessário
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1)
        
        return {
            "success": True,
            "message": f"Notebook criado: {file_path}",
            "file_path": file_path,
            "cell_count": len(notebook['cells'])
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def notebook_to_script(
    notebook_path: str,
    script_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Converte um notebook para script Python.
    
    Args:
        notebook_path: Caminho do notebook
        script_path: Caminho do script de saída
        
    Returns:
        Resultado com conteúdo do script
    """
    notebook = read_notebook(notebook_path)
    
    if not notebook.get('success'):
        return notebook
    
    script_lines = []
    script_lines.append(f"# Converted from: {Path(notebook_path).name}")
    script_lines.append(f"# Generated by JARVIS CodeAgent")
    script_lines.append("")
    
    for i, cell in enumerate(notebook.get('cells', [])):
        cell_type = cell.get('cell_type')
        source = ''.join(cell.get('source', []))
        
        if cell_type == 'markdown':
            # Converter markdown para comentários
            script_lines.append(f"# --- Cell {i+1} (Markdown) ---")
            for line in source.splitlines():
                script_lines.append(f"# {line}")
            script_lines.append("")
        elif cell_type == 'code':
            script_lines.append(f"# --- Cell {i+1} ---")
            script_lines.append(source)
            script_lines.append("")
    
    script_content = '\n'.join(script_lines)
    
    if script_path:
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            return {
                "success": True,
                "message": f"Script salvo em: {script_path}",
                "script_path": script_path,
                "content": script_content
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return {
        "success": True,
        "content": script_content
    }
