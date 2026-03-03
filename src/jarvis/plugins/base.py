"""
JARVIS - Sistema Base de Plugins
================================
Define a interface base para todos os plugins do JARVIS.
Cada plugin deve herdar de JarvisPlugin e implementar os métodos abstratos.

Autor: Thiago
Versão: 0.2.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PluginPriority(Enum):
    """Prioridade de execução do plugin"""
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 100


class PluginStatus(Enum):
    """Status do plugin"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    ERROR = "error"
    INITIALIZING = "initializing"


@dataclass
class PluginContext:
    """
    Contexto passado para os plugins durante execução.
    Contém informações sobre o usuário, sessão e comando.
    """
    user_id: str
    user_message: str
    session_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor do metadata com fallback"""
        return self.metadata.get(key, default)


@dataclass
class PluginResponse:
    """
    Resposta retornada pelos plugins.
    Permite controle granular sobre o que o Jarvis faz após execução.
    """
    message: str                          # Mensagem para o Jarvis falar
    success: bool = True                  # Se a execução foi bem sucedida
    should_speak: bool = True             # Se o Jarvis deve falar a resposta
    data: dict = field(default_factory=dict)  # Dados extras para outros plugins
    follow_up: Optional[str] = None       # Pergunta de follow-up opcional
    
    @classmethod
    def error(cls, message: str) -> "PluginResponse":
        """Cria uma resposta de erro padronizada"""
        return cls(
            message=message,
            success=False,
            should_speak=True
        )
    
    @classmethod
    def silent_success(cls, data: dict = None) -> "PluginResponse":
        """Cria uma resposta de sucesso sem fala"""
        return cls(
            message="",
            success=True,
            should_speak=False,
            data=data or {}
        )


class JarvisPlugin(ABC):
    """
    Classe base abstrata para todos os plugins do JARVIS.
    
    Para criar um novo plugin:
    1. Crie uma classe que herda de JarvisPlugin
    2. Defina name, description e trigger_phrases
    3. Implemente o método execute()
    4. Opcionalmente implemente initialize() e shutdown()
    
    Exemplo:
        class MeuPlugin(JarvisPlugin):
            name = "Meu Plugin"
            description = "Faz algo incrível"
            trigger_phrases = ["fazer algo", "execute algo"]
            
            async def execute(self, context: PluginContext) -> PluginResponse:
                return PluginResponse(message="Feito, chefe!")
    """
    
    # Metadados do plugin (sobrescrever na subclasse)
    name: str = "Plugin Base"
    description: str = "Descrição do plugin"
    version: str = "1.0.0"
    author: str = "JARVIS Team"
    
    # Frases que ativam este plugin (case-insensitive)
    trigger_phrases: list[str] = []
    
    # Configurações do plugin
    priority: PluginPriority = PluginPriority.NORMAL
    requires_internet: bool = False
    requires_auth: bool = False
    
    def __init__(self):
        self._status = PluginStatus.INITIALIZING
        self._error_message: Optional[str] = None
        self._config: dict = {}
    
    @property
    def status(self) -> PluginStatus:
        """Retorna o status atual do plugin"""
        return self._status
    
    @property
    def is_enabled(self) -> bool:
        """Verifica se o plugin está habilitado"""
        return self._status == PluginStatus.ENABLED
    
    def configure(self, config: dict) -> None:
        """
        Configura o plugin com parâmetros externos.
        Chamado pelo PluginManager durante inicialização.
        """
        self._config = config
        logger.debug(f"Plugin {self.name} configurado: {list(config.keys())}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        return self._config.get(key, default)
    
    async def initialize(self) -> bool:
        """
        Inicializa o plugin. Chamado uma vez quando o JARVIS inicia.
        Retorna True se inicialização bem sucedida, False caso contrário.
        
        Sobrescreva este método para:
        - Conectar a APIs externas
        - Carregar recursos
        - Validar configurações
        """
        self._status = PluginStatus.ENABLED
        logger.info(f"Plugin {self.name} v{self.version} inicializado")
        return True
    
    async def shutdown(self) -> None:
        """
        Encerra o plugin graciosamente. Chamado quando o JARVIS desliga.
        
        Sobrescreva este método para:
        - Fechar conexões
        - Salvar estado
        - Liberar recursos
        """
        self._status = PluginStatus.DISABLED
        logger.info(f"Plugin {self.name} encerrado")
    
    def matches(self, text: str) -> bool:
        """
        Verifica se o texto do usuário ativa este plugin.
        Usa busca case-insensitive por padrão.
        
        Args:
            text: Mensagem do usuário
            
        Returns:
            True se alguma trigger_phrase foi encontrada
        """
        text_lower = text.lower()
        return any(phrase.lower() in text_lower for phrase in self.trigger_phrases)
    
    def get_match_score(self, text: str) -> float:
        """
        Calcula um score de match (0.0 a 1.0).
        Útil quando múltiplos plugins podem responder.
        
        Args:
            text: Mensagem do usuário
            
        Returns:
            Score de 0.0 (sem match) a 1.0 (match exato)
        """
        if not self.matches(text):
            return 0.0
        
        text_lower = text.lower()
        max_score = 0.0
        
        for phrase in self.trigger_phrases:
            phrase_lower = phrase.lower()
            if phrase_lower in text_lower:
                # Score baseado na proporção da frase no texto
                score = len(phrase_lower) / len(text_lower)
                max_score = max(max_score, score)
        
        return min(max_score, 1.0)
    
    @abstractmethod
    async def execute(self, context: PluginContext) -> PluginResponse:
        """
        Executa a ação principal do plugin.
        
        Este método DEVE ser implementado por todas as subclasses.
        
        Args:
            context: Contexto com informações do usuário e sessão
            
        Returns:
            PluginResponse com a mensagem para o Jarvis falar
        """
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', status={self.status.value})>"
