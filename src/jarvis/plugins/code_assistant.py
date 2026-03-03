"""
JARVIS - Plugin Code Assistant
==============================
Plugin que integra o CodeAgent (Engenheiro de Software) com o JARVIS.

Este plugin permite que o usuário solicite análises de código,
refatorações e criação de scripts por comando de voz.

Exemplos de comandos:
- "Analise o código do arquivo main.py"
- "Corrija o erro no agent.py"
- "Crie um script para fazer backup"
- "Refatore a função de login"
- "Explique como funciona esse código"

Autor: JARVIS Team
Versão: 0.1.0
"""

import asyncio
import logging
from typing import Optional
from pathlib import Path

from .base import (
    JarvisPlugin,
    PluginContext,
    PluginResponse,
    PluginStatus,
    PluginPriority
)

logger = logging.getLogger(__name__)


class CodeAssistantPlugin(JarvisPlugin):
    """
    Plugin de integração do CodeAgent com JARVIS.
    
    Conecta o sistema de plugins existente ao SubAgent de programação,
    permitindo solicitações de código via interface de voz.
    """
    
    # Metadados do plugin
    name = "Code Assistant"
    description = "Engenheiro de Software Sênior para análise, correção e criação de código"
    version = "0.1.0"
    author = "JARVIS Team"
    
    # Frases que ativam este plugin
    trigger_phrases = [
        # Análise
        "analis",  # analise, analisar, análise
        "código",
        "code review",
        
        # Correção
        "corrij",  # corrija, corrigir
        "fix",
        "consert",  # conserte, consertar
        
        # Refatoração
        "refator",  # refatorar, refatore, refatoração
        "melhore o código",
        "otimiz",  # otimize, otimizar
        
        # Criação
        "crie um script",
        "crie uma função",
        "crie uma classe",
        "programe",
        "desenvolv",  # desenvolva, desenvolver
        
        # Debugging
        "debug",
        "erro no código",
        "bug",
        "problema no",
        "não está funcionando",
        
        # Explicação
        "explique o código",
        "como funciona",
        "entender o código",
        
        # Testes
        "teste",
        "coverage",
        "unit test",
        
        # Geral
        "engenheiro de software",
        "programador",
        "desenvolvedor",
        "assistente de código",
    ]
    
    # Configurações
    priority = PluginPriority.HIGH  # Alta prioridade para comandos de código
    requires_internet = True  # Precisa de API do Gemini
    requires_auth = False
    
    def __init__(self):
        super().__init__()
        self._agent = None
        self._workspace_path = None
    
    async def initialize(self) -> bool:
        """
        Inicializa o plugin e o CodeAgent.
        
        Returns:
            True se inicialização bem sucedida
        """
        try:
            # Configurar caminho do workspace
            self._workspace_path = self.get_config(
                "workspace_path",
                str(Path(__file__).parent.parent.parent.parent)  # JARVIS root
            )
            
            logger.info(f"CodeAssistant inicializando com workspace: {self._workspace_path}")
            
            # Lazy load do CodeAgent para evitar imports pesados no startup
            try:
                from ..agents.code_agent import CodeAgent
                
                self._agent = CodeAgent(
                    workspace_path=self._workspace_path,
                    enable_github=self.get_config("enable_github", False),
                    model=self.get_config("model", "gemini-2.5-flash")
                )
                
                # Não inicializa o agente aqui, faz lazy init no primeiro uso
                self._status = PluginStatus.ENABLED
                logger.info(f"Plugin {self.name} v{self.version} inicializado")
                return True
                
            except ImportError as e:
                # ADK não instalado - plugin em modo degradado
                logger.warning(
                    f"Google ADK não instalado. CodeAssistant em modo limitado. "
                    f"Execute: pip install google-adk mcp"
                )
                self._status = PluginStatus.ERROR
                self._error_message = f"Dependência não instalada: {e}"
                return False
                
        except Exception as e:
            logger.error(f"Erro ao inicializar CodeAssistant: {e}")
            self._status = PluginStatus.ERROR
            self._error_message = str(e)
            return False
    
    async def execute(self, context: PluginContext) -> PluginResponse:
        """
        Executa uma solicitação de programação.
        
        Args:
            context: Contexto com a mensagem do usuário
            
        Returns:
            PluginResponse com o resultado
        """
        if not self._agent:
            return PluginResponse.error(
                "CodeAssistant não está disponível. "
                "Verifique se as dependências estão instaladas."
            )
        
        user_message = context.user_message
        
        try:
            # Detectar tipo de tarefa
            task_type = self._detect_task_type(user_message)
            
            # Informar que está processando (para tarefas longas)
            logger.info(f"CodeAssistant processando: {task_type}")
            
            # Executar no CodeAgent
            result = await self._agent.run(
                request=user_message,
                user_id=context.user_id,
                session_id=context.session_id
            )
            
            if result.success:
                # Formatar resposta para fala
                spoken_response = self._format_for_speech(result.message, task_type)
                
                return PluginResponse(
                    message=spoken_response,
                    success=True,
                    should_speak=True,
                    data={
                        "full_response": result.message,
                        "task_type": task_type,
                        "execution_output": result.execution_output,
                        "files_affected": result.files_affected
                    },
                    follow_up="Posso ajudar com mais alguma coisa no código?"
                )
            else:
                return PluginResponse.error(
                    f"Não consegui completar a tarefa: {result.message}"
                )
                
        except asyncio.TimeoutError:
            return PluginResponse.error(
                "A análise está demorando muito. Tente um arquivo menor ou seja mais específico."
            )
        except Exception as e:
            logger.error(f"Erro no CodeAssistant: {e}")
            return PluginResponse.error(
                f"Ocorreu um erro ao processar: {str(e)}"
            )
    
    def _detect_task_type(self, message: str) -> str:
        """Detecta o tipo de tarefa baseado na mensagem"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["analis", "review", "verificar"]):
            return "analyze"
        elif any(word in message_lower for word in ["corrij", "fix", "consert", "bug", "erro"]):
            return "debug"
        elif any(word in message_lower for word in ["refator", "melhor", "otimiz"]):
            return "refactor"
        elif any(word in message_lower for word in ["crie", "criar", "novo", "desenvolv"]):
            return "create"
        elif any(word in message_lower for word in ["explic", "como funciona", "entender"]):
            return "explain"
        elif any(word in message_lower for word in ["teste", "test", "coverage"]):
            return "test"
        else:
            return "general"
    
    def _format_for_speech(self, full_response: str, task_type: str) -> str:
        """
        Formata a resposta do CodeAgent para fala pelo JARVIS.
        
        A resposta completa pode ser muito longa para falar,
        então extraímos um resumo falável.
        """
        # Limite de caracteres para fala confortável
        MAX_SPEECH_LENGTH = 500
        
        # Prefixos por tipo de tarefa
        prefixes = {
            "analyze": "Análise concluída. ",
            "debug": "Encontrei o problema. ",
            "refactor": "Refatoração pronta. ",
            "create": "Código criado. ",
            "explain": "Aqui está a explicação. ",
            "test": "Testes analisados. ",
            "general": "Pronto. "
        }
        
        prefix = prefixes.get(task_type, "")
        
        # Se a resposta for curta, use diretamente
        if len(full_response) <= MAX_SPEECH_LENGTH:
            return f"{prefix}{full_response}"
        
        # Para respostas longas, extrair resumo
        # Procura primeiro parágrafo ou linhas iniciais
        lines = full_response.split('\n')
        summary_lines = []
        current_length = len(prefix)
        
        for line in lines:
            # Pula linhas de código markdown
            if line.strip().startswith('```'):
                summary_lines.append("Incluí código que pode ser visualizado no log.")
                break
            
            # Pula linhas vazias no início
            if not line.strip() and not summary_lines:
                continue
            
            if current_length + len(line) > MAX_SPEECH_LENGTH:
                break
            
            summary_lines.append(line.strip())
            current_length += len(line)
        
        summary = ' '.join(summary_lines)
        
        # Adiciona nota sobre conteúdo completo
        if len(full_response) > MAX_SPEECH_LENGTH:
            summary += " O resultado completo está disponível no log."
        
        return f"{prefix}{summary}"
    
    async def shutdown(self) -> None:
        """Encerra o plugin e libera recursos"""
        if self._agent:
            await self._agent.shutdown()
            self._agent = None
        self._status = PluginStatus.DISABLED
        logger.info(f"Plugin {self.name} encerrado")
    
    def get_match_score(self, text: str) -> float:
        """
        Calcula score de match para priorização.
        
        CodeAssistant tem score alto para termos específicos de programação.
        """
        text_lower = text.lower()
        
        # Termos de alta relevância
        high_relevance = [
            "código", "code", "programa", "script", "função", "classe",
            "bug", "erro", "refator", "debug", "analise o arquivo"
        ]
        
        # Termos de média relevância
        medium_relevance = [
            "python", "javascript", "arquivo", "pasta", "projeto",
            "github", "git", "commit"
        ]
        
        score = 0.0
        
        # High relevance = 0.4 cada (max 0.8)
        high_matches = sum(1 for term in high_relevance if term in text_lower)
        score += min(high_matches * 0.4, 0.8)
        
        # Medium relevance = 0.2 cada (max 0.2)
        medium_matches = sum(1 for term in medium_relevance if term in text_lower)
        score += min(medium_matches * 0.2, 0.2)
        
        return min(score, 1.0)


# Para descoberta automática pelo PluginManager
__plugin__ = CodeAssistantPlugin
