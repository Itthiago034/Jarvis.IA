"""
JARVIS - Web Research Tools
===========================
Ferramentas para pesquisa na web, documentação e Stack Overflow.
"""

import os
import re
import json
import asyncio
from typing import Optional, List, Dict, Any
from urllib.parse import quote_plus
import aiohttp  # type: ignore[reportMissingImports]
from bs4 import BeautifulSoup  # type: ignore[reportMissingImports]


class WebResearchTools:
    """Ferramentas de pesquisa na web"""
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria sessão HTTP"""
        if self._session is None or self._session.closed:
            headers = {"User-Agent": self.user_agent}
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session
    
    async def close(self):
        """Fecha a sessão"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    # ==================== STACK OVERFLOW ====================
    
    async def search_stackoverflow(self, query: str, tags: Optional[List[str]] = None) -> List[Dict]:
        """Busca no Stack Overflow"""
        session = await self._get_session()
        
        params = {
            "order": "desc",
            "sort": "relevance",
            "intitle": query,
            "site": "stackoverflow",
            "filter": "withbody",
            "pagesize": 10
        }
        if tags:
            params["tagged"] = ";".join(tags)
        
        try:
            async with session.get(
                "https://api.stackexchange.com/2.3/search/advanced",
                params=params
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("items", [])
        except Exception as e:
            print(f"Erro ao buscar Stack Overflow: {e}")
        return []
    
    async def get_stackoverflow_answers(self, question_id: int) -> List[Dict]:
        """Obtém respostas de uma pergunta do Stack Overflow"""
        session = await self._get_session()
        
        params = {
            "order": "desc",
            "sort": "votes",
            "site": "stackoverflow",
            "filter": "withbody"
        }
        
        try:
            async with session.get(
                f"https://api.stackexchange.com/2.3/questions/{question_id}/answers",
                params=params
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("items", [])
        except Exception:
            pass
        return []
    
    # ==================== DOCUMENTAÇÃO ====================
    
    async def search_python_docs(self, query: str) -> str:
        """Busca na documentação do Python"""
        session = await self._get_session()
        search_url = f"https://docs.python.org/3/search.html?q={quote_plus(query)}"
        
        try:
            # Usar a API de busca do Read the Docs
            async with session.get(
                "https://readthedocs.org/api/v2/search/",
                params={"q": f"project:python {query}", "page_size": 5}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results", [])
                    if results:
                        output = [f"📚 Documentação Python para '{query}':\n"]
                        for r in results[:5]:
                            output.append(f"  • {r.get('title', 'Sem título')}")
                            output.append(f"    {r.get('link', '')}\n")
                        return "\n".join(output)
        except Exception:
            pass
        
        return f"Busque manualmente em: {search_url}"
    
    async def search_mdn_docs(self, query: str) -> str:
        """Busca no MDN Web Docs (JavaScript, CSS, HTML)"""
        session = await self._get_session()
        
        try:
            async with session.get(
                "https://developer.mozilla.org/api/v1/search",
                params={"q": query, "locale": "pt-BR"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    documents = data.get("documents", [])
                    if documents:
                        output = [f"📚 MDN Docs para '{query}':\n"]
                        for doc in documents[:5]:
                            output.append(f"  • {doc.get('title', '')}")
                            output.append(f"    https://developer.mozilla.org{doc.get('mdn_url', '')}\n")
                        return "\n".join(output)
        except Exception:
            pass
        
        return f"Busque em: https://developer.mozilla.org/search?q={quote_plus(query)}"
    
    # ==================== BUSCA GERAL ====================
    
    async def search_duckduckgo(self, query: str) -> List[Dict]:
        """Busca no DuckDuckGo (sem tracking)"""
        session = await self._get_session()
        
        try:
            # Usar a API instant answer do DuckDuckGo
            async with session.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = []
                    
                    # Abstract (resposta direta)
                    if data.get("Abstract"):
                        results.append({
                            "title": data.get("Heading", "Resultado"),
                            "snippet": data.get("Abstract"),
                            "url": data.get("AbstractURL", "")
                        })
                    
                    # Related topics
                    for topic in data.get("RelatedTopics", [])[:5]:
                        if isinstance(topic, dict) and "Text" in topic:
                            results.append({
                                "title": topic.get("Text", "")[:50],
                                "snippet": topic.get("Text", ""),
                                "url": topic.get("FirstURL", "")
                            })
                    
                    return results
        except Exception:
            pass
        return []
    
    async def fetch_webpage(self, url: str, extract_text: bool = True) -> str:
        """Busca conteúdo de uma página web"""
        session = await self._get_session()
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    
                    if extract_text:
                        soup = BeautifulSoup(html, "html.parser")
                        
                        # Remover scripts, estilos, etc
                        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                            tag.decompose()
                        
                        # Extrair texto principal
                        main_content = soup.find("main") or soup.find("article") or soup.find("body")
                        if main_content:
                            text = main_content.get_text(separator="\n", strip=True)
                            # Limitar tamanho
                            if len(text) > 8000:
                                text = text[:8000] + "\n\n... [conteúdo truncado]"
                            return text
                    
                    return html[:10000]
        except Exception as e:
            return f"Erro ao acessar {url}: {e}"
        
        return f"Não foi possível acessar: {url}"
    
    # ==================== PACKAGE REGISTRIES ====================
    
    async def search_npm(self, package_name: str) -> Dict:
        """Busca pacote no npm"""
        session = await self._get_session()
        
        try:
            async with session.get(f"https://registry.npmjs.org/{package_name}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    latest = data.get("dist-tags", {}).get("latest", "")
                    latest_info = data.get("versions", {}).get(latest, {})
                    
                    return {
                        "name": data.get("name"),
                        "description": data.get("description"),
                        "version": latest,
                        "homepage": latest_info.get("homepage"),
                        "repository": data.get("repository", {}).get("url"),
                        "keywords": data.get("keywords", []),
                        "url": f"https://www.npmjs.com/package/{package_name}"
                    }
        except Exception:
            pass
        return {}
    
    async def search_pypi(self, package_name: str) -> Dict:
        """Busca pacote no PyPI"""
        session = await self._get_session()
        
        try:
            async with session.get(f"https://pypi.org/pypi/{package_name}/json") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    info = data.get("info", {})
                    
                    return {
                        "name": info.get("name"),
                        "description": info.get("summary"),
                        "version": info.get("version"),
                        "homepage": info.get("home_page") or info.get("project_url"),
                        "author": info.get("author"),
                        "license": info.get("license"),
                        "requires_python": info.get("requires_python"),
                        "url": f"https://pypi.org/project/{package_name}/"
                    }
        except Exception:
            pass
        return {}


# ==================== FUNÇÕES DE FERRAMENTA PARA O AGENTE ====================

def get_research_tools():
    """Retorna as ferramentas de pesquisa para o CodeAgent"""
    research = WebResearchTools()
    
    async def search_stackoverflow(query: str, tags: str = "") -> str:
        """
        Busca soluções no Stack Overflow.
        
        Args:
            query: Pergunta ou problema a buscar
            tags: Tags separadas por vírgula (ex: "python,django")
        
        Returns:
            Perguntas e respostas relevantes
        """
        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
        questions = await research.search_stackoverflow(query, tag_list)
        
        if not questions:
            return f"Nenhum resultado no Stack Overflow para: {query}"
        
        results = [f"🔍 Stack Overflow - '{query}':\n"]
        
        for q in questions[:5]:
            score = q.get("score", 0)
            answers = q.get("answer_count", 0)
            accepted = "✅" if q.get("is_answered") else ""
            
            results.append(
                f"📌 {q.get('title', 'Sem título')} {accepted}\n"
                f"   Score: {score} | Respostas: {answers}\n"
                f"   {q.get('link', '')}\n"
            )
            
            # Incluir preview do body se disponível
            body = q.get("body", "")
            if body:
                # Remover HTML tags
                clean_body = re.sub(r'<[^>]+>', '', body)[:300]
                results.append(f"   Preview: {clean_body}...\n")
        
        return "\n".join(results)
    
    async def get_stackoverflow_solution(question_id: int) -> str:
        """
        Obtém a melhor resposta de uma pergunta do Stack Overflow.
        
        Args:
            question_id: ID da pergunta (número na URL)
        
        Returns:
            Resposta mais votada formatada
        """
        answers = await research.get_stackoverflow_answers(question_id)
        
        if not answers:
            return f"Nenhuma resposta encontrada para a pergunta {question_id}"
        
        # Pegar a mais votada
        best = answers[0]
        score = best.get("score", 0)
        accepted = "✅ Aceita" if best.get("is_accepted") else ""
        body = best.get("body", "")
        
        # Limpar HTML
        clean_body = re.sub(r'<[^>]+>', '', body)
        
        return (
            f"💡 Melhor resposta (Score: {score}) {accepted}\n\n"
            f"{clean_body[:3000]}"
        )
    
    async def search_documentation(query: str, source: str = "auto") -> str:
        """
        Busca em documentações oficiais.
        
        Args:
            query: Termo a buscar
            source: Fonte ("python", "mdn", "npm", "pypi", "auto")
        
        Returns:
            Links e informações da documentação
        """
        if source == "auto":
            # Detectar automaticamente
            query_lower = query.lower()
            if any(kw in query_lower for kw in ["javascript", "js", "css", "html", "dom", "fetch"]):
                source = "mdn"
            elif any(kw in query_lower for kw in ["react", "vue", "node", "express", "npm"]):
                source = "npm"
            else:
                source = "python"
        
        if source == "python":
            return await research.search_python_docs(query)
        elif source == "mdn":
            return await research.search_mdn_docs(query)
        elif source == "npm":
            pkg = await research.search_npm(query)
            if pkg:
                return (
                    f"📦 {pkg.get('name', query)} v{pkg.get('version', '?')}\n"
                    f"   {pkg.get('description', 'Sem descrição')}\n"
                    f"   URL: {pkg.get('url', '')}\n"
                    f"   Keywords: {', '.join(pkg.get('keywords', [])[:5])}"
                )
            return f"Pacote '{query}' não encontrado no npm"
        elif source == "pypi":
            pkg = await research.search_pypi(query)
            if pkg:
                return (
                    f"📦 {pkg.get('name', query)} v{pkg.get('version', '?')}\n"
                    f"   {pkg.get('description', 'Sem descrição')}\n"
                    f"   Autor: {pkg.get('author', '?')}\n"
                    f"   Python: {pkg.get('requires_python', 'any')}\n"
                    f"   URL: {pkg.get('url', '')}"
                )
            return f"Pacote '{query}' não encontrado no PyPI"
        
        return f"Fonte '{source}' não reconhecida"
    
    async def web_search(query: str) -> str:
        """
        Faz uma busca geral na web.
        
        Args:
            query: Termo de busca
        
        Returns:
            Resultados encontrados
        """
        results = await research.search_duckduckgo(query)
        
        if not results:
            return f"Nenhum resultado para: {query}\nTente reformular a busca."
        
        output = [f"🌐 Resultados para '{query}':\n"]
        for r in results[:7]:
            output.append(f"• {r.get('title', 'Sem título')}")
            if r.get("snippet"):
                output.append(f"  {r['snippet'][:200]}")
            if r.get("url"):
                output.append(f"  🔗 {r['url']}\n")
        
        return "\n".join(output)
    
    async def fetch_url_content(url: str) -> str:
        """
        Busca e extrai o conteúdo de uma URL.
        
        Args:
            url: URL completa da página
        
        Returns:
            Texto extraído da página
        """
        content = await research.fetch_webpage(url)
        return content
    
    async def get_package_info(package_name: str, registry: str = "auto") -> str:
        """
        Obtém informações de um pacote.
        
        Args:
            package_name: Nome do pacote
            registry: Registro ("npm", "pypi", "auto")
        
        Returns:
            Informações do pacote
        """
        if registry == "auto":
            # Tentar PyPI primeiro, depois npm
            pkg = await research.search_pypi(package_name)
            if not pkg:
                pkg = await research.search_npm(package_name)
                registry = "npm"
            else:
                registry = "pypi"
        elif registry == "npm":
            pkg = await research.search_npm(package_name)
        else:
            pkg = await research.search_pypi(package_name)
        
        if not pkg:
            return f"Pacote '{package_name}' não encontrado"
        
        return (
            f"📦 **{pkg.get('name', package_name)}** ({registry})\n"
            f"   Versão: {pkg.get('version', '?')}\n"
            f"   {pkg.get('description', 'Sem descrição')}\n"
            f"   URL: {pkg.get('url', '')}"
        )
    
    return {
        "search_stackoverflow": search_stackoverflow,
        "get_stackoverflow_solution": get_stackoverflow_solution,
        "search_documentation": search_documentation,
        "web_search": web_search,
        "fetch_url_content": fetch_url_content,
        "get_package_info": get_package_info,
    }
