"""
JARVIS - Gerenciador de Plugins
===============================
Responsável por carregar, gerenciar e executar plugins.
Implementa descoberta automática e execução inteligente.

Autor: Thiago
Versão: 0.2.0
"""

import asyncio
import importlib
import inspect
import logging
from pathlib import Path
from typing import Optional, Type
import yaml

from .base import (
    JarvisPlugin, 
    PluginContext, 
    PluginResponse, 
    PluginStatus,
    PluginPriority
)

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Gerenciador central de plugins do JARVIS.
    
    Funcionalidades:
    - Descoberta automática de plugins
    - Carregamento sob demanda
    - Execução com fallback
    - Priorização inteligente
    
    Uso:
        manager = PluginManager()
        await manager.initialize()
        response = await manager.execute("como está o tempo?", context)
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self._plugins: dict[str, JarvisPlugin] = {}
        self._config_path = config_path or Path(__file__).parent.parent.parent.parent / "config" / "plugins.yaml"
        self._config: dict = {}
        self._initialized = False
    
    @property
    def plugins(self) -> dict[str, JarvisPlugin]:
        """Retorna dicionário de plugins carregados"""
        return self._plugins.copy()
    
    @property
    def enabled_plugins(self) -> list[JarvisPlugin]:
        """Retorna lista de plugins habilitados"""
        return [p for p in self._plugins.values() if p.is_enabled]
    
    def _load_config(self) -> dict:
        """Carrega configuração de plugins do arquivo YAML"""
        if not self._config_path.exists():
            logger.warning(f"Arquivo de configuração não encontrado: {self._config_path}")
            return {"enabled": True, "plugins": {}}
        
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return {"enabled": True, "plugins": {}}
    
    def _discover_plugins(self) -> list[Type[JarvisPlugin]]:
        """
        Descobre automaticamente todos os plugins disponíveis.
        Busca em todos os módulos da pasta plugins/.
        """
        discovered = []
        plugins_dir = Path(__file__).parent
        
        for file_path in plugins_dir.glob("*.py"):
            if file_path.name.startswith("_") or file_path.name == "base.py" or file_path.name == "manager.py":
                continue
            
            module_name = file_path.stem
            try:
                module = importlib.import_module(f".{module_name}", package="jarvis.plugins")
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, JarvisPlugin) and 
                        obj is not JarvisPlugin and
                        not inspect.isabstract(obj)):
                        discovered.append(obj)
                        logger.debug(f"Plugin descoberto: {obj.name}")
                        
            except Exception as e:
                logger.error(f"Erro ao carregar módulo {module_name}: {e}")
        
        return discovered
    
    def register(self, plugin_class: Type[JarvisPlugin]) -> None:
        """
        Registra um plugin manualmente.
        
        Args:
            plugin_class: Classe do plugin (não instância)
        """
        try:
            plugin = plugin_class()
            plugin_id = plugin_class.__name__
            
            if plugin_id in self._plugins:
                logger.warning(f"Plugin {plugin_id} já registrado, substituindo...")
            
            self._plugins[plugin_id] = plugin
            logger.info(f"Plugin registrado: {plugin.name} ({plugin_id})")
            
        except Exception as e:
            logger.error(f"Erro ao registrar plugin {plugin_class}: {e}")
    
    async def initialize(self) -> None:
        """
        Inicializa o gerenciador e todos os plugins.
        Deve ser chamado uma vez na inicialização do JARVIS.
        """
        if self._initialized:
            logger.warning("PluginManager já inicializado")
            return
        
        logger.info("Inicializando PluginManager...")
        
        # Carrega configuração
        self._config = self._load_config()
        
        if not self._config.get("enabled", True):
            logger.info("Sistema de plugins desabilitado na configuração")
            return
        
        # Descobre e registra plugins
        discovered = self._discover_plugins()
        for plugin_class in discovered:
            self.register(plugin_class)
        
        # Inicializa plugins habilitados
        plugins_config = self._config.get("plugins", {})
        
        for plugin_id, plugin in self._plugins.items():
            plugin_cfg = plugins_config.get(plugin_id, {})
            
            # Verifica se está habilitado na config
            if not plugin_cfg.get("enabled", True):
                plugin._status = PluginStatus.DISABLED
                logger.info(f"Plugin {plugin.name} desabilitado por configuração")
                continue
            
            # Configura e inicializa
            plugin.configure(plugin_cfg.get("config", {}))
            
            try:
                success = await plugin.initialize()
                if not success:
                    plugin._status = PluginStatus.ERROR
                    logger.error(f"Falha ao inicializar plugin {plugin.name}")
            except Exception as e:
                plugin._status = PluginStatus.ERROR
                plugin._error_message = str(e)
                logger.error(f"Exceção ao inicializar {plugin.name}: {e}")
        
        self._initialized = True
        logger.info(f"PluginManager inicializado com {len(self.enabled_plugins)} plugins ativos")
    
    async def shutdown(self) -> None:
        """Encerra todos os plugins graciosamente"""
        logger.info("Encerrando PluginManager...")
        
        for plugin in self._plugins.values():
            try:
                await plugin.shutdown()
            except Exception as e:
                logger.error(f"Erro ao encerrar {plugin.name}: {e}")
        
        self._plugins.clear()
        self._initialized = False
        logger.info("PluginManager encerrado")
    
    def find_matching_plugins(self, text: str) -> list[tuple[JarvisPlugin, float]]:
        """
        Encontra todos os plugins que podem responder ao texto.
        
        Args:
            text: Mensagem do usuário
            
        Returns:
            Lista de tuplas (plugin, score) ordenada por score
        """
        matches = []
        
        for plugin in self.enabled_plugins:
            score = plugin.get_match_score(text)
            if score > 0:
                matches.append((plugin, score))
        
        # Ordena por score (maior primeiro), depois por prioridade
        matches.sort(key=lambda x: (x[1], x[0].priority.value), reverse=True)
        
        return matches
    
    async def execute(
        self, 
        text: str, 
        context: PluginContext,
        plugin_id: Optional[str] = None
    ) -> Optional[PluginResponse]:
        """
        Executa o plugin mais adequado para o texto.
        
        Args:
            text: Mensagem do usuário
            context: Contexto da execução
            plugin_id: ID específico do plugin (opcional)
            
        Returns:
            PluginResponse ou None se nenhum plugin correspondeu
        """
        # Se plugin específico foi solicitado
        if plugin_id:
            plugin = self._plugins.get(plugin_id)
            if plugin and plugin.is_enabled:
                return await self._execute_plugin(plugin, context)
            else:
                logger.warning(f"Plugin {plugin_id} não encontrado ou desabilitado")
                return None
        
        # Encontra plugins correspondentes
        matches = self.find_matching_plugins(text)
        
        if not matches:
            logger.debug(f"Nenhum plugin correspondeu a: {text[:50]}...")
            return None
        
        # Tenta executar o melhor match
        for plugin, score in matches:
            logger.debug(f"Tentando plugin {plugin.name} (score: {score:.2f})")
            
            try:
                response = await self._execute_plugin(plugin, context)
                if response and response.success:
                    return response
            except Exception as e:
                logger.error(f"Erro ao executar {plugin.name}: {e}")
                continue
        
        return None
    
    async def _execute_plugin(
        self, 
        plugin: JarvisPlugin, 
        context: PluginContext
    ) -> PluginResponse:
        """Executa um plugin específico com tratamento de erros"""
        try:
            logger.info(f"Executando plugin: {plugin.name}")
            response = await asyncio.wait_for(
                plugin.execute(context),
                timeout=30.0  # Timeout de 30 segundos
            )
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout ao executar {plugin.name}")
            return PluginResponse.error(
                f"Desculpe, o {plugin.name} demorou demais para responder."
            )
        except Exception as e:
            logger.error(f"Erro ao executar {plugin.name}: {e}")
            return PluginResponse.error(
                f"Houve um problema ao executar o {plugin.name}."
            )
    
    def get_plugin(self, plugin_id: str) -> Optional[JarvisPlugin]:
        """Obtém um plugin pelo ID"""
        return self._plugins.get(plugin_id)
    
    def list_plugins(self) -> list[dict]:
        """Lista todos os plugins com seus metadados"""
        return [
            {
                "id": plugin_id,
                "name": plugin.name,
                "description": plugin.description,
                "version": plugin.version,
                "status": plugin.status.value,
                "triggers": plugin.trigger_phrases[:3],  # Primeiras 3
                "priority": plugin.priority.name
            }
            for plugin_id, plugin in self._plugins.items()
        ]
    
    def __repr__(self) -> str:
        enabled = len(self.enabled_plugins)
        total = len(self._plugins)
        return f"<PluginManager(plugins={enabled}/{total}, initialized={self._initialized})>"


# Instância global (singleton)
_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Obtém a instância global do PluginManager"""
    global _manager
    if _manager is None:
        _manager = PluginManager()
    return _manager
