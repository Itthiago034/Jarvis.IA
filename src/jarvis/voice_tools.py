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
# FUNÇÕES DE ANÁLISE DE CÓDIGO (DELEGAÇÃO PARA CODEAGENT)
# =============================================================================

async def read_code_file(file_path: str, start_line: int = None, end_line: int = None) -> str:
    """
    Lê o conteúdo de um arquivo de código.
    Esta ferramenta NÃO usa terminal - lê diretamente do sistema de arquivos.
    
    Use para: ver código, analisar scripts, verificar configurações.
    
    Args:
        file_path: Caminho do arquivo (absoluto ou relativo ao projeto JARVIS)
        start_line: Linha inicial (opcional, 1-indexed)
        end_line: Linha final (opcional, 1-indexed)
        
    Returns:
        Conteúdo do arquivo ou mensagem de erro
    """
    logger.info(f"📖 Lendo arquivo: {file_path}")
    
    try:
        # Resolução de caminho
        path = Path(file_path)
        if not path.is_absolute():
            # Tenta resolver relativo ao projeto JARVIS
            project_root = Path(__file__).parent.parent.parent
            path = project_root / file_path
        
        if not path.exists():
            return f"Arquivo não encontrado: {file_path}. Verifique se o caminho está correto."
        
        if not path.is_file():
            return f"'{file_path}' não é um arquivo válido."
        
        # Lê o arquivo
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        # Aplica range de linhas se especificado
        total_lines = len(lines)
        if start_line is not None or end_line is not None:
            start_idx = (start_line - 1) if start_line and start_line > 0 else 0
            end_idx = end_line if end_line else total_lines
            lines = lines[start_idx:end_idx]
        
        content = ''.join(lines)
        
        # Limita tamanho para resposta por voz
        if len(content) > 3000:
            content = content[:3000] + f"\n\n... (arquivo truncado - total: {total_lines} linhas)"
        
        return f"Conteúdo de {path.name} ({total_lines} linhas):\n\n{content}"
        
    except PermissionError:
        return f"Sem permissão para ler o arquivo: {file_path}"
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        return f"Erro ao ler arquivo: {str(e)}"


