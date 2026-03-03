"""
JARVIS - Git Tools
==================
Ferramentas para controle de versão Git.
Equivalente às funcionalidades get_changed_files e análise de diff.
"""

import subprocess
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FileStatus(Enum):
    """Status de um arquivo no Git"""
    MODIFIED = "modified"
    ADDED = "added"
    DELETED = "deleted"
    RENAMED = "renamed"
    COPIED = "copied"
    UNTRACKED = "untracked"
    STAGED = "staged"
    CONFLICT = "conflict"


@dataclass
class ChangedFile:
    """Representa um arquivo modificado"""
    path: str
    status: FileStatus
    staged: bool
    additions: int = 0
    deletions: int = 0
    old_path: Optional[str] = None  # Para arquivos renomeados


def run_git_command(
    command: List[str],
    cwd: Optional[str] = None
) -> Tuple[bool, str, str]:
    """
    Executa um comando git.
    
    Returns:
        Tupla (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ['git'] + command,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd
        )
        return (
            result.returncode == 0,
            result.stdout,
            result.stderr
        )
    except subprocess.TimeoutExpired:
        return False, "", "Git command timeout"
    except FileNotFoundError:
        return False, "", "Git não está instalado"
    except Exception as e:
        return False, "", str(e)


def is_git_repository(path: str = ".") -> bool:
    """Verifica se o diretório é um repositório Git"""
    success, _, _ = run_git_command(['rev-parse', '--git-dir'], cwd=path)
    return success


def get_changed_files(
    path: str = ".",
    include_untracked: bool = True,
    include_staged: bool = True,
    include_unstaged: bool = True
) -> List[Dict[str, Any]]:
    """
    Lista arquivos modificados no repositório.
    
    Args:
        path: Caminho do repositório
        include_untracked: Incluir arquivos não rastreados
        include_staged: Incluir arquivos staged
        include_unstaged: Incluir arquivos não staged
        
    Returns:
        Lista de arquivos com path, status, staged
    """
    if not is_git_repository(path):
        return [{"error": "Não é um repositório Git"}]
    
    files = []
    
    # Arquivos staged
    if include_staged:
        success, stdout, _ = run_git_command(
            ['diff', '--cached', '--name-status'],
            cwd=path
        )
        if success:
            for line in stdout.strip().splitlines():
                if line:
                    parts = line.split('\t')
                    status_char = parts[0][0]
                    file_path = parts[-1]
                    
                    files.append({
                        "path": file_path,
                        "status": _map_status(status_char),
                        "staged": True,
                        "old_path": parts[1] if len(parts) > 2 else None
                    })
    
    # Arquivos modificados (não staged)
    if include_unstaged:
        success, stdout, _ = run_git_command(
            ['diff', '--name-status'],
            cwd=path
        )
        if success:
            for line in stdout.strip().splitlines():
                if line:
                    parts = line.split('\t')
                    status_char = parts[0][0]
                    file_path = parts[-1]
                    
                    files.append({
                        "path": file_path,
                        "status": _map_status(status_char),
                        "staged": False,
                        "old_path": parts[1] if len(parts) > 2 else None
                    })
    
    # Arquivos não rastreados
    if include_untracked:
        success, stdout, _ = run_git_command(
            ['ls-files', '--others', '--exclude-standard'],
            cwd=path
        )
        if success:
            for line in stdout.strip().splitlines():
                if line:
                    files.append({
                        "path": line,
                        "status": "untracked",
                        "staged": False
                    })
    
    return files


def get_file_diff(
    file_path: str,
    staged: bool = False,
    context_lines: int = 3,
    repo_path: str = "."
) -> Dict[str, Any]:
    """
    Obtém o diff de um arquivo específico.
    
    Args:
        file_path: Caminho do arquivo
        staged: Se True, mostra diff staged
        context_lines: Linhas de contexto
        repo_path: Caminho do repositório
        
    Returns:
        Dicionário com diff, additions, deletions
    """
    args = ['diff']
    if staged:
        args.append('--cached')
    args.extend([f'-U{context_lines}', '--', file_path])
    
    success, stdout, stderr = run_git_command(args, cwd=repo_path)
    
    if not success:
        return {"error": stderr or "Não foi possível obter diff"}
    
    # Contar adições e remoções
    additions = 0
    deletions = 0
    for line in stdout.splitlines():
        if line.startswith('+') and not line.startswith('+++'):
            additions += 1
        elif line.startswith('-') and not line.startswith('---'):
            deletions += 1
    
    return {
        "file_path": file_path,
        "diff": stdout,
        "additions": additions,
        "deletions": deletions,
        "staged": staged
    }


def get_commit_history(
    path: str = ".",
    max_commits: int = 10,
    file_path: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Obtém histórico de commits.
    
    Args:
        path: Caminho do repositório
        max_commits: Número máximo de commits
        file_path: Filtrar por arquivo específico
        
    Returns:
        Lista de commits com hash, author, date, message
    """
    args = [
        'log',
        f'-{max_commits}',
        '--pretty=format:%H|%an|%ad|%s',
        '--date=short'
    ]
    
    if file_path:
        args.extend(['--', file_path])
    
    success, stdout, _ = run_git_command(args, cwd=path)
    
    if not success:
        return []
    
    commits = []
    for line in stdout.strip().splitlines():
        parts = line.split('|', 3)
        if len(parts) >= 4:
            commits.append({
                "hash": parts[0][:8],
                "full_hash": parts[0],
                "author": parts[1],
                "date": parts[2],
                "message": parts[3]
            })
    
    return commits


