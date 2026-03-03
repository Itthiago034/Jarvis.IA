"""
JARVIS - Search Tools
=====================
Ferramentas para busca em código e arquivos.
Equivalente às funcionalidades grep_search, file_search e semantic_search.
"""

import os
import re
import fnmatch
import logging
from typing import List, Optional, Dict, Any, Generator
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Configurações
MAX_RESULTS = 100
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
    '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
    '.html', '.css', '.scss', '.sass', '.less',
    '.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.cfg',
    '.md', '.txt', '.rst', '.log',
    '.sql', '.sh', '.bash', '.ps1', '.bat', '.cmd'
}

# Padrões a ignorar
IGNORE_PATTERNS = {
    '__pycache__', 'node_modules', '.git', '.svn', '.hg',
    'venv', 'env', '.venv', 'virtualenv',
    'dist', 'build', '.next', '.nuxt',
    '*.pyc', '*.pyo', '*.class', '*.o', '*.obj',
    '.DS_Store', 'Thumbs.db'
}


@dataclass
class SearchMatch:
    """Representa um resultado de busca"""
    file_path: str
    line_number: int
    line_content: str
    match_start: int = 0
    match_end: int = 0


@dataclass
class FileMatch:
    """Representa um arquivo que corresponde ao padrão"""
    path: str
    name: str
    relative_path: str


def should_ignore(path: str) -> bool:
    """Verifica se um caminho deve ser ignorado"""
    path_parts = Path(path).parts
    for part in path_parts:
        if part in IGNORE_PATTERNS:
            return True
        for pattern in IGNORE_PATTERNS:
            if '*' in pattern and fnmatch.fnmatch(part, pattern):
                return True
    return False


def grep_search(
    query: str,
    root_path: str,
    is_regex: bool = False,
    include_pattern: Optional[str] = None,
    max_results: int = MAX_RESULTS,
    case_sensitive: bool = False
) -> List[Dict[str, Any]]:
    """
    Busca por texto em arquivos (equivalente ao grep_search).
    
    Args:
        query: String ou regex para buscar
        root_path: Diretório raiz para busca
        is_regex: Se True, trata query como regex
        include_pattern: Padrão glob para filtrar arquivos (ex: "*.py")
        max_results: Número máximo de resultados
        case_sensitive: Se True, busca é case-sensitive
    
    Returns:
        Lista de dicionários com file_path, line_number, line_content
    
    Exemplo:
        results = grep_search("def main", "/project", include_pattern="*.py")
    """
    results = []
    flags = 0 if case_sensitive else re.IGNORECASE
    
    try:
        if is_regex:
            pattern = re.compile(query, flags)
        else:
            pattern = re.compile(re.escape(query), flags)
    except re.error as e:
        logger.error(f"Regex inválido: {e}")
        return [{"error": f"Regex inválido: {e}"}]
    
    root = Path(root_path)
    
    for file_path in _walk_files(root, include_pattern):
        if len(results) >= max_results:
            break
            
        try:
            # Verificar tamanho do arquivo
            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                continue
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if len(results) >= max_results:
                        break
                        
                    match = pattern.search(line)
                    if match:
                        results.append({
                            "file_path": str(file_path),
                            "line_number": line_num,
                            "line_content": line.strip()[:500],  # Limitar tamanho
                            "match_start": match.start(),
                            "match_end": match.end()
                        })
                        
        except (IOError, OSError) as e:
            logger.debug(f"Não foi possível ler {file_path}: {e}")
            continue
    
    return results


def file_search(
    pattern: str,
    root_path: str,
    max_results: int = MAX_RESULTS
) -> List[Dict[str, str]]:
    """
    Busca arquivos por padrão glob (equivalente ao file_search).
    
    Args:
        pattern: Padrão glob (ex: "**/*.py", "src/**/*.ts")
        root_path: Diretório raiz para busca
        max_results: Número máximo de resultados
    
    Returns:
        Lista de dicionários com path, name, relative_path
    
    Exemplo:
        files = file_search("**/*.py", "/project")
    """
    results = []
    root = Path(root_path)
    
    try:
        for file_path in root.glob(pattern):
            if len(results) >= max_results:
                break
                
            if file_path.is_file() and not should_ignore(str(file_path)):
                results.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "relative_path": str(file_path.relative_to(root))
                })
    except Exception as e:
        logger.error(f"Erro na busca de arquivos: {e}")
        return [{"error": str(e)}]
    
    return results


