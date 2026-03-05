"""
JARVIS CLI - Histórico de Conversas
===================================
Gerencia o histórico de conversas persistente.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

from .config import HISTORY_DIR, ensure_dirs


@dataclass
class Message:
    """Uma mensagem na conversa"""
    role: str  # "user" ou "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    """Uma sessão de chat"""
    id: str
    title: str
    created_at: str
    updated_at: str
    project_path: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    
    def add_message(self, role: str, content: str, agent: Optional[str] = None):
        """Adiciona uma mensagem à sessão"""
        self.messages.append(Message(role=role, content=content, agent=agent))
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "project_path": self.project_path,
            "messages": [asdict(m) for m in self.messages]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ChatSession":
        """Cria sessão a partir de dicionário"""
        messages = [Message(**m) for m in data.get("messages", [])]
        return cls(
            id=data["id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            project_path=data.get("project_path"),
            messages=messages
        )
    
    def export_markdown(self) -> str:
        """Exporta a conversa como Markdown"""
        lines = [
            f"# {self.title}",
            f"\n*Criado em: {self.created_at}*",
            f"*Projeto: {self.project_path or 'N/A'}*\n",
            "---\n"
        ]
        
        for msg in self.messages:
            if msg.role == "user":
                agent_info = f" (@{msg.agent})" if msg.agent else ""
                lines.append(f"## 👤 Usuário{agent_info}\n")
            else:
                lines.append(f"## 🤖 CodeAgent\n")
            
            lines.append(msg.content)
            lines.append("\n---\n")
        
        return "\n".join(lines)


class ChatHistory:
    """Gerencia histórico de conversas"""
    
    def __init__(self):
        ensure_dirs()
        self._current_session: Optional[ChatSession] = None
    
    def new_session(self, title: Optional[str] = None, project_path: Optional[str] = None) -> ChatSession:
        """Cria uma nova sessão de chat"""
        now = datetime.now()
        session_id = str(uuid.uuid4())[:8]
        
        if not title:
            title = f"Sessão {now.strftime('%d/%m %H:%M')}"
        
        self._current_session = ChatSession(
            id=session_id,
            title=title,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            project_path=project_path
        )
        
        return self._current_session
    
    @property
    def current(self) -> Optional[ChatSession]:
        """Retorna sessão atual"""
        return self._current_session
    
    def add_message(self, role: str, content: str, agent: Optional[str] = None):
        """Adiciona mensagem à sessão atual"""
        if self._current_session:
            self._current_session.add_message(role, content, agent)
            self._save_session(self._current_session)
    
    def _get_session_path(self, session_id: str) -> Path:
        """Retorna caminho do arquivo de sessão"""
        return HISTORY_DIR / f"{session_id}.json"
    
    def _save_session(self, session: ChatSession):
        """Salva sessão em arquivo"""
        path = self._get_session_path(session.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """Carrega uma sessão pelo ID"""
        path = self._get_session_path(session_id)
        if not path.exists():
            return None
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._current_session = ChatSession.from_dict(data)
            return self._current_session
        except Exception:
            return None
    
    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Lista sessões recentes"""
        sessions = []
        
        for path in HISTORY_DIR.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                sessions.append({
                    "id": data["id"],
                    "title": data["title"],
                    "updated_at": data["updated_at"],
                    "message_count": len(data.get("messages", []))
                })
            except Exception:
                continue
        
        # Ordenar por data de atualização
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        return sessions[:limit]
    
    def delete_session(self, session_id: str) -> bool:
        """Deleta uma sessão"""
        path = self._get_session_path(session_id)
        if path.exists():
            path.unlink()
            if self._current_session and self._current_session.id == session_id:
                self._current_session = None
            return True
        return False
    
    def export_session(self, session_id: str, output_path: str, format: str = "md") -> bool:
        """Exporta sessão para arquivo"""
        session = self.load_session(session_id)
        if not session:
            return False
        
        try:
            if format == "md":
                content = session.export_markdown()
            elif format == "json":
                content = json.dumps(session.to_dict(), indent=2, ensure_ascii=False)
            else:
                return False
            
            Path(output_path).write_text(content, encoding="utf-8")
            return True
        except Exception:
            return False
    
    def get_last_session(self) -> Optional[ChatSession]:
        """Retorna a última sessão"""
        sessions = self.list_sessions(limit=1)
        if sessions:
            return self.load_session(sessions[0]["id"])
        return None
    
    def continue_last(self) -> Optional[ChatSession]:
        """Continua a última sessão"""
        return self.get_last_session()