def get_current_branch(path: str = ".") -> str:
    """Obtém nome da branch atual"""
    success, stdout, _ = run_git_command(
        ['rev-parse', '--abbrev-ref', 'HEAD'],
        cwd=path
    )
    return stdout.strip() if success else "unknown"


def get_branches(path: str = ".") -> List[Dict[str, Any]]:
    """
    Lista todas as branches.
    
    Returns:
        Lista de branches com name, current, remote
    """
    success, stdout, _ = run_git_command(
        ['branch', '-a', '-v'],
        cwd=path
    )
    
    if not success:
        return []
    
    branches = []
    for line in stdout.strip().splitlines():
        is_current = line.startswith('*')
        parts = line.strip('* ').split()
        if parts:
            name = parts[0]
            is_remote = name.startswith('remotes/')
            branches.append({
                "name": name.replace('remotes/', ''),
                "current": is_current,
                "remote": is_remote,
                "commit": parts[1] if len(parts) > 1 else ""
            })
    
    return branches


def get_repository_status(path: str = ".") -> Dict[str, Any]:
    """
    Obtém status completo do repositório.
    
    Returns:
        Dicionário com informações completas do repositório
    """
    if not is_git_repository(path):
        return {"error": "Não é um repositório Git"}
    
    changed_files = get_changed_files(path)
    
    # Contar por tipo
    staged_count = sum(1 for f in changed_files if f.get('staged', False))
    unstaged_count = sum(1 for f in changed_files if not f.get('staged', False) and f.get('status') != 'untracked')
    untracked_count = sum(1 for f in changed_files if f.get('status') == 'untracked')
    
    # Verificar se há commits para push
    success, stdout, _ = run_git_command(
        ['rev-list', '@{u}..HEAD', '--count'],
        cwd=path
    )
    commits_ahead = int(stdout.strip()) if success and stdout.strip() else 0
    
    # Commits para pull
    success, stdout, _ = run_git_command(
        ['rev-list', 'HEAD..@{u}', '--count'],
        cwd=path
    )
    commits_behind = int(stdout.strip()) if success and stdout.strip() else 0
    
    return {
        "is_git_repo": True,
        "current_branch": get_current_branch(path),
        "changed_files": changed_files,
        "staged_count": staged_count,
        "unstaged_count": unstaged_count,
        "untracked_count": untracked_count,
        "commits_ahead": commits_ahead,
        "commits_behind": commits_behind,
        "has_changes": len(changed_files) > 0,
        "clean": len(changed_files) == 0
    }


def stage_files(
    files: List[str],
    path: str = "."
) -> Dict[str, Any]:
    """
    Adiciona arquivos ao staging.
    
    Args:
        files: Lista de caminhos de arquivos
        path: Caminho do repositório
        
    Returns:
        Resultado da operação
    """
    success, stdout, stderr = run_git_command(
        ['add'] + files,
        cwd=path
    )
    
    return {
        "success": success,
        "message": stdout or stderr,
        "files": files
    }


def unstage_files(
    files: List[str],
    path: str = "."
) -> Dict[str, Any]:
    """
    Remove arquivos do staging.
    """
    success, stdout, stderr = run_git_command(
        ['reset', 'HEAD', '--'] + files,
        cwd=path
    )
    
    return {
        "success": success,
        "message": stdout or stderr,
        "files": files
    }


def create_commit(
    message: str,
    path: str = "."
) -> Dict[str, Any]:
    """
    Cria um commit com a mensagem fornecida.
    
    Args:
        message: Mensagem do commit
        path: Caminho do repositório
        
    Returns:
        Resultado com hash do commit
    """
    success, stdout, stderr = run_git_command(
        ['commit', '-m', message],
        cwd=path
    )
    
    if success:
        # Extrair hash do commit
        hash_match = re.search(r'\[[\w-]+ ([a-f0-9]+)\]', stdout)
        commit_hash = hash_match.group(1) if hash_match else ""
        
        return {
            "success": True,
            "message": stdout.strip(),
            "commit_hash": commit_hash
        }
    
    return {
        "success": False,
        "error": stderr or stdout
    }


def get_blame(
    file_path: str,
    start_line: int = 1,
    end_line: Optional[int] = None,
    repo_path: str = "."
) -> List[Dict[str, Any]]:
    """
    Obtém informações de blame de um arquivo.
    
    Args:
        file_path: Caminho do arquivo
        start_line: Linha inicial
        end_line: Linha final
        repo_path: Caminho do repositório
        
    Returns:
        Lista com informações de autor por linha
    """
    args = ['blame', '--line-porcelain']
    if end_line:
        args.extend([f'-L{start_line},{end_line}'])
    args.append(file_path)
    
    success, stdout, _ = run_git_command(args, cwd=repo_path)
    
    if not success:
        return []
    
    blame_info = []
    current_line = {}
    
    for line in stdout.splitlines():
        if line.startswith('author '):
            current_line['author'] = line[7:]
        elif line.startswith('author-time '):
            current_line['timestamp'] = int(line[12:])
        elif line.startswith('summary '):
            current_line['commit_message'] = line[8:]
        elif line.startswith('\t'):
            current_line['content'] = line[1:]
            blame_info.append(current_line.copy())
            current_line = {}
    
    return blame_info


def _map_status(status_char: str) -> str:
    """Mapeia caractere de status para string"""
    mapping = {
        'M': 'modified',
        'A': 'added',
        'D': 'deleted',
        'R': 'renamed',
        'C': 'copied',
        'U': 'conflict',
        '?': 'untracked'
    }
    return mapping.get(status_char.upper(), 'unknown')
