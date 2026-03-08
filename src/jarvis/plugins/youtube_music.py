"""
JARVIS - Plugin de YouTube Music
=================================
Controla o YouTube Music no Windows através de comandos de voz.
Funciona com app desktop ou navegador.

Autor: Thiago
Versão: 1.1.0
"""

import asyncio
import subprocess
import logging
import webbrowser
import re
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus
import ctypes

from .base import JarvisPlugin, PluginContext, PluginResponse, PluginPriority

logger = logging.getLogger(__name__)


class YouTubeMusicPlugin(JarvisPlugin):
    """
    Plugin de controle do YouTube Music.
    
    Funcionalidades:
    - Abrir o YouTube Music (app ou navegador)
    - Play/Pause
    - Próxima/Anterior música
    - Controle de volume
    - Abrir playlists específicas
    
    As teclas de mídia funcionam com o app ou navegador.
    """
    
    name = "YouTube Music"
    description = "Controla o YouTube Music: play, pause, buscar músicas"
    version = "1.1.0"
    author = "JARVIS Team"
    
    trigger_phrases = [
        # Abrir
        "abrir youtube music",
        "abre o youtube music",
        "abra o youtube music",
        "abrir yt music",
        "abre o yt music",
        "iniciar youtube music",
        
        # Buscar/Tocar músicas específicas
        "coloca a música",
        "coloca música",
        "toca a música",
        "tocar a música",
        "bota a música",
        "bota música",
        "põe a música",
        "colocar música",
        "buscar música",
        "pesquisar música",
        "quero ouvir",
        "quero escutar",
        "toca pra mim",
        "coloca pra mim",
        
        # Play/Pause (específico para YT Music)
        "tocar no youtube",
        "toca no youtube music",
        "play youtube music",
        "pausar youtube",
        "pause youtube music",
        
        # Navegação
        "próxima youtube",
        "pular youtube",
        "anterior youtube",
        "voltar youtube",
        
        # Playlists
        "minhas músicas",
        "minha playlist",
        "músicas curtidas",
        "mix pessoal",
        "supermix",
        "descobertas da semana",
        
        # Rádio
        "rádio youtube",
        "criar rádio"
    ]
    
    priority = PluginPriority.HIGH
    requires_internet = True
    
    # Virtual Key Codes para controle de mídia (Windows)
    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_VOLUME_UP = 0xAF
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_MUTE = 0xAD
    
    # URLs do YouTube Music
    YT_MUSIC_BASE = "https://music.youtube.com"
    YT_MUSIC_LIBRARY = "https://music.youtube.com/library"
    YT_MUSIC_LIKED = "https://music.youtube.com/playlist?list=LM"
    YT_MUSIC_SUPERMIX = "https://music.youtube.com/playlist?list=RDTMAK5uy_kset8DisdE7LSD4TNjEVvrKRTmG7a56sY"
    YT_MUSIC_SEARCH = "https://music.youtube.com/search?q="
    
    # Caminhos do app YouTube Music (se instalado via PWA ou Microsoft Store)
    YT_MUSIC_PATHS = [
        Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
    ]
    
    def __init__(self):
        super().__init__()
        self._browser_path: Optional[Path] = None
        self._use_app_mode = True  # Abrir em modo app (sem barra de endereço)
    
    async def initialize(self) -> bool:
        """Inicializa e localiza o navegador"""
        # Tenta encontrar o Chrome (melhor experiência com YT Music)
        for path in self.YT_MUSIC_PATHS:
            if path.exists():
                self._browser_path = path
                logger.info(f"Chrome encontrado em: {path}")
                break
        
        if not self._browser_path:
            logger.info("Chrome não encontrado. Usará navegador padrão.")
        
        return await super().initialize()
    
    def _press_media_key(self, vk_code: int) -> bool:
        """Simula pressionamento de tecla de mídia"""
        try:
            KEYEVENTF_EXTENDEDKEY = 0x0001
            KEYEVENTF_KEYUP = 0x0002
            
            ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
            ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            logger.error(f"Erro ao pressionar tecla de mídia: {e}")
            return False
    
    async def _open_youtube_music(self, url: str = None) -> bool:
        """Abre o YouTube Music"""
        target_url = url or self.YT_MUSIC_BASE
        
        try:
            if self._browser_path and self._use_app_mode:
                # Abre em modo app (PWA-like) - sem barra de navegação
                subprocess.Popen([
                    str(self._browser_path),
                    f"--app={target_url}",
                    "--new-window"
                ])
            else:
                # Usa navegador padrão
                webbrowser.open(target_url)
            
            await asyncio.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Erro ao abrir YouTube Music: {e}")
            return False
    
    def _is_browser_running(self) -> bool:
        """Verifica se o navegador está rodando"""
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
                capture_output=True,
                text=True
            )
            return "chrome.exe" in result.stdout
        except Exception:
            return False
    
    def _classify_command(self, text: str) -> tuple[str, Optional[str]]:
        """Classifica o comando e retorna (ação, url_opcional)"""
        text_lower = text.lower()
        
        # Playlists específicas
        if any(phrase in text_lower for phrase in ["curtidas", "liked", "favoritas"]):
            return ("open_url", self.YT_MUSIC_LIKED)
        
        if any(phrase in text_lower for phrase in ["supermix", "mix pessoal", "meu mix"]):
            return ("open_url", self.YT_MUSIC_SUPERMIX)
        
        if any(phrase in text_lower for phrase in ["biblioteca", "library", "minhas músicas"]):
            return ("open_url", self.YT_MUSIC_LIBRARY)
        
        # ===== BUSCAR MÚSICA ESPECÍFICA =====
        # Padrões para extrair nome da música
        search_patterns = [
            r"(?:coloca|toca|bota|põe|tocar|colocar|botar)\s+(?:a\s+)?(?:música\s+)?(.+?)(?:\s+no\s+youtube|\s+pra\s+mim)?$",
            r"(?:quero\s+ouvir|quero\s+escutar)\s+(.+?)$",
            r"(?:buscar|pesquisar|procurar)\s+(?:a\s+)?(?:música\s+)?(.+?)(?:\s+no\s+youtube)?$",
            r"(?:play|tocar)\s+(.+?)(?:\s+no\s+youtube)?$",
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                song_name = match.group(1).strip()
                # Limpar termos comuns que não são parte do nome
                song_name = re.sub(r"\s*(no youtube|no yt|music|pra mim|por favor|please)\s*", "", song_name, flags=re.IGNORECASE).strip()
                
                if song_name and len(song_name) > 2:
                    search_url = self.YT_MUSIC_SEARCH + quote_plus(song_name)
                    return ("search", search_url)
        
        # Abrir (sem busca específica)
        if any(phrase in text_lower for phrase in ["abrir", "abre", "abra", "iniciar"]):
            if "youtube" in text_lower or "yt music" in text_lower:
                return ("open", None)
        
        # Play (sem busca - apenas dar play na música atual)
        if any(phrase in text_lower for phrase in ["tocar", "toca", "play", "continuar"]) and not any(phrase in text_lower for phrase in ["música", "musica"]):
            return ("play", None)
        
        # Pause
        if any(phrase in text_lower for phrase in ["pausar", "pause", "pausa", "para"]):
            return ("pause", None)
        
        # Próxima
        if any(phrase in text_lower for phrase in ["próxima", "proxima", "pular", "pula", "next"]):
            return ("next", None)
        
        # Anterior
        if any(phrase in text_lower for phrase in ["anterior", "voltar", "volta", "previous"]):
            return ("previous", None)
        
        # Volume
        if any(phrase in text_lower for phrase in ["aumentar", "subir", "mais alto"]):
            return ("volume_up", None)
        
        if any(phrase in text_lower for phrase in ["diminuir", "abaixa", "abaixar", "mais baixo"]):
            return ("volume_down", None)
        
        if any(phrase in text_lower for phrase in ["mutar", "mute", "silenciar"]):
            return ("mute", None)
        
        return ("toggle", None)
    
    async def execute(self, context: PluginContext) -> PluginResponse:
        """Executa o comando de controle do YouTube Music"""
        command, url = self._classify_command(context.user_message)
        
        logger.info(f"Comando YouTube Music: {command}")
        
        if command == "open":
            success = await self._open_youtube_music()
            if success:
                return PluginResponse(
                    message="Abrindo o YouTube Music para você.",
                    success=True
                )
            return PluginResponse.error("Não consegui abrir o YouTube Music.")
        
        elif command == "open_url":
            success = await self._open_youtube_music(url)
            if success:
                # Determinar nome da playlist
                playlist_name = "sua playlist"
                if "LM" in (url or ""):
                    playlist_name = "suas músicas curtidas"
                elif "RDTMAK" in (url or ""):
                    playlist_name = "seu Supermix"
                elif "library" in (url or ""):
                    playlist_name = "sua biblioteca"
                
                return PluginResponse(
                    message=f"Abrindo {playlist_name} no YouTube Music.",
                    success=True
                )
            return PluginResponse.error("Não consegui abrir a playlist.")
        
        elif command == "search":
            # Extrair nome da música da URL para exibir
            song_query = ""
            if url and "q=" in url:
                from urllib.parse import unquote_plus
                song_query = unquote_plus(url.split("q=")[1])
            
            success = await self._open_youtube_music(url)
            if success:
                return PluginResponse(
                    message=f"Buscando '{song_query}' no YouTube Music. Só clicar na música para tocar!",
                    success=True
                )
            return PluginResponse.error("Não consegui abrir a busca no YouTube Music.")
        
        elif command == "play" or command == "toggle":
            self._press_media_key(self.VK_MEDIA_PLAY_PAUSE)
            return PluginResponse(
                message="Tocando música no YouTube Music.",
                success=True
            )
        
        elif command == "pause":
            self._press_media_key(self.VK_MEDIA_PLAY_PAUSE)
            return PluginResponse(
                message="Música pausada.",
                success=True
            )
        
        elif command == "next":
            self._press_media_key(self.VK_MEDIA_NEXT_TRACK)
            return PluginResponse(
                message="Pulando para a próxima música.",
                success=True
            )
        
        elif command == "previous":
            self._press_media_key(self.VK_MEDIA_PREV_TRACK)
            return PluginResponse(
                message="Voltando para a música anterior.",
                success=True
            )
        
        elif command == "volume_up":
            for _ in range(5):
                self._press_media_key(self.VK_VOLUME_UP)
            return PluginResponse(
                message="Volume aumentado.",
                success=True
            )
        
        elif command == "volume_down":
            for _ in range(5):
                self._press_media_key(self.VK_VOLUME_DOWN)
            return PluginResponse(
                message="Volume diminuído.",
                success=True
            )
        
        elif command == "mute":
            self._press_media_key(self.VK_VOLUME_MUTE)
            return PluginResponse(
                message="Áudio mutado.",
                success=True
            )
        
        return PluginResponse(
            message="Comando de música executado.",
            success=True
        )


# Função para registro do plugin
def get_plugin():
    """Retorna instância do plugin"""
    return YouTubeMusicPlugin()
