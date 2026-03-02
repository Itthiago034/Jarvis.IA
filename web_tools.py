"""
Módulo de acesso à internet para o JARVIS.
Permite buscar informações na web, notícias e fazer pesquisas.

Usa DuckDuckGo (gratuito, sem API key) como backend principal.
"""

import asyncio
import aiohttp
import logging
import re
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus
from datetime import datetime

logger = logging.getLogger(__name__)

# ============== CONFIGURAÇÃO ==============

# User-Agent para requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Timeout para requests
REQUEST_TIMEOUT = 15

# ============== BUSCA WEB (DuckDuckGo) ==============

async def search_web(
    query: str,
    max_results: int = 5,
    region: str = "br-pt"
) -> Dict[str, Any]:
    """
    Busca informações na web usando DuckDuckGo.
    
    Args:
        query: Termo de busca
        max_results: Número máximo de resultados
        region: Região para resultados (br-pt = Brasil)
    
    Returns:
        Dict com success, results (lista de {title, url, snippet})
    """
    logger.info(f"Buscando na web: {query}")
    
    try:
        # DuckDuckGo HTML search (não requer API key)
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}&kl={region}"
        
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=REQUEST_TIMEOUT) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"Erro na busca: HTTP {response.status}",
                        "results": []
                    }
                
                html = await response.text()
        
        # Parse simples do HTML (sem BeautifulSoup para manter leve)
        results = _parse_duckduckgo_html(html, max_results)
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "source": "DuckDuckGo"
        }
        
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "Timeout na busca (conexão lenta)",
            "results": []
        }
    except Exception as e:
        logger.error(f"Erro na busca web: {e}")
        return {
            "success": False,
            "error": str(e),
            "results": []
        }


def _parse_duckduckgo_html(html: str, max_results: int) -> List[Dict[str, str]]:
    """Parse básico do HTML do DuckDuckGo."""
    results = []
    
    # Padrão para extrair resultados
    # Cada resultado está em <div class="result">
    result_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
    snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+(?:<[^>]+>[^<]*</[^>]+>)*[^<]*)</a>'
    
    # Encontrar todos os links de resultado
    links = re.findall(result_pattern, html)
    snippets = re.findall(snippet_pattern, html)
    
    # Limpar snippets de tags HTML
    clean_snippets = []
    for snippet in snippets:
        clean = re.sub(r'<[^>]+>', '', snippet)
        clean = clean.strip()
        clean_snippets.append(clean)
    
    for i, (url, title) in enumerate(links[:max_results]):
        result = {
            "title": title.strip(),
            "url": url,
            "snippet": clean_snippets[i] if i < len(clean_snippets) else ""
        }
        results.append(result)
    
    return results


# ============== BUSCA DE NOTÍCIAS ==============

async def search_news(
    query: str = "",
    max_results: int = 5
) -> Dict[str, Any]:
    """
    Busca notícias recentes.
    
    Args:
        query: Termo de busca (vazio = notícias gerais do Brasil)
        max_results: Número máximo de resultados
    
    Returns:
        Dict com success, results
    """
    # Adicionar filtro de notícias
    search_query = f"{query} notícias" if query else "notícias Brasil hoje"
    
    result = await search_web(search_query, max_results)
    result["type"] = "news"
    
    return result


# ============== BUSCA DE DEFINIÇÃO/RESPOSTA RÁPIDA ==============

