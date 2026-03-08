"""
JARVIS - Ferramentas do Agente de Voz
=====================================
Funções que o agente de voz pode executar para controlar o sistema.

Estas ferramentas são registradas como function tools no LiveKit Agent,
permitindo que o JARVIS execute ações reais no computador.

Autor: Thiago
Versão: 1.0.0
"""

import subprocess
import webbrowser
import logging
import os
import asyncio
import aiohttp
import re
import html
from pathlib import Path
from urllib.parse import quote_plus
from typing import Optional, List, Dict
import ctypes

logger = logging.getLogger(__name__)


# =============================================================================
# FUNÇÕES DE APLICATIVOS
# =============================================================================

async def open_application(app_name: str) -> str:
    """
    Abre um aplicativo no computador.
    
    Args:
        app_name: Nome do aplicativo (ex: "chrome", "vscode", "calculadora")
        
    Returns:
        Mensagem de confirmação ou erro
    """
    apps = {
        # Navegadores
        "chrome": "start chrome",
        "google chrome": "start chrome",
        "firefox": "start firefox",
        "edge": "start msedge",
        "navegador": "start msedge",
        
        # Desenvolvimento
        "vscode": "code",
        "vs code": "code",
        "visual studio code": "code",
        "terminal": "start wt",
        "powershell": "start powershell",
        "cmd": "start cmd",
        
        # Office
        "word": "start winword",
        "excel": "start excel",
        "powerpoint": "start powerpnt",
        "outlook": "start outlook",
        
        # Sistema
        "calculadora": "calc",
        "notepad": "notepad",
        "bloco de notas": "notepad",
        "explorador": "explorer",
        "explorer": "explorer",
        "arquivos": "explorer",
        "configurações": "start ms-settings:",
        
        # Comunicação
        "discord": "start discord:",
        "whatsapp": "start whatsapp:",
        "telegram": "start tg:",
        "teams": "start msteams:",
        "spotify": "start spotify:",
    }
    
    app_lower = app_name.lower().strip()
    
    # Busca exata
    command = apps.get(app_lower)
    
    # Busca parcial
    if not command:
        for key, cmd in apps.items():
            if key in app_lower or app_lower in key:
                command = cmd
                break
    
    if command:
        try:
            subprocess.Popen(command, shell=True)
            return f"Aplicativo '{app_name}' aberto com sucesso."
        except Exception as e:
            logger.error(f"Erro ao abrir {app_name}: {e}")
            return f"Erro ao abrir {app_name}: {str(e)}"
    else:
        return f"Aplicativo '{app_name}' não encontrado. Aplicativos disponíveis: chrome, vscode, calculadora, word, excel, terminal, discord, etc."


async def open_website(url_or_name: str) -> str:
    """
    Abre um site no navegador padrão.
    
    Args:
        url_or_name: URL ou nome do site (ex: "youtube", "github", "https://google.com")
        
    Returns:
        Mensagem de confirmação
    """
    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "netflix": "https://netflix.com",
        "prime video": "https://primevideo.com",
        "amazon prime": "https://primevideo.com",
        "crunchyroll": "https://crunchyroll.com",
        "twitter": "https://twitter.com",
        "x": "https://x.com",
        "instagram": "https://instagram.com",
        "facebook": "https://facebook.com",
        "linkedin": "https://linkedin.com",
        "reddit": "https://reddit.com",
        "twitch": "https://twitch.tv",
        "chatgpt": "https://chat.openai.com",
        "claude": "https://claude.ai",
        "youtube music": "https://music.youtube.com",
    }
    
    name_lower = url_or_name.lower().strip()
    
    #Verifica se é uma URL
    if name_lower.startswith(("http://", "https://", "www.")):
        url = url_or_name if url_or_name.startswith("http") else f"https://{url_or_name}"
    else:
        # Busca no dicionário de sites
        url = sites.get(name_lower)
        if not url:
            for key, site_url in sites.items():
                if key in name_lower or name_lower in key:
                    url = site_url
                    break
    
    if url:
        try:
            webbrowser.open(url)
            return f"Site '{url_or_name}' aberto no navegador."
        except Exception as e:
            logger.error(f"Erro ao abrir site: {e}")
            return f"Erro ao abrir site: {str(e)}"
    else:
        return f"Site '{url_or_name}' não reconhecido. Sites disponíveis: youtube, google, gmail, github, netflix, etc."