async def analyze_code_file(file_path: str, issue_description: str = "") -> str:
    """
    Analisa um arquivo de código e identifica problemas.
    Esta ferramenta NÃO usa terminal - faz análise estática do código.
    
    Use para: encontrar erros, bugs, problemas de sintaxe, sugerir correções.
    
    Args:
        file_path: Caminho do arquivo a analisar
        issue_description: Descrição do problema (opcional - ajuda na análise)
        
    Returns:
        Análise do código com problemas encontrados e sugestões
    """
    logger.info(f"🔍 Analisando código: {file_path}")
    
    try:
        # Primeiro, lê o arquivo
        path = Path(file_path)
        if not path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            path = project_root / file_path
        
        if not path.exists():
            return f"Arquivo não encontrado: {file_path}"
        
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            lines = content.splitlines()
        
        analysis_parts = [f"📋 Análise de {path.name}"]
        problems = []
        
        # Detecta tipo de arquivo
        suffix = path.suffix.lower()
        
        # Análise específica para Python
        if suffix == '.py':
            import ast
            import py_compile
            
            # 1. Verifica erros de sintaxe
            try:
                ast.parse(content)
                analysis_parts.append("✅ Sintaxe Python: OK")
            except SyntaxError as e:
                problems.append(f"❌ Erro de sintaxe na linha {e.lineno}: {e.msg}")
                if e.lineno and e.lineno <= len(lines):
                    problems.append(f"   Código: {lines[e.lineno - 1].strip()}")
            
            # 2. Análise de imports
            try:
                tree = ast.parse(content)
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        imports.append(f"{node.module}")
                
                if imports:
                    analysis_parts.append(f"📦 Imports: {', '.join(imports[:10])}")
                    if len(imports) > 10:
                        analysis_parts.append(f"   ... e mais {len(imports) - 10} imports")
            except:
                pass
            
            # 3. Análise de funções/classes
            try:
                tree = ast.parse(content)
                functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                
                if classes:
                    analysis_parts.append(f"🏗️ Classes: {', '.join(classes)}")
                if functions:
                    analysis_parts.append(f"⚙️ Funções: {', '.join(functions[:10])}")
                    if len(functions) > 10:
                        analysis_parts.append(f"   ... e mais {len(functions) - 10} funções")
            except:
                pass
            
            # 4. Padrões problemáticos comuns
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # except genérico
                if line_stripped.startswith('except:') or line_stripped == 'except Exception:':
                    problems.append(f"⚠️ Linha {i}: except genérico - considere capturar exceções específicas")
                
                # print debug
                if line_stripped.startswith('print(') and 'debug' in line_stripped.lower():
                    problems.append(f"⚠️ Linha {i}: possível print de debug")
                
                # TODO/FIXME
                if 'TODO' in line or 'FIXME' in line:
                    problems.append(f"📝 Linha {i}: {line_stripped[:60]}")
        
        # Análise para JavaScript/TypeScript
        elif suffix in ['.js', '.ts', '.jsx', '.tsx']:
            # Verifica padrões comuns
            for i, line in enumerate(lines, 1):
                if 'console.log' in line:
                    problems.append(f"⚠️ Linha {i}: console.log encontrado")
                if 'var ' in line:
                    problems.append(f"⚠️ Linha {i}: uso de 'var' - prefira 'let' ou 'const'")
        
        # Estatísticas gerais
        analysis_parts.append(f"\n📊 Estatísticas:")
        analysis_parts.append(f"   - Total de linhas: {len(lines)}")
        analysis_parts.append(f"   - Linhas em branco: {sum(1 for l in lines if not l.strip())}")
        analysis_parts.append(f"   - Linhas de código: {sum(1 for l in lines if l.strip() and not l.strip().startswith('#'))}")
        
        # Problemas encontrados
        if problems:
            analysis_parts.append(f"\n🔴 Problemas encontrados ({len(problems)}):")
            for p in problems[:10]:
                analysis_parts.append(f"   {p}")
            if len(problems) > 10:
                analysis_parts.append(f"   ... e mais {len(problems) - 10} problemas")
        else:
            analysis_parts.append("\n✅ Nenhum problema óbvio encontrado")
        
        # Se foi passada descrição do problema, adiciona contexto
        if issue_description:
            analysis_parts.append(f"\n🎯 Sobre o problema reportado: '{issue_description}'")
            analysis_parts.append("   Recomendo verificar as linhas relacionadas ao erro mencionado.")
        
        return "\n".join(analysis_parts)
        
    except Exception as e:
        logger.error(f"Erro na análise: {e}")
        return f"Erro ao analisar arquivo: {str(e)}"


