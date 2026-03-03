"""
JARVIS - Plugin de Aplicativos
==============================
Abre e controla aplicativos do Windows por comando de voz.

Autor: Thiago
Versão: 1.0.0
"""

import asyncio
import subprocess
import logging
import os
from pathlib import Path
from typing import Optional, Tuple

from .base import JarvisPlugin, PluginContext, PluginResponse, PluginPriority

logger = logging.getLogger(__name__)


class AppsPlugin(JarvisPlugin):
    """
    Plugin para abrir aplicativos.
    
    Funcionalidades:
    - Abrir aplicativos populares
    - Abrir sites
    - Abrir pastas
    """
    
    name = "Aplicativos"
    description = "Abre aplicativos, sites e pastas"
    version = "1.0.0"
    author = "JARVIS Team"
    
    trigger_phrases = [
        # Genérico
        "abrir",
        "abre",
        "abra",
        "iniciar",
        "executar",
        "rodar",
        "abra o",
        "abre o",
        
        # Específicos
        "chrome",
        "navegador",
        "firefox",
        "edge",
        "vscode",
        "vs code",
        "visual studio",
        "excel",
        "word",
        "powerpoint",
        "notepad",
        "bloco de notas",
        "calculadora",
        "explorador",
        "explorer",
        "terminal",
        "powershell",
        "cmd",
        "discord",
        "whatsapp",
        "telegram",
        "youtube",
        "netflix",
        "prime video",
        "crunchyroll"
    ]
    
    priority = PluginPriority.HIGH
    requires_internet = False
    
    # Mapeamento de apps conhecidos
    APPS = {
        # Navegadores
        "chrome": ("start chrome", "Abrindo o Chrome."),
        "google chrome": ("start chrome", "Abrindo o Chrome."),
        "firefox": ("start firefox", "Abrindo o Firefox."),
        "edge": ("start msedge", "Abrindo o Microsoft Edge."),
        "navegador": ("start msedge", "Abrindo o navegador."),
        "browser": ("start msedge", "Abrindo o navegador."),
        
        # Desenvolvimento
        "vscode": ("code", "Abrindo o Visual Studio Code."),
        "vs code": ("code", "Abrindo o Visual Studio Code."),
        "visual studio code": ("code", "Abrindo o Visual Studio Code."),
        "terminal": ("start wt", "Abrindo o Terminal."),
        "powershell": ("start powershell", "Abrindo o PowerShell."),
        "cmd": ("start cmd", "Abrindo o Prompt de Comando."),
        
        # Office
        "word": ("start winword", "Abrindo o Word."),
        "excel": ("start excel", "Abrindo o Excel."),
        "powerpoint": ("start powerpnt", "Abrindo o PowerPoint."),
        "outlook": ("start outlook", "Abrindo o Outlook."),
        
        # Sistema
        "calculadora": ("calc", "Abrindo a calculadora."),
        "calculator": ("calc", "Abrindo a calculadora."),
        "notepad": ("notepad", "Abrindo o Bloco de Notas."),
        "bloco de notas": ("notepad", "Abrindo o Bloco de Notas."),
        "explorador": ("explorer", "Abrindo o Explorador de Arquivos."),
        "explorer": ("explorer", "Abrindo o Explorador de Arquivos."),
        "arquivos": ("explorer", "Abrindo o Explorador de Arquivos."),
        "configurações": ("start ms-settings:", "Abrindo as Configurações."),
        "settings": ("start ms-settings:", "Abrindo as Configurações."),
        
        # Comunicação
        "discord": ("start discord:", "Abrindo o Discord."),
        "whatsapp": ("start whatsapp:", "Abrindo o WhatsApp."),
        "telegram": ("start tg:", "Abrindo o Telegram."),
        "teams": ("start msteams:", "Abrindo o Teams."),
        
        # Entretenimento
        "spotify": ("start spotify:", "Abrindo o Spotify."),
        
        # Pastas especiais
        "downloads": (f'explorer "{Path.home() / "Downloads"}"', "Abrindo Downloads."),
        "documentos": (f'explorer "{Path.home() / "Documents"}"', "Abrindo Documentos."),
        "área de trabalho": (f'explorer "{Path.home() / "Desktop"}"', "Abrindo Área de Trabalho."),
        "desktop": (f'explorer "{Path.home() / "Desktop"}"', "Abrindo Área de Trabalho."),
    }
    
    # Sites conhecidos
    SITES = {
        "youtube": ("https://youtube.com", "Abrindo o YouTube."),
        "google": ("https://google.com", "Abrindo o Google."),
        "gmail": ("https://mail.google.com", "Abrindo o Gmail."),
        "github": ("https://github.com", "Abrindo o GitHub."),
        "netflix": ("https://netflix.com", "Abrindo a Netflix."),
        "prime video": ("https://primevideo.com", "Abrindo o Prime Video."),
        "amazon prime": ("https://primevideo.com", "Abrindo o Prime Video."),
        "crunchyroll": ("https://crunchyroll.com", "Abrindo a Crunchyroll."),
        "twitter": ("https://twitter.com", "Abrindo o Twitter."),
        "x": ("https://x.com", "Abrindo o X."),
        "instagram": ("https://instagram.com", "Abrindo o Instagram."),
        "facebook": ("https://facebook.com", "Abrindo o Facebook."),
        "linkedin": ("https://linkedin.com", "Abrindo o LinkedIn."),
        "reddit": ("https://reddit.com", "Abrindo o Reddit."),
        "twitch": ("https://twitch.tv", "Abrindo a Twitch."),
        "chatgpt": ("https://chat.openai.com", "Abrindo o ChatGPT."),
        "claude": ("https://claude.ai", "Abrindo o Claude."),
    }
    
    def _extract_target(self, text: str) -> str:
        """Extrai o nome do app/site do texto"""
        text_lower = text.lower()
        
        # Remove palavras de comando
        remove_words = [
            "abrir", "abre", "abra", "o", "a", "os", "as",
            "iniciar", "executar", "rodar", "por favor",
            "pode", "quero", "preciso", "me"
        ]
        
        words = text_lower.split()
        filtered = [w for w in words if w not in remove_words]
        
        return " ".join(filtered).strip()
    
    def _find_app(self, target: str) -> Optional[Tuple[str, str]]:
        """Encontra o comando para o app/site"""
        target_lower = target.lower().strip()
        
        # Busca exata
        if target_lower in self.APPS:
            return self.APPS[target_lower]
        
        if target_lower in self.SITES:
            url, msg = self.SITES[target_lower]
            return (f'start {url}', msg)
        
        # Busca parcial em apps
        for key, value in self.APPS.items():
            if key in target_lower or target_lower in key:
                return value
        
        # Busca parcial em sites
        for key, (url, msg) in self.SITES.items():
            if key in target_lower or target_lower in key:
                return (f'start {url}', msg)
        
        return None
    
    async def _run_command(self, command: str) -> bool:
        """Executa um comando do sistema"""
        try:
            subprocess.Popen(command, shell=True)
            await asyncio.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"Erro ao executar comando: {e}")
            return False
    
    async def execute(self, context: PluginContext) -> PluginResponse:
        """Executa a abertura do aplicativo"""
        target = self._extract_target(context.user_message)
        
        if not target:
            return PluginResponse(
                message="O que você gostaria que eu abrisse?",
                success=True,
                follow_up="Diga o nome do aplicativo ou site."
            )
        
        logger.info(f"Tentando abrir: {target}")
        
        # Busca o comando
        result = self._find_app(target)
        
        if result:
            command, message = result
            success = await self._run_command(command)
            
            if success:
                return PluginResponse(
                    message=message,
                    success=True,
                    data={"target": target, "command": command}
                )
            else:
                return PluginResponse.error(
                    f"Não consegui abrir {target}. Verifique se está instalado."
                )
        
        # Tenta abrir via menu Iniciar
        logger.info(f"App não mapeado, tentando via menu: {target}")
        
        try:
            # Tenta abrir como se digitasse no menu Iniciar
            subprocess.Popen(f'start "" "{target}"', shell=True)
            return PluginResponse(
                message=f"Tentando abrir {target}.",
                success=True
            )
        except:
            return PluginResponse.error(
                f"Não encontrei {target}. Verifique se está instalado ou se o nome está correto."
            )