async def quick_answer(query: str) -> Dict[str, Any]:
    """
    Tenta obter uma resposta rápida/definição usando DuckDuckGo Instant Answer API.
    
    Args:
        query: Pergunta ou termo
    
    Returns:
        Dict com success, answer, source
    """
    logger.info(f"Buscando resposta rápida: {query}")
    
    try:
        # DuckDuckGo Instant Answer API (gratuita)
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"
        
        headers = {"User-Agent": USER_AGENT}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=REQUEST_TIMEOUT) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "answer": None
                    }
                
                data = await response.json()
        
        # Verificar se há resposta instantânea
        abstract = data.get("Abstract", "")
        answer = data.get("Answer", "")
        definition = data.get("Definition", "")
        
        if answer:
            return {
                "success": True,
                "answer": answer,
                "source": data.get("AnswerType", "instant_answer"),
                "url": data.get("AbstractURL", "")
            }
        elif abstract:
            return {
                "success": True,
                "answer": abstract,
                "source": data.get("AbstractSource", ""),
                "url": data.get("AbstractURL", "")
            }
        elif definition:
            return {
                "success": True,
                "answer": definition,
                "source": "Wiktionary",
                "url": data.get("DefinitionURL", "")
            }
        else:
            # Sem resposta instantânea, fazer busca normal
            return {
                "success": False,
                "answer": None,
                "fallback": "use_search"
            }
            
    except Exception as e:
        logger.error(f"Erro na resposta rápida: {e}")
        return {
            "success": False,
            "error": str(e),
            "answer": None
        }


# ============== VERIFICAR CLIMA (SIMPLES) ==============

async def get_weather(city: str = "São Paulo") -> Dict[str, Any]:
    """
    Obtém previsão do tempo básica usando wttr.in (gratuito, sem API key).
    
    Args:
        city: Nome da cidade
    
    Returns:
        Dict com success, weather_info
    """
    logger.info(f"Buscando clima para: {city}")
    
    try:
        # wttr.in com formato JSON
        url = f"https://wttr.in/{quote_plus(city)}?format=j1"
        
        headers = {"User-Agent": USER_AGENT}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=REQUEST_TIMEOUT) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}"
                    }
                
                data = await response.json()
        
        current = data.get("current_condition", [{}])[0]
        weather_desc = current.get("lang_pt", [{}])
        
        return {
            "success": True,
            "city": city,
            "temperature": f"{current.get('temp_C', '?')}°C",
            "feels_like": f"{current.get('FeelsLikeC', '?')}°C",
            "humidity": f"{current.get('humidity', '?')}%",
            "description": weather_desc[0].get("value", current.get("weatherDesc", [{}])[0].get("value", "")) if weather_desc else current.get("weatherDesc", [{}])[0].get("value", ""),
            "wind": f"{current.get('windspeedKmph', '?')} km/h"
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar clima: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============== FORMATAR RESULTADOS ==============

def format_search_results(results: Dict[str, Any]) -> str:
    """Formata resultados de busca para exibição."""
    if not results.get("success"):
        return f"❌ Erro na busca: {results.get('error', 'Desconhecido')}"
    
    if not results.get("results"):
        return "Nenhum resultado encontrado."
    
    output = [f"🔍 Resultados para: {results.get('query', '')}\n"]
    
    for i, r in enumerate(results["results"], 1):
        output.append(f"{i}. **{r['title']}**")
        if r.get("snippet"):
            output.append(f"   {r['snippet'][:150]}...")
        output.append(f"   🔗 {r['url']}\n")
    
    return "\n".join(output)


def format_weather(weather: Dict[str, Any]) -> str:
    """Formata informações do clima."""
    if not weather.get("success"):
        return f"❌ Erro ao buscar clima: {weather.get('error', 'Desconhecido')}"
    
    return (
        f"🌡️ Clima em {weather['city']}:\n"
        f"   Temperatura: {weather['temperature']} (sensação: {weather['feels_like']})\n"
        f"   Condição: {weather['description']}\n"
        f"   Umidade: {weather['humidity']}\n"
        f"   Vento: {weather['wind']}"
    )


# ============== TESTE ==============

if __name__ == "__main__":
    async def test():
        print("=== TESTE DE BUSCA WEB ===\n")
        
        # Teste busca
        result = await search_web("Python asyncio tutorial", max_results=3)
        print(format_search_results(result))
        
        print("\n=== TESTE RESPOSTA RÁPIDA ===\n")
        
        # Teste resposta rápida
        answer = await quick_answer("população do Brasil")
        if answer.get("success"):
            print(f"Resposta: {answer['answer']}")
            print(f"Fonte: {answer['source']}")
        else:
            print("Sem resposta instantânea")
        
        print("\n=== TESTE CLIMA ===\n")
        
        # Teste clima
        weather = await get_weather("São Paulo")
        print(format_weather(weather))
    
    asyncio.run(test())
