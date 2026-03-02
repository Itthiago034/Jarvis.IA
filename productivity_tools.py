"""
Módulo de produtividade para o JARVIS.
Integra com Trello, Notion e Microsoft To-Do para gerenciamento de tarefas.

CONFIGURAÇÃO NECESSÁRIA:
- Crie um arquivo .env com as chaves de API
- Ou configure as variáveis de ambiente

Variáveis necessárias:
- TRELLO_API_KEY: Obter em https://trello.com/app-key
- TRELLO_TOKEN: Gerado após autorização
- NOTION_API_KEY: Obter em https://www.notion.so/my-integrations
- NOTION_DATABASE_ID: ID do banco de dados de tarefas
"""

import asyncio
import aiohttp
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ============== CONFIGURAÇÃO ==============

# Carregar do ambiente
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY", "")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN", "")
TRELLO_DEFAULT_BOARD = os.getenv("TRELLO_BOARD_ID", "")
TRELLO_DEFAULT_LIST = os.getenv("TRELLO_LIST_ID", "")

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")

REQUEST_TIMEOUT = 15


# ============== CLASSES DE DADOS ==============

@dataclass
class Task:
    """Representa uma tarefa."""
    id: str
    title: str
    description: str = ""
    due_date: Optional[str] = None
    status: str = "pendente"
    priority: str = "normal"
    source: str = "local"  # trello, notion, todo


# ============== TRELLO ==============

class TrelloClient:
    """Cliente para API do Trello."""
    
    BASE_URL = "https://api.trello.com/1"
    
    def __init__(self, api_key: str = TRELLO_API_KEY, token: str = TRELLO_TOKEN):
        self.api_key = api_key
        self.token = token
        self.configured = bool(api_key and token)
    
    def _get_auth_params(self) -> Dict[str, str]:
        return {"key": self.api_key, "token": self.token}
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Faz requisição à API do Trello."""
        if not self.configured:
            return {"success": False, "error": "Trello não configurado. Configure TRELLO_API_KEY e TRELLO_TOKEN."}
        
        url = f"{self.BASE_URL}{endpoint}"
        params = {**self._get_auth_params(), **kwargs.get("params", {})}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, 
                    params=params,
                    json=kwargs.get("json"),
                    timeout=REQUEST_TIMEOUT
                ) as response:
                    if response.status >= 400:
                        text = await response.text()
                        return {"success": False, "error": f"HTTP {response.status}: {text}"}
                    
                    data = await response.json()
                    return {"success": True, "data": data}
        except Exception as e:
            logger.error(f"Erro Trello: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_boards(self) -> Dict[str, Any]:
        """Lista os boards do usuário."""
        return await self._request("GET", "/members/me/boards")
    
    async def get_lists(self, board_id: str) -> Dict[str, Any]:
        """Lista as listas de um board."""
        return await self._request("GET", f"/boards/{board_id}/lists")
    
    async def get_cards(self, list_id: str = "", board_id: str = "") -> Dict[str, Any]:
        """Lista os cards de uma lista ou board."""
        if list_id:
            return await self._request("GET", f"/lists/{list_id}/cards")
        elif board_id:
            return await self._request("GET", f"/boards/{board_id}/cards")
        else:
            return {"success": False, "error": "Especifique list_id ou board_id"}
    
    async def create_card(
        self, 
        name: str, 
        list_id: str = TRELLO_DEFAULT_LIST,
        description: str = "",
        due_date: str = ""
    ) -> Dict[str, Any]:
        """Cria um novo card no Trello."""
        if not list_id:
            return {"success": False, "error": "List ID não configurado"}
        
        params = {
            "name": name,
            "idList": list_id,
            "desc": description
        }
        if due_date:
            params["due"] = due_date
        
        return await self._request("POST", "/cards", params=params)
    
    async def move_card(self, card_id: str, list_id: str) -> Dict[str, Any]:
        """Move um card para outra lista."""
        return await self._request("PUT", f"/cards/{card_id}", params={"idList": list_id})
    
    async def archive_card(self, card_id: str) -> Dict[str, Any]:
        """Arquiva um card (marca como concluído)."""
        return await self._request("PUT", f"/cards/{card_id}", params={"closed": "true"})


# ============== NOTION ==============

class NotionClient:
    """Cliente para API do Notion."""
    
    BASE_URL = "https://api.notion.com/v1"
    API_VERSION = "2022-06-28"
    
    def __init__(self, api_key: str = NOTION_API_KEY, database_id: str = NOTION_DATABASE_ID):
        self.api_key = api_key
        self.database_id = database_id
        self.configured = bool(api_key and database_id)
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": self.API_VERSION
        }
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Faz requisição à API do Notion."""
        if not self.configured:
            return {"success": False, "error": "Notion não configurado. Configure NOTION_API_KEY e NOTION_DATABASE_ID."}
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url,
                    headers=self._get_headers(),
                    json=kwargs.get("json"),
                    timeout=REQUEST_TIMEOUT
                ) as response:
                    data = await response.json()
                    
                    if response.status >= 400:
                        return {"success": False, "error": data.get("message", f"HTTP {response.status}")}
                    
                    return {"success": True, "data": data}
        except Exception as e:
            logger.error(f"Erro Notion: {e}")
            return {"success": False, "error": str(e)}
    
    async def query_database(self, filter_obj: Dict = None) -> Dict[str, Any]:
        """Consulta o banco de dados de tarefas."""
        body = {}
        if filter_obj:
            body["filter"] = filter_obj
        
        return await self._request("POST", f"/databases/{self.database_id}/query", json=body)
    
    async def create_page(
        self,
        title: str,
        properties: Dict = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """Cria uma nova página (tarefa) no Notion."""
        body = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {  # Assumindo que a coluna de nome é "Name"
                    "title": [{"text": {"content": title}}]
                },
                **(properties or {})
            }
        }
        
        if description:
            body["children"] = [{
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": description}}]
                }
            }]
        
        return await self._request("POST", "/pages", json=body)
    
    async def update_page(self, page_id: str, properties: Dict) -> Dict[str, Any]:
        """Atualiza propriedades de uma página."""
        body = {"properties": properties}
        return await self._request("PATCH", f"/pages/{page_id}", json=body)


