from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext
from livekit.agents.llm import function_tool
from livekit.plugins import noise_cancellation, google
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from mem0 import AsyncMemoryClient
from wsl_tools import execute_wsl_command, wsl_system_info, wsl_docker_status, check_wsl_available
from windows_tools import execute_windows_command, open_terminal_with_command, classify_command
from web_tools import search_web, search_news, quick_answer, get_weather, format_search_results, format_weather
from productivity_tools import list_tasks, create_task, complete_task, get_upcoming_deadlines, format_tasks, format_deadlines, check_productivity_config
from monitoring_tools import get_system_metrics, get_top_processes, check_system_health, find_resource_hogs, format_system_metrics, format_top_processes, format_health_check
import logging
import os
import json

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Assistant(Agent):
    def __init__(self, chat_ctx: ChatContext = None):
        super().__init__(

            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Charon",
                temperature=0.6,
            ),
            chat_ctx=chat_ctx,
        )

    @function_tool(
        name="executar_comando_wsl",
        description="Executa um comando Linux no WSL (Windows Subsystem for Linux). Use para listar arquivos, verificar status de serviços, executar scripts, gerenciar Docker, etc."
    )
    async def executar_comando_wsl(self, comando: str) -> str:
        """
        Execute um comando no ambiente Linux via WSL.
        
        Args:
            comando: O comando bash/Linux a ser executado (ex: ls -la, docker ps, git status)
        
        Returns:
            O resultado da execução do comando
        """
        logger.info(f"Executando comando WSL: {comando}")
        result = await execute_wsl_command(comando)
        
        if result.get("blocked"):
            return "Comando bloqueado por segurança. Preciso de confirmação explícita para comandos potencialmente perigosos."
        
        if result.get("timeout"):
            return f"O comando excedeu o tempo limite de execução."
        
        if result["success"]:
            output = result["output"] if result["output"] else "Comando executado com sucesso (sem saída)."
            return output
        else:
            error_msg = result["error"] if result["error"] else "Erro desconhecido na execução."
            return f"Erro ao executar comando: {error_msg}"

    @function_tool(
        name="info_sistema_linux",
        description="Obtém informações detalhadas do sistema Linux no WSL: versão do kernel, uso de memória e espaço em disco."
    )
    async def info_sistema_linux(self) -> str:
        """Retorna informações do sistema Linux no WSL."""
        logger.info("Obtendo informações do sistema WSL")
        result = await wsl_system_info()
        
        if result["success"]:
            return result["output"]
        else:
            return f"Não foi possível obter informações do sistema: {result['error']}"

    @function_tool(
        name="status_docker",
        description="Verifica o status de todos os containers Docker em execução ou parados no WSL."
    )
    async def status_docker(self) -> str:
        """Lista os containers Docker e seus status."""
        logger.info("Verificando status dos containers Docker")
        result = await wsl_docker_status()
        
        if result["success"]:
            output = result["output"]
            if not output.strip():
                return "Nenhum container Docker encontrado."
            return output
        else:
            return f"Erro ao verificar Docker: {result['error']}"

    # ============== FERRAMENTAS WINDOWS ==============

    @function_tool(
        name="executar_comando_windows",
        description="Executa um comando PowerShell no Windows. Use para listar arquivos (dir, Get-ChildItem), verificar processos (Get-Process), rede (ipconfig), sistema (systeminfo), etc. Comandos perigosos são bloqueados automaticamente."
    )
    async def executar_comando_windows(self, comando: str, confirmado: bool = False) -> str:
        """
        Executa um comando PowerShell no Windows.
        
        Args:
            comando: O comando PowerShell a executar (ex: dir, Get-Process, ipconfig)
            confirmado: Se True, executa mesmo comandos que requerem confirmação
        
        Returns:
            O resultado da execução ou mensagem sobre bloqueio/confirmação
        """
        logger.info(f"Executando comando Windows: {comando}")
        result = await execute_windows_command(comando, confirmed=confirmado)
        
        if result.get("blocked"):
            return f"⛔ {result['error']}"
        
        if result.get("needs_confirmation"):
            return f"⚠️ Este comando pode modificar o sistema: '{comando}'. {result['reason']}. Peça confirmação explícita ao usuário antes de executar com confirmado=True."
        
        if result.get("timeout"):
            return "O comando excedeu o tempo limite de execução."
        
        if result["success"]:
            output = result["output"] if result["output"] else "Comando executado com sucesso (sem saída)."
            return output
        else:
            error_msg = result["error"] if result["error"] else "Erro desconhecido."
            return f"Erro ao executar comando: {error_msg}"

    @function_tool(
        name="abrir_terminal",
        description="Abre uma janela de terminal PowerShell visível para o usuário, opcionalmente executando um comando. Use quando o usuário quiser ver e interagir com o terminal."
    )
    async def abrir_terminal(self, comando: str = "", titulo: str = "JARVIS Terminal") -> str:
        """
        Abre uma janela de terminal visível.
        
        Args:
            comando: Comando opcional a executar no terminal
            titulo: Título da janela do terminal
        
        Returns:
            Confirmação de abertura
        """
        logger.info(f"Abrindo terminal com comando: {comando}")
        result = await open_terminal_with_command(comando, titulo)
        
        if result["success"]:
            return result["message"]
        else:
            return f"Erro ao abrir terminal: {result['error']}"

    @function_tool(
        name="verificar_seguranca_comando",
        description="Verifica a classificação de segurança de um comando antes de executá-lo. Retorna SAFE (pode executar), CONFIRM (precisa confirmação) ou BLOCKED (nunca executar)."
    )
    async def verificar_seguranca_comando(self, comando: str) -> str:
        """
        Verifica a segurança de um comando.
        
        Args:
            comando: O comando a verificar
        
        Returns:
            Nível de segurança e razão
        """
        safety, reason = classify_command(comando)
        
        if safety == "BLOCKED":
            return f"🔴 BLOQUEADO: {reason}"
        elif safety == "CONFIRM":
            return f"🟡 REQUER CONFIRMAÇÃO: {reason}"
        else:
            return f"🟢 SEGURO: {reason}"

    # ============== FERRAMENTAS WEB ==============

    @function_tool(
        name="buscar_na_web",
        description="Busca informações na internet. Use quando o usuário perguntar sobre algo que requer informações atualizadas ou que você não sabe."
    )
    async def buscar_na_web(self, query: str, max_resultados: int = 5) -> str:
        """
        Busca na web usando DuckDuckGo.
        
        Args:
            query: Termo de busca
            max_resultados: Número de resultados (padrão 5)
        """
        logger.info(f"Buscando na web: {query}")
        result = await search_web(query, max_results=max_resultados)
        return format_search_results(result)

    @function_tool(
        name="buscar_noticias",
        description="Busca notícias recentes sobre um tema ou notícias gerais do Brasil."
    )
    async def buscar_noticias(self, tema: str = "") -> str:
        """
        Busca notícias.
        
        Args:
            tema: Tema das notícias (vazio = notícias gerais)
        """
        logger.info(f"Buscando notícias: {tema}")
        result = await search_news(tema)
        return format_search_results(result)

    @function_tool(
        name="consultar_clima",
        description="Consulta a previsão do tempo para uma cidade."
    )
    async def consultar_clima(self, cidade: str = "São Paulo") -> str:
        """
        Consulta clima de uma cidade.
        
        Args:
            cidade: Nome da cidade
        """
        logger.info(f"Consultando clima: {cidade}")
        result = await get_weather(cidade)
        return format_weather(result)

    @function_tool(
        name="resposta_rapida",
        description="Tenta obter uma resposta rápida para perguntas simples como definições, conversões, cálculos."
    )
    async def resposta_rapida(self, pergunta: str) -> str:
        """
        Tenta resposta instantânea.
        
        Args:
            pergunta: Pergunta ou termo
        """
        result = await quick_answer(pergunta)
        if result.get("success") and result.get("answer"):
            return f"{result['answer']}\n(Fonte: {result.get('source', 'DuckDuckGo')})"
        return "Não encontrei uma resposta direta. Posso fazer uma busca mais ampla."

    # ============== FERRAMENTAS DE PRODUTIVIDADE ==============

    @function_tool(
        name="listar_tarefas",
        description="Lista tarefas pendentes do Trello ou Notion. Use para verificar o que precisa ser feito."
    )
    async def listar_tarefas(self, fonte: str = "trello") -> str:
        """
        Lista tarefas.
        
        Args:
            fonte: "trello" ou "notion"
        """
        logger.info(f"Listando tarefas de: {fonte}")
        result = await list_tasks(fonte)
        return format_tasks(result)

    @function_tool(
        name="criar_tarefa",
        description="Cria uma nova tarefa no Trello ou Notion."
    )
    async def criar_tarefa(
        self, 
        titulo: str, 
        descricao: str = "", 
        data_limite: str = "",
        fonte: str = "trello"
    ) -> str:
        """
        Cria uma tarefa.
        
        Args:
            titulo: Título da tarefa
            descricao: Descrição opcional
            data_limite: Data limite (formato ISO)
            fonte: "trello" ou "notion"
        """
        logger.info(f"Criando tarefa: {titulo}")
        result = await create_task(titulo, descricao, data_limite, fonte)
        if result.get("success"):
            return f"✅ {result['message']}"
        return f"❌ Erro: {result.get('error', 'Desconhecido')}"

    @function_tool(
        name="verificar_prazos",
        description="Verifica tarefas com prazo nos próximos dias."
    )
    async def verificar_prazos(self, dias: int = 7, fonte: str = "trello") -> str:
        """
        Verifica prazos próximos.
        
        Args:
            dias: Número de dias para verificar
            fonte: "trello" ou "notion"
        """
        result = await get_upcoming_deadlines(dias, fonte)
        return format_deadlines(result)

    # ============== FERRAMENTAS DE MONITORAMENTO ==============

    @function_tool(
        name="monitorar_sistema",
        description="Mostra métricas detalhadas do sistema: CPU, memória, disco. Use para verificar performance do computador."
    )
    async def monitorar_sistema(self) -> str:
        """Coleta métricas do sistema."""
        logger.info("Coletando métricas do sistema")
        result = await get_system_metrics()
        return format_system_metrics(result)

    @function_tool(
        name="verificar_saude_sistema",
        description="Verifica a saúde do sistema e gera alertas proativos sobre problemas de performance."
    )
    async def verificar_saude_sistema(self) -> str:
        """Verifica saúde do sistema."""
        logger.info("Verificando saúde do sistema")
        result = await check_system_health()
        return format_health_check(result)

    @function_tool(
        name="processos_top",
        description="Lista os processos que mais consomem recursos (CPU ou memória)."
    )
    async def processos_top(self, ordenar_por: str = "memory", limite: int = 10) -> str:
        """
        Lista top processos.
        
        Args:
            ordenar_por: "memory" ou "cpu"
            limite: Número de processos
        """
        logger.info(f"Listando top processos por {ordenar_por}")
        result = await get_top_processes(ordenar_por, limite)
        return format_top_processes(result)

    @function_tool(
        name="identificar_processos_pesados",
        description="Identifica processos consumindo recursos excessivos que podem estar causando lentidão."
    )
    async def identificar_processos_pesados(self) -> str:
        """Identifica resource hogs."""
        logger.info("Identificando processos pesados")
        result = await find_resource_hogs()
        
        if not result.get("success"):
            return f"❌ Erro: {result.get('error')}"
        
        hogs = result.get("resource_hogs", [])
        if not hogs:
            return "✅ Nenhum processo consumindo recursos excessivos."
        
        output = ["⚠️ Processos consumindo muitos recursos:\n"]
        for h in hogs:
            issues = ", ".join(h["issue"]) if h["issue"] else "recursos elevados"
            output.append(f"  • {h['name']} (PID {h['pid']}): {issues}")
        
        return "\n".join(output)