async def open_folder(folder_name: str) -> str:
    """
    Abre uma pasta no explorador de arquivos.
    
    Args:
        folder_name: Nome da pasta (ex: "downloads", "documentos", "desktop")
        
    Returns:
        Mensagem de confirmação
    """
    home = Path.home()
    folders = {
        "downloads": home / "Downloads",
        "documentos": home / "Documents",
        "documents": home / "Documents",
        "desktop": home / "Desktop",
        "área de trabalho": home / "Desktop",
        "imagens": home / "Pictures",
        "pictures": home / "Pictures",
        "videos": home / "Videos",
        "vídeos": home / "Videos",
        "música": home / "Music",
        "music": home / "Music",
    }
    
    folder_lower = folder_name.lower().strip()
    path = folders.get(folder_lower)
    
    if not path:
        # Busca parcial
        for key, folder_path in folders.items():
            if key in folder_lower or folder_lower in key:
                path = folder_path
                break
    
    if path and path.exists():
        try:
            subprocess.Popen(f'explorer "{path}"', shell=True)
            return f"Pasta '{folder_name}' aberta."
        except Exception as e:
            return f"Erro ao abrir pasta: {str(e)}"
    else:
        return f"Pasta '{folder_name}' não encontrada. Pastas disponíveis: downloads, documentos, desktop, imagens, videos, música."


# =============================================================================
# FUNÇÕES DE MÚSICA/YOUTUBE MUSIC
# =============================================================================

async def play_music(song_name: str, artist: str = "") -> str:
    """
    Busca e toca uma música no YouTube Music.
    
    Args:
        song_name: Nome da música
        artist: Nome do artista (opcional)
        
    Returns:
        Mensagem de confirmação
    """
    query = f"{song_name} {artist}".strip()
    encoded_query = quote_plus(query)
    url = f"https://music.youtube.com/search?q={encoded_query}"
    
    try:
        webbrowser.open(url)
        return f"Buscando '{query}' no YouTube Music."
    except Exception as e:
        logger.error(f"Erro ao buscar música: {e}")
        return f"Erro ao buscar música: {str(e)}"


async def search_youtube(query: str) -> str:
    """
    Faz uma busca no YouTube.
    
    Args:
        query: Termo de busca
        
    Returns:
        Mensagem de confirmação
    """
    encoded_query = quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    
    try:
        webbrowser.open(url)
        return f"Buscando '{query}' no YouTube."
    except Exception as e:
        return f"Erro ao buscar no YouTube: {str(e)}"


# Definir teclas de mídia do Windows
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_MUTE = 0xAD


def _press_key(key_code: int):
    """Pressiona uma tecla de mídia."""
    try:
        ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)  # Key down
        ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)  # Key up
        return True
    except Exception as e:
        logger.error(f"Erro ao pressionar tecla: {e}")
        return False


async def media_play_pause() -> str:
    """Pausa ou retoma a música/vídeo atual."""
    if _press_key(VK_MEDIA_PLAY_PAUSE):
        return "Play/Pause executado."
    return "Erro ao executar play/pause."


async def media_next() -> str:
    """Pula para a próxima música/vídeo."""
    if _press_key(VK_MEDIA_NEXT_TRACK):
        return "Próxima faixa."
    return "Erro ao pular faixa."


async def media_previous() -> str:
    """Volta para a música/vídeo anterior."""
    if _press_key(VK_MEDIA_PREV_TRACK):
        return "Faixa anterior."
    return "Erro ao voltar faixa."


async def volume_up() -> str:
    """Aumenta o volume do sistema."""
    for _ in range(5):  # Aumenta 5 níveis
        _press_key(VK_VOLUME_UP)
    return "Volume aumentado."


async def volume_down() -> str:
    """Diminui o volume do sistema."""
    for _ in range(5):  # Diminui 5 níveis
        _press_key(VK_VOLUME_DOWN)
    return "Volume diminuído."


async def volume_mute() -> str:
    """Muta ou desmuta o áudio do sistema."""
    if _press_key(VK_VOLUME_MUTE):
        return "Áudio mutado/desmutado."
    return "Erro ao mutar áudio."


# =============================================================================
# FUNÇÕES DE SISTEMA
# =============================================================================

async def get_system_info() -> str:
    """
    Retorna informações sobre o sistema (bateria, CPU, memória).
    
    Returns:
        Informações do sistema formatadas
    """
    try:
        import psutil
        
        info_parts = []
        
        # Bateria
        battery = psutil.sensors_battery()
        if battery:
            charging = "carregando" if battery.power_plugged else "na bateria"
            info_parts.append(f"Bateria: {battery.percent}% ({charging})")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.5)
        info_parts.append(f"CPU: {cpu_percent}%")
        
        # Memória
        memory = psutil.virtual_memory()
        mem_used_gb = memory.used / (1024 ** 3)
        mem_total_gb = memory.total / (1024 ** 3)
        info_parts.append(f"Memória: {mem_used_gb:.1f}GB / {mem_total_gb:.1f}GB ({memory.percent}%)")
        
        # Disco
        disk = psutil.disk_usage('/')
        disk_free_gb = disk.free / (1024 ** 3)
        info_parts.append(f"Disco livre: {disk_free_gb:.1f}GB")
        
        return " | ".join(info_parts)
        
    except ImportError:
        return "psutil não instalado. Execute: pip install psutil"
    except Exception as e:
        return f"Erro ao obter informações do sistema: {str(e)}"


