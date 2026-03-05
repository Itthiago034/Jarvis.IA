#!/usr/bin/env python3
"""
JARVIS CodeAgent CLI
====================
Interface de linha de comando para interagir com o CodeAgent.

Uso:
    jarvis-code                     # Modo interativo
    jarvis-code "sua pergunta"      # Comando único
    jarvis-code @coder "crie X"     # Com agente específico
    jarvis-code -f arquivo.py       # Com contexto de arquivo
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Adicionar src ao path se necessário
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Tentar importar typer
try:
    import typer  # type: ignore[reportMissingImports]
    from typing_extensions import Annotated
    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False

from jarvis.cli.config import get_config, ensure_dirs
from jarvis.cli.agents import (
    AgentType, get_agent_profile, parse_agent_from_message, 
    list_agents, AGENTS
)
from jarvis.cli.context import ContextDetector, ProjectContext
from jarvis.cli.history import ChatHistory
from jarvis.cli.output import (
    print_markdown, print_error, print_success, print_info,
    print_welcome, print_context_info, print_agent_header,
    print_user_input, print_warning, clear_screen, RICH_AVAILABLE
)

# Carregar variáveis de ambiente
load_dotenv()

# App Typer
app = typer.Typer(
    name="jarvis-code",
    help="🤖 JARVIS CodeAgent - Seu Engenheiro de Software no Terminal",
    add_completion=False
) if TYPER_AVAILABLE else None


class CodeAgentCLI:
    """Classe principal do CLI"""
    
    def __init__(self):
        self.config = get_config()
        self.history = ChatHistory()
        self.context: Optional[ProjectContext] = None
        self.current_agent = AgentType.CODER
        self._agent_instance = None
    
    async def initialize(self) -> bool:
        """Inicializa o CodeAgent"""
        try:
            from jarvis.agents.code_agent import CodeAgent
            
            api_key = self.config.get_api_key()
            if not api_key:
                print_error("GOOGLE_API_KEY não configurada. Configure no .env ou variável de ambiente.")
                return False
            
            self._agent_instance = CodeAgent(
                workspace_path=str(self.context.root_path) if self.context else os.getcwd(),
                model=self.config.model
            )
            
            success = await self._agent_instance.initialize()
            if not success:
                print_error("Falha ao inicializar CodeAgent")
                return False
            
            return True
            
        except ImportError as e:
            print_error(f"Dependências não encontradas: {e}")
            print_info("Execute: pip install google-adk mcp")
            return False
        except Exception as e:
            print_error(f"Erro ao inicializar: {e}")
            return False
    
    async def send_message(self, message: str, agent_type: Optional[AgentType] = None) -> str:
        """Envia mensagem para o agente"""
        if not self._agent_instance:
            return "Erro: Agente não inicializado"
        
        # Usar agente especificado ou padrão
        agent = agent_type or self.current_agent
        profile = get_agent_profile(agent)
        
        # Construir prompt com contexto
        full_prompt = self._build_prompt(message, profile)
        
        try:
            # Chamar o agente
            result = await self._agent_instance.run(full_prompt)
            
            # Salvar no histórico
            self.history.add_message("user", message, agent.value)
            self.history.add_message("assistant", result.message)
            
            return result.message
            
        except Exception as e:
            return f"Erro: {str(e)}"
    
    def _build_prompt(self, message: str, profile) -> str:
        """Constrói o prompt completo com contexto"""
        parts = []
        
        # Instrução do agente
        parts.append(f"# Modo: {profile.name}\n{profile.instruction}\n")
        
        # Contexto do projeto
        if self.context:
            parts.append(self.context.to_prompt_context())
        
        # Mensagem do usuário
        parts.append(f"\n## Solicitação do Usuário\n{message}")
        
        return "\n".join(parts)
    
    def detect_context(self, path: Optional[str] = None):
        """Detecta contexto do projeto"""
        detector = ContextDetector(path)
        self.context = detector.detect()
    
    def process_command(self, command: str) -> Optional[str]:
        """Processa comandos especiais (começam com /)"""
        cmd = command.lower().strip()
        
        if cmd in ["/exit", "/quit", "/q"]:
            return "EXIT"
        
        if cmd in ["/help", "/h", "/?"] :
            return self._show_help()
        
        if cmd == "/agents":
            return list_agents()
        
        if cmd == "/context":
            if self.context:
                return self.context.to_prompt_context()
            return "Nenhum contexto detectado"
        
        if cmd == "/clear":
            clear_screen()
            return None
        
        if cmd == "/history":
            return self._show_history()
        
        if cmd.startswith("/export"):
            parts = cmd.split(maxsplit=1)
            output = parts[1] if len(parts) > 1 else "chat_export.md"
            return self._export_history(output)
        
        if cmd.startswith("/agent "):
            agent_name = cmd.split(maxsplit=1)[1]
            return self._switch_agent(agent_name)
        
        if cmd == "/new":
            self.history.new_session(project_path=str(self.context.root_path) if self.context else None)
            return "Nova sessão iniciada"
        
        if cmd == "/continue":
            session = self.history.continue_last()
            if session:
                return f"Continuando sessão: {session.title}"
            return "Nenhuma sessão anterior encontrada"
        
        return f"Comando desconhecido: {command}. Use /help para ver comandos."
    
    def _show_help(self) -> str:
        """Mostra ajuda"""
        return """
