"""
JARVIS - Plugin de Spotify
==========================
Controla o Spotify no Windows através de comandos de voz.
Usa controle local do app (não requer API OAuth).

Autor: Thiago
Versão: 1.0.0
"""

import asyncio
import subprocess
import logging
from pathlib import Path
from typing import Optional
import ctypes

from .base import JarvisPlugin, PluginContext, PluginResponse, PluginPriority

logger = logging.getLogger(__name__)


class SpotifyPlugin(JarvisPlugin):
    """
    Plugin de controle do Spotify.
    
    Funcionalidades:
    - Abrir o Spotify
    - Play/Pause
    - Próxima/Anterior música
    - Controle de volume
    
    Não requer API key - usa controle local do Windows.
    """
    
    name = "Spotify"
    description = "Controla o Spotify: play, pause, próxima, anterior"
    version = "1.0.0"
    author = "JARVIS Team"
    
    trigger_phrases = [
        # Abrir
        "abrir spotify",
        "abre o spotify",
        "abra o spotify",
        "iniciar spotify",
        
        # Play/Pause
        "tocar música",
        "toca música",
        "coloca música",
        "colocar música",
        "play",
        "pausar",
        "pause",
        "pausa a música",
        "para a música",
        "continuar música",
        
        # Navegação
        "próxima música",
        "próxima",
        "pular música",
        "pula música",
        "next",
        "música anterior",
        "anterior",
        "voltar música",
        "volta a música",
        "previous",
        
        # Volume
        "aumentar volume",
        "abaixa o volume",
        "diminuir volume",
        "volume máximo",
        "mutar",
        "silenciar"
    ]
    
    priority = PluginPriority.HIGH
    requires_internet = False
    
    # Virtual Key Codes para controle de mídia (Windows)
    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    VK_VOLUME_UP = 0xAF
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_MUTE = 0xAD
    
    # Caminhos comuns do Spotify no Windows
    SPOTIFY_PATHS = [
        Path.home() / "AppData" / "Roaming" / "Spotify" / "Spotify.exe",
        Path("C:/Program Files/WindowsApps/SpotifyAB.SpotifyMusic_1.0.0.0_x64/Spotify.exe"),
        Path("C:/Users") / Path.home().name / "AppData" / "Local" / "Microsoft" / "WindowsApps" / "Spotify.exe"
    ]
    
    def __init__(self):
        super().__init__()
        self._spotify_path: Optional[Path] = None
    
    async def initialize(self) -> bool:
        """Inicializa e localiza o Spotify"""
        # Tenta encontrar o Spotify
        for path in self.SPOTIFY_PATHS:
            if path.exists():
                self._spotify_path = path
                logger.info(f"Spotify encontrado em: {path}")
                break
        
        if not self._spotify_path:
            logger.warning("Spotify não encontrado nos caminhos padrão. Tentarei abrir via menu Iniciar.")
        
        return await super().initialize()
    
    def _press_media_key(self, vk_code: int) -> bool:
        """Simula pressionamento de tecla de mídia"""
        try:
            # Constantes do Windows
            KEYEVENTF_EXTENDEDKEY = 0x0001
            KEYEVENTF_KEYUP = 0x0002
            
            # Pressiona a tecla
            ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
            # Solta a tecla
            ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            logger.error(f"Erro ao pressionar tecla de mídia: {e}")
            return False
    
    async def _open_spotify(self) -> bool:
        """Abre o aplicativo Spotify"""
        try:
            if self._spotify_path and self._spotify_path.exists():
                subprocess.Popen([str(self._spotify_path)])
            else:
                # Tenta via menu Iniciar
                subprocess.Popen(["cmd", "/c", "start", "spotify:"], shell=True)
            
            await asyncio.sleep(2)  # Aguarda abrir
            return True
        except Exception as e:
            logger.error(f"Erro ao abrir Spotify: {e}")
            return False
    
    def _is_spotify_running(self) -> bool:
        """Verifica se o Spotify está rodando"""
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Spotify.exe"],
                capture_output=True,
                text=True
            )
            return "Spotify.exe" in result.stdout
        except Exception:
            return False
    
    def _classify_command(self, text: str) -> str:
        """Classifica o tipo de comando do usuário"""
        text_lower = text.lower()
        
        # Abrir
        if any(phrase in text_lower for phrase in ["abrir", "abre", "abra", "iniciar"]):
            return "open"
        
        # Play
        if any(phrase in text_lower for phrase in ["tocar", "toca", "coloca", "colocar", "play", "continuar"]):
            return "play"
        
        # Pause
        if any(phrase in text_lower for phrase in ["pausar", "pause", "pausa", "para"]):
            return "pause"
        
        # Próxima
        if any(phrase in text_lower for phrase in ["próxima", "proxima", "pular", "pula", "next"]):
            return "next"
        
        # Anterior
        if any(phrase in text_lower for phrase in ["anterior", "voltar", "volta", "previous"]):
            return "previous"
        
        # Volume
        if any(phrase in text_lower for phrase in ["aumentar", "subir", "mais alto"]):
            return "volume_up"
        
        if any(phrase in text_lower for phrase in ["diminuir", "abaixa", "abaixar", "mais baixo"]):
            return "volume_down"
        
        if any(phrase in text_lower for phrase in ["mutar", "mute", "silenciar"]):
            return "mute"
        
        # Default - toggle play/pause
        return "toggle"
    
    async def execute(self, context: PluginContext) -> PluginResponse:
        """Executa o comando de controle do Spotify"""
        command = self._classify_command(context.user_message)
        
        logger.info(f"Comando Spotify classificado: {command}")
        
        # Executa o comando apropriado
        if command == "open":
            if self._is_spotify_running():
                return PluginResponse(
                    message="O Spotify já está aberto, chefe.",
                    success=True
                )
            
            success = await self._open_spotify()
            if success:
                return PluginResponse(
                    message="Abrindo o Spotify para você.",
                    success=True
                )
            else:
                return PluginResponse.error(
                    "Não consegui abrir o Spotify. Verifique se está instalado."
                )
        
        elif command == "play" or command == "toggle":
            self._press_media_key(self.VK_MEDIA_PLAY_PAUSE)
            return PluginResponse(
                message="Entendido, tocando música.",
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
            # Pressiona 5 vezes para aumento perceptível
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