async def list_project_files(folder_path: str = "", pattern: str = "*.py") -> str:
    """
    Lista arquivos de um diretório do projeto.
    Esta ferramenta NÃO usa terminal - lê diretamente do sistema de arquivos.
    
    Use para: ver estrutura do projeto, encontrar arquivos.
    
    Args:
        folder_path: Caminho da pasta (vazio = raiz do projeto)
        pattern: Padrão de arquivos (ex: "*.py", "*.js", "*")
        
    Returns:
        Lista de arquivos encontrados
    """
    logger.info(f"📂 Listando arquivos: {folder_path or 'projeto'}")
    
    try:
        project_root = Path(__file__).parent.parent.parent
        
        if folder_path:
            path = Path(folder_path)
            if not path.is_absolute():
                path = project_root / folder_path
        else:
            path = project_root
        
        if not path.exists():
            return f"Pasta não encontrada: {folder_path}"
        
        if not path.is_dir():
            return f"'{folder_path}' não é uma pasta válida"
        
        # Lista arquivos com o padrão
        files = list(path.glob(pattern))
        
        # Também lista subpastas
        folders = [f for f in path.iterdir() if f.is_dir() and not f.name.startswith('.') and f.name not in ['__pycache__', 'venv', 'node_modules', '.git']]
        
        result_parts = [f"📁 Conteúdo de {path.name}/"]
        
        if folders:
            result_parts.append(f"\n📂 Pastas ({len(folders)}):")
            for f in sorted(folders)[:15]:
                result_parts.append(f"   📁 {f.name}/")
            if len(folders) > 15:
                result_parts.append(f"   ... e mais {len(folders) - 15} pastas")
        
        if files:
            result_parts.append(f"\n📄 Arquivos '{pattern}' ({len(files)}):")
            for f in sorted(files)[:20]:
                size = f.stat().st_size
                size_str = f"{size}B" if size < 1024 else f"{size/1024:.1f}KB"
                result_parts.append(f"   📄 {f.name} ({size_str})")
            if len(files) > 20:
                result_parts.append(f"   ... e mais {len(files) - 20} arquivos")
        
        if not folders and not files:
            result_parts.append("   (pasta vazia ou sem arquivos correspondentes)")
        
        return "\n".join(result_parts)
        
    except Exception as e:
        logger.error(f"Erro ao listar: {e}")
        return f"Erro ao listar arquivos: {str(e)}"


async def write_code_file(file_path: str, content: str, create_dirs: bool = True) -> str:
    """
    Cria ou sobrescreve um arquivo com o conteúdo especificado.
    Esta ferramenta NÃO usa terminal - escreve diretamente no sistema de arquivos.
    
    Use para: criar arquivos .md, .py, .txt, configs, salvar código refatorado.
    
    Args:
        file_path: Caminho do arquivo (absoluto ou relativo ao projeto)
        content: Conteúdo completo a ser escrito no arquivo
        create_dirs: Se True, cria os diretórios pais se não existirem
        
    Returns:
        Mensagem de confirmação ou erro
    """
    logger.info(f"📝 Escrevendo arquivo: {file_path}")
    
    try:
        path = Path(file_path)
        if not path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            path = project_root / file_path
        
        # Cria diretórios pais se necessário
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Escreve o arquivo
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = path.stat().st_size
        size_str = f"{file_size}B" if file_size < 1024 else f"{file_size/1024:.1f}KB"
        
        return f"✅ Arquivo '{path.name}' salvo com sucesso ({size_str}, {len(content.splitlines())} linhas)"
        
    except PermissionError:
        return f"❌ Sem permissão para escrever em: {file_path}"
    except Exception as e:
        logger.error(f"Erro ao escrever arquivo: {e}")
        return f"❌ Erro ao escrever arquivo: {str(e)}"


async def append_to_file(file_path: str, content: str) -> str:
    """
    Adiciona conteúdo ao final de um arquivo existente.
    Esta ferramenta NÃO usa terminal.
    
    Use para: adicionar notas, logs, conteúdo extra sem sobrescrever.
    
    Args:
        file_path: Caminho do arquivo
        content: Conteúdo a adicionar ao final
        
    Returns:
        Mensagem de confirmação ou erro
    """
    logger.info(f"📎 Adicionando conteúdo a: {file_path}")
    
    try:
        path = Path(file_path)
        if not path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            path = project_root / file_path
        
        if not path.exists():
            return f"❌ Arquivo não encontrado: {file_path}. Use write_code_file para criar."
        
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        return f"✅ Conteúdo adicionado a '{path.name}'"
        
    except Exception as e:
        logger.error(f"Erro ao adicionar conteúdo: {e}")
        return f"❌ Erro: {str(e)}"