📚 **Comandos Disponíveis:**

**Chat:**
  `@coder <msg>`     - Usar agente de código
  `@reviewer <msg>`  - Usar agente de review
  `@debugger <msg>`  - Usar agente de debug
  `@tester <msg>`    - Usar agente de testes
  `@docs <msg>`      - Usar agente de documentação
  `@security <msg>`  - Usar agente de segurança

**Navegação:**
  `/agents`          - Listar todos os agentes
  `/agent <nome>`    - Trocar agente padrão
  `/context`         - Ver contexto do projeto
  `/clear`           - Limpar tela

**Histórico:**
  `/new`             - Nova sessão
  `/continue`        - Continuar última sessão
  `/history`         - Ver sessões anteriores
  `/export [arq]`    - Exportar conversa

**Sistema:**
  `/help`            - Esta ajuda
  `/exit`            - Sair
"""
    
    def _show_history(self) -> str:
        """Lista sessões do histórico"""
        sessions = self.history.list_sessions()
        if not sessions:
            return "Nenhuma sessão no histórico"
        
        lines = ["📜 **Sessões Recentes:**\n"]
        for s in sessions:
            lines.append(f"  `{s['id']}` - {s['title']} ({s['message_count']} msgs)")
        return "\n".join(lines)
    
    def _export_history(self, output: str) -> str:
        """Exporta histórico atual"""
        if not self.history.current:
            return "Nenhuma sessão ativa para exportar"
        
        if self.history.export_session(self.history.current.id, output):
            return f"Sessão exportada para: {output}"
        return "Erro ao exportar sessão"
    
    def _switch_agent(self, agent_name: str) -> str:
        """Troca agente padrão"""
        try:
            self.current_agent = AgentType(agent_name.lower())
            profile = get_agent_profile(self.current_agent)
            return f"Agente trocado para: {profile.emoji} {profile.name}"
        except ValueError:
            return f"Agente desconhecido: {agent_name}. Use /agents para ver disponíveis."
    
    async def run_interactive(self):
        """Executa modo interativo"""
        print_welcome()
        
        # Detectar contexto
        self.detect_context()
        if self.context:
            print_context_info(self.context)
        
        # Inicializar agente
        print_info("Inicializando CodeAgent...")
        if not await self.initialize():
            return
        
        print_success(f"Respondendo com {self.config.model}")
        
        # Mostra info de ferramentas/arquivos
        if RICH_AVAILABLE:
            from rich.console import Console  # type: ignore[reportMissingImports]
            tools_count = len(self._agent_instance._tools) if hasattr(self._agent_instance, '_tools') else 28
            Console().print(f"[dim]Using: {tools_count} tools | {self.current_agent.value} agent[/dim]\n")
        
        # Iniciar sessão
        self.history.new_session(project_path=str(self.context.root_path) if self.context else None)
        
        # Loop principal
        while True:
            try:
                # Input do usuário - estilo Gemini CLI com ">"
                if RICH_AVAILABLE:
                    from rich.console import Console  # type: ignore[reportMissingImports]
                    user_input = Console().input("[bold green]>[/bold green] ")
                else:
                    user_input = input("> ")
                
                user_input = user_input.strip()
                
                if not user_input:
                    continue
                
                # Processar comandos
                if user_input.startswith("/"):
                    result = self.process_command(user_input)
                    if result == "EXIT":
                        print_info("Até logo! 👋")
                        break
                    if result:
                        print_markdown(result)
                    continue
                
                # Detectar agente na mensagem
                agent_type, message = parse_agent_from_message(user_input)
                if agent_type:
                    profile = get_agent_profile(agent_type)
                else:
                    profile = get_agent_profile(self.current_agent)
                
                # Mostra status de processamento
                if RICH_AVAILABLE:
                    from rich.console import Console  # type: ignore[reportMissingImports]
                    Console().print(f"[dim italic]Responding with {self.config.model}[/dim italic]")
                    from rich.status import Status  # type: ignore[reportMissingImports]
                    with Console().status("[bold cyan]...[/bold cyan]", spinner="dots"):
                        response = await self.send_message(message or user_input, agent_type)
                else:
                    print(f"Responding with {self.config.model}")
                    response = await self.send_message(message or user_input, agent_type)
                
                # Resposta formatada
                if RICH_AVAILABLE:
                    from rich.console import Console  # type: ignore[reportMissingImports]
                    Console().print(f"[bold green]✦[/bold green] ", end="")
                print_markdown(response)
                
                # Aguarda próximo comando
                if RICH_AVAILABLE:
                    from rich.console import Console  # type: ignore[reportMissingImports]
                    Console().print(f"\n[dim]✦ Awaiting your next command or request.[/dim]\n")
                
            except KeyboardInterrupt:
                print("\n")
                print_info("Use /exit para sair")
            except EOFError:
                break
        
        # Cleanup
        if self._agent_instance:
            await self._agent_instance.shutdown()
    
    async def run_single(self, message: str, agent: Optional[str] = None, files: Optional[list] = None):
        """Executa comando único"""
        # Detectar contexto
        self.detect_context()
        
        # Inicializar
        if not await self.initialize():
            return
        
        # Detectar agente
        agent_type = None
        if agent:
            try:
                agent_type = AgentType(agent.lower())
            except ValueError:
                print_error(f"Agente desconhecido: {agent}")
                return
        else:
            agent_type, message = parse_agent_from_message(message)
        
        # Adicionar contexto de arquivos
        if files:
            file_contents = []
            for f in files:
                path = Path(f)
                if path.exists():
                    try:
                        content = path.read_text(encoding="utf-8")
                        file_contents.append(f"### Arquivo: {f}\n```\n{content}\n```")
                    except Exception as e:
                        print_warning(f"Não foi possível ler {f}: {e}")
            
            if file_contents:
                message = message + "\n\n## Arquivos de Contexto:\n" + "\n".join(file_contents)
        
        # Enviar
        response = await self.send_message(message, agent_type)
        print_markdown(response)
        
        # Cleanup
        if self._agent_instance:
            await self._agent_instance.shutdown()


# Comandos Typer (se disponível)
if TYPER_AVAILABLE:
    @app.command()
    def main(
        message: Annotated[Optional[str], typer.Argument(help="Mensagem para o agente")] = None,
        agent: Annotated[Optional[str], typer.Option("-a", "--agent", help="Agente a usar (@coder, @reviewer, etc)")] = None,
        files: Annotated[Optional[list[str]], typer.Option("-f", "--file", help="Arquivos de contexto")] = None,
        context: Annotated[Optional[str], typer.Option("-c", "--context", help="Diretório de contexto")] = None,
        continue_session: Annotated[bool, typer.Option("--continue", help="Continuar última sessão")] = False,
        list_agents_flag: Annotated[bool, typer.Option("--agents", help="Listar agentes disponíveis")] = False,
    ):
        """
        🤖 JARVIS CodeAgent - Seu Engenheiro de Software no Terminal
        
        Exemplos:
            jarvis-code                          # Modo interativo
            jarvis-code "analise este código"    # Comando único
            jarvis-code @reviewer -f main.py     # Review de arquivo
            jarvis-code @debugger "erro X"       # Debug
        """
        ensure_dirs()
        
        if list_agents_flag:
            print(list_agents())
            return
        
        cli = CodeAgentCLI()
        
        if context:
            cli.detect_context(context)
        
        if message:
            # Modo comando único
            asyncio.run(cli.run_single(message, agent, files))
        else:
            # Modo interativo
            asyncio.run(cli.run_interactive())


def main_entrypoint():
    """Entry point para o CLI"""
    if TYPER_AVAILABLE:
        app()
    else:
        # Fallback sem typer
        import argparse
        parser = argparse.ArgumentParser(description="JARVIS CodeAgent CLI")
        parser.add_argument("message", nargs="?", help="Mensagem para o agente")
        parser.add_argument("-a", "--agent", help="Agente a usar")
        parser.add_argument("-f", "--file", action="append", help="Arquivos de contexto")
        parser.add_argument("--agents", action="store_true", help="Listar agentes")
        
        args = parser.parse_args()
        
        if args.agents:
            print(list_agents())
            return
        
        cli = CodeAgentCLI()
        
        if args.message:
            asyncio.run(cli.run_single(args.message, args.agent, args.file))
        else:
            asyncio.run(cli.run_interactive())


if __name__ == "__main__":
    main_entrypoint()