async def run_terminal_command(command: str) -> str:
    """
    Executa um comando no terminal (PowerShell).
    ATENÇÃO: Apenas comandos seguros são permitidos.
    
    Args:
        command: Comando a executar
        
    Returns:
        Saída do comando ou mensagem de erro
    """
    # Lista de comandos/prefixos permitidos
    safe_prefixes = [
        "dir", "ls", "type", "cat", "echo", "date", "time",
        "python --version", "pip list", "pip show",
        "git status", "git log", "git branch",
        "ipconfig", "hostname", "whoami",
        "systeminfo", "tasklist",
    ]
    
    # Comandos bloqueados
    blocked = [
        "rm", "del", "rmdir", "format", "shutdown", "restart",
        "reg", "regedit", "net user", "net localgroup",
        "powershell -c", "cmd /c", "start /b",
    ]
    
    cmd_lower = command.lower().strip()
    
    # Verifica bloqueios
    for b in blocked:
        if b in cmd_lower:
            return f"Comando '{command}' bloqueado por segurança."
    
    # Verifica se é permitido
    is_safe = any(cmd_lower.startswith(p) for p in safe_prefixes)
    
    if not is_safe:
        return f"Comando '{command}' não está na lista de permitidos. Comandos seguros: dir, ls, git status, pip list, etc."
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout or result.stderr or "Comando executado sem saída."
        # Limita saída
        if len(output) > 500:
            output = output[:500] + "... (saída truncada)"
        return output
    except subprocess.TimeoutExpired:
        return "Comando excedeu o tempo limite de 30 segundos."
    except Exception as e:
        return f"Erro ao executar comando: {str(e)}"


# =============================================================================
# FUNÇÕES DE BUSCA WEB
# =============================================================================

async def search_web_info(query: str) -> str:
    """
    Busca informações na web e retorna os resultados em texto.
    NÃO abre o navegador - retorna as informações diretamente.
    
    Use para: notícias, informações sobre pessoas, eventos, preços, etc.
    
    Args:
        query: O que buscar (ex: "últimas notícias sobre Bitcoin")
        
    Returns:
        Resumo dos resultados encontrados em texto
    """
    logger.info(f"🔍 Buscando na web: {query}")
    results = []
    
    try:
        async with aiohttp.ClientSession() as session:
            # 1. Tentar DuckDuckGo Instant Answer API primeiro
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            }
            
            try:
                async with session.get(
                    "https://api.duckduckgo.com/",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Resposta principal (Abstract)
                        if data.get("Abstract"):
                            results.append({
                                "title": data.get("Heading", "Resultado"),
                                "snippet": data.get("Abstract", ""),
                                "source": data.get("AbstractSource", "DuckDuckGo")
                            })
                        
                        # Tópicos relacionados
                        for topic in data.get("RelatedTopics", [])[:5]:
                            if isinstance(topic, dict) and topic.get("Text"):
                                results.append({
                                    "title": topic.get("Text", "")[:80],
                                    "snippet": topic.get("Text", ""),
                                    "source": "DuckDuckGo"
                                })
                            elif isinstance(topic, dict) and topic.get("Topics"):
                                for sub in topic.get("Topics", [])[:2]:
                                    if sub.get("Text"):
                                        results.append({
                                            "title": sub.get("Text", "")[:80],
                                            "snippet": sub.get("Text", ""),
                                            "source": "DuckDuckGo"
                                        })
            except Exception as e:
                logger.warning(f"DuckDuckGo API error: {e}")
            
            # 2. Se poucos resultados, fazer scraping do HTML do DuckDuckGo
            if len(results) < 3:
                try:
                    html_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
                    async with session.get(
                        html_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=15)
                    ) as resp:
                        if resp.status == 200:
                            html_content = await resp.text()
                            
                            # Parse simples dos resultados
                            result_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
                            snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+)</a>'
                            
                            links = re.findall(result_pattern, html_content)
                            snippets = re.findall(snippet_pattern, html_content)
                            
                            for i, (url, title) in enumerate(links[:5]):
                                snippet = snippets[i] if i < len(snippets) else ""
                                results.append({
                                    "title": html.unescape(title),
                                    "snippet": html.unescape(snippet),
                                    "source": "Web"
                                })
                except Exception as e:
                    logger.warning(f"DuckDuckGo HTML scrape error: {e}")
        
        # Formatar resultados para resposta por voz
        if results:
            response_parts = [f"Encontrei informações sobre '{query}':"]
            for i, result in enumerate(results[:5], 1):
                snippet = result.get('snippet', '')
                if snippet:
                    # Limitar tamanho do snippet
                    if len(snippet) > 200:
                        snippet = snippet[:200] + "..."
                    response_parts.append(f"\n{i}. {snippet}")
            
            return "\n".join(response_parts)
        else:
            return f"Não encontrei informações específicas sobre '{query}'. Quer que eu abra uma busca no navegador?"
            
    except Exception as e:
        logger.error(f"Erro na busca web: {e}")
        return f"Ocorreu um erro ao buscar '{query}'. Tente novamente."


