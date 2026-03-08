from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext, function_tool
from livekit.plugins import noise_cancellation, google
from .prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from .voice_tools import (
    open_application as _open_application, 
    open_website as _open_website, 
    open_folder as _open_folder,
    play_music as _play_music, 
    search_youtube as _search_youtube,
    media_play_pause as _media_play_pause, 
    media_next as _media_next, 
    media_previous as _media_previous,
    volume_up as _volume_up, 
    volume_down as _volume_down, 
    volume_mute as _volume_mute,
    get_system_info as _get_system_info, 
    run_terminal_command as _run_terminal_command,
    search_web_info as _search_web_info,
    open_browser_search as _open_browser_search
)
from mem0 import AsyncMemoryClient
import logging
import os
import json
from pathlib import Path

# Define o diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# FERRAMENTAS DO JARVIS (usando nova API do LiveKit 1.4.x)
# ============================================================================

@function_tool(
    name="open_application",
    description="Abre um aplicativo no computador. Use para abrir Chrome, VS Code, Word, Excel, calculadora, terminal, Discord, Spotify, etc."
)
async def tool_open_application(app_name: str) -> str:
    """
    Abre um aplicativo no computador.
    
    Args:
        app_name: Nome do aplicativo (ex: "chrome", "vscode", "calculadora")
    """
    logger.info(f"🚀 Abrindo aplicativo: {app_name}")
    return await _open_application(app_name)


@function_tool(
    name="open_website",
    description="Abre um site no navegador. Use para YouTube, Google, Gmail, GitHub, Netflix, etc."
)
async def tool_open_website(url_or_name: str) -> str:
    """
    Abre um site no navegador padrão.
    
    Args:
        url_or_name: Nome do site ou URL
    """
    logger.info(f"🌐 Abrindo site: {url_or_name}")
    return await _open_website(url_or_name)


@function_tool(
    name="open_folder",
    description="Abre uma pasta como Downloads, Documentos, Desktop no explorador de arquivos."
)
async def tool_open_folder(folder_name: str) -> str:
    """
    Abre uma pasta no explorador.
    
    Args:
        folder_name: Nome da pasta (downloads, documentos, desktop)
    """
    logger.info(f"📁 Abrindo pasta: {folder_name}")
    return await _open_folder(folder_name)


@function_tool(
    name="play_music",
    description="Busca e toca uma música no YouTube Music. Use quando o usuário pedir para tocar uma música específica."
)
async def tool_play_music(song_name: str, artist: str = "") -> str:
    """
    Busca e toca uma música no YouTube Music.
    
    Args:
        song_name: Nome da música
        artist: Artista (opcional)
    """
    logger.info(f"🎵 Buscando música: {song_name} - {artist}")
    return await _play_music(song_name, artist)


@function_tool(
    name="search_youtube",
    description="Faz uma busca no YouTube. Use quando o usuário quiser pesquisar vídeos."
)
async def tool_search_youtube(query: str) -> str:
    """
    Busca no YouTube.
    
    Args:
        query: Termo de busca
    """
    logger.info(f"🔍 Buscando no YouTube: {query}")
    return await _search_youtube(query)


@function_tool(
    name="media_play_pause",
    description="Pausa ou continua a música/vídeo atual. Use quando pedirem para pausar ou dar play."
)
async def tool_media_play_pause() -> str:
    """Pausa ou retoma a mídia."""
    logger.info("⏯️ Play/Pause")
    return await _media_play_pause()


@function_tool(
    name="media_next",
    description="Pula para a próxima música ou vídeo."
)
async def tool_media_next() -> str:
    """Próxima faixa."""
    logger.info("⏭️ Próxima faixa")
    return await _media_next()


@function_tool(
    name="media_previous",
    description="Volta para a música ou vídeo anterior."
)
async def tool_media_previous() -> str:
    """Faixa anterior."""
    logger.info("⏮️ Faixa anterior")
    return await _media_previous()


@function_tool(
    name="volume_up",
    description="Aumenta o volume do sistema."
)
async def tool_volume_up() -> str:
    """Aumenta o volume."""
    logger.info("🔊 Aumentando volume")
    return await _volume_up()


@function_tool(
    name="volume_down",
    description="Diminui o volume do sistema."
)
async def tool_volume_down() -> str:
    """Diminui o volume."""
    logger.info("🔉 Diminuindo volume")
    return await _volume_down()


@function_tool(
    name="volume_mute",
    description="Muta ou desmuta o áudio do sistema."
)
async def tool_volume_mute() -> str:
    """Muta/desmuta."""
    logger.info("🔇 Mute toggle")
    return await _volume_mute()


@function_tool(
    name="get_system_info",
    description="Retorna informações do sistema: bateria, CPU, memória, disco."
)
async def tool_get_system_info() -> str:
    """Informações do sistema."""
    logger.info("💻 Obtendo info do sistema")
    return await _get_system_info()


@function_tool(
    name="run_terminal_command",
    description="Executa um comando seguro no terminal. Apenas comandos de leitura permitidos."
)
async def tool_run_terminal_command(command: str) -> str:
    """
    Executa comando no terminal.
    
    Args:
        command: Comando a executar (git status, pip list, dir, etc.)
    """
    logger.info(f"⌨️ Executando: {command}")
    return await _run_terminal_command(command)


@function_tool(
    name="search_web_info",
    description="Busca informações na internet e retorna os resultados em TEXTO - NÃO abre o navegador. Use para: notícias, informações sobre pessoas/eventos, preços, fatos. SEMPRE use esta ferramenta quando pedirem informações ou notícias sem pedir para abrir o navegador."
)
async def tool_search_web_info(query: str) -> str:
    """
    Busca informações na web e retorna texto.
    
    Args:
        query: O que buscar (ex: "últimas notícias sobre Bitcoin", "quem é Elon Musk")
    """
    logger.info(f"🔍 Buscando informações: {query}")
    return await _search_web_info(query)


@function_tool(
    name="open_browser_search",
    description="Abre o NAVEGADOR com uma busca no Google. Use APENAS quando o usuário pedir EXPLICITAMENTE para 'abrir no navegador' ou 'mostrar no browser/chrome'."
)
async def tool_open_browser_search(query: str) -> str:
    """
    Abre busca no navegador.
    
    Args:
        query: Termo de busca
    """
    logger.info(f"🌐 Abrindo busca no navegador: {query}")
    return await _open_browser_search(query)


# Lista de todas as ferramentas disponíveis para o agente
JARVIS_TOOLS = [
    tool_open_application,
    tool_open_website,
    tool_open_folder,
    tool_play_music,
    tool_search_youtube,
    tool_media_play_pause,
    tool_media_next,
    tool_media_previous,
    tool_volume_up,
    tool_volume_down,
    tool_volume_mute,
    tool_get_system_info,
    tool_run_terminal_command,
    tool_search_web_info,
    tool_open_browser_search,
]


class Assistant(Agent):
    def __init__(self, chat_ctx: ChatContext = None):
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Charon",
                temperature=0.6,
            ),
            chat_ctx=chat_ctx,
            # Nova API: passa ferramentas como lista
            tools=JARVIS_TOOLS,
        )


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