async def refactor_code(file_path: str, old_code: str, new_code: str) -> str:
    """
    Substitui um trecho de código por outro em um arquivo.
    Esta ferramenta NÃO usa terminal - edita diretamente o arquivo.
    
    Use para: corrigir erros, refatorar funções, atualizar código.
    
    Args:
        file_path: Caminho do arquivo a editar
        old_code: Código exato a ser substituído (deve existir no arquivo)
        new_code: Novo código que substituirá o antigo
        
    Returns:
        Mensagem de confirmação ou erro
    """
    logger.info(f"🔧 Refatorando código em: {file_path}")
    
    try:
        path = Path(file_path)
        if not path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            path = project_root / file_path
        
        if not path.exists():
            return f"❌ Arquivo não encontrado: {file_path}"
        
        # Lê o arquivo
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Verifica se o código antigo existe
        if old_code not in content:
            # Tenta encontrar algo similar
            old_lines = old_code.strip().splitlines()
            if old_lines:
                first_line = old_lines[0].strip()
                if first_line in content:
                    return f"❌ Código não encontrado exatamente. Encontrei linha similar: '{first_line[:50]}...'. Verifique espaços/indentação."
            return f"❌ Código a substituir não encontrado no arquivo. Verifique se copiou exatamente."
        
        # Conta ocorrências
        occurrences = content.count(old_code)
        if occurrences > 1:
            return f"⚠️ Encontrei {occurrences} ocorrências do código. Seja mais específico para evitar substituições erradas."
        
        # Substitui
        new_content = content.replace(old_code, new_code, 1)
        
        # Escreve de volta
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        lines_removed = len(old_code.splitlines())
        lines_added = len(new_code.splitlines())
        
        return f"✅ Código refatorado em '{path.name}' (-{lines_removed} +{lines_added} linhas)"
        
    except Exception as e:
        logger.error(f"Erro na refatoração: {e}")
        return f"❌ Erro na refatoração: {str(e)}"


async def create_markdown_doc(file_path: str, title: str, content: str, add_toc: bool = False) -> str:
    """
    Cria um documento Markdown formatado.
    Esta ferramenta NÃO usa terminal.
    
    Use para: criar documentação, READMEs, guias, notas.
    
    Args:
        file_path: Caminho do arquivo .md a criar
        title: Título principal do documento
        content: Conteúdo do documento (pode incluir markdown)
        add_toc: Se True, adiciona índice automático
        
    Returns:
        Mensagem de confirmação
    """
    logger.info(f"📄 Criando documento MD: {file_path}")
    
    try:
        path = Path(file_path)
        if not path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            path = project_root / file_path
        
        # Garante extensão .md
        if path.suffix.lower() != '.md':
            path = path.with_suffix('.md')
        
        # Cria diretórios se necessário
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Monta o documento
        doc_parts = [f"# {title}\n"]
        
        # Adiciona metadata
        from datetime import datetime
        doc_parts.append(f"> Criado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        
        # Adiciona TOC se solicitado
        if add_toc:
            doc_parts.append("## 📋 Índice\n")
            # Extrai headers do conteúdo
            for line in content.splitlines():
                if line.startswith('## '):
                    header = line[3:].strip()
                    anchor = header.lower().replace(' ', '-').replace(':', '')
                    doc_parts.append(f"- [{header}](#{anchor})")
            doc_parts.append("\n---\n")
        
        # Adiciona conteúdo
        doc_parts.append(content)
        
        # Escreve arquivo
        full_content = "\n".join(doc_parts)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return f"✅ Documento '{path.name}' criado com sucesso ({len(content.splitlines())} linhas)"
        
    except Exception as e:
        logger.error(f"Erro ao criar documento: {e}")
        return f"❌ Erro ao criar documento: {str(e)}"


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
        # Ferramentas de análise de código
        "read_code_file": read_code_file,
        "analyze_code_file": analyze_code_file,
        "list_project_files": list_project_files,
        # Ferramentas de escrita/edição de arquivos
        "write_code_file": write_code_file,
        "append_to_file": append_to_file,
        "refactor_code": refactor_code,
        "create_markdown_doc": create_markdown_doc,
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
