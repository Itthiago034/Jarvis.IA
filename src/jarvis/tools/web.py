"""
JARVIS - Web Tools
==================
Ferramentas para buscar informações na web e acessar páginas.
Equivalente às funcionalidades fetch_webpage e semantic_search web.
"""

import aiohttp
import asyncio
import logging
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import html

logger = logging.getLogger(__name__)

# Configurações
DEFAULT_TIMEOUT = 30
MAX_CONTENT_SIZE = 512 * 1024  # 512KB
USER_AGENT = "JARVIS-CodeAgent/1.0 (AI Assistant)"


@dataclass
class WebPage:
    """Resultado de uma busca de página web"""
    url: str
    title: str
    content: str
    status_code: int
    content_type: str
    success: bool
    error: Optional[str] = None


async def fetch_webpage(
    url: str,
    timeout: int = DEFAULT_TIMEOUT,
    extract_text: bool = True
) -> Dict[str, Any]:
    """
    Busca uma página web e extrai seu conteúdo.
    
    Args:
        url: URL da página
        timeout: Timeout em segundos
        extract_text: Se True, extrai apenas texto (remove HTML)
    
    Returns:
        Dicionário com url, title, content, status_code, success
    
    Exemplo:
        result = await fetch_webpage("https://docs.python.org/3/library/asyncio.html")
        print(result["title"])
    """
    logger.info(f"Buscando página: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": USER_AGENT}
            
            async with session.get(url, timeout=timeout, headers=headers) as response:
                content_type = response.headers.get('Content-Type', '')
                
                # Verificar se é conteúdo suportado
                if not any(t in content_type for t in ['text/html', 'text/plain', 'application/json']):
                    return {
                        "url": url,
                        "title": "",
                        "content": f"Tipo de conteúdo não suportado: {content_type}",
                        "status_code": response.status,
                        "success": False,
                        "error": "Unsupported content type"
                    }
                
                # Ler conteúdo com limite
                content = await response.text()
                if len(content) > MAX_CONTENT_SIZE:
                    content = content[:MAX_CONTENT_SIZE] + "\n\n[Conteúdo truncado...]"
                
                # Extrair texto se solicitado
                if extract_text and 'text/html' in content_type:
                    title = _extract_title(content)
                    content = _html_to_text(content)
                else:
                    title = urlparse(url).netloc
                
                return {
                    "url": url,
                    "title": title,
                    "content": content,
                    "status_code": response.status,
                    "content_type": content_type,
                    "success": response.status == 200
                }
                
    except asyncio.TimeoutError:
        return {
            "url": url,
            "title": "",
            "content": "",
            "status_code": 0,
            "success": False,
            "error": f"Timeout após {timeout} segundos"
        }
    except aiohttp.ClientError as e:
        return {
            "url": url,
            "title": "",
            "content": "",
            "status_code": 0,
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Erro ao buscar {url}: {e}")
        return {
            "url": url,
            "title": "",
            "content": "",
            "status_code": 0,
            "success": False,
            "error": str(e)
        }


def fetch_webpage_sync(
    url: str,
    timeout_seconds: int = DEFAULT_TIMEOUT,
    extract_text_only: bool = True
) -> Dict[str, Any]:
    """
    Versão síncrona do fetch_webpage para uso como tool do ADK.
    
    Args:
        url: URL da página web a ser buscada
        timeout_seconds: Tempo máximo de espera em segundos
        extract_text_only: Se True, remove tags HTML e retorna apenas texto
    
    Returns:
        Dicionário com url, title, content, status_code, success, error
    """
    try:
        import urllib.request
        import urllib.error
        
        headers = {"User-Agent": USER_AGENT}
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            content = response.read().decode('utf-8', errors='ignore')
            content_type = response.headers.get('Content-Type', '')
            
            if len(content) > MAX_CONTENT_SIZE:
                content = content[:MAX_CONTENT_SIZE] + "\n\n[Conteúdo truncado...]"
            
            if extract_text_only and 'text/html' in content_type:
                title = _extract_title(content)
                content = _html_to_text(content)
            else:
                title = urlparse(url).netloc
            
            return {
                "url": url,
                "title": title,
                "content": content,
                "status_code": response.status,
                "content_type": content_type,
                "success": response.status == 200
            }
            
    except urllib.error.URLError as e:
        return {
            "url": url,
            "title": "",
            "content": "",
            "status_code": 0,
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "url": url,
            "title": "",
            "content": "",
            "status_code": 0,
            "success": False,
            "error": str(e)
        }


def search_documentation(
    query: str,
    sources: Optional[List[str]] = None
) -> List[Dict[str, str]]:
    """
    Retorna URLs de documentação relevante para uma query.
    
    Args:
        query: Tópico de busca (ex: "python asyncio", "react hooks")
        sources: Lista de fontes preferidas (opcional)
    
    Returns:
        Lista de dicionários com url e description
    """
    # Mapeamento de tópicos para documentação
    DOCUMENTATION_SOURCES = {
        # Python
        "python": "https://docs.python.org/3/",
        "asyncio": "https://docs.python.org/3/library/asyncio.html",
        "typing": "https://docs.python.org/3/library/typing.html",
        "pathlib": "https://docs.python.org/3/library/pathlib.html",
        "dataclass": "https://docs.python.org/3/library/dataclasses.html",
        
        # Frameworks Python
        "fastapi": "https://fastapi.tiangolo.com/",
        "django": "https://docs.djangoproject.com/",
        "flask": "https://flask.palletsprojects.com/",
        "pydantic": "https://docs.pydantic.dev/",
        
        # JavaScript/TypeScript
        "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "typescript": "https://www.typescriptlang.org/docs/",
        "nodejs": "https://nodejs.org/docs/",
        "react": "https://react.dev/",
        "nextjs": "https://nextjs.org/docs",
        "vue": "https://vuejs.org/guide/",
        
        # AI/ML
        "google adk": "https://google.github.io/adk-docs/",
        "langchain": "https://python.langchain.com/docs/",
        "gemini": "https://ai.google.dev/gemini-api/docs",
        "openai": "https://platform.openai.com/docs",
        
        # DevOps
        "docker": "https://docs.docker.com/",
        "kubernetes": "https://kubernetes.io/docs/",
        "git": "https://git-scm.com/doc",
        "github": "https://docs.github.com/",
    }
    
    results = []
    query_lower = query.lower()
    
    for topic, url in DOCUMENTATION_SOURCES.items():
        if topic in query_lower or any(word in topic for word in query_lower.split()):
            results.append({
                "topic": topic,
                "url": url,
                "description": f"Documentação oficial de {topic}"
            })
    
    # Se nenhum resultado específico, sugerir busca
    if not results:
        results.append({
            "topic": "search",
            "url": f"https://www.google.com/search?q={query.replace(' ', '+')}+documentation",
            "description": f"Buscar documentação para: {query}"
        })
    
    return results[:10]


def _extract_title(html_content: str) -> str:
    """Extrai o título de uma página HTML"""
    match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
    if match:
        return html.unescape(match.group(1)).strip()
    return ""


def _html_to_text(html_content: str) -> str:
    """Converte HTML para texto puro"""
    # Remover scripts e styles
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remover comentários
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Substituir quebras de linha por espaços
    text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</?p[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</?div[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</?li[^>]*>', '\n• ', text, flags=re.IGNORECASE)
    text = re.sub(r'</?h[1-6][^>]*>', '\n\n', text, flags=re.IGNORECASE)
    
    # Remover todas as outras tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decodificar entidades HTML
    text = html.unescape(text)
    
    # Limpar espaços extras
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


async def search_google(
    query: str,
    num_results: int = 5
) -> List[Dict[str, str]]:
    """
    Nota: Esta função requer uma API key do Google Custom Search.
    Para uso sem API, considere usar o DuckDuckGo ou busca local.
    
    Args:
        query: Termo de busca
        num_results: Número de resultados
    
    Returns:
        Lista de resultados com title, url, snippet
    """
    logger.warning("search_google requer Google Custom Search API Key")
    return [{
        "title": "API Key Required",
        "url": "https://developers.google.com/custom-search/v1/introduction",
        "snippet": "Configure GOOGLE_API_KEY e GOOGLE_CX para usar busca Google"
    }]