def list_directory(
    path: str,
    recursive: bool = False,
    show_hidden: bool = False
) -> List[Dict[str, Any]]:
    """
    Lista conteúdo de um diretório (equivalente ao list_dir).
    
    Args:
        path: Caminho do diretório
        recursive: Se True, lista recursivamente
        show_hidden: Se True, mostra arquivos ocultos
    
    Returns:
        Lista de dicionários com name, type, size
    """
    results = []
    target = Path(path)
    
    if not target.exists():
        return [{"error": f"Diretório não existe: {path}"}]
    
    if not target.is_dir():
        return [{"error": f"Não é um diretório: {path}"}]
    
    try:
        items = target.rglob('*') if recursive else target.iterdir()
        
        for item in items:
            if not show_hidden and item.name.startswith('.'):
                continue
                
            if should_ignore(str(item)):
                continue
            
            results.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
                "path": str(item)
            })
            
    except PermissionError:
        return [{"error": f"Sem permissão para acessar: {path}"}]
    except Exception as e:
        return [{"error": str(e)}]
    
    return sorted(results, key=lambda x: (x["type"] != "directory", x["name"]))


def simple_semantic_search(
    query: str,
    root_path: str,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    Busca semântica simplificada usando keywords.
    
    Para busca semântica completa com embeddings, integrar com:
    - Google Vertex AI Embeddings
    - Sentence Transformers
    - OpenAI Embeddings
    
    Esta versão usa busca por palavras-chave expandida.
    
    Args:
        query: Consulta em linguagem natural
        root_path: Diretório raiz
        max_results: Máximo de resultados
    
    Returns:
        Lista de arquivos relevantes com contexto
    """
    # Extrair palavras-chave da query
    keywords = _extract_keywords(query)
    
    results = []
    scores = {}  # arquivo -> score
    
    for keyword in keywords:
        matches = grep_search(keyword, root_path, max_results=50)
        
        for match in matches:
            if "error" in match:
                continue
                
            file_path = match["file_path"]
            if file_path not in scores:
                scores[file_path] = {
                    "score": 0,
                    "matches": [],
                    "keywords_found": set()
                }
            
            scores[file_path]["score"] += 1
            scores[file_path]["keywords_found"].add(keyword)
            if len(scores[file_path]["matches"]) < 3:
                scores[file_path]["matches"].append(match)
    
    # Ordenar por score e converter para lista
    sorted_files = sorted(
        scores.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )[:max_results]
    
    for file_path, data in sorted_files:
        results.append({
            "file_path": file_path,
            "relevance_score": data["score"],
            "keywords_found": list(data["keywords_found"]),
            "sample_matches": data["matches"]
        })
    
    return results


def _walk_files(
    root: Path,
    include_pattern: Optional[str] = None
) -> Generator[Path, None, None]:
    """Generator para percorrer arquivos"""
    
    if include_pattern:
        # Usar glob se padrão específico
        for file_path in root.glob(include_pattern):
            if file_path.is_file() and not should_ignore(str(file_path)):
                yield file_path
    else:
        # Percorrer todos os arquivos de código
        for dirpath, dirnames, filenames in os.walk(root):
            # Filtrar diretórios ignorados
            dirnames[:] = [d for d in dirnames if d not in IGNORE_PATTERNS and not d.startswith('.')]
            
            for filename in filenames:
                file_path = Path(dirpath) / filename
                ext = file_path.suffix.lower()
                
                if ext in SUPPORTED_EXTENSIONS and not should_ignore(str(file_path)):
                    yield file_path


def _extract_keywords(query: str) -> List[str]:
    """Extrai palavras-chave relevantes de uma query"""
    # Remover palavras comuns (stopwords simplificado)
    stopwords = {
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
        'de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no',
        'para', 'com', 'que', 'como', 'onde', 'qual',
        'the', 'a', 'an', 'is', 'are', 'was', 'were',
        'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'how', 'what', 'where', 'when', 'which', 'who'
    }
    
    # Tokenizar
    words = re.findall(r'\b\w+\b', query.lower())
    
    # Filtrar
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    
    return keywords[:10]  # Limitar a 10 keywords