async def entrypoint(ctx: agents.JobContext):
    
    async def shutdown_hook(chat_ctx: ChatContext, mem0: AsyncMemoryClient, memory_str: str):
        logging.info("Shutting down, saving chat context to memory...")

        messages_formatted = []

        logging.info(f"Chat context messages: {chat_ctx.items}")

        for item in chat_ctx.items:
            if not hasattr(item, 'content') or item.content is None:
              continue
            content_str = ''.join(item.content) if isinstance(item.content, list) else str(item.content)

            if memory_str and memory_str in content_str:
                continue

            if item.role in ['user', 'assistant']:
                messages_formatted.append({
                    "role": item.role,
                    "content": content_str.strip()
                })

        logging.info(f"Formatted messages to add to memory: {messages_formatted}")
        # Assuming user_id is consistent
        await mem0.add(messages_formatted, user_id="Thiago")
        logging.info("Chat context saved to memory.")

    # Initialize Memory Client
    mem0 = AsyncMemoryClient()
    user_id = "Thiago"

    # Load existing memories - try get_all first, fallback to search
    initial_ctx = ChatContext()
    memory_str = ''
    results = []
    
    try:
        # Try to get all memories for the user
        results = await mem0.get_all(user_id=user_id)
        logging.info(f"Retrieved {len(results) if results else 0} memories using get_all")
    except Exception as e:
        logging.warning(f"get_all failed: {e}. Trying search method...")
        try:
            # Fallback: use search with a broad query (empty query causes 400 error)
            response = await mem0.search("informações preferências contexto", filters={"user_id": user_id})
            results = response["results"] if isinstance(response, dict) and "results" in response else response
            logging.info(f"Retrieved {len(results) if results else 0} memories using search")
        except Exception as e2:
            logging.warning(f"Search also failed: {e2}. No memories loaded.")
            results = []

    if results:
        memories = [
            {
                "memory": result.get("memory") if isinstance(result, dict) else result.get("memory", ""),
                "updated_at": result.get("updated_at") if isinstance(result, dict) else result.get("updated_at", "")
            }
            for result in results
            if isinstance(result, dict) and result.get("memory")
        ]
        
        if memories:
            memory_str = json.dumps(memories, ensure_ascii=False)
            logging.info(f"Formatted memories: {memory_str}")
            initial_ctx.add_message(
                role="assistant",
                content=f"O nome do usuário é {user_id}. Aqui estão informações importantes sobre ele que você deve lembrar e usar nas conversas: {memory_str}."
            )
    else:
        logging.info("No memories found for this user. Starting fresh conversation.")

    await ctx.connect()

    session = AgentSession()

    agent = Assistant(chat_ctx=initial_ctx)

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Use a shutdown callback to capture the context at the end
    ctx.add_shutdown_callback(lambda: shutdown_hook(session._agent.chat_ctx, mem0, memory_str))

    await session.generate_reply(
        instructions=SESSION_INSTRUCTION  + "\nCumprimente o usuário de forma breve e confiante."
    )


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )

