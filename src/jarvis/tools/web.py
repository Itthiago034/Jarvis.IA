"""
JARVIS - Web Tools (EXPANDED)
=============================
Ferramentas COMPLETAS para acesso amplo à internet.
Inclui: navegação web, múltiplos motores de busca, downloads,
APIs REST, extração de dados, scraping e muito mais.

Autor: JARVIS CodeAgent
Versão: 2.0
"""

import aiohttp
import asyncio
import logging
import re
import os
import json
import base64
import hashlib
from typing import Optional, Dict, Any, List, Union, Tuple
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse, quote_plus, urlencode, parse_qs
from pathlib import Path
import html
from datetime import datetime
import ssl
import certifi

logger = logging.getLogger(__name__)

# ==================== CONFIGURAÇÕES ====================
DEFAULT_TIMEOUT = 30
EXTENDED_TIMEOUT = 60
MAX_CONTENT_SIZE = 2 * 1024 * 1024  # 2MB
MAX_DOWNLOAD_SIZE = 100 * 1024 * 1024  # 100MB para downloads
CHUNK_SIZE = 8192

# User agents para diferentes propósitos
USER_AGENTS = {
    "default": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "mobile": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "android": "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "bot": "JARVIS-WebAgent/2.0 (AI Assistant; Python/aiohttp)",
    "googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "curl": "curl/8.5.0",
}

# Tipos MIME suportados
SUPPORTED_TEXT_TYPES = [
    'text/html', 'text/plain', 'application/json', 'application/xml',
    'text/xml', 'text/css', 'text/javascript', 'application/javascript',
    'text/csv', 'text/markdown', 'application/rss+xml', 'application/atom+xml',
    'application/ld+json', 'text/calendar', 'application/x-yaml'
]


# ==================== DATACLASSES ====================

@dataclass
class WebPage:
    """Resultado completo de uma página web"""
    url: str
    final_url: str  # URL após redirecionamentos
    title: str
    content: str
    status_code: int
    content_type: str
    success: bool
    error: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    meta: Dict[str, str] = field(default_factory=dict)
    load_time: float = 0.0


@dataclass
class SearchResult:
    """Resultado de uma busca na web"""
    title: str
    url: str
    snippet: str
    source: str  # google, bing, duckduckgo, brave, etc.
    position: int = 0
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DownloadResult:
    """Resultado de um download"""
    url: str
    local_path: str
    file_name: str
    file_size: int
    content_type: str
    success: bool
    error: Optional[str] = None
    checksum: Optional[str] = None


@dataclass
class APIResponse:
    """Resposta de uma API"""
    url: str
    method: str
    status_code: int
    data: Any
    headers: Dict[str, str]
    success: bool
    error: Optional[str] = None
    response_time: float = 0.0


# ==================== CLASSE PRINCIPAL WEB BROWSER ====================

class WebBrowser:
    """
    Navegador web completo para o JARVIS.
    Suporta sessões persistentes, cookies, headers customizados,
    proxies, e muito mais.
    """
    
    def __init__(
        self,
        user_agent: str = "default",
        proxy: Optional[str] = None,
        verify_ssl: bool = True
    ):
        self._session: Optional[aiohttp.ClientSession] = None
        self._proxy = proxy
        self._verify_ssl = verify_ssl
        self._headers: Dict[str, str] = {
            "User-Agent": USER_AGENTS.get(user_agent, USER_AGENTS["default"]),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        self._history: List[str] = []
        self._cookies: Dict[str, Dict[str, str]] = {}
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria sessão HTTP persistente"""
        if self._session is None or self._session.closed:
            # Configurar SSL de forma mais permissiva
            try:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            except Exception:
                ssl_context = False
            
            connector = aiohttp.TCPConnector(
                limit=20,
                limit_per_host=10,
                ssl=ssl_context,
                force_close=False
            )
            
            timeout = aiohttp.ClientTimeout(
                total=EXTENDED_TIMEOUT,
                connect=15,
                sock_read=45
            )
            
            self._session = aiohttp.ClientSession(
                headers=self._headers,
                connector=connector,
                timeout=timeout,
                cookie_jar=aiohttp.CookieJar(unsafe=True),
                trust_env=True  # Para usar proxy de ambiente
            )
        return self._session
    
    async def close(self):
        """Fecha a sessão"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    def set_header(self, key: str, value: str):
        """Define um header customizado"""
        self._headers[key] = value
    
    def set_headers(self, headers: Dict[str, str]):
        """Define múltiplos headers"""
        self._headers.update(headers)
    
    def set_user_agent(self, agent_type: str):
        """Define o user agent"""
        if agent_type in USER_AGENTS:
            self._headers["User-Agent"] = USER_AGENTS[agent_type]
        else:
            self._headers["User-Agent"] = agent_type
    
    def get_history(self) -> List[str]:
        """Retorna o histórico de navegação"""
        return self._history.copy()
    
    def clear_history(self):
        """Limpa o histórico"""
        self._history.clear()
    
    async def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        follow_redirects: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
        extract_text: bool = False
    ) -> Dict[str, Any]:
        """
        Realiza uma requisição GET completa.
        
        Args:
            url: URL para acessar
            params: Query parameters
            headers: Headers adicionais
            follow_redirects: Seguir redirecionamentos
            timeout: Timeout em segundos
            extract_text: Extrair apenas texto (remover HTML)
        
        Returns:
            Dicionário com resposta completa
        """
        session = await self._get_session()
        merged_headers = {**self._headers, **(headers or {})}
        start_time = datetime.now()
        
        try:
            async with session.get(
                url,
                params=params,
                headers=merged_headers,
                allow_redirects=follow_redirects,
                proxy=self._proxy,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                load_time = (datetime.now() - start_time).total_seconds()
                content_type = response.headers.get('Content-Type', '')
                final_url = str(response.url)
                
                # Determinar como ler o conteúdo
                if any(ct in content_type for ct in ['image/', 'audio/', 'video/', 'application/octet-stream', 'application/pdf']):
                    content = f"[Conteúdo binário: {content_type}, tamanho: {response.content_length or 'desconhecido'} bytes]"
                    title = urlparse(final_url).path.split('/')[-1] or "binary"
                else:
                    content = await response.text(errors='replace')
                    if len(content) > MAX_CONTENT_SIZE:
                        content = content[:MAX_CONTENT_SIZE] + "\n\n[... Conteúdo truncado ...]"
                    
                    title = _extract_title(content) if 'text/html' in content_type else ""
                    
                    if extract_text and 'text/html' in content_type:
                        content = _html_to_text(content)
                
                self._history.append(final_url)
                
                # Extrair links e imagens se for HTML
                links = []
                images = []
                meta = {}
                if 'text/html' in content_type and not extract_text:
                    links = _extract_links(content, final_url)
                    images = _extract_images(content, final_url)
                    meta = _extract_meta(content)
                
                return {
                    "url": url,
                    "final_url": final_url,
                    "title": title,
                    "content": content,
                    "status_code": response.status,
                    "content_type": content_type,
                    "headers": dict(response.headers),
                    "links": links[:100],  # Limitar links
                    "images": images[:50],  # Limitar imagens
                    "meta": meta,
                    "load_time": load_time,
                    "success": 200 <= response.status < 400
                }
                
        except asyncio.TimeoutError:
            return {"url": url, "success": False, "error": f"Timeout após {timeout}s", "status_code": 0}
        except aiohttp.ClientSSLError as e:
            return {"url": url, "success": False, "error": f"Erro SSL: {e}", "status_code": 0}
        except aiohttp.ClientError as e:
            return {"url": url, "success": False, "error": f"Erro de conexão: {e}", "status_code": 0}
        except Exception as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            return {"url": url, "success": False, "error": str(e), "status_code": 0}
    
    async def post(
        self,
        url: str,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Realiza uma requisição POST.
        
        Args:
            url: URL para enviar dados
            data: Form data (application/x-www-form-urlencoded)
            json_data: JSON data (application/json)
            headers: Headers adicionais
            timeout: Timeout em segundos
        
        Returns:
            Dicionário com resposta
        """
        session = await self._get_session()
        merged_headers = {**self._headers, **(headers or {})}
        
        try:
            async with session.post(
                url,
                data=data,
                json=json_data,
                headers=merged_headers,
                proxy=self._proxy,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                content_type = response.headers.get('Content-Type', '')
                
                if 'application/json' in content_type:
                    try:
                        content = await response.json()
                    except:
                        content = await response.text()
                else:
                    content = await response.text(errors='replace')
                    if len(content) > MAX_CONTENT_SIZE:
                        content = content[:MAX_CONTENT_SIZE]
                
                return {
                    "url": str(response.url),
                    "status_code": response.status,
                    "content": content,
                    "content_type": content_type,
                    "headers": dict(response.headers),
                    "success": 200 <= response.status < 400
                }
                
        except Exception as e:
            return {"url": url, "success": False, "error": str(e), "status_code": 0}
    
    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Realiza uma requisição HTTP genérica.
        
        Args:
            method: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
            url: URL do recurso
            headers: Headers adicionais
            params: Query parameters
            data: Form data
            json_data: JSON data
            timeout: Timeout em segundos
        
        Returns:
            Dicionário com resposta
        """
        session = await self._get_session()
        merged_headers = {**self._headers, **(headers or {})}
        start_time = datetime.now()
        
        try:
            async with session.request(
                method.upper(),
                url,
                params=params,
                data=data,
                json=json_data,
                headers=merged_headers,
                proxy=self._proxy,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response_time = (datetime.now() - start_time).total_seconds()
                content_type = response.headers.get('Content-Type', '')
                
                if 'application/json' in content_type:
                    try:
                        content = await response.json()
                    except:
                        content = await response.text()
                else:
                    content = await response.text(errors='replace')
                
                return {
                    "url": str(response.url),
                    "method": method.upper(),
                    "status_code": response.status,
                    "content": content,
                    "content_type": content_type,
                    "headers": dict(response.headers),
                    "response_time": response_time,
                    "success": 200 <= response.status < 400
                }
                
        except Exception as e:
            return {"url": url, "method": method.upper(), "success": False, "error": str(e), "status_code": 0}
    
    async def download_file(
        self,
        url: str,
        save_path: str,
        filename: Optional[str] = None,
        headers: Optional[Dict] = None,
        chunk_size: int = CHUNK_SIZE
    ) -> Dict[str, Any]:
        """
        Baixa um arquivo da internet.
        
        Args:
            url: URL do arquivo
            save_path: Diretório onde salvar
            filename: Nome do arquivo (opcional, extrai da URL)
            headers: Headers adicionais
            chunk_size: Tamanho do chunk para download
        
        Returns:
            Dicionário com resultado do download
        """
        session = await self._get_session()
        merged_headers = {**self._headers, **(headers or {})}
        
        try:
            async with session.get(
                url,
                headers=merged_headers,
                proxy=self._proxy,
                timeout=aiohttp.ClientTimeout(total=300)  # 5 min para downloads
            ) as response:
                if response.status != 200:
                    return {
                        "url": url,
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "status_code": response.status
                    }
                
                # Determinar nome do arquivo
                if not filename:
                    # Tentar extrair do header Content-Disposition
                    cd = response.headers.get('Content-Disposition', '')
                    if 'filename=' in cd:
                        filename = re.findall(r'filename[^;=\n]*=([\'"]?)([^\'";\n]*)\1', cd)
                        filename = filename[0][1] if filename else None
                    
                    if not filename:
                        # Extrair da URL
                        parsed = urlparse(str(response.url))
                        filename = parsed.path.split('/')[-1] or 'download'
                        if not Path(filename).suffix:
                            # Adicionar extensão baseada no content-type
                            ct = response.headers.get('Content-Type', '')
                            ext_map = {
                                'image/jpeg': '.jpg', 'image/png': '.png', 'image/gif': '.gif',
                                'application/pdf': '.pdf', 'application/zip': '.zip',
                                'text/html': '.html', 'application/json': '.json'
                            }
                            for ct_pattern, ext in ext_map.items():
                                if ct_pattern in ct:
                                    filename += ext
                                    break
                
                # Criar diretório se necessário
                save_dir = Path(save_path)
                save_dir.mkdir(parents=True, exist_ok=True)
                
                file_path = save_dir / filename
                total_size = 0
                
                # Verificar tamanho
                content_length = response.content_length
                if content_length and content_length > MAX_DOWNLOAD_SIZE:
                    return {
                        "url": url,
                        "success": False,
                        "error": f"Arquivo muito grande: {content_length} bytes (máx: {MAX_DOWNLOAD_SIZE})"
                    }
                
                # Baixar em chunks
                hasher = hashlib.md5()
                with open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        if total_size + len(chunk) > MAX_DOWNLOAD_SIZE:
                            return {
                                "url": url,
                                "success": False,
                                "error": "Download excedeu tamanho máximo"
                            }
                        f.write(chunk)
                        hasher.update(chunk)
                        total_size += len(chunk)
                
                return {
                    "url": url,
                    "local_path": str(file_path),
                    "file_name": filename,
                    "file_size": total_size,
                    "content_type": response.headers.get('Content-Type', ''),
                    "checksum": hasher.hexdigest(),
                    "success": True
                }
                
        except Exception as e:
            return {"url": url, "success": False, "error": str(e)}


# ==================== FUNÇÕES DE BUSCA NA WEB ====================

async def search_web(
    query: str,
    engine: str = "duckduckgo",
    num_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Busca na web usando diferentes motores de busca.
    
    Args:
        query: Termo de busca
        engine: Motor de busca (duckduckgo, brave, google, bing)
        num_results: Número de resultados desejados
    
    Returns:
        Lista de resultados com title, url, snippet
    """
    engines = {
        "duckduckgo": _search_duckduckgo,
        "brave": _search_brave,
        "google": _search_google_scrape,
        "bing": _search_bing_scrape,
    }
    
    search_func = engines.get(engine.lower(), _search_duckduckgo)
    
    try:
        results = await search_func(query, num_results)
        return results
    except Exception as e:
        logger.error(f"Erro na busca {engine}: {e}")
        return [{"error": str(e), "source": engine}]


async def _search_duckduckgo(query: str, num_results: int = 10) -> List[Dict]:
    """Busca no DuckDuckGo - gratuito e sem API key"""
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Usar a API Instant Answer
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1"
        }
        
        try:
            async with session.get(
                "https://api.duckduckgo.com/",
                params=params,
                headers={"User-Agent": USER_AGENTS["default"]},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Abstract (resposta principal)
                    if data.get("Abstract"):
                        results.append({
                            "title": data.get("Heading", "Resultado"),
                            "url": data.get("AbstractURL", ""),
                            "snippet": data.get("Abstract", ""),
                            "source": "duckduckgo",
                            "type": "abstract"
                        })
                    
                    # Related topics
                    for i, topic in enumerate(data.get("RelatedTopics", [])[:num_results]):
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append({
                                "title": topic.get("Text", "")[:80] + "..." if len(topic.get("Text", "")) > 80 else topic.get("Text", ""),
                                "url": topic.get("FirstURL", ""),
                                "snippet": topic.get("Text", ""),
                                "source": "duckduckgo",
                                "position": i + 1
                            })
                        elif isinstance(topic, dict) and topic.get("Topics"):
                            # Subtópicos
                            for sub in topic.get("Topics", [])[:3]:
                                if sub.get("Text"):
                                    results.append({
                                        "title": sub.get("Text", "")[:80],
                                        "url": sub.get("FirstURL", ""),
                                        "snippet": sub.get("Text", ""),
                                        "source": "duckduckgo"
                                    })
                    
                    # Infobox se disponível
                    if data.get("Infobox"):
                        for item in data["Infobox"].get("content", [])[:5]:
                            if item.get("label") and item.get("value"):
                                results.append({
                                    "title": f"{item['label']}: {item['value'][:50]}",
                                    "url": data.get("AbstractURL", ""),
                                    "snippet": f"{item['label']}: {item['value']}",
                                    "source": "duckduckgo",
                                    "type": "infobox"
                                })
                                
        except Exception as e:
            logger.warning(f"DuckDuckGo API error: {e}")
        
        # Se poucos resultados, tentar HTML scraping
        if len(results) < 3:
            try:
                html_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
                async with session.get(
                    html_url,
                    headers={"User-Agent": USER_AGENTS["default"]},
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    if resp.status == 200:
                        html_content = await resp.text()
                        
                        # Parse simples dos resultados
                        result_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
                        snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+)</a>'
                        
                        links = re.findall(result_pattern, html_content)
                        snippets = re.findall(snippet_pattern, html_content)
                        
                        for i, (url, title) in enumerate(links[:num_results]):
                            snippet = snippets[i] if i < len(snippets) else ""
                            results.append({
                                "title": html.unescape(title),
                                "url": url,
                                "snippet": html.unescape(snippet),
                                "source": "duckduckgo",
                                "position": len(results) + 1
                            })
                            
            except Exception as e:
                logger.warning(f"DuckDuckGo HTML scrape error: {e}")
    
    return results[:num_results]


async def _search_brave(query: str, num_results: int = 10) -> List[Dict]:
    """Busca no Brave Search - requer API key"""
    api_key = os.getenv("BRAVE_API_KEY")
    
    if not api_key:
        return [{
            "title": "Brave Search API Key Required",
            "url": "https://brave.com/search/api/",
            "snippet": "Configure BRAVE_API_KEY para usar Brave Search",
            "source": "brave"
        }]
    
    async with aiohttp.ClientSession() as session:
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": api_key
        }
        params = {
            "q": query,
            "count": num_results
        }
        
        try:
            async with session.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = []
                    
                    for i, item in enumerate(data.get("web", {}).get("results", [])):
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "snippet": item.get("description", ""),
                            "source": "brave",
                            "position": i + 1
                        })
                    
                    return results
                else:
                    return [{"error": f"Brave API error: {resp.status}", "source": "brave"}]
                    
        except Exception as e:
            return [{"error": str(e), "source": "brave"}]


async def _search_google_scrape(query: str, num_results: int = 10) -> List[Dict]:
    """Busca no Google via scraping (backup)"""
    results = []
    
    async with aiohttp.ClientSession() as session:
        url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}&hl=pt-BR"
        
        try:
            async with session.get(
                url,
                headers={
                    "User-Agent": USER_AGENTS["default"],
                    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
                },
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    html_content = await resp.text()
                    
                    # Pattern para extrair resultados do Google
                    # Nota: Pode mudar com atualizações do Google
                    patterns = [
                        r'<a href="/url\?q=([^&"]+)[^"]*"[^>]*><h3[^>]*>([^<]+)</h3>',
                        r'<div class="[^"]*"><a href="([^"]+)"[^>]*><h3[^>]*>([^<]+)</h3>',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, html_content)
                        for i, (url, title) in enumerate(matches[:num_results]):
                            if not url.startswith('http'):
                                continue
                            results.append({
                                "title": html.unescape(title),
                                "url": url,
                                "snippet": "",
                                "source": "google",
                                "position": i + 1
                            })
                        
                        if results:
                            break
                            
        except Exception as e:
            logger.warning(f"Google scrape error: {e}")
    
    if not results:
        results.append({
            "title": "Busca Google",
            "url": f"https://www.google.com/search?q={quote_plus(query)}",
            "snippet": "Acesse diretamente o Google para resultados completos",
            "source": "google"
        })
    
    return results


async def _search_bing_scrape(query: str, num_results: int = 10) -> List[Dict]:
    """Busca no Bing via scraping"""
    results = []
    
    async with aiohttp.ClientSession() as session:
        url = f"https://www.bing.com/search?q={quote_plus(query)}&count={num_results}"
        
        try:
            async with session.get(
                url,
                headers={"User-Agent": USER_AGENTS["default"]},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    html_content = await resp.text()
                    
                    # Pattern para Bing
                    title_pattern = r'<h2><a[^>]*href="([^"]+)"[^>]*>([^<]+)</a></h2>'
                    matches = re.findall(title_pattern, html_content)
                    
                    for i, (url, title) in enumerate(matches[:num_results]):
                        results.append({
                            "title": html.unescape(title),
                            "url": url,
                            "snippet": "",
                            "source": "bing",
                            "position": i + 1
                        })
                        
        except Exception as e:
            logger.warning(f"Bing scrape error: {e}")
    
    return results


# ==================== FUNÇÕES PRINCIPAIS (COMPATIBILIDADE) ====================

async def fetch_webpage(
    url: str,
    timeout: int = DEFAULT_TIMEOUT,
    extract_text: bool = True,
    follow_redirects: bool = True
) -> Dict[str, Any]:
    """
    Busca uma página web e extrai seu conteúdo.
    
    Args:
        url: URL da página
        timeout: Timeout em segundos
        extract_text: Se True, extrai apenas texto (remove HTML)
        follow_redirects: Seguir redirecionamentos
    
    Returns:
        Dicionário com url, title, content, status_code, success
    """
    browser = WebBrowser()
    try:
        result = await browser.get(
            url,
            timeout=timeout,
            extract_text=extract_text,
            follow_redirects=follow_redirects
        )
        return result
    finally:
        await browser.close()


def fetch_webpage_sync(
    url: str,
    timeout_seconds: int = DEFAULT_TIMEOUT,
    extract_text_only: bool = True
) -> Dict[str, Any]:
    """
    Versão síncrona do fetch_webpage.
    
    Args:
        url: URL da página web
        timeout_seconds: Tempo máximo de espera
        extract_text_only: Se True, remove HTML
    
    Returns:
        Dicionário com url, title, content, status_code, success
    """
    try:
        import urllib.request
        import urllib.error
        
        headers = {"User-Agent": USER_AGENTS["default"]}
        request = urllib.request.Request(url, headers=headers)
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(request, timeout=timeout_seconds, context=ssl_context) as response:
            content = response.read().decode('utf-8', errors='replace')
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
            
    except urllib.error.HTTPError as e:
        return {"url": url, "success": False, "error": f"HTTP {e.code}: {e.reason}", "status_code": e.code}
    except urllib.error.URLError as e:
        return {"url": url, "success": False, "error": str(e.reason), "status_code": 0}
    except Exception as e:
        return {"url": url, "success": False, "error": str(e), "status_code": 0}


def search_documentation(
    query: str,
    sources: Optional[List[str]] = None
) -> List[Dict[str, str]]:
    """
    Retorna URLs de documentação relevante para uma query.
    
    Args:
        query: Tópico de busca
        sources: Lista de fontes preferidas
    
    Returns:
        Lista de dicionários com url e description
    """
    DOCUMENTATION_SOURCES = {
        # Python
        "python": "https://docs.python.org/3/",
        "asyncio": "https://docs.python.org/3/library/asyncio.html",
        "typing": "https://docs.python.org/3/library/typing.html",
        "pathlib": "https://docs.python.org/3/library/pathlib.html",
        "dataclass": "https://docs.python.org/3/library/dataclasses.html",
        "requests": "https://requests.readthedocs.io/",
        "aiohttp": "https://docs.aiohttp.org/",
        "pytest": "https://docs.pytest.org/",
        "pandas": "https://pandas.pydata.org/docs/",
        "numpy": "https://numpy.org/doc/",
        
        # Frameworks Python
        "fastapi": "https://fastapi.tiangolo.com/",
        "django": "https://docs.djangoproject.com/",
        "flask": "https://flask.palletsprojects.com/",
        "pydantic": "https://docs.pydantic.dev/",
        "sqlalchemy": "https://docs.sqlalchemy.org/",
        "celery": "https://docs.celeryq.dev/",
        
        # JavaScript/TypeScript
        "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "typescript": "https://www.typescriptlang.org/docs/",
        "nodejs": "https://nodejs.org/docs/",
        "react": "https://react.dev/",
        "nextjs": "https://nextjs.org/docs",
        "vue": "https://vuejs.org/guide/",
        "angular": "https://angular.io/docs",
        "svelte": "https://svelte.dev/docs",
        
        # AI/ML
        "google adk": "https://google.github.io/adk-docs/",
        "langchain": "https://python.langchain.com/docs/",
        "gemini": "https://ai.google.dev/gemini-api/docs",
        "openai": "https://platform.openai.com/docs",
        "pytorch": "https://pytorch.org/docs/",
        "tensorflow": "https://www.tensorflow.org/api_docs",
        "huggingface": "https://huggingface.co/docs",
        "transformers": "https://huggingface.co/docs/transformers",
        
        # DevOps
        "docker": "https://docs.docker.com/",
        "kubernetes": "https://kubernetes.io/docs/",
        "git": "https://git-scm.com/doc",
        "github": "https://docs.github.com/",
        "github actions": "https://docs.github.com/actions",
        "terraform": "https://developer.hashicorp.com/terraform/docs",
        "ansible": "https://docs.ansible.com/",
        
        # Databases
        "postgresql": "https://www.postgresql.org/docs/",
        "mysql": "https://dev.mysql.com/doc/",
        "mongodb": "https://www.mongodb.com/docs/",
        "redis": "https://redis.io/docs/",
        "elasticsearch": "https://www.elastic.co/guide/",
        
        # Cloud
        "aws": "https://docs.aws.amazon.com/",
        "gcp": "https://cloud.google.com/docs",
        "azure": "https://learn.microsoft.com/azure/",
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
    
    if not results:
        results.append({
            "topic": "search",
            "url": f"https://www.google.com/search?q={quote_plus(query)}+documentation",
            "description": f"Buscar documentação para: {query}"
        })
    
    return results[:15]


# ==================== FUNÇÕES AUXILIARES ====================

def _extract_title(html_content: str) -> str:
    """Extrai o título de uma página HTML"""
    patterns = [
        r'<title[^>]*>([^<]+)</title>',
        r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"',
        r'<h1[^>]*>([^<]+)</h1>',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            return html.unescape(match.group(1)).strip()[:200]
    
    return ""


def _html_to_text(html_content: str) -> str:
    """Converte HTML para texto puro de forma melhorada"""
    # Remover scripts, styles, comments
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<noscript[^>]*>.*?</noscript>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    text = re.sub(r'<svg[^>]*>.*?</svg>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Preservar estrutura com quebras de linha
    text = re.sub(r'<br[^>]*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)
    text = re.sub(r'</h[1-6]>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<h[1-6][^>]*>', '\n\n### ', text, flags=re.IGNORECASE)
    text = re.sub(r'</tr>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</td>', ' | ', text, flags=re.IGNORECASE)
    text = re.sub(r'</th>', ' | ', text, flags=re.IGNORECASE)
    
    # Preservar links como texto
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', r'\2 (\1)', text, flags=re.IGNORECASE)
    
    # Remover todas as outras tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decodificar entidades HTML
    text = html.unescape(text)
    
    # Limpar espaços
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n[ \t]+', '\n', text)
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def _extract_links(html_content: str, base_url: str) -> List[str]:
    """Extrai todos os links de uma página HTML"""
    links = []
    pattern = r'<a[^>]*href=["\']([^"\']+)["\']'
    
    for match in re.finditer(pattern, html_content, re.IGNORECASE):
        href = match.group(1)
        
        # Ignorar âncoras e javascript
        if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
            continue
        
        # Converter para URL absoluta
        full_url = urljoin(base_url, href)
        
        if full_url not in links:
            links.append(full_url)
    
    return links


def _extract_images(html_content: str, base_url: str) -> List[str]:
    """Extrai URLs de imagens de uma página HTML"""
    images = []
    pattern = r'<img[^>]*src=["\']([^"\']+)["\']'
    
    for match in re.finditer(pattern, html_content, re.IGNORECASE):
        src = match.group(1)
        
        # Ignorar data URLs pequenas e ícones
        if src.startswith('data:') and len(src) < 1000:
            continue
        
        full_url = urljoin(base_url, src)
        
        if full_url not in images:
            images.append(full_url)
    
    return images


def _extract_meta(html_content: str) -> Dict[str, str]:
    """Extrai metadados de uma página HTML"""
    meta = {}
    
    patterns = {
        "description": r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
        "keywords": r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']+)["\']',
        "author": r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']+)["\']',
        "og:title": r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']',
        "og:description": r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']',
        "og:image": r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
        "canonical": r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            meta[key] = html.unescape(match.group(1))[:500]
    
    return meta


# ==================== API REST HELPER ====================

async def api_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    auth_token: Optional[str] = None,
    api_key: Optional[str] = None,
    api_key_header: str = "X-API-Key",
    timeout: int = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """
    Faz uma requisição a uma API REST.
    
    Args:
        url: URL da API
        method: Método HTTP (GET, POST, PUT, DELETE, PATCH)
        headers: Headers adicionais
        params: Query parameters
        json_data: Corpo JSON da requisição
        auth_token: Token Bearer para Authorization
        api_key: API Key
        api_key_header: Nome do header para API Key
        timeout: Timeout em segundos
    
    Returns:
        Dicionário com resposta da API
    """
    browser = WebBrowser()
    
    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        **(headers or {})
    }
    
    if auth_token:
        req_headers["Authorization"] = f"Bearer {auth_token}"
    
    if api_key:
        req_headers[api_key_header] = api_key
    
    try:
        result = await browser.request(
            method=method,
            url=url,
            headers=req_headers,
            params=params,
            json_data=json_data,
            timeout=timeout
        )
        return result
    finally:
        await browser.close()


# ==================== FERRAMENTAS PARA O AGENTE ====================

def get_web_tools():
    """Retorna as ferramentas web para o CodeAgent"""
    
    async def browse_url(url: str, extract_text: bool = True) -> str:
        """
        Navega para uma URL e retorna o conteúdo.
        
        Args:
            url: URL completa para acessar (incluindo https://)
            extract_text: Se True, retorna apenas texto sem HTML
        
        Returns:
            Conteúdo da página ou mensagem de erro
        """
        result = await fetch_webpage(url, extract_text=extract_text)
        
        if result.get("success"):
            title = result.get("title", "")
            content = result.get("content", "")
            return f"📄 {title}\n\nURL: {result.get('final_url', url)}\n\n{content}"
        else:
            return f"❌ Erro ao acessar {url}: {result.get('error', 'Erro desconhecido')}"
    
    async def web_search(query: str, engine: str = "duckduckgo", count: int = 5) -> str:
        """
        Busca na web usando motores de busca.
        
        Args:
            query: O que você quer buscar
            engine: Motor de busca (duckduckgo, brave, google, bing)
            count: Número de resultados (máximo 10)
        
        Returns:
            Resultados formatados da busca
        """
        results = await search_web(query, engine=engine, num_results=min(count, 10))
        
        if not results:
            return f"Nenhum resultado encontrado para: {query}"
        
        output = [f"🔍 Resultados para '{query}':\n"]
        
        for i, r in enumerate(results, 1):
            if r.get("error"):
                output.append(f"⚠️ Erro: {r.get('error')}")
                continue
            
            output.append(f"{i}. {r.get('title', 'Sem título')}")
            output.append(f"   🔗 {r.get('url', '')}")
            if r.get('snippet'):
                output.append(f"   {r.get('snippet', '')[:200]}")
            output.append("")
        
        return "\n".join(output)
    
    async def download_from_url(url: str, save_folder: str = "./downloads") -> str:
        """
        Baixa um arquivo da internet.
        
        Args:
            url: URL do arquivo para baixar
            save_folder: Pasta onde salvar (padrão: ./downloads)
        
        Returns:
            Caminho do arquivo baixado ou erro
        """
        browser = WebBrowser()
        try:
            result = await browser.download_file(url, save_folder)
            
            if result.get("success"):
                return (
                    f"✅ Download concluído!\n"
                    f"📁 Arquivo: {result.get('file_name')}\n"
                    f"📍 Local: {result.get('local_path')}\n"
                    f"📊 Tamanho: {result.get('file_size', 0) / 1024:.2f} KB\n"
                    f"🔐 MD5: {result.get('checksum', 'N/A')}"
                )
            else:
                return f"❌ Erro no download: {result.get('error')}"
        finally:
            await browser.close()
    
    async def call_api(
        url: str,
        method: str = "GET",
        json_body: Optional[str] = None,
        auth: Optional[str] = None
    ) -> str:
        """
        Faz uma requisição a uma API REST.
        
        Args:
            url: URL da API
            method: GET, POST, PUT, DELETE, PATCH
            json_body: Corpo JSON como string (ex: '{"key": "value"}')
            auth: Token de autenticação Bearer
        
        Returns:
            Resposta da API formatada
        """
        json_data = None
        if json_body:
            try:
                json_data = json.loads(json_body)
            except json.JSONDecodeError as e:
                return f"❌ JSON inválido: {e}"
        
        result = await api_request(
            url=url,
            method=method,
            json_data=json_data,
            auth_token=auth
        )
        
        if result.get("success"):
            data = result.get("content", result.get("data", ""))
            if isinstance(data, dict):
                data = json.dumps(data, indent=2, ensure_ascii=False)
            return f"✅ {method} {url}\nStatus: {result.get('status_code')}\n\n{data}"
        else:
            return f"❌ Erro na API: {result.get('error')}"
    
    return {
        "browse_url": browse_url,
        "web_search": web_search,
        "download_from_url": download_from_url,
        "call_api": call_api
    }


# ==================== EXPORTS ====================

__all__ = [
    # Classes
    "WebBrowser",
    "WebPage",
    "SearchResult", 
    "DownloadResult",
    "APIResponse",
    
    # Funções principais
    "fetch_webpage",
    "fetch_webpage_sync",
    "search_web",
    "search_documentation",
    "api_request",
    
    # Helpers
    "get_web_tools",
    
    # Constantes
    "USER_AGENTS",
    "DEFAULT_TIMEOUT",
]