async def open_browser_search(query: str) -> str:
    """
    Abre o navegador com uma busca no Google.
    Use APENAS quando o usuário pedir explicitamente para ABRIR no navegador.
    
    Args:
        query: Termo de busca
        
    Returns:
        Mensagem de confirmação
    """
    encoded_query = quote_plus(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    
    try:
        webbrowser.open(url)
        return f"Busca por '{query}' aberta no navegador."
    except Exception as e:
        logger.error(f"Erro ao abrir busca no navegador: {e}")
        return f"Erro ao abrir navegador: {str(e)}"


# =============================================================================
# REGISTRO DE FERRAMENTAS PARA LIVEKIT
# =============================================================================

def get_voice_tools():
    """
    Retorna a lista de ferramentas para registrar no agente LiveKit.
    
    Formato esperado pelo Google Realtime API com function calling.
    """
    return {
        "open_application": open_application,
        "open_website": open_website,
        "open_folder": open_folder,
        "play_music": play_music,
        "search_youtube": search_youtube,
        "media_play_pause": media_play_pause,
        "media_next": media_next,
        "media_previous": media_previous,
        "volume_up": volume_up,
        "volume_down": volume_down,
        "volume_mute": volume_mute,
        "get_system_info": get_system_info,
        "run_terminal_command": run_terminal_command,
        "search_web_info": search_web_info,
        "open_browser_search": open_browser_search,
    }


# Schemas para o Google Realtime API
TOOL_DECLARATIONS = [
    {
        "name": "open_application",
        "description": "Abre um aplicativo no computador. Use para abrir Chrome, VS Code, Word, Excel, calculadora, terminal, Discord, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "Nome do aplicativo a abrir (ex: 'chrome', 'vscode', 'calculadora', 'word')"
                }
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "open_website",
        "description": "Abre um site no navegador padrão. Use para abrir YouTube, Google, Gmail, GitHub, Netflix, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "url_or_name": {
                    "type": "string",
                    "description": "Nome do site ou URL (ex: 'youtube', 'github', 'https://google.com')"
                }
            },
            "required": ["url_or_name"]
        }
    },
    {
        "name": "open_folder",
        "description": "Abre uma pasta no explorador de arquivos.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_name": {
                    "type": "string",
                    "description": "Nome da pasta (ex: 'downloads', 'documentos', 'desktop')"
                }
            },
            "required": ["folder_name"]
        }
    },
    {
        "name": "play_music",
        "description": "Busca e toca uma música no YouTube Music.",
        "parameters": {
            "type": "object",
            "properties": {
                "song_name": {
                    "type": "string",
                    "description": "Nome da música"
                },
                "artist": {
                    "type": "string",
                    "description": "Nome do artista (opcional)"
                }
            },
            "required": ["song_name"]
        }
    },
    {
        "name": "search_youtube",
        "description": "Faz uma busca no YouTube.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termo de busca"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "media_play_pause",
        "description": "Pausa ou retoma a música/vídeo que está tocando. Use quando o usuário pedir para pausar ou continuar.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "media_next",
        "description": "Pula para a próxima música ou vídeo.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "media_previous",
        "description": "Volta para a música ou vídeo anterior.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "volume_up",
        "description": "Aumenta o volume do sistema.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "volume_down",
        "description": "Diminui o volume do sistema.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "volume_mute",
        "description": "Muta ou desmuta o áudio do sistema.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_system_info",
        "description": "Retorna informações sobre o sistema: bateria, CPU, memória RAM, espaço em disco.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "run_terminal_command",
        "description": "Executa um comando seguro no terminal. Apenas comandos de leitura são permitidos.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Comando a executar (ex: 'git status', 'pip list', 'dir')"
                }
            },
            "required": ["command"]
        }
    },
]