# ============== FUNÇÕES DE PRODUTIVIDADE (ALTO NÍVEL) ==============

async def list_tasks(source: str = "trello") -> Dict[str, Any]:
    """
    Lista tarefas pendentes.
    
    Args:
        source: "trello" ou "notion"
    
    Returns:
        Dict com success e lista de tarefas
    """
    if source.lower() == "trello":
        client = TrelloClient()
        if not client.configured:
            return {"success": False, "error": "Trello não configurado", "tasks": []}
        
        result = await client.get_cards(list_id=TRELLO_DEFAULT_LIST)
        if not result.get("success"):
            return {"success": False, "error": result.get("error"), "tasks": []}
        
        tasks = []
        for card in result.get("data", []):
            tasks.append(Task(
                id=card["id"],
                title=card["name"],
                description=card.get("desc", ""),
                due_date=card.get("due"),
                status="pendente" if not card.get("dueComplete") else "concluído",
                source="trello"
            ))
        
        return {"success": True, "tasks": tasks, "source": "trello"}
    
    elif source.lower() == "notion":
        client = NotionClient()
        if not client.configured:
            return {"success": False, "error": "Notion não configurado", "tasks": []}
        
        result = await client.query_database()
        if not result.get("success"):
            return {"success": False, "error": result.get("error"), "tasks": []}
        
        tasks = []
        for page in result.get("data", {}).get("results", []):
            props = page.get("properties", {})
            # Extrair título (assume coluna "Name" ou "Title")
            title_prop = props.get("Name") or props.get("Title") or {}
            title = ""
            if title_prop.get("title"):
                title = title_prop["title"][0]["plain_text"] if title_prop["title"] else ""
            
            tasks.append(Task(
                id=page["id"],
                title=title,
                source="notion"
            ))
        
        return {"success": True, "tasks": tasks, "source": "notion"}
    
    else:
        return {"success": False, "error": f"Fonte desconhecida: {source}", "tasks": []}


async def create_task(
    title: str,
    description: str = "",
    due_date: str = "",
    source: str = "trello"
) -> Dict[str, Any]:
    """
    Cria uma nova tarefa.
    
    Args:
        title: Título da tarefa
        description: Descrição opcional
        due_date: Data de vencimento (formato ISO)
        source: "trello" ou "notion"
    
    Returns:
        Dict com success e tarefa criada
    """
    if source.lower() == "trello":
        client = TrelloClient()
        result = await client.create_card(title, description=description, due_date=due_date)
        if result.get("success"):
            return {
                "success": True,
                "message": f"Tarefa '{title}' criada no Trello",
                "task_id": result["data"]["id"]
            }
        return result
    
    elif source.lower() == "notion":
        client = NotionClient()
        result = await client.create_page(title, description=description)
        if result.get("success"):
            return {
                "success": True,
                "message": f"Tarefa '{title}' criada no Notion",
                "task_id": result["data"]["id"]
            }
        return result
    
    else:
        return {"success": False, "error": f"Fonte desconhecida: {source}"}


