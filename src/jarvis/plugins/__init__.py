"""
JARVIS - Sistema de Plugins
===========================
Pacote de plugins do JARVIS.

Uso:
    from jarvis.plugins import PluginManager, get_plugin_manager
    from jarvis.plugins.base import JarvisPlugin, PluginContext, PluginResponse
"""

from .base import (
    JarvisPlugin,
    PluginContext,
    PluginResponse,
    PluginPriority,
    PluginStatus
)
from .manager import PluginManager, get_plugin_manager

# Plugins incluídos
from .weather import WeatherPlugin
from .spotify import SpotifyPlugin
from .youtube_music import YouTubeMusicPlugin
from .system import SystemPlugin
from .datetime_plugin import DateTimePlugin
from .apps import AppsPlugin
from .code_assistant import CodeAssistantPlugin

__all__ = [
    # Base
    "JarvisPlugin",
    "PluginContext",
    "PluginResponse",
    "PluginPriority",
    "PluginStatus",
    
    # Manager
    "PluginManager",
    "get_plugin_manager",
    
    # Plugins
    "WeatherPlugin",
    "SpotifyPlugin",
    "YouTubeMusicPlugin",
    "SystemPlugin",
    "DateTimePlugin",
    "AppsPlugin",
]