async def complete_task(task_id: str, source: str = "trello") -> Dict[str, Any]:
    """
    Marca uma tarefa como concluída.
    
    Args:
        task_id: ID da tarefa
        source: "trello" ou "notion"
    
    Returns:
        Dict com success
    """
    if source.lower() == "trello":
        client = TrelloClient()
        result = await client.archive_card(task_id)
        if result.get("success"):
            return {"success": True, "message": "Tarefa arquivada no Trello"}
        return result
    
    elif source.lower() == "notion":
        client = NotionClient()
        # Assume que há uma propriedade "Status" do tipo "select"
        result = await client.update_page(task_id, {
            "Status": {"select": {"name": "Concluído"}}
        })
        if result.get("success"):
            return {"success": True, "message": "Tarefa concluída no Notion"}
        return result
    
    else:
        return {"success": False, "error": f"Fonte desconhecida: {source}"}


async def get_upcoming_deadlines(days: int = 7, source: str = "trello") -> Dict[str, Any]:
    """
    Lista tarefas com prazo nos próximos X dias.
    
    Args:
        days: Número de dias para verificar
        source: "trello" ou "notion"
    
    Returns:
        Dict com tarefas próximas do vencimento
    """
    result = await list_tasks(source)
    if not result.get("success"):
        return result
    
    upcoming = []
    now = datetime.now()
    cutoff = now + timedelta(days=days)
    
    for task in result.get("tasks", []):
        if task.due_date:
            try:
                due = datetime.fromisoformat(task.due_date.replace("Z", "+00:00"))
                if due <= cutoff:
                    upcoming.append({
                        "title": task.title,
                        "due_date": task.due_date,
                        "days_left": (due - now).days
                    })
            except:
                pass
    
    # Ordenar por data
    upcoming.sort(key=lambda x: x.get("days_left", 999))
    
    return {
        "success": True,
        "upcoming": upcoming,
        "count": len(upcoming)
    }


# ============== FORMATAÇÃO ==============

def format_tasks(result: Dict[str, Any]) -> str:
    """Formata lista de tarefas para exibição."""
    if not result.get("success"):
        return f"❌ Erro: {result.get('error', 'Desconhecido')}"
    
    tasks = result.get("tasks", [])
    if not tasks:
        return "📋 Nenhuma tarefa encontrada."
    
    output = [f"📋 Tarefas ({result.get('source', 'desconhecido')}):\n"]
    
    for i, task in enumerate(tasks, 1):
        status_icon = "✅" if task.status == "concluído" else "⬜"
        due = f" 📅 {task.due_date[:10]}" if task.due_date else ""
        output.append(f"{status_icon} {i}. {task.title}{due}")
    
    return "\n".join(output)


def format_deadlines(result: Dict[str, Any]) -> str:
    """Formata prazos para exibição."""
    if not result.get("success"):
        return f"❌ Erro: {result.get('error', 'Desconhecido')}"
    
    upcoming = result.get("upcoming", [])
    if not upcoming:
        return "✅ Nenhum prazo próximo."
    
    output = ["⏰ Prazos próximos:\n"]
    
    for task in upcoming:
        days = task["days_left"]
        if days < 0:
            urgency = "🔴 ATRASADO"
        elif days == 0:
            urgency = "🟠 HOJE"
        elif days == 1:
            urgency = "🟡 AMANHÃ"
        else:
            urgency = f"🟢 {days} dias"
        
        output.append(f"  • {task['title']} - {urgency}")
    
    return "\n".join(output)


# ============== VERIFICAR CONFIGURAÇÃO ==============

def check_productivity_config() -> Dict[str, bool]:
    """Verifica quais integrações estão configuradas."""
    return {
        "trello": bool(TRELLO_API_KEY and TRELLO_TOKEN),
        "notion": bool(NOTION_API_KEY and NOTION_DATABASE_ID)
    }


# ============== TESTE ==============

if __name__ == "__main__":
    print("=== VERIFICAÇÃO DE CONFIGURAÇÃO ===\n")
    config = check_productivity_config()
    
    for service, configured in config.items():
        status = "✅ Configurado" if configured else "❌ Não configurado"
        print(f"{service}: {status}")
    
    print("\n=== INSTRUÇÕES DE CONFIGURAÇÃO ===")
    print("""
Para configurar o Trello:
1. Acesse https://trello.com/app-key
2. Copie a API Key
3. Clique em "Token" e autorize
4. Adicione ao .env:
   TRELLO_API_KEY=sua_key
   TRELLO_TOKEN=seu_token
   TRELLO_BOARD_ID=id_do_board
   TRELLO_LIST_ID=id_da_lista

Para configurar o Notion:
1. Acesse https://www.notion.so/my-integrations
2. Crie uma nova integração
3. Copie o token
4. Compartilhe o database com a integração
5. Adicione ao .env:
   NOTION_API_KEY=seu_token
   NOTION_DATABASE_ID=id_do_database
""")
