# 🦅 PROPOSTA DE APRIMORAMENTO - OPENCLAW v3.0

> **Análise Arquitetural e Roadmap de Evolução**  
> Autor: Arquitetura de Software & Engenharia de IA  
> Data: Março 2026  
> Versão Atual: 0.2.0 (JARVIS) → Versão Alvo: 3.0.0 (OpenClaw)

---

## 🔄 REBRANDING: JARVIS → OPENCLAW

O projeto está evoluindo de **JARVIS** para **OpenClaw** - um assistente de IA mais inteligente, seguro e autônomo.

### Por que OpenClaw?
- **Open** - Código aberto, transparente, extensível
- **Claw** - Garras que agarram e executam tarefas com precisão

### Principais Evoluções
| Aspecto | JARVIS (v0.2) | OpenClaw (v3.0) |
|---------|---------------|-----------------|
| **Autonomia** | Reativo (só responde) | Proativo (aprende e age) |
| **Segurança** | Básica | Enterprise-grade |
| **Web Access** | Limitado | Secure Web Fetch |
| **Aprendizado** | Memória simples | Routine Learning |
| **Proteção** | Nenhuma | Anti-hacker, Encryption |

---

## 📋 Sumário Executivo

O OpenClaw (anteriormente JARVIS) atingiu uma maturidade considerável com:
- **Agente de voz funcional** (LiveKit + Google Realtime)
- **Sistema de plugins extensível** (15+ plugins/tools)
- **Memória persistente** (mem0)
- **CodeAgent poderoso** (50+ ferramentas)

Este documento propõe evoluções em **seis pilares**:
1. 🏗️ **Arquitetura** - Modernização e escalabilidade
2. ⚡ **Performance** - Otimização de componentes críticos
3. ✨ **Features** - Novas funcionalidades de alto impacto
4. 🔒 **Segurança** - Proteção enterprise contra ataques e vazamentos
5. 🧠 **Aprendizado de Rotina** - Ações autônomas baseadas em padrões
6. 🌐 **Web Fetch Seguro** - Acesso à internet com proteção

---

## 🏗️ PARTE 1: EVOLUÇÃO DA ARQUITETURA

### 1.1 Arquitetura Atual vs. Proposta

```
┌──────────────────────────────────────────────────────────────────────┐
│                    ARQUITETURA ATUAL (v0.2)                          │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   LiveKit   │────▶│   Agent     │────▶│  Functions  │
│   (Audio)   │     │  (Gemini)   │     │  (ctypes)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │    mem0     │
                    │  (memória)  │
                    └─────────────┘

Problemas:
❌ Acoplamento direto Agent → Functions
❌ Sem camada de abstração
❌ Plugins desconectados do fluxo principal
❌ Sem observabilidade
❌ Windows-only
```

```
┌──────────────────────────────────────────────────────────────────────┐
│                    ARQUITETURA PROPOSTA (v3.0)                       │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ LiveKit  │  │   CLI    │  │  WebAPI  │  │  gRPC    │            │
│  │ (Voice)  │  │ (Typer)  │  │ (FastAPI)│  │ (future) │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┴─────────────┴─────────────┴─────────────┴──────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    Message Broker / Event Bus                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Redis Streams / RabbitMQ / In-Memory (aio-pika alternativa)│   │
│  │  - Comandos async                                            │   │
│  │  - Event sourcing                                            │   │
│  │  - Dead letter queue                                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    Orchestrator (Core Brain)                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Intent Router                                                 │ │
│  │  ├── Intent Classification (local ou LLM)                      │ │
│  │  ├── Multi-turn Conversation State Machine                     │ │
│  │  ├── Plugin Selector (smart routing)                           │ │
│  │  └── Fallback Handler                                          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  LLM Manager                                                    │ │
│  │  ├── Primary: Google Gemini (Realtime + Standard)              │ │
│  │  ├── Fallback: Ollama (local) / Groq (fast)                    │ │
│  │  ├── Specialized: Claude (code) / GPT-4 (reasoning)            │ │
│  │  └── Router based on task type                                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    Execution Layer (Workers)                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │  Plugin    │  │   Tool     │  │  CodeAgent │  │ Automation │    │
│  │  Executor  │  │  Executor  │  │  Executor  │  │  Executor  │    │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │
│        │               │               │               │            │
│  ┌─────▼───────────────▼───────────────▼───────────────▼──────┐    │
│  │              Sandbox / Isolation Layer                     │    │
│  │  - Docker containers (opcional)                            │    │
│  │  - Process isolation (multiprocessing)                     │    │
│  │  - Resource limits (CPU, Memory, I/O)                      │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    Platform Abstraction Layer                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  OS Adapters                                                    │ │
│  │  ├── WindowsAdapter (atual, ctypes/subprocess)                 │ │
│  │  ├── LinuxAdapter (xdotool, dbus)                              │ │
│  │  ├── MacAdapter (osascript, AppleScript)                       │ │
│  │  └── UniversalAdapter (cross-platform fallback)                │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    Data & Memory Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Short-term │  │   Long-term  │  │   Semantic   │              │
│  │   (Redis)    │  │   (mem0/SQL) │  │   (Chroma)   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                     │
│  Memory Types:                                                      │
│  ├── Working Memory (sessão atual)                                 │
│  ├── Episodic Memory (eventos passados)                            │
│  ├── Semantic Memory (fatos/conhecimento)                          │
│  └── Procedural Memory (como fazer coisas)                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    Observability Layer                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │ Structured │  │  Metrics   │  │  Tracing   │  │  Alerting  │    │
│  │  Logging   │  │ (Prometheus│  │ (OpenTelm) │  │  (Webhooks)│    │
│  │ (structlog)│  │  /StatsD)  │  │            │  │            │    │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Modernização do Sistema de Memória

**Problema Atual:**
```python
# Código atual - fallback fraco
try:
    results = await mem0.get_all(user_id=user_id)
except Exception as e:
    # Fallback genérico que pode não encontrar nada relevante
    response = await mem0.search("informações preferências contexto", ...)
```

**Solução Proposta - Sistema de Memória Hierárquica:**

```python
# Proposta: src/jarvis/memory/memory_manager.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
import hashlib
from datetime import datetime, timedelta

class MemoryType(Enum):
    WORKING = "working"      # Sessão atual (Redis/in-memory)
    EPISODIC = "episodic"    # Eventos passados (mem0)
    SEMANTIC = "semantic"    # Fatos/conhecimento (ChromaDB)
    PROCEDURAL = "procedural" # Como fazer (templates)

@dataclass
class Memory:
    id: str
    content: str
    memory_type: MemoryType
    importance: float  # 0.0 - 1.0
    created_at: datetime
    last_accessed: datetime
    access_count: int
    embedding: Optional[List[float]] = None
    metadata: dict = None
    
    @property
    def relevance_score(self) -> float:
        """Score que decai com tempo mas aumenta com acessos."""
        age_days = (datetime.now() - self.last_accessed).days
        decay = 0.95 ** age_days  # 5% decay por dia
        access_boost = min(self.access_count / 10, 1.0)
        return self.importance * decay * (1 + access_boost)

class MemoryManager:
    """Gerenciador unificado de memória com múltiplos backends."""
    
    def __init__(self):
        self.working = WorkingMemory()   # Redis/dict
        self.episodic = EpisodicMemory() # mem0
        self.semantic = SemanticMemory() # ChromaDB (LOCAL, GRÁTIS)
        
    async def remember(
        self, 
        content: str, 
        memory_type: MemoryType,
        importance: float = 0.5,
        deduplicate: bool = True
    ) -> Memory:
        """Armazena uma nova memória com deduplicação."""
        
        if deduplicate:
            # Hash para detectar duplicatas
            content_hash = hashlib.md5(content.encode()).hexdigest()
            existing = await self._find_by_hash(content_hash)
            if existing:
                existing.access_count += 1
                existing.last_accessed = datetime.now()
                return existing
        
        memory = Memory(
            id=str(uuid4()),
            content=content,
            memory_type=memory_type,
            importance=importance,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1
        )
        
        await self._store(memory)
        return memory
    
    async def recall(
        self, 
        query: str,
        memory_types: List[MemoryType] = None,
        limit: int = 10,
        min_relevance: float = 0.3
    ) -> List[Memory]:
        """Recupera memórias relevantes com ranking."""
        
        all_memories = []
        
        # Busca em paralelo em todos os backends
        tasks = [
            self.working.search(query, limit),
            self.episodic.search(query, limit),
            self.semantic.search(query, limit)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_memories.extend(result)
        
        # Filtra por tipo se especificado
        if memory_types:
            all_memories = [m for m in all_memories if m.memory_type in memory_types]
        
        # Rankeia por relevância
        all_memories.sort(key=lambda m: m.relevance_score, reverse=True)
        
        # Filtra por threshold
        return [m for m in all_memories[:limit] if m.relevance_score >= min_relevance]
    
    async def consolidate(self):
        """Consolida memórias de working → episodic (executar periodicamente)."""
        working_memories = await self.working.get_all()
        
        for memory in working_memories:
            if memory.importance >= 0.7:
                # Memórias importantes vão para episodic
                await self.episodic.store(memory)
            elif memory.access_count >= 3:
                # Memórias acessadas frequentemente também
                await self.episodic.store(memory)
        
        # Limpa working memory
        await self.working.clear_old(max_age_hours=24)
    
    async def forget(self, max_age_days: int = 180):
        """Remove memórias antigas e irrelevantes."""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        
        # Remove de cada backend
        await asyncio.gather(
            self.episodic.delete_before(cutoff),
            self.semantic.delete_before(cutoff)
        )
```

**Backends Recomendados (GRATUITOS):**

| Backend | Uso | Custo |
|---------|-----|-------|
| **Redis** | Working memory (sessão) | Grátis (local) |
| **ChromaDB** | Semantic search (embeddings) | Grátis, open-source |
| **SQLite** | Episodic (backup local) | Grátis, nativo Python |
| **mem0** | Episodic (cloud opcional) | Tier gratuito disponível |

---

### 1.3 Sistema de Multi-LLM com Fallback

**Problema Atual:**
```python
# Só usa Google Realtime, sem fallback
llm=google.beta.realtime.RealtimeModel(
    voice="Charon",
    temperature=0.6,
)
```

**Solução - LLM Router Inteligente:**

```python
# Proposta: src/jarvis/llm/llm_router.py

from enum import Enum
from typing import Optional, Callable
import asyncio

class LLMProvider(Enum):
    GOOGLE_REALTIME = "google_realtime"  # Voz em tempo real
    GOOGLE_GEMINI = "google_gemini"      # Texto rápido
    OLLAMA_LOCAL = "ollama_local"        # Offline/privacidade
    GROQ = "groq"                        # Ultra-rápido
    ANTHROPIC = "anthropic"              # Raciocínio complexo

class TaskComplexity(Enum):
    SIMPLE = "simple"       # "que horas são?"
    MODERATE = "moderate"   # "abra o youtube"
    COMPLEX = "complex"     # "analise este código"
    EXPERT = "expert"       # "refatore todo o projeto"

class LLMRouter:
    """
    Router inteligente que escolhe o melhor LLM para cada tarefa.
    Prioriza modelos locais/gratuitos sempre que possível.
    """
    
    def __init__(self):
        self.providers = {}
        self.fallback_chain = [
            LLMProvider.GOOGLE_REALTIME,
            LLMProvider.GOOGLE_GEMINI,
            LLMProvider.OLLAMA_LOCAL,  # Fallback local se APIs falharem
        ]
        self.metrics = LLMMetrics()
        
    def register_provider(
        self, 
        provider: LLMProvider, 
        client: any,
        health_check: Callable
    ):
        """Registra um provedor de LLM."""
        self.providers[provider] = {
            "client": client,
            "health_check": health_check,
            "available": True,
            "latency_avg": 0.0,
            "error_rate": 0.0
        }
    
    async def route(
        self, 
        request: str,
        complexity: TaskComplexity = None,
        require_voice: bool = False,
        require_code: bool = False,
        max_latency_ms: int = None
    ) -> tuple[LLMProvider, any]:
        """
        Roteia para o melhor LLM disponível.
        
        Strategy:
        1. Se require_voice → Google Realtime (único com streaming de voz)
        2. Se require_code → Prefere Anthropic/Gemini (melhores para código)
        3. Se max_latency → Prefere Groq/Ollama (mais rápidos)
        4. Fallback em cascata se primário falhar
        """
        
        # Voice streaming só funciona com Google Realtime
        if require_voice:
            return await self._get_with_fallback(LLMProvider.GOOGLE_REALTIME)
        
        # Auto-detect complexity se não fornecida
        if complexity is None:
            complexity = self._classify_complexity(request)
        
        # Escolhe provedor baseado em complexidade
        preferred = self._select_by_complexity(complexity, require_code)
        
        # Verifica latência se especificada
        if max_latency_ms:
            preferred = self._filter_by_latency(preferred, max_latency_ms)
        
        return await self._get_with_fallback(preferred)
    
    def _classify_complexity(self, request: str) -> TaskComplexity:
        """Classifica complexidade da requisição (heurística local)."""
        
        # Keywords simples
        simple_patterns = [
            "que horas", "que dia", "data", "hora",
            "abrir", "abra", "abre", "fechar",
            "aumentar volume", "diminuir volume",
            "pausar", "play", "próxima"
        ]
        
        # Keywords complexas
        complex_patterns = [
            "analise", "analisa", "código", "error",
            "explique", "como funciona", "debug",
            "refatore", "otimize", "crie um"
        ]
        
        request_lower = request.lower()
        
        if any(p in request_lower for p in simple_patterns):
            return TaskComplexity.SIMPLE
        if any(p in request_lower for p in complex_patterns):
            return TaskComplexity.COMPLEX
        
        # Heurística por tamanho
        if len(request) < 30:
            return TaskComplexity.SIMPLE
        elif len(request) < 100:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.COMPLEX
    
    def _select_by_complexity(
        self, 
        complexity: TaskComplexity,
        require_code: bool
    ) -> LLMProvider:
        """Seleciona provedor por complexidade."""
        
        if require_code:
            # Para código, prefere Gemini (bom e gratuito)
            return LLMProvider.GOOGLE_GEMINI
        
        mapping = {
            TaskComplexity.SIMPLE: LLMProvider.OLLAMA_LOCAL,  # Rápido, offline
            TaskComplexity.MODERATE: LLMProvider.GOOGLE_GEMINI,
            TaskComplexity.COMPLEX: LLMProvider.GOOGLE_GEMINI,
            TaskComplexity.EXPERT: LLMProvider.GOOGLE_GEMINI,
        }
        
        return mapping.get(complexity, LLMProvider.GOOGLE_GEMINI)
    
    async def _get_with_fallback(self, preferred: LLMProvider):
        """Tenta provedor preferido, fallback em cascata se falhar."""
        
        # Tenta o preferido primeiro
        if await self._is_available(preferred):
            return preferred, self.providers[preferred]["client"]
        
        # Fallback chain
        for provider in self.fallback_chain:
            if provider != preferred and await self._is_available(provider):
                logger.warning(f"Fallback: {preferred} → {provider}")
                return provider, self.providers[provider]["client"]
        
        raise RuntimeError("Nenhum LLM disponível!")
    
    async def _is_available(self, provider: LLMProvider) -> bool:
        """Verifica disponibilidade com health check."""
        if provider not in self.providers:
            return False
        
        p = self.providers[provider]
        
        # Cache de disponibilidade por 30s
        if p.get("last_check") and (time.time() - p["last_check"]) < 30:
            return p["available"]
        
        try:
            available = await asyncio.wait_for(
                p["health_check"](),
                timeout=5.0
            )
            p["available"] = available
            p["last_check"] = time.time()
            return available
        except:
            p["available"] = False
            return False
```

**Configuração de Provedores Gratuitos:**

```python
# src/jarvis/llm/providers.py

# 1. OLLAMA (Local, totalmente gratuito)
# Instalar: https://ollama.ai
# Modelos recomendados: llama3.2, mistral, gemma2

async def setup_ollama():
    """Configura Ollama como LLM local gratuito."""
    import ollama
    
    # Verifica se Ollama está rodando
    try:
        ollama.list()
        return OllamaClient()
    except:
        logger.warning("Ollama não está rodando. Execute: ollama serve")
        return None

# 2. GROQ (API gratuita, ultra-rápida)
# Registro: https://console.groq.com (gratuito)
# Limite: 30 req/min no tier free

async def setup_groq():
    """Configura Groq para responses ultra-rápidas."""
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    
    return Groq(api_key=api_key)

# 3. Google Gemini (Tier gratuito generoso)
# 15 RPM, 1M tokens/dia grátis

async def setup_gemini():
    """Configura Google Gemini."""
    import google.generativeai as genai
    
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    return genai.GenerativeModel("gemini-1.5-flash")
```

---

### 1.4 Platform Abstraction Layer (Cross-Platform)

**Problema Atual:**
```python
# Windows-only no voice_tools.py
subprocess.Popen("start chrome", shell=True)  # Só funciona no Windows
ctypes.windll.user32.keybd_event(...)          # Windows API
```

**Solução - Abstração de Plataforma:**

```python
# Proposta: src/jarvis/platform/adapters.py

from abc import ABC, abstractmethod
import platform
import subprocess
from typing import Optional

class PlatformAdapter(ABC):
    """Interface abstrata para operações de sistema."""
    
    @abstractmethod
    async def open_application(self, app_name: str) -> str:
        pass
    
    @abstractmethod
    async def open_url(self, url: str) -> str:
        pass
    
    @abstractmethod
    async def send_media_key(self, key: str) -> str:
        pass
    
    @abstractmethod
    async def get_system_info(self) -> dict:
        pass
    
    @abstractmethod
    async def run_command(self, command: str, safe_only: bool = True) -> str:
        pass


class WindowsAdapter(PlatformAdapter):
    """Adaptador para Windows (implementação atual)."""
    
    APPS = {
        "chrome": "start chrome",
        "vscode": "code",
        "terminal": "start wt",
        "explorer": "explorer",
        # ... resto do mapeamento atual
    }
    
    async def open_application(self, app_name: str) -> str:
        cmd = self.APPS.get(app_name.lower())
        if cmd:
            subprocess.Popen(cmd, shell=True)
            return f"Aplicativo '{app_name}' aberto."
        return f"Aplicativo '{app_name}' não encontrado."
    
    async def send_media_key(self, key: str) -> str:
        import ctypes
        
        KEYS = {
            "play_pause": 0xB3,
            "next": 0xB0,
            "previous": 0xB1,
            "volume_up": 0xAF,
            "volume_down": 0xAE,
            "mute": 0xAD,
        }
        
        vk = KEYS.get(key)
        if vk:
            ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
            return f"Tecla '{key}' enviada."
        return f"Tecla '{key}' não reconhecida."


class LinuxAdapter(PlatformAdapter):
    """Adaptador para Linux (NOVO)."""
    
    APPS = {
        "chrome": "google-chrome",
        "firefox": "firefox",
        "vscode": "code",
        "terminal": "gnome-terminal",
        "explorer": "nautilus",
    }
    
    async def open_application(self, app_name: str) -> str:
        cmd = self.APPS.get(app_name.lower(), app_name)
        try:
            subprocess.Popen([cmd], start_new_session=True)
            return f"Aplicativo '{app_name}' aberto."
        except FileNotFoundError:
            return f"Aplicativo '{app_name}' não encontrado."
    
    async def open_url(self, url: str) -> str:
        subprocess.Popen(["xdg-open", url])
        return f"URL aberta: {url}"
    
    async def send_media_key(self, key: str) -> str:
        # Usa playerctl (instalável via apt/pacman)
        import shutil
        
        if not shutil.which("playerctl"):
            return "playerctl não instalado. Execute: sudo apt install playerctl"
        
        COMMANDS = {
            "play_pause": "playerctl play-pause",
            "next": "playerctl next",
            "previous": "playerctl previous",
        }
        
        cmd = COMMANDS.get(key)
        if cmd:
            subprocess.run(cmd.split())
            return f"Comando '{key}' executado."
        
        # Volume via pactl
        if key == "volume_up":
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])
        elif key == "volume_down":
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"])
        elif key == "mute":
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
        
        return f"Volume '{key}' ajustado."


class MacAdapter(PlatformAdapter):
    """Adaptador para macOS (NOVO)."""
    
    async def open_application(self, app_name: str) -> str:
        # macOS usa 'open -a'
        try:
            subprocess.run(["open", "-a", app_name])
            return f"Aplicativo '{app_name}' aberto."
        except:
            return f"Erro ao abrir '{app_name}'."
    
    async def open_url(self, url: str) -> str:
        subprocess.run(["open", url])
        return f"URL aberta: {url}"
    
    async def send_media_key(self, key: str) -> str:
        # macOS usa osascript para controle de mídia
        scripts = {
            "play_pause": 'tell application "Music" to playpause',
            "next": 'tell application "Music" to next track',
            "previous": 'tell application "Music" to previous track',
        }
        
        script = scripts.get(key)
        if script:
            subprocess.run(["osascript", "-e", script])
            return f"Comando '{key}' executado."
        
        # Volume
        if key == "volume_up":
            subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
        elif key == "volume_down":
            subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
        
        return f"Volume ajustado."


def get_platform_adapter() -> PlatformAdapter:
    """Factory que retorna o adaptador correto para o OS atual."""
    system = platform.system().lower()
    
    if system == "windows":
        return WindowsAdapter()
    elif system == "linux":
        return LinuxAdapter()
    elif system == "darwin":  # macOS
        return MacAdapter()
    else:
        raise RuntimeError(f"Sistema operacional não suportado: {system}")
```

---

## ⚡ PARTE 2: ALTERNATIVAS EFICIENTES

### 2.1 Funções Lentas/Ineficientes Identificadas

| Componente | Problema | Impacto | Solução |
|------------|----------|---------|---------|
| **Plugin Matching** | O(n×m) linear search | Latência em cada comando | Indexação com Trie/Hash |
| **mem0 Fallback** | Query genérica ineficaz | Memórias relevantes perdidas | Semantic search local |
| **Tool Discovery** | Glob + importlib em cada init | Startup lento | Cache + lazy loading |
| **HTTP Requests** | Síncronos (requests) | Blocking I/O | aiohttp everywhere |
| **Voice Embedding** | Resemblyzer (2019) | Menos preciso | Whisper/Pyannote |
| **File Operations** | Síncronas | Blocking em I/O pesado | aiofiles |

### 2.2 Alternativas Gratuitas Recomendadas

#### **2.2.1 Para Busca/Embedding (substituir parte do mem0)**

```python
# ChromaDB - Vector DB local, totalmente gratuito
# Instalação: pip install chromadb

import chromadb
from chromadb.utils import embedding_functions

# Usar embedding gratuito do Sentence Transformers
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # Leve e eficiente
)

client = chromadb.PersistentClient(path="./jarvis_memories")
collection = client.get_or_create_collection(
    name="memories",
    embedding_function=embedding_fn
)

# Adicionar memória
collection.add(
    documents=["User likes Boa Sorte by Vanessa da Mata"],
    metadatas=[{"type": "preference", "importance": 0.8}],
    ids=["mem_001"]
)

# Buscar por similaridade semântica
results = collection.query(
    query_texts=["favorite song"],
    n_results=5
)
```

**Comparação de Vector DBs Gratuitos:**

| DB | Tipo | Performance | Facilidade | Recomendação |
|----|------|-------------|------------|--------------|
| **ChromaDB** | Local | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ **Escolha principal** |
| **Qdrant** | Local/Cloud | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Para escala maior |
| **Weaviate** | Local/Cloud | ⭐⭐⭐⭐ | ⭐⭐⭐ | Se precisar GraphQL |
| **FAISS** | Local | ⭐⭐⭐⭐⭐ | ⭐⭐ | Só se precisar máxima perf |
| **LanceDB** | Local | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Alternativa moderna |

#### **2.2.2 Para LLM Local (Ollama)**

```python
# Ollama - LLMs locais gratuitos
# Instalação: https://ollama.ai

import ollama

# Baixar modelo (uma vez)
# Terminal: ollama pull llama3.2

async def query_local_llm(prompt: str) -> str:
    """Usa LLM local quando não precisa de voz."""
    response = ollama.chat(
        model="llama3.2",  # ou mistral, gemma2
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

# Streaming
async def stream_local_llm(prompt: str):
    stream = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in stream:
        yield chunk["message"]["content"]
```

**Modelos Ollama Recomendados:**

| Modelo | Tamanho | Uso | VRAM |
|--------|---------|-----|------|
| **llama3.2:1b** | 1.3GB | Tarefas simples, rápido | 2GB |
| **llama3.2:3b** | 2.0GB | Balanceado | 4GB |
| **mistral:7b** | 4.1GB | Geral, bom em PT-BR | 8GB |
| **codellama:7b** | 3.8GB | Código/programação | 8GB |
| **gemma2:2b** | 1.6GB | Compacto, Google | 3GB |

#### **2.2.3 Para Verificação de Voz (substituir Resemblyzer)**

```python
# Pyannote (mais moderno que Resemblyzer)
# pip install pyannote.audio

from pyannote.audio import Model, Inference

# Modelo de speaker embedding
model = Model.from_pretrained(
    "pyannote/embedding",
    use_auth_token="HF_TOKEN"  # Gratuito no HuggingFace
)

inference = Inference(model, window="whole")

def get_voice_embedding(audio_path: str):
    """Extrai embedding de voz mais preciso."""
    embedding = inference(audio_path)
    return embedding

# Comparação de similaridade
from scipy.spatial.distance import cosine

def verify_speaker(embedding1, embedding2, threshold=0.5):
    similarity = 1 - cosine(embedding1, embedding2)
    return similarity > threshold
```

**Alternativa mais leve - SpeechBrain:**
```python
# pip install speechbrain

from speechbrain.pretrained import EncoderClassifier

classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa-voxceleb"
)

def get_embedding(audio_file):
    signal = classifier.load_audio(audio_file)
    embeddings = classifier.encode_batch(signal)
    return embeddings
```

#### **2.2.4 Para Plugin Matching (indexação)**

```python
# Substituir busca linear por Trie + Fuzzy matching
# pip install rapidfuzz python-Levenshtein

from rapidfuzz import fuzz, process
from collections import defaultdict

class FastPluginMatcher:
    """Matcher de plugins otimizado com fuzzy search."""
    
    def __init__(self):
        self.phrase_to_plugin = {}  # "abrir chrome" → AppsPlugin
        self.all_phrases = []
        self._index_built = False
    
    def build_index(self, plugins: list):
        """Constrói índice uma vez no startup."""
        for plugin in plugins:
            for phrase in plugin.trigger_phrases:
                phrase_lower = phrase.lower()
                self.phrase_to_plugin[phrase_lower] = plugin
                self.all_phrases.append(phrase_lower)
        
        self._index_built = True
    
    def find_best_match(
        self, 
        user_input: str, 
        threshold: int = 70
    ) -> tuple[any, int]:
        """
        Encontra melhor plugin em O(1) amortizado.
        
        Args:
            user_input: Entrada do usuário
            threshold: Score mínimo (0-100)
        
        Returns:
            (plugin, score) ou (None, 0)
        """
        if not self._index_built:
            raise RuntimeError("Índice não construído! Chame build_index() primeiro.")
        
        user_lower = user_input.lower()
        
        # 1. Busca exata (O(1))
        if user_lower in self.phrase_to_plugin:
            return self.phrase_to_plugin[user_lower], 100
        
        # 2. Fuzzy match com rapidfuzz (otimizado em C)
        result = process.extractOne(
            user_lower,
            self.all_phrases,
            scorer=fuzz.token_set_ratio,  # Bom para reordenação de palavras
            score_cutoff=threshold
        )
        
        if result:
            phrase, score, _ = result
            return self.phrase_to_plugin[phrase], score
        
        return None, 0
```

---

## ✨ PARTE 3: NOVAS FEATURES PROPOSTAS

### 3.1 Roadmap de Features (Priorizado)

```
┌────────────────────────────────────────────────────────────────┐
│                    ROADMAP JARVIS v3.0                         │
└────────────────────────────────────────────────────────────────┘

📅 FASE 1 - FUNDAÇÃO (1-2 semanas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├── 🔒 Segurança
│   ├── Whitelist robusta para comandos
│   ├── Rate limiting por função
│   └── Audit log de ações
│
├── 🧠 Memória v2
│   ├── ChromaDB para semantic search local
│   ├── Deduplicação automática
│   └── Sistema de importância/decay
│
└── 🔧 Estabilidade
    ├── Retry + exponential backoff
    ├── Circuit breaker para APIs
    └── Graceful degradation

📅 FASE 2 - INTELIGÊNCIA (2-4 semanas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├── 🤖 Multi-LLM
│   ├── Ollama para offline/privacidade
│   ├── Smart routing por complexidade
│   └── Fallback chain automático
│
├── 🎯 Intent Classification
│   ├── Classificador local (sklearn/transformers)
│   ├── Reduz chamadas ao LLM
│   └── Faster response time
│
└── 📊 Context Window Management
    ├── Summarização automática
    ├── Priorização de contexto
    └── Sliding window inteligente

📅 FASE 3 - AUTOMAÇÃO (4-6 semanas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├── 🔄 Workflows
│   ├── Sequência de ações programáveis
│   ├── Triggers (horário, evento, comando)
│   └── Templates de workflow
│
├── 🔗 Integrações
│   ├── Home Assistant (casa inteligente)
│   ├── Notion/Obsidian (notas)
│   ├── Calendar (Google/Outlook)
│   └── Email (Gmail/Outlook)
│
└── 👁️ Computer Vision
    ├── Screenshot analysis
    ├── UI element detection
    └── Visual automation

📅 FASE 4 - AUTONOMIA (6-8 semanas)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├── 🧩 Agentes Autônomos
│   ├── Task decomposition
│   ├── Self-healing (auto-correção)
│   └── Learning from feedback
│
├── 🌐 Web Agent
│   ├── Navegação autônoma
│   ├── Form filling
│   └── Data extraction
│
└── 📱 Mobile Bridge
    ├── Companion app
    ├── Push notifications
    └── Remote commands
```

### 3.2 Feature Detalhada: Sistema de Workflows

```python
# Proposta: src/jarvis/workflows/workflow_engine.py

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Callable
import asyncio
from datetime import datetime, time

class TriggerType(Enum):
    VOICE_COMMAND = "voice"      # "Jarvis, modo trabalho"
    SCHEDULE = "schedule"        # Horário específico
    EVENT = "event"              # Evento do sistema
    CONDITION = "condition"      # Condição lógica

class ActionType(Enum):
    OPEN_APP = "open_app"
    OPEN_URL = "open_url"
    RUN_COMMAND = "run_command"
    SEND_NOTIFICATION = "notify"
    WAIT = "wait"
    SPEAK = "speak"
    CUSTOM = "custom"

@dataclass
class WorkflowStep:
    action: ActionType
    params: Dict[str, Any]
    on_error: str = "continue"  # continue, stop, retry

@dataclass 
class Workflow:
    name: str
    description: str
    trigger: TriggerType
    trigger_config: Dict[str, Any]
    steps: List[WorkflowStep]
    enabled: bool = True
    
class WorkflowEngine:
    """Motor de execução de workflows."""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.executors: Dict[ActionType, Callable] = {}
        self._setup_default_executors()
    
    def _setup_default_executors(self):
        """Configura executores padrão."""
        self.executors = {
            ActionType.OPEN_APP: self._exec_open_app,
            ActionType.OPEN_URL: self._exec_open_url,
            ActionType.WAIT: self._exec_wait,
            ActionType.SPEAK: self._exec_speak,
            ActionType.RUN_COMMAND: self._exec_command,
        }
    
    def register_workflow(self, workflow: Workflow):
        """Registra um novo workflow."""
        self.workflows[workflow.name] = workflow
    
    async def execute_workflow(self, name: str) -> Dict[str, Any]:
        """Executa um workflow pelo nome."""
        workflow = self.workflows.get(name)
        if not workflow:
            return {"success": False, "error": f"Workflow '{name}' não encontrado"}
        
        if not workflow.enabled:
            return {"success": False, "error": f"Workflow '{name}' está desabilitado"}
        
        results = []
        for i, step in enumerate(workflow.steps):
            try:
                executor = self.executors.get(step.action)
                if not executor:
                    results.append({"step": i, "error": f"Executor não encontrado: {step.action}"})
                    if step.on_error == "stop":
                        break
                    continue
                
                result = await executor(**step.params)
                results.append({"step": i, "success": True, "result": result})
                
            except Exception as e:
                results.append({"step": i, "error": str(e)})
                if step.on_error == "stop":
                    break
                elif step.on_error == "retry":
                    # Retry uma vez
                    try:
                        result = await executor(**step.params)
                        results.append({"step": i, "success": True, "result": result, "retried": True})
                    except:
                        pass
        
        return {"success": True, "workflow": name, "results": results}
    
    # Executores padrão
    async def _exec_open_app(self, app_name: str) -> str:
        from ..platform import get_platform_adapter
        adapter = get_platform_adapter()
        return await adapter.open_application(app_name)
    
    async def _exec_open_url(self, url: str) -> str:
        import webbrowser
        webbrowser.open(url)
        return f"URL aberta: {url}"
    
    async def _exec_wait(self, seconds: float) -> str:
        await asyncio.sleep(seconds)
        return f"Aguardou {seconds}s"
    
    async def _exec_speak(self, text: str) -> str:
        # Integrar com TTS
        return f"Falado: {text}"
    
    async def _exec_command(self, command: str) -> str:
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout or result.stderr


# Exemplo de workflows pré-definidos
PRESET_WORKFLOWS = [
    Workflow(
        name="modo_trabalho",
        description="Prepara ambiente para trabalho",
        trigger=TriggerType.VOICE_COMMAND,
        trigger_config={"phrases": ["modo trabalho", "hora de trabalhar", "vamos trabalhar"]},
        steps=[
            WorkflowStep(ActionType.SPEAK, {"text": "Preparando ambiente de trabalho"}),
            WorkflowStep(ActionType.OPEN_APP, {"app_name": "vscode"}),
            WorkflowStep(ActionType.WAIT, {"seconds": 2}),
            WorkflowStep(ActionType.OPEN_APP, {"app_name": "chrome"}),
            WorkflowStep(ActionType.OPEN_URL, {"url": "https://github.com"}),
            WorkflowStep(ActionType.OPEN_APP, {"app_name": "terminal"}),
            WorkflowStep(ActionType.SPEAK, {"text": "Ambiente pronto, bom trabalho chefe"}),
        ]
    ),
    Workflow(
        name="modo_relaxar",
        description="Prepara ambiente para descanso",
        trigger=TriggerType.VOICE_COMMAND,
        trigger_config={"phrases": ["modo relaxar", "hora de descansar", "vou relaxar"]},
        steps=[
            WorkflowStep(ActionType.SPEAK, {"text": "Preparando momento de descanso"}),
            WorkflowStep(ActionType.OPEN_URL, {"url": "https://music.youtube.com"}),
            WorkflowStep(ActionType.WAIT, {"seconds": 3}),
            WorkflowStep(ActionType.OPEN_URL, {"url": "https://youtube.com"}),
            WorkflowStep(ActionType.SPEAK, {"text": "Pronto para relaxar"}),
        ]
    ),
    Workflow(
        name="bom_dia",
        description="Rotina matinal automática",
        trigger=TriggerType.SCHEDULE,
        trigger_config={"time": "07:00", "days": ["mon", "tue", "wed", "thu", "fri"]},
        steps=[
            WorkflowStep(ActionType.SPEAK, {"text": "Bom dia chefe. Preparando seu dia"}),
            WorkflowStep(ActionType.OPEN_APP, {"app_name": "chrome"}),
            WorkflowStep(ActionType.OPEN_URL, {"url": "https://mail.google.com"}),
            WorkflowStep(ActionType.WAIT, {"seconds": 2}),
            WorkflowStep(ActionType.OPEN_URL, {"url": "https://calendar.google.com"}),
            # Poderia integrar com API de clima
            WorkflowStep(ActionType.SPEAK, {"text": "Emails e calendário abertos. Tenha um ótimo dia"}),
        ]
    ),
]
```

### 3.3 Feature: Intent Classification Local

```python
# Proposta: src/jarvis/nlp/intent_classifier.py
# Reduz chamadas ao LLM classificando intenções localmente

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path

class LocalIntentClassifier:
    """
    Classificador de intenções local (sem LLM).
    Usa para comandos simples, economizando tokens/latência.
    """
    
    INTENTS = {
        "open_app": [
            "abrir aplicativo", "abre o", "abra o", "iniciar", 
            "executar", "rodar", "abrir chrome", "abrir vscode"
        ],
        "open_website": [
            "abrir site", "abre o youtube", "entra no", 
            "vai pro", "acessa o", "abrir url"
        ],
        "play_music": [
            "tocar música", "coloca música", "bota uma música",
            "quero ouvir", "toca a música", "reproduzir"
        ],
        "media_control": [
            "pausar", "pause", "play", "continuar",
            "próxima", "anterior", "pular", "voltar"
        ],
        "volume": [
            "aumentar volume", "diminuir volume", "abaixar som",
            "volume", "mais alto", "mais baixo", "mutar"
        ],
        "system_info": [
            "bateria", "memória", "cpu", "ram", "disco",
            "espaço", "quanto de", "como está o sistema"
        ],
        "time_date": [
            "que horas", "que dia", "data de hoje",
            "hora atual", "que dia é hoje"
        ],
        "weather": [
            "tempo", "clima", "previsão", "vai chover",
            "temperatura", "como está o tempo"
        ],
        "general_question": [
            "o que é", "quem é", "como funciona",
            "me explica", "qual é", "por que"
        ],
        "code_task": [
            "analise o código", "corrija o erro", "refatore",
            "crie um", "debug", "otimize", "documente"
        ],
    }
    
    def __init__(self, model_path: str = "./models/intent_classifier.joblib"):
        self.model_path = Path(model_path)
        self.pipeline = None
        self._load_or_train()
    
    def _load_or_train(self):
        """Carrega modelo salvo ou treina novo."""
        if self.model_path.exists():
            self.pipeline = joblib.load(self.model_path)
        else:
            self._train()
    
    def _train(self):
        """Treina o classificador com dados de exemplo."""
        # Preparar dados
        texts = []
        labels = []
        
        for intent, examples in self.INTENTS.items():
            for example in examples:
                texts.append(example)
                labels.append(intent)
        
        # Pipeline: TF-IDF + Naive Bayes
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
            ('clf', MultinomialNB())
        ])
        
        self.pipeline.fit(texts, labels)
        
        # Salvar modelo
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, self.model_path)
    
    def classify(self, text: str, confidence_threshold: float = 0.6) -> tuple[str, float]:
        """
        Classifica a intenção de um texto.
        
        Returns:
            (intent, confidence) ou ("unknown", 0.0) se abaixo do threshold
        """
        probas = self.pipeline.predict_proba([text])[0]
        max_idx = probas.argmax()
        confidence = probas[max_idx]
        
        if confidence >= confidence_threshold:
            intent = self.pipeline.classes_[max_idx]
            return intent, confidence
        
        return "unknown", confidence
    
    def should_use_llm(self, text: str) -> bool:
        """Determina se deve usar LLM ou processar localmente."""
        intent, confidence = self.classify(text)
        
        # Se não conseguiu classificar com confiança, usa LLM
        if intent == "unknown":
            return True
        
        # Tarefas complexas sempre vão pro LLM
        complex_intents = ["code_task", "general_question"]
        if intent in complex_intents:
            return True
        
        return False


# Integração com o agente
class SmartAssistant:
    """Assistente que usa classificação local quando possível."""
    
    def __init__(self):
        self.classifier = LocalIntentClassifier()
        self.local_handlers = {
            "open_app": self._handle_open_app,
            "open_website": self._handle_open_website,
            "play_music": self._handle_play_music,
            "media_control": self._handle_media,
            "volume": self._handle_volume,
            "time_date": self._handle_time,
        }
    
    async def process(self, user_input: str):
        """Processa entrada decidindo entre local e LLM."""
        
        # Tenta classificar localmente
        intent, confidence = self.classifier.classify(user_input)
        
        if intent in self.local_handlers and confidence > 0.7:
            # Processa localmente (rápido, sem custo)
            handler = self.local_handlers[intent]
            return await handler(user_input)
        
        # Fallback para LLM (mais lento, mais inteligente)
        return await self._process_with_llm(user_input)
```

### 3.4 Feature: Sistema de Proatividade

```python
# Proposta: src/jarvis/proactive/proactive_engine.py

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Callable
from dataclasses import dataclass

@dataclass
class ProactiveRule:
    name: str
    check_interval: int  # segundos
    condition: Callable[[], bool]
    action: Callable[[], str]
    cooldown: int = 3600  # não repetir por 1h
    last_triggered: datetime = None

class ProactiveEngine:
    """
    Motor de ações proativas.
    JARVIS pode agir sem ser solicitado quando faz sentido.
    """
    
    def __init__(self):
        self.rules: List[ProactiveRule] = []
        self.running = False
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configura regras proativas padrão."""
        
        # Regra: Bateria baixa
        self.add_rule(ProactiveRule(
            name="low_battery_warning",
            check_interval=300,  # Verificar a cada 5 min
            condition=self._check_low_battery,
            action=lambda: "Chefe, a bateria está em menos de 20%. Sugiro conectar o carregador.",
            cooldown=1800  # Não repetir por 30 min
        ))
        
        # Regra: Hora de pausa
        self.add_rule(ProactiveRule(
            name="break_reminder",
            check_interval=1800,  # Verificar a cada 30 min
            condition=self._check_work_time,
            action=lambda: "Você está trabalhando há mais de 2 horas. Que tal uma pausa rápida?",
            cooldown=7200  # Não repetir por 2h
        ))
        
        # Regra: Uso alto de memória
        self.add_rule(ProactiveRule(
            name="high_memory_warning",
            check_interval=600,
            condition=self._check_high_memory,
            action=lambda: "O uso de memória está alto. Quer que eu liste os processos consumindo mais recursos?",
            cooldown=3600
        ))
    
    def _check_low_battery(self) -> bool:
        try:
            import psutil
            battery = psutil.sensors_battery()
            return battery and battery.percent < 20 and not battery.power_plugged
        except:
            return False
    
    def _check_work_time(self) -> bool:
        # Simplificado - poderia rastrear atividade real
        now = datetime.now()
        # Entre 9h e 18h, em dia de semana
        return (9 <= now.hour <= 18 and now.weekday() < 5)
    
    def _check_high_memory(self) -> bool:
        try:
            import psutil
            return psutil.virtual_memory().percent > 85
        except:
            return False
    
    def add_rule(self, rule: ProactiveRule):
        self.rules.append(rule)
    
    async def start(self, speak_callback: Callable[[str], None]):
        """Inicia o motor de proatividade."""
        self.running = True
        self.speak = speak_callback
        
        while self.running:
            await self._check_rules()
            await asyncio.sleep(60)  # Check base a cada minuto
    
    async def _check_rules(self):
        now = datetime.now()
        
        for rule in self.rules:
            # Verifica cooldown
            if rule.last_triggered:
                if (now - rule.last_triggered).seconds < rule.cooldown:
                    continue
            
            # Verifica condição
            try:
                if rule.condition():
                    message = rule.action()
                    rule.last_triggered = now
                    
                    # Fala a mensagem
                    if self.speak:
                        await self.speak(message)
            except Exception as e:
                logger.error(f"Erro na regra proativa {rule.name}: {e}")
    
    def stop(self):
        self.running = False
```

---

## 📊 MÉTRICAS DE SUCESSO

### KPIs Propostos

| Métrica | Atual | Meta v3.0 | Como Medir |
|---------|-------|-----------|------------|
| **Latência de resposta** | ~2s | <500ms (simples) | Prometheus/logging |
| **Taxa de acerto de intent** | N/A | >90% | Testes automatizados |
| **Uptime do agente** | N/A | 99.5% | Health checks |
| **Memórias relevantes** | ~50% | >85% | Feedback do usuário |
| **Cobertura de testes** | ~20%? | >70% | pytest-cov |
| **Comandos/dia** | N/A | Baseline + growth | Analytics |

---

## 🛠️ IMPLEMENTAÇÃO SUGERIDA

### Ordem de Implementação (Quick Wins First)

```
SEMANA 1-2: Fundação
├── [ ] ChromaDB para memória semântica
├── [ ] Whitelist robusta de comandos
├── [ ] Retry/circuit breaker
└── [ ] Logging estruturado (structlog)

SEMANA 3-4: Performance  
├── [ ] FastPluginMatcher (rapidfuzz)
├── [ ] LocalIntentClassifier
├── [ ] Ollama como fallback local
└── [ ] aiofiles para I/O

SEMANA 5-6: Features
├── [ ] WorkflowEngine básico
├── [ ] 3 workflows pré-definidos
├── [ ] ProactiveEngine
└── [ ] Testes de integração

SEMANA 7-8: Polish
├── [ ] Platform abstraction (Linux/Mac)
├── [ ] Documentação completa
├── [ ] CI/CD pipeline
└── [ ] Métricas e dashboard
```

---

## 📚 RECURSOS E REFERÊNCIAS

### Bibliotecas Recomendadas (Todas Gratuitas)

```
# Memory & Search
chromadb>=0.4.0          # Vector DB local
sentence-transformers    # Embeddings gratuitos

# LLM Local
ollama                   # Framework para LLMs locais

# Performance
rapidfuzz>=3.0.0        # Fuzzy matching otimizado
aiofiles>=23.0.0        # File I/O assíncrono
orjson>=3.9.0           # JSON parsing rápido

# Observability
structlog>=24.0.0       # Logging estruturado
prometheus-client       # Métricas

# NLP Local
scikit-learn>=1.4.0     # ML clássico
joblib>=1.3.0           # Serialização de modelos
```

### Links Úteis

- [ChromaDB Docs](https://docs.trychroma.com/)
- [Ollama Models](https://ollama.ai/library)
- [LiveKit Agents](https://docs.livekit.io/agents/)
- [Google ADK](https://github.com/google/adk-python)
- [Pyannote Speaker Diarization](https://github.com/pyannote/pyannote-audio)

---

## 🔒 PARTE 4: SISTEMA DE SEGURANÇA ENTERPRISE

### 4.1 Visão Geral de Segurança

O OpenClaw implementa um sistema de segurança em **camadas múltiplas** para garantir proteção contra:
- 🛡️ Injeção de comandos maliciosos
- 🔐 Vazamento de dados sensíveis
- 🚫 Acesso não autorizado
- 🦠 Execução de código malicioso
- 🌐 Ataques via web (XSS, CSRF, etc.)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ARQUITETURA DE SEGURANÇA OPENCLAW                │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     🛡️ CAMADA 1: PERÍMETRO                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │ Rate Limit  │  │   WAF       │  │ Input       │  │ Auth      │  │
│  │ (100/min)   │  │ (Firewall)  │  │ Sanitizer   │  │ Manager   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                     🔐 CAMADA 2: AUTENTICAÇÃO                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Multi-Factor Authentication                                 │   │
│  │  ├── Voice Biometrics (speaker verification)                 │   │
│  │  ├── Device Fingerprint                                      │   │
│  │  ├── Session Tokens (JWT + refresh)                          │   │
│  │  └── Optional: Hardware Key (FIDO2)                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                     🔒 CAMADA 3: AUTORIZAÇÃO                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Permission System                                           │   │
│  │  ├── Command Whitelist (ações permitidas)                    │   │
│  │  ├── Resource Access Control (arquivos, APIs)                │   │
│  │  ├── Time-based Restrictions (horários)                      │   │
│  │  └── Geolocation Policies (opcional)                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                     📦 CAMADA 4: EXECUÇÃO SEGURA                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Sandbox & Isolation                                         │   │
│  │  ├── Process Isolation (subprocess com limits)               │   │
│  │  ├── Network Isolation (firewall rules)                      │   │
│  │  ├── Resource Limits (CPU, RAM, tempo)                       │   │
│  │  └── Container Option (Docker sandbox)                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                     🗄️ CAMADA 5: DADOS                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Data Protection                                             │   │
│  │  ├── Encryption at Rest (AES-256)                            │   │
│  │  ├── Encryption in Transit (TLS 1.3)                         │   │
│  │  ├── Secure Key Storage (OS keychain)                        │   │
│  │  └── Data Minimization (não guarda o desnecessário)          │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                     📋 CAMADA 6: AUDITORIA                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Audit & Monitoring                                          │   │
│  │  ├── Immutable Logs (append-only)                            │   │
│  │  ├── Anomaly Detection                                       │   │
│  │  ├── Real-time Alerts                                        │   │
│  │  └── Forensics Support                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Implementação: Command Whitelist & Sanitization

```python
# Proposta: src/openclaw/security/command_guard.py

import re
import hashlib
import hmac
from enum import Enum
from typing import Optional, List, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    SAFE = "safe"           # Pode executar sempre
    LOW = "low"             # Log apenas
    MEDIUM = "medium"       # Requer confirmação
    HIGH = "high"           # Requer autenticação extra
    CRITICAL = "critical"   # Bloqueado por padrão

@dataclass
class CommandPolicy:
    pattern: str
    risk_level: RiskLevel
    description: str
    requires_confirmation: bool = False
    max_daily_uses: int = -1  # -1 = ilimitado

class CommandGuard:
    """
    Sistema de proteção contra comandos maliciosos.
    Implementa whitelist + blacklist + análise de risco.
    """
    
    # Comandos SEMPRE bloqueados (blacklist)
    BLOCKED_PATTERNS = [
        r"rm\s+-rf\s+/",              # Delete root
        r"format\s+c:",               # Format drive
        r"del\s+/s\s+/q",             # Delete all Windows
        r":\(\)\{\s*:\|:\s*&\s*\};:", # Fork bomb
        r">\s*/dev/sd",               # Overwrite disk
        r"mkfs\.",                    # Format filesystem
        r"dd\s+if=.*of=/dev/",        # Direct disk write
        r"curl.*\|\s*bash",           # Pipe to bash
        r"wget.*\|\s*sh",             # Pipe to shell
        r"powershell.*-enc",          # Encoded PowerShell
        r"base64.*\|\s*bash",         # Base64 to bash
        r"eval\s*\(",                 # Eval execution
        r"exec\s*\(",                 # Exec execution
        r"__import__",                # Python import injection
        r"os\.system",                # Direct system call
        r"subprocess\.call.*shell=True", # Shell injection
    ]
    
    # Comandos permitidos (whitelist) com níveis de risco
    ALLOWED_COMMANDS = {
        # SAFE - Sempre permitidos
        "open_app": CommandPolicy(
            pattern=r"^(abrir?|open|iniciar)\s+\w+$",
            risk_level=RiskLevel.SAFE,
            description="Abrir aplicativo conhecido"
        ),
        "media_control": CommandPolicy(
            pattern=r"^(play|pause|stop|next|previous|volume)$",
            risk_level=RiskLevel.SAFE,
            description="Controle de mídia"
        ),
        "time_query": CommandPolicy(
            pattern=r"^(que horas|que dia|data|hora).*$",
            risk_level=RiskLevel.SAFE,
            description="Consulta de horário"
        ),
        
        # LOW - Permitidos com log
        "web_search": CommandPolicy(
            pattern=r"^(pesquisar?|buscar?|search)\s+.+$",
            risk_level=RiskLevel.LOW,
            description="Pesquisa na web",
            max_daily_uses=100
        ),
        "read_file": CommandPolicy(
            pattern=r"^(ler|read|mostrar?)\s+arquivo\s+.+$",
            risk_level=RiskLevel.LOW,
            description="Leitura de arquivo"
        ),
        
        # MEDIUM - Requer confirmação verbal
        "write_file": CommandPolicy(
            pattern=r"^(escrever?|criar?|salvar?)\s+arquivo\s+.+$",
            risk_level=RiskLevel.MEDIUM,
            description="Escrita de arquivo",
            requires_confirmation=True,
            max_daily_uses=50
        ),
        "install_package": CommandPolicy(
            pattern=r"^(instalar?|install)\s+.+$",
            risk_level=RiskLevel.MEDIUM,
            description="Instalação de pacote",
            requires_confirmation=True,
            max_daily_uses=20
        ),
        
        # HIGH - Requer autenticação extra
        "system_command": CommandPolicy(
            pattern=r"^(executar?|run|rodar?)\s+comando\s+.+$",
            risk_level=RiskLevel.HIGH,
            description="Comando de sistema",
            requires_confirmation=True,
            max_daily_uses=10
        ),
        "delete_file": CommandPolicy(
            pattern=r"^(deletar?|apagar?|remover?)\s+.+$",
            risk_level=RiskLevel.HIGH,
            description="Deleção de arquivo",
            requires_confirmation=True,
            max_daily_uses=20
        ),
    }
    
    def __init__(self):
        self.daily_usage = {}  # {command_name: {date: count}}
        self.blocked_attempts = []  # Log de tentativas bloqueadas
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pré-compila regex para performance."""
        self.blocked_regex = [re.compile(p, re.IGNORECASE) for p in self.BLOCKED_PATTERNS]
        self.allowed_regex = {
            name: re.compile(policy.pattern, re.IGNORECASE)
            for name, policy in self.ALLOWED_COMMANDS.items()
        }
    
    def check_command(self, command: str, user_id: str = "default") -> tuple[bool, str, RiskLevel]:
        """
        Verifica se um comando pode ser executado.
        
        Returns:
            (allowed: bool, message: str, risk_level: RiskLevel)
        """
        command_clean = command.strip().lower()
        
        # 1. Verifica blacklist primeiro (SEMPRE bloquear)
        for regex in self.blocked_regex:
            if regex.search(command_clean):
                self._log_blocked(command, user_id, "blacklist_match")
                return (False, "Comando bloqueado por segurança.", RiskLevel.CRITICAL)
        
        # 2. Sanitiza o comando
        sanitized = self._sanitize(command_clean)
        if sanitized != command_clean:
            logger.warning(f"Comando sanitizado: '{command_clean}' → '{sanitized}'")
        
        # 3. Verifica whitelist
        for name, regex in self.allowed_regex.items():
            if regex.match(sanitized):
                policy = self.ALLOWED_COMMANDS[name]
                
                # Verifica limite diário
                if not self._check_daily_limit(name, policy.max_daily_uses):
                    return (False, f"Limite diário atingido para '{name}'.", policy.risk_level)
                
                # Incrementa contador
                self._increment_usage(name)
                
                return (True, policy.description, policy.risk_level)
        
        # 4. Comando não reconhecido - análise contextual
        return self._analyze_unknown_command(sanitized, user_id)
    
    def _sanitize(self, command: str) -> str:
        """Remove caracteres potencialmente perigosos."""
        # Remove caracteres de controle
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', command)
        
        # Remove tentativas de escape
        sanitized = sanitized.replace('\\', '')
        
        # Limita tamanho
        sanitized = sanitized[:500]
        
        # Remove múltiplos espaços
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized.strip()
    
    def _check_daily_limit(self, command_name: str, max_uses: int) -> bool:
        """Verifica limite diário de uso."""
        if max_uses == -1:
            return True
        
        today = datetime.now().date().isoformat()
        usage = self.daily_usage.get(command_name, {}).get(today, 0)
        
        return usage < max_uses
    
    def _increment_usage(self, command_name: str):
        """Incrementa contador de uso diário."""
        today = datetime.now().date().isoformat()
        
        if command_name not in self.daily_usage:
            self.daily_usage[command_name] = {}
        
        if today not in self.daily_usage[command_name]:
            self.daily_usage[command_name][today] = 0
        
        self.daily_usage[command_name][today] += 1
    
    def _log_blocked(self, command: str, user_id: str, reason: str):
        """Registra tentativa bloqueada para auditoria."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "command": command[:200],  # Trunca para segurança
            "reason": reason,
            "ip": "local"  # Poderia capturar IP real
        }
        self.blocked_attempts.append(entry)
        logger.warning(f"BLOCKED: {entry}")
        
        # Alerta se muitas tentativas
        recent_blocks = [
            b for b in self.blocked_attempts
            if datetime.fromisoformat(b["timestamp"]) > datetime.now() - timedelta(minutes=5)
        ]
        
        if len(recent_blocks) > 10:
            logger.critical(f"ALERT: {len(recent_blocks)} blocked attempts in 5 minutes!")
            # Poderia enviar notificação/webhook aqui
    
    def _analyze_unknown_command(
        self, 
        command: str, 
        user_id: str
    ) -> tuple[bool, str, RiskLevel]:
        """Analisa comando desconhecido com heurísticas."""
        
        # Heurísticas de risco
        risk_indicators = [
            (r"http[s]?://", 0.3),     # URLs
            (r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", 0.5),  # IPs
            (r"[;&|`$]", 0.7),          # Shell operators
            (r"password|senha|key|token|secret", 0.8),  # Sensitive words
            (r"sudo|admin|root", 0.9),  # Privilege escalation
        ]
        
        risk_score = 0.0
        for pattern, weight in risk_indicators:
            if re.search(pattern, command, re.IGNORECASE):
                risk_score = max(risk_score, weight)
        
        if risk_score > 0.7:
            self._log_blocked(command, user_id, f"high_risk_score:{risk_score}")
            return (False, "Comando não reconhecido com risco elevado.", RiskLevel.HIGH)
        
        if risk_score > 0.4:
            return (True, "Comando desconhecido - processando com cautela.", RiskLevel.MEDIUM)
        
        return (True, "Comando será processado pelo LLM.", RiskLevel.LOW)


class InputSanitizer:
    """Sanitiza todas as entradas do usuário."""
    
    # Caracteres permitidos em comandos de voz
    ALLOWED_CHARS = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        "àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ"
        "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ"
        " .,!?-_'\"()"
    )
    
    @classmethod
    def sanitize_voice_input(cls, text: str) -> str:
        """Sanitiza entrada de voz."""
        if not text:
            return ""
        
        # Remove caracteres não permitidos
        sanitized = ''.join(c for c in text if c in cls.ALLOWED_CHARS)
        
        # Normaliza espaços
        sanitized = ' '.join(sanitized.split())
        
        # Limita tamanho
        return sanitized[:1000]
    
    @classmethod
    def sanitize_path(cls, path: str) -> Optional[str]:
        """Sanitiza caminho de arquivo."""
        if not path:
            return None
        
        # Remove traversal attempts
        dangerous_patterns = ['..', '~', '%', '\x00']
        for pattern in dangerous_patterns:
            if pattern in path:
                logger.warning(f"Path traversal attempt blocked: {path}")
                return None
        
        # Normaliza separadores
        path = path.replace('/', '\\')
        
        return path
    
    @classmethod
    def sanitize_url(cls, url: str) -> Optional[str]:
        """Sanitiza URL (mais detalhes na seção Web Fetch)."""
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
            
            # Apenas HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return None
            
            # Bloqueia localhost/IPs internos
            blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
            if parsed.hostname in blocked_hosts:
                return None
            
            # Bloqueia ranges privados
            if parsed.hostname:
                parts = parsed.hostname.split('.')
                if len(parts) == 4:
                    try:
                        first = int(parts[0])
                        if first in [10, 192, 172]:  # Private ranges
                            return None
                    except:
                        pass
            
            return url
        except:
            return None
```

### 4.3 Implementação: Encryption Manager

```python
# Proposta: src/openclaw/security/encryption.py

import os
import base64
import hashlib
import secrets
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import keyring
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    """
    Gerenciador de criptografia para dados sensíveis.
    Usa AES-256 via Fernet + OS keychain para chaves.
    """
    
    SERVICE_NAME = "OpenClaw"
    KEY_NAME = "master_key"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self._fernet = None
        self._initialize_key()
    
    def _initialize_key(self):
        """Inicializa ou recupera a chave mestre do OS keychain."""
        try:
            # Tenta recuperar chave existente
            stored_key = keyring.get_password(self.SERVICE_NAME, self.KEY_NAME)
            
            if stored_key:
                self._fernet = Fernet(stored_key.encode())
                logger.debug("Master key loaded from keychain")
            else:
                # Gera nova chave
                new_key = Fernet.generate_key()
                keyring.set_password(self.SERVICE_NAME, self.KEY_NAME, new_key.decode())
                self._fernet = Fernet(new_key)
                logger.info("New master key generated and stored")
                
        except Exception as e:
            logger.error(f"Keychain error: {e}. Using derived key.")
            # Fallback: deriva chave de identificador único da máquina
            self._fernet = self._derive_fallback_key()
    
    def _derive_fallback_key(self) -> Fernet:
        """Deriva chave de fallback do machine ID."""
        import uuid
        
        # Usa MAC address + hostname como seed
        machine_id = f"{uuid.getnode()}-{os.name}-{self.user_id}"
        
        salt = b"openclaw_salt_v1"  # Salt fixo (ok para fallback)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Criptografa string retornando base64."""
        if not data:
            return ""
        
        encrypted = self._fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """Descriptografa string."""
        if not encrypted_data:
            return None
        
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def encrypt_file(self, filepath: Path) -> bool:
        """Criptografa arquivo in-place."""
        try:
            content = filepath.read_bytes()
            encrypted = self._fernet.encrypt(content)
            
            # Salva com extensão .enc
            encrypted_path = filepath.with_suffix(filepath.suffix + '.enc')
            encrypted_path.write_bytes(encrypted)
            
            # Remove original (seguro)
            filepath.unlink()
            
            logger.info(f"File encrypted: {filepath} → {encrypted_path}")
            return True
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            return False
    
    def decrypt_file(self, encrypted_path: Path) -> Optional[Path]:
        """Descriptografa arquivo."""
        try:
            content = encrypted_path.read_bytes()
            decrypted = self._fernet.decrypt(content)
            
            # Remove .enc da extensão
            if encrypted_path.suffix == '.enc':
                original_path = encrypted_path.with_suffix('')
            else:
                original_path = encrypted_path.with_suffix('.dec')
            
            original_path.write_bytes(decrypted)
            
            logger.info(f"File decrypted: {encrypted_path} → {original_path}")
            return original_path
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            return None
    
    def hash_sensitive(self, data: str) -> str:
        """Gera hash seguro para dados sensíveis (não reversível)."""
        salt = secrets.token_bytes(16)
        
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            data.encode(),
            salt,
            iterations=100000
        )
        
        # Retorna salt + hash concatenados
        return base64.urlsafe_b64encode(salt + hash_bytes).decode()
    
    def verify_hash(self, data: str, stored_hash: str) -> bool:
        """Verifica se dados correspondem ao hash."""
        try:
            decoded = base64.urlsafe_b64decode(stored_hash.encode())
            salt = decoded[:16]
            original_hash = decoded[16:]
            
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                data.encode(),
                salt,
                iterations=100000
            )
            
            return secrets.compare_digest(original_hash, new_hash)
        except:
            return False


class SecureConfig:
    """Gerenciador de configurações sensíveis."""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path("./config/secrets.enc")
        self.encryption = EncryptionManager()
        self._cache = {}
    
    def set(self, key: str, value: str):
        """Armazena valor criptografado."""
        self._cache[key] = self.encryption.encrypt(value)
        self._save()
    
    def get(self, key: str) -> Optional[str]:
        """Recupera valor descriptografado."""
        if key not in self._cache:
            self._load()
        
        encrypted = self._cache.get(key)
        if encrypted:
            return self.encryption.decrypt(encrypted)
        return None
    
    def _save(self):
        """Salva configurações criptografadas."""
        import json
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = json.dumps(self._cache)
        encrypted = self.encryption.encrypt(data)
        
        self.config_path.write_text(encrypted)
    
    def _load(self):
        """Carrega configurações."""
        import json
        
        if self.config_path.exists():
            encrypted = self.config_path.read_text()
            decrypted = self.encryption.decrypt(encrypted)
            
            if decrypted:
                self._cache = json.loads(decrypted)
```

### 4.4 Implementação: Audit Logger

```python
# Proposta: src/openclaw/security/audit.py

import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue

class AuditEventType(Enum):
    COMMAND_EXECUTED = "command_executed"
    COMMAND_BLOCKED = "command_blocked"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    DATA_ACCESS = "data_access"
    CONFIG_CHANGE = "config_change"
    ERROR = "error"
    SECURITY_ALERT = "security_alert"
    WEB_ACCESS = "web_access"
    FILE_OPERATION = "file_operation"

@dataclass
class AuditEvent:
    timestamp: str
    event_type: AuditEventType
    user_id: str
    action: str
    details: Dict[str, Any]
    risk_level: str
    success: bool
    source_ip: str = "local"
    session_id: str = ""
    previous_hash: str = ""  # Para chain de integridade
    
    def to_dict(self) -> dict:
        d = asdict(self)
        d['event_type'] = self.event_type.value
        return d
    
    def compute_hash(self) -> str:
        """Computa hash do evento para integridade."""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

class AuditLogger:
    """
    Sistema de auditoria imutável com chain de integridade.
    Logs não podem ser alterados sem detecção.
    """
    
    def __init__(self, log_dir: Path = None):
        self.log_dir = log_dir or Path("./logs/audit")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self._last_hash = "genesis"
        self._queue = queue.Queue()
        self._lock = threading.Lock()
        
        # Writer thread para I/O assíncrono
        self._writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self._writer_thread.start()
        
        self._load_last_hash()
    
    def _load_last_hash(self):
        """Carrega último hash para continuar a chain."""
        today_file = self._get_log_file()
        
        if today_file.exists():
            try:
                lines = today_file.read_text().strip().split('\n')
                if lines:
                    last_event = json.loads(lines[-1])
                    # Recomputa hash para verificar integridade
                    event = AuditEvent(**last_event)
                    event.event_type = AuditEventType(event.event_type)
                    self._last_hash = event.compute_hash()
            except:
                pass
    
    def _get_log_file(self) -> Path:
        """Retorna arquivo de log do dia atual."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"audit_{date_str}.jsonl"
    
    def log(
        self,
        event_type: AuditEventType,
        user_id: str,
        action: str,
        details: Dict[str, Any] = None,
        risk_level: str = "low",
        success: bool = True,
        session_id: str = ""
    ):
        """Registra evento de auditoria."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            user_id=user_id,
            action=action,
            details=details or {},
            risk_level=risk_level,
            success=success,
            session_id=session_id,
            previous_hash=self._last_hash
        )
        
        # Adiciona à queue para escrita assíncrona
        self._queue.put(event)
    
    def _writer_loop(self):
        """Loop de escrita em background."""
        while True:
            try:
                event = self._queue.get(timeout=1.0)
                self._write_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Audit write error: {e}")
    
    def _write_event(self, event: AuditEvent):
        """Escreve evento no arquivo de log."""
        with self._lock:
            log_file = self._get_log_file()
            
            # Atualiza hash da chain
            self._last_hash = event.compute_hash()
            
            # Append ao arquivo (imutável)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event.to_dict()) + '\n')
    
    def verify_integrity(self, log_file: Path = None) -> tuple[bool, str]:
        """Verifica integridade da chain de logs."""
        log_file = log_file or self._get_log_file()
        
        if not log_file.exists():
            return True, "No logs to verify"
        
        try:
            lines = log_file.read_text().strip().split('\n')
            previous_hash = "genesis"
            
            for i, line in enumerate(lines):
                event_dict = json.loads(line)
                
                # Verifica se previous_hash bate
                if event_dict['previous_hash'] != previous_hash:
                    return False, f"Chain broken at line {i+1}"
                
                # Atualiza hash para próximo
                event = AuditEvent(**event_dict)
                event.event_type = AuditEventType(event.event_type)
                previous_hash = event.compute_hash()
            
            return True, f"Integrity verified: {len(lines)} events"
            
        except Exception as e:
            return False, f"Verification error: {e}"
    
    def get_recent_alerts(self, minutes: int = 60) -> list:
        """Retorna alertas de segurança recentes."""
        log_file = self._get_log_file()
        alerts = []
        
        if not log_file.exists():
            return alerts
        
        cutoff = datetime.now().timestamp() - (minutes * 60)
        
        for line in log_file.read_text().strip().split('\n'):
            try:
                event = json.loads(line)
                event_time = datetime.fromisoformat(event['timestamp']).timestamp()
                
                if event_time > cutoff and event['event_type'] == 'security_alert':
                    alerts.append(event)
            except:
                continue
        
        return alerts


# Singleton global para auditoria
_audit_logger = None

def get_audit_logger() -> AuditLogger:
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger

def audit_log(event_type: AuditEventType, **kwargs):
    """Função conveniente para logging de auditoria."""
    get_audit_logger().log(event_type, **kwargs)
```

### 4.5 Rate Limiting & DDoS Protection

```python
# Proposta: src/openclaw/security/rate_limiter.py

import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Tuple
import threading

@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10  # Máximo em 1 segundo
    cooldown_seconds: int = 60  # Tempo de bloqueio após exceder

class RateLimiter:
    """
    Rate limiter com múltiplas janelas temporais.
    Protege contra abuso e DDoS.
    """
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self._requests: Dict[str, list] = defaultdict(list)
        self._blocked: Dict[str, float] = {}  # user_id → unblock_time
        self._lock = threading.Lock()
    
    def check(self, user_id: str) -> Tuple[bool, str]:
        """
        Verifica se usuário pode fazer requisição.
        
        Returns:
            (allowed: bool, message: str)
        """
        with self._lock:
            now = time.time()
            
            # Verifica se está bloqueado
            if user_id in self._blocked:
                if now < self._blocked[user_id]:
                    wait_time = int(self._blocked[user_id] - now)
                    return False, f"Rate limited. Aguarde {wait_time}s."
                else:
                    del self._blocked[user_id]
            
            # Limpa requisições antigas (> 1 hora)
            self._requests[user_id] = [
                ts for ts in self._requests[user_id]
                if now - ts < 3600
            ]
            
            requests = self._requests[user_id]
            
            # Verifica burst (último segundo)
            recent_second = sum(1 for ts in requests if now - ts < 1)
            if recent_second >= self.config.burst_limit:
                self._block_user(user_id, now)
                return False, "Burst limit exceeded."
            
            # Verifica por minuto
            recent_minute = sum(1 for ts in requests if now - ts < 60)
            if recent_minute >= self.config.requests_per_minute:
                self._block_user(user_id, now)
                return False, "Minute limit exceeded."
            
            # Verifica por hora
            if len(requests) >= self.config.requests_per_hour:
                self._block_user(user_id, now, duration=3600)
                return False, "Hour limit exceeded."
            
            # Registra requisição
            self._requests[user_id].append(now)
            
            return True, "OK"
    
    def _block_user(self, user_id: str, now: float, duration: int = None):
        """Bloqueia usuário temporariamente."""
        duration = duration or self.config.cooldown_seconds
        self._blocked[user_id] = now + duration
    
    def get_stats(self, user_id: str) -> dict:
        """Retorna estatísticas de uso."""
        now = time.time()
        requests = self._requests.get(user_id, [])
        
        return {
            "requests_last_minute": sum(1 for ts in requests if now - ts < 60),
            "requests_last_hour": len([ts for ts in requests if now - ts < 3600]),
            "is_blocked": user_id in self._blocked,
            "limits": {
                "per_minute": self.config.requests_per_minute,
                "per_hour": self.config.requests_per_hour,
                "burst": self.config.burst_limit
            }
        }
```

---

## 🧠 PARTE 5: SISTEMA DE APRENDIZADO DE ROTINA

### 5.1 Visão Geral do Routine Learning

O OpenClaw aprende com o comportamento do usuário para **agir proativamente** sem ser solicitado.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ROUTINE LEARNING PIPELINE                        │
└─────────────────────────────────────────────────────────────────────┘

   Ação do Usuário          Análise               Padrão Detectado
        │                     │                        │
        ▼                     ▼                        ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────────────────┐
│  "Abre VS   │      │  Pattern    │      │ Segunda-feira 9h        │
│   Code"     │─────▶│  Detector   │─────▶│ sempre abre VSCode      │
│  (9h, Seg)  │      │             │      │ + Chrome + Terminal     │
└─────────────┘      └─────────────┘      └─────────────────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │  Confidence │
                    │  Calculator │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
    Confiança < 80%           Confiança >= 80%
    ┌─────────────┐           ┌─────────────────┐
    │ Continua    │           │ Propõe ação:    │
    │ aprendendo  │           │ "Quer que eu    │
    └─────────────┘           │ abra VSCode?"   │
                              └─────────────────┘
                                      │
                              ┌───────┴───────┐
                              │               │
                              ▼               ▼
                         Usuário          Usuário
                         aceita           recusa
                              │               │
                              ▼               ▼
                    ┌─────────────┐  ┌─────────────┐
                    │ Aumenta     │  │ Reduz       │
                    │ confiança   │  │ confiança   │
                    │ +10%        │  │ -20%        │
                    └─────────────┘  └─────────────┘
```

### 5.2 Implementação: Pattern Detector

```python
# Proposta: src/openclaw/learning/routine_detector.py

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class ActionRecord:
    """Registro de uma ação do usuário."""
    action: str              # Ex: "open_app:vscode"
    timestamp: datetime
    day_of_week: int         # 0=Segunda, 6=Domingo
    hour: int                # 0-23
    minute: int              # 0-59
    context: Dict = field(default_factory=dict)  # Metadados extras
    
    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "day_of_week": self.day_of_week,
            "hour": self.hour,
            "minute": self.minute,
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ActionRecord':
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

@dataclass
class RoutinePattern:
    """Padrão de rotina detectado."""
    action: str
    day_of_week: Optional[int]  # None = qualquer dia
    hour: int
    minute_range: Tuple[int, int]  # Ex: (0, 15) = entre :00 e :15
    confidence: float  # 0.0 - 1.0
    occurrences: int
    last_triggered: Optional[datetime] = None
    user_feedback_positive: int = 0
    user_feedback_negative: int = 0
    
    @property
    def adjusted_confidence(self) -> float:
        """Confiança ajustada pelo feedback do usuário."""
        feedback_boost = (self.user_feedback_positive - self.user_feedback_negative * 2) * 0.05
        return max(0.0, min(1.0, self.confidence + feedback_boost))
    
    def matches_time(self, dt: datetime) -> bool:
        """Verifica se datetime bate com o padrão."""
        if self.day_of_week is not None and dt.weekday() != self.day_of_week:
            return False
        
        if dt.hour != self.hour:
            return False
        
        if not (self.minute_range[0] <= dt.minute <= self.minute_range[1]):
            return False
        
        return True

class RoutineDetector:
    """
    Detecta padrões de rotina do usuário.
    Aprende quando o usuário faz ações repetidas.
    """
    
    MIN_OCCURRENCES = 3      # Mínimo de ocorrências para detectar padrão
    MIN_CONFIDENCE = 0.6     # Confiança mínima para considerar padrão
    SUGGEST_THRESHOLD = 0.8  # Confiança para sugerir ação
    TIME_WINDOW_MINUTES = 15 # Janela de tempo para agrupar ações
    
    def __init__(self, data_path: Path = None):
        self.data_path = data_path or Path("./data/routines")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        self.actions: List[ActionRecord] = []
        self.patterns: List[RoutinePattern] = []
        
        self._load_data()
    
    def record_action(self, action: str, context: Dict = None):
        """Registra uma ação do usuário."""
        now = datetime.now()
        
        record = ActionRecord(
            action=action,
            timestamp=now,
            day_of_week=now.weekday(),
            hour=now.hour,
            minute=now.minute,
            context=context or {}
        )
        
        self.actions.append(record)
        self._save_data()
        
        # Re-analisa padrões
        self._analyze_patterns()
        
        logger.debug(f"Action recorded: {action} at {now}")
    
    def get_suggestions(self) -> List[Tuple[RoutinePattern, str]]:
        """
        Retorna sugestões de ações baseadas na hora atual.
        
        Returns:
            Lista de (pattern, suggested_message)
        """
        now = datetime.now()
        suggestions = []
        
        for pattern in self.patterns:
            # Verifica se já foi triggered recentemente (evita spam)
            if pattern.last_triggered:
                if now - pattern.last_triggered < timedelta(hours=1):
                    continue
            
            # Verifica se bate com hora atual
            if pattern.matches_time(now):
                if pattern.adjusted_confidence >= self.SUGGEST_THRESHOLD:
                    message = self._generate_suggestion_message(pattern)
                    suggestions.append((pattern, message))
        
        return suggestions
    
    def user_accepted(self, pattern: RoutinePattern):
        """Usuário aceitou a sugestão."""
        pattern.user_feedback_positive += 1
        pattern.last_triggered = datetime.now()
        self._save_data()
        logger.info(f"Pattern accepted: {pattern.action}, new confidence: {pattern.adjusted_confidence:.2f}")
    
    def user_rejected(self, pattern: RoutinePattern):
        """Usuário rejeitou a sugestão."""
        pattern.user_feedback_negative += 1
        pattern.last_triggered = datetime.now()
        self._save_data()
        logger.info(f"Pattern rejected: {pattern.action}, new confidence: {pattern.adjusted_confidence:.2f}")
    
    def _analyze_patterns(self):
        """Analisa ações para detectar padrões."""
        # Agrupa ações por (action, day, hour_window)
        grouped = defaultdict(list)
        
        for record in self.actions:
            # Arredonda minuto para janela de 15 min
            minute_window = (record.minute // self.TIME_WINDOW_MINUTES) * self.TIME_WINDOW_MINUTES
            
            key = (record.action, record.day_of_week, record.hour, minute_window)
            grouped[key].append(record)
        
        # Converte grupos em padrões
        new_patterns = []
        
        for (action, day, hour, minute_window), records in grouped.items():
            occurrences = len(records)
            
            if occurrences >= self.MIN_OCCURRENCES:
                # Calcula confiança baseada em consistência
                # Mais ocorrências e menos variação = mais confiança
                weeks_with_data = len(set(r.timestamp.isocalendar()[1] for r in records))
                consistency = occurrences / max(weeks_with_data, 1)
                
                confidence = min(1.0, consistency * 0.3 + (occurrences / 10) * 0.4)
                
                # Verifica se já existe padrão similar
                existing = self._find_existing_pattern(action, day, hour, minute_window)
                
                if existing:
                    # Atualiza existente
                    existing.confidence = confidence
                    existing.occurrences = occurrences
                    new_patterns.append(existing)
                else:
                    # Cria novo
                    pattern = RoutinePattern(
                        action=action,
                        day_of_week=day,
                        hour=hour,
                        minute_range=(minute_window, minute_window + self.TIME_WINDOW_MINUTES - 1),
                        confidence=confidence,
                        occurrences=occurrences
                    )
                    new_patterns.append(pattern)
        
        self.patterns = new_patterns
        logger.debug(f"Patterns analyzed: {len(self.patterns)} patterns found")
    
    def _find_existing_pattern(
        self, 
        action: str, 
        day: int, 
        hour: int, 
        minute_window: int
    ) -> Optional[RoutinePattern]:
        """Encontra padrão existente similar."""
        for p in self.patterns:
            if (p.action == action and 
                p.day_of_week == day and 
                p.hour == hour and 
                p.minute_range[0] == minute_window):
                return p
        return None
    
    def _generate_suggestion_message(self, pattern: RoutinePattern) -> str:
        """Gera mensagem de sugestão amigável."""
        action_parts = pattern.action.split(':')
        action_type = action_parts[0]
        action_target = action_parts[1] if len(action_parts) > 1 else ""
        
        day_names = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
        day_str = day_names[pattern.day_of_week] if pattern.day_of_week is not None else "esse horário"
        
        templates = {
            "open_app": f"Percebi que você costuma abrir o {action_target} por volta desse horário nas {day_str}s. Quer que eu abra?",
            "open_url": f"Você costuma acessar {action_target} nesse horário. Devo abrir?",
            "play_music": f"Hora da música? Costumo tocar suas playlists nesse horário nas {day_str}s.",
            "workflow": f"Quer que eu execute a rotina '{action_target}'? Você costuma fazer isso agora.",
        }
        
        return templates.get(action_type, f"Detectei que você costuma executar '{pattern.action}' agora. Devo fazer isso?")
    
    def _save_data(self):
        """Salva dados em disco."""
        data = {
            "actions": [a.to_dict() for a in self.actions[-1000:]],  # Mantém últimas 1000
            "patterns": [vars(p) for p in self.patterns]
        }
        
        filepath = self.data_path / "routines.json"
        filepath.write_text(json.dumps(data, indent=2, default=str))
    
    def _load_data(self):
        """Carrega dados do disco."""
        filepath = self.data_path / "routines.json"
        
        if filepath.exists():
            try:
                data = json.loads(filepath.read_text())
                self.actions = [ActionRecord.from_dict(a) for a in data.get("actions", [])]
                self.patterns = [RoutinePattern(**p) for p in data.get("patterns", [])]
                logger.info(f"Loaded {len(self.actions)} actions and {len(self.patterns)} patterns")
            except Exception as e:
                logger.error(f"Error loading routine data: {e}")


class ProactiveLearningEngine:
    """
    Motor que combina detecção de rotinas com ações proativas.
    Integra com o assistente de voz.
    """
    
    def __init__(self):
        self.detector = RoutineDetector()
        self.pending_suggestions: Dict[str, RoutinePattern] = {}
    
    async def on_user_action(self, action: str, context: Dict = None):
        """Chamado quando usuário executa uma ação."""
        self.detector.record_action(action, context)
    
    async def check_suggestions(self) -> Optional[str]:
        """
        Verifica se há sugestões para fazer.
        Chamado periodicamente pelo agente.
        """
        suggestions = self.detector.get_suggestions()
        
        if suggestions:
            # Retorna a sugestão de maior confiança
            best = max(suggestions, key=lambda x: x[0].adjusted_confidence)
            pattern, message = best
            
            # Guarda para processar resposta
            suggestion_id = f"{pattern.action}_{pattern.hour}"
            self.pending_suggestions[suggestion_id] = pattern
            
            return message
        
        return None
    
    async def process_response(self, response: str, suggestion_id: str):
        """Processa resposta do usuário para sugestão."""
        pattern = self.pending_suggestions.get(suggestion_id)
        
        if not pattern:
            return
        
        # Detecta se aceitou ou recusou
        positive_words = ["sim", "pode", "ok", "claro", "vai", "quero", "yes", "sure"]
        negative_words = ["não", "nao", "agora não", "depois", "no", "nope"]
        
        response_lower = response.lower()
        
        if any(word in response_lower for word in positive_words):
            self.detector.user_accepted(pattern)
            return True  # Executar ação
        elif any(word in response_lower for word in negative_words):
            self.detector.user_rejected(pattern)
            return False
        
        return None  # Resposta ambígua
```

### 5.3 Configuração de Limites de Proatividade

```python
# Proposta: src/openclaw/learning/proactive_config.py

@dataclass
class ProactiveConfig:
    """Configurações de comportamento proativo."""
    
    # Quando sugerir
    suggestion_confidence_threshold: float = 0.8  # 80%+ para sugerir
    
    # Limites de sugestões
    max_suggestions_per_hour: int = 3
    max_suggestions_per_day: int = 10
    
    # Horários permitidos
    quiet_hours_start: int = 22  # 22:00
    quiet_hours_end: int = 7     # 07:00
    
    # Ações automáticas (sem perguntar)
    auto_execute_threshold: float = 0.95  # 95%+ para auto-executar
    allowed_auto_actions: List[str] = field(default_factory=lambda: [
        "open_app",      # Abrir apps
        "play_music",    # Tocar música
        "workflow:*",    # Workflows aprovados
    ])
    
    # Ações que NUNCA são automáticas
    never_auto_actions: List[str] = field(default_factory=lambda: [
        "delete_*",      # Deletar qualquer coisa
        "send_*",        # Enviar mensagens/emails
        "purchase_*",    # Compras
        "system_*",      # Comandos de sistema
    ])
```

---

## 🌐 PARTE 6: WEB FETCH SEGURO

### 6.1 Visão Geral do Safe Web Access

O OpenClaw pode acessar a internet de forma segura, bloqueando sites maliciosos.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SAFE WEB FETCH PIPELINE                          │
└─────────────────────────────────────────────────────────────────────┘

  Requisição                Validação              Fetch Seguro
      │                        │                       │
      ▼                        ▼                       ▼
┌─────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ fetch_url   │      │ URL Validator   │      │ Sandboxed       │
│ ("site.com")│─────▶│ ├── Blocklist   │─────▶│ HTTP Client     │
│             │      │ ├── Safe Browse │      │ ├── Timeout     │
│             │      │ └── DNS Check   │      │ ├── Size Limit  │
└─────────────┘      └─────────────────┘      │ └── No Redirect │
                            │                 └─────────────────┘
                     ┌──────┴──────┐                   │
                     │             │                   ▼
                     ▼             ▼           ┌─────────────────┐
              URL Bloqueada   URL Segura       │ Content         │
              ┌──────────┐   ┌──────────┐      │ Sanitizer       │
              │ "Site    │   │ Procede  │      │ ├── HTML Clean  │
              │ suspeito │   │ com fetch│      │ ├── Script Rem  │
              │ bloqueado"   └──────────┘      │ └── Size Trim   │
              └──────────┘                     └─────────────────┘
                                                       │
                                                       ▼
                                               ┌─────────────────┐
                                               │ Safe Response   │
                                               │ (text only)     │
                                               └─────────────────┘
```

### 6.2 Implementação: SafeWebFetcher

```python
# Proposta: src/openclaw/web/safe_fetcher.py

import asyncio
import aiohttp
import re
import hashlib
import logging
from urllib.parse import urlparse, urljoin
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
import ssl
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

@dataclass
class FetchResult:
    success: bool
    url: str
    content: Optional[str]
    content_type: str
    status_code: int
    error: Optional[str] = None
    blocked_reason: Optional[str] = None
    fetch_time_ms: int = 0

class URLValidator:
    """
    Valida URLs antes de acessar.
    Bloqueia sites maliciosos, suspeitos e perigosos.
    """
    
    # Domínios SEMPRE bloqueados
    BLOCKED_DOMAINS = {
        # Phishing conhecidos
        "phishing-site.com", "fake-bank.com",
        
        # Malware
        "malware-download.net",
        
        # Trackers agressivos
        "tracking-scripts.com",
        
        # Conteúdo ilegal
        # (lista seria mais extensa em produção)
    }
    
    # Padrões de URL suspeitos
    SUSPICIOUS_PATTERNS = [
        r"\.exe$",                    # Executáveis
        r"\.bat$", r"\.cmd$",         # Scripts Windows
        r"\.sh$", r"\.bash$",         # Scripts Unix
        r"\.ps1$",                    # PowerShell
        r"\.vbs$", r"\.js$",          # Scripts
        r"phishing", r"malware",      # Keywords
        r"free-?money", r"win-?prize", # Scam keywords
        r"login.*\.(?!com|org|net)",  # Fake logins
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",  # IPs diretos
        r"@.*@",                      # Multiple @ (email spoofing)
        r"\.tk$", r"\.ml$", r"\.ga$", # TLDs de alto risco
    ]
    
    # Categorias bloqueadas
    BLOCKED_CATEGORIES = {
        "adult", "gambling", "weapons", "drugs",
        "hacking", "malware", "phishing", "scam"
    }
    
    def __init__(self):
        self._blocklist_file = Path("./data/blocklist.txt")
        self._custom_blocklist: set = set()
        self._load_blocklist()
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pré-compila regex para performance."""
        self._suspicious_regex = [
            re.compile(p, re.IGNORECASE) 
            for p in self.SUSPICIOUS_PATTERNS
        ]
    
    def _load_blocklist(self):
        """Carrega blocklist customizada."""
        if self._blocklist_file.exists():
            self._custom_blocklist = set(
                line.strip().lower() 
                for line in self._blocklist_file.read_text().split('\n')
                if line.strip() and not line.startswith('#')
            )
    
    def add_to_blocklist(self, domain: str):
        """Adiciona domínio à blocklist."""
        self._custom_blocklist.add(domain.lower())
        
        with open(self._blocklist_file, 'a') as f:
            f.write(f"\n{domain.lower()}")
    
    def validate(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Valida URL.
        
        Returns:
            (is_valid: bool, block_reason: Optional[str])
        """
        try:
            parsed = urlparse(url)
        except:
            return False, "URL inválida"
        
        # 1. Verifica scheme
        if parsed.scheme not in ['http', 'https']:
            return False, f"Scheme não permitido: {parsed.scheme}"
        
        # 2. Verifica hostname
        hostname = parsed.hostname
        if not hostname:
            return False, "Hostname não encontrado"
        
        hostname_lower = hostname.lower()
        
        # 3. Bloqueia localhost e IPs internos
        if self._is_internal(hostname_lower):
            return False, "Acesso a rede interna bloqueado"
        
        # 4. Verifica blocklist de domínios
        if hostname_lower in self.BLOCKED_DOMAINS:
            return False, "Domínio na blocklist global"
        
        if hostname_lower in self._custom_blocklist:
            return False, "Domínio na blocklist customizada"
        
        # 5. Verifica padrões suspeitos
        full_url = url.lower()
        for regex in self._suspicious_regex:
            if regex.search(full_url):
                return False, f"URL contém padrão suspeito"
        
        # 6. Verifica TLD de alto risco
        tld = hostname_lower.split('.')[-1]
        if tld in ['tk', 'ml', 'ga', 'cf', 'gq']:
            logger.warning(f"TLD de alto risco: {tld}")
            # Permite mas com warning (não bloqueia)
        
        return True, None
    
    def _is_internal(self, hostname: str) -> bool:
        """Verifica se é endereço interno."""
        internal_patterns = [
            'localhost',
            '127.0.0.1',
            '0.0.0.0',
            '::1',
            '10.',
            '172.16.', '172.17.', '172.18.', '172.19.',
            '172.20.', '172.21.', '172.22.', '172.23.',
            '172.24.', '172.25.', '172.26.', '172.27.',
            '172.28.', '172.29.', '172.30.', '172.31.',
            '192.168.',
            'internal',
            'intranet',
        ]
        
        return any(hostname.startswith(p) for p in internal_patterns)


class ContentSanitizer:
    """Remove conteúdo potencialmente perigoso de HTML."""
    
    # Tags removidas completamente
    REMOVE_TAGS = [
        'script', 'style', 'iframe', 'frame', 'object', 
        'embed', 'form', 'input', 'button', 'select',
        'textarea', 'noscript', 'applet', 'meta'
    ]
    
    # Atributos removidos
    REMOVE_ATTRS = [
        'onclick', 'onload', 'onerror', 'onmouseover',
        'onfocus', 'onblur', 'onchange', 'onsubmit',
        'javascript:', 'data:', 'vbscript:'
    ]
    
    @classmethod
    def sanitize_html(cls, html: str, max_length: int = 50000) -> str:
        """
        Sanitiza HTML removendo elementos perigosos.
        Retorna texto limpo.
        """
        if not html:
            return ""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove tags perigosas
            for tag_name in cls.REMOVE_TAGS:
                for tag in soup.find_all(tag_name):
                    tag.decompose()
            
            # Remove atributos perigosos
            for tag in soup.find_all(True):
                for attr in list(tag.attrs.keys()):
                    attr_lower = attr.lower()
                    if any(bad in attr_lower for bad in cls.REMOVE_ATTRS):
                        del tag[attr]
                    elif attr_lower.startswith('on'):
                        del tag[attr]
            
            # Extrai texto limpo
            text = soup.get_text(separator='\n', strip=True)
            
            # Limita tamanho
            if len(text) > max_length:
                text = text[:max_length] + "\n\n[Conteúdo truncado...]"
            
            return text
            
        except Exception as e:
            logger.error(f"HTML sanitization error: {e}")
            return ""
    
    @classmethod
    def extract_links(cls, html: str, base_url: str) -> List[str]:
        """Extrai links seguros do HTML."""
        links = []
        validator = URLValidator()
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                
                # Converte para URL absoluta
                full_url = urljoin(base_url, href)
                
                # Valida
                is_valid, _ = validator.validate(full_url)
                if is_valid:
                    links.append(full_url)
            
            return links[:50]  # Limita a 50 links
            
        except:
            return []


class SafeWebFetcher:
    """
    Cliente HTTP seguro com múltiplas camadas de proteção.
    """
    
    DEFAULT_TIMEOUT = 10  # segundos
    MAX_RESPONSE_SIZE = 1 * 1024 * 1024  # 1MB
    MAX_REDIRECTS = 3
    
    # User-Agent inofensivo
    USER_AGENT = "OpenClaw/1.0 (AI Assistant; +https://github.com/openclaw)"
    
    def __init__(self):
        self.validator = URLValidator()
        self.sanitizer = ContentSanitizer()
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Retorna sessão HTTP reutilizável."""
        if self._session is None or self._session.closed:
            # SSL context seguro
            ssl_context = ssl.create_default_context()
            
            # Connector com limites
            connector = aiohttp.TCPConnector(
                limit=10,  # Max conexões simultâneas
                limit_per_host=2,
                ssl=ssl_context,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(total=self.DEFAULT_TIMEOUT)
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": self.USER_AGENT}
            )
        
        return self._session
    
    async def fetch(
        self, 
        url: str,
        extract_text: bool = True,
        follow_redirects: bool = True
    ) -> FetchResult:
        """
        Busca conteúdo de URL de forma segura.
        
        Args:
            url: URL para buscar
            extract_text: Se True, extrai apenas texto (sem HTML)
            follow_redirects: Se True, segue redirects (com limite)
        
        Returns:
            FetchResult com conteúdo ou erro
        """
        start_time = datetime.now()
        
        # 1. Valida URL
        is_valid, block_reason = self.validator.validate(url)
        
        if not is_valid:
            logger.warning(f"URL blocked: {url} - {block_reason}")
            return FetchResult(
                success=False,
                url=url,
                content=None,
                content_type="",
                status_code=0,
                blocked_reason=block_reason
            )
        
        try:
            session = await self._get_session()
            
            # 2. Faz requisição
            async with session.get(
                url,
                allow_redirects=follow_redirects,
                max_redirects=self.MAX_REDIRECTS
            ) as response:
                
                # 3. Verifica status
                if response.status >= 400:
                    return FetchResult(
                        success=False,
                        url=url,
                        content=None,
                        content_type=response.content_type or "",
                        status_code=response.status,
                        error=f"HTTP {response.status}"
                    )
                
                # 4. Verifica tamanho
                content_length = response.content_length or 0
                if content_length > self.MAX_RESPONSE_SIZE:
                    return FetchResult(
                        success=False,
                        url=url,
                        content=None,
                        content_type=response.content_type or "",
                        status_code=response.status,
                        error=f"Response too large: {content_length} bytes"
                    )
                
                # 5. Lê conteúdo
                content = await response.text(errors='ignore')
                
                # 6. Sanitiza se HTML
                if extract_text and 'html' in (response.content_type or '').lower():
                    content = self.sanitizer.sanitize_html(content)
                
                fetch_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                return FetchResult(
                    success=True,
                    url=str(response.url),  # URL final após redirects
                    content=content,
                    content_type=response.content_type or "",
                    status_code=response.status,
                    fetch_time_ms=fetch_time
                )
                
        except asyncio.TimeoutError:
            return FetchResult(
                success=False,
                url=url,
                content=None,
                content_type="",
                status_code=0,
                error="Timeout"
            )
        except aiohttp.ClientError as e:
            return FetchResult(
                success=False,
                url=url,
                content=None,
                content_type="",
                status_code=0,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Fetch error for {url}: {e}")
            return FetchResult(
                success=False,
                url=url,
                content=None,
                content_type="",
                status_code=0,
                error=str(e)
            )
    
    async def fetch_json(self, url: str) -> Tuple[Optional[dict], Optional[str]]:
        """Busca JSON de forma segura."""
        result = await self.fetch(url, extract_text=False)
        
        if not result.success:
            return None, result.error or result.blocked_reason
        
        try:
            import json
            data = json.loads(result.content)
            return data, None
        except:
            return None, "Invalid JSON"
    
    async def search_web(
        self, 
        query: str, 
        num_results: int = 5
    ) -> List[Dict]:
        """
        Busca na web usando DuckDuckGo (privacidade).
        Retorna lista de resultados.
        """
        # Usando DuckDuckGo Instant Answer API (gratuito)
        search_url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
        
        result = await self.fetch(search_url, extract_text=False)
        
        if not result.success:
            return []
        
        try:
            import json
            data = json.loads(result.content)
            
            results = []
            
            # Abstract
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Result'),
                    'snippet': data['Abstract'],
                    'url': data.get('AbstractURL', ''),
                    'source': data.get('AbstractSource', '')
                })
            
            # Related topics
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('Text', '')[:100],
                        'snippet': topic.get('Text', ''),
                        'url': topic.get('FirstURL', ''),
                        'source': 'DuckDuckGo'
                    })
            
            return results[:num_results]
            
        except:
            return []
    
    async def close(self):
        """Fecha sessão HTTP."""
        if self._session and not self._session.closed:
            await self._session.close()


# Função de conveniência para uso no assistente
async def safe_web_search(query: str) -> str:
    """
    Busca segura na web - função para tools do agente.
    """
    fetcher = SafeWebFetcher()
    
    try:
        results = await fetcher.search_web(query)
        
        if not results:
            return "Não encontrei resultados para essa busca."
        
        response = f"Encontrei {len(results)} resultados:\n\n"
        
        for i, r in enumerate(results, 1):
            response += f"{i}. **{r['title']}**\n"
            response += f"   {r['snippet'][:200]}...\n"
            if r['url']:
                response += f"   Link: {r['url']}\n"
            response += "\n"
        
        return response
        
    finally:
        await fetcher.close()


async def safe_fetch_page(url: str) -> str:
    """
    Busca página de forma segura - função para tools do agente.
    """
    fetcher = SafeWebFetcher()
    
    try:
        result = await fetcher.fetch(url)
        
        if not result.success:
            if result.blocked_reason:
                return f"URL bloqueada por segurança: {result.blocked_reason}"
            return f"Erro ao acessar página: {result.error}"
        
        # Limita conteúdo para resposta
        content = result.content[:5000] if result.content else ""
        
        return f"Conteúdo de {result.url}:\n\n{content}"
        
    finally:
        await fetcher.close()
```

### 6.3 Integração com Google Safe Browsing (Opcional)

```python
# Proposta: src/openclaw/web/safe_browsing.py

import aiohttp
import hashlib
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class GoogleSafeBrowsing:
    """
    Integração com Google Safe Browsing API.
    Requer API key (gratuita para uso não comercial).
    
    Referência: https://developers.google.com/safe-browsing
    """
    
    API_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    
    THREAT_TYPES = [
        "MALWARE",
        "SOCIAL_ENGINEERING",  # Phishing
        "UNWANTED_SOFTWARE",
        "POTENTIALLY_HARMFUL_APPLICATION"
    ]
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
        self._enabled = bool(self.api_key)
        
        if not self._enabled:
            logger.warning("Safe Browsing API key not configured. Feature disabled.")
    
    async def check_url(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Verifica URL contra base do Google.
        
        Returns:
            (is_safe: bool, threat_type: Optional[str])
        """
        if not self._enabled:
            return True, None  # Assume seguro se não configurado
        
        try:
            payload = {
                "client": {
                    "clientId": "openclaw",
                    "clientVersion": "1.0.0"
                },
                "threatInfo": {
                    "threatTypes": self.THREAT_TYPES,
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}]
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.API_URL}?key={self.api_key}",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"Safe Browsing API error: {response.status}")
                        return True, None  # Assume seguro em caso de erro
                    
                    data = await response.json()
                    
                    matches = data.get("matches", [])
                    
                    if matches:
                        threat_type = matches[0].get("threatType", "UNKNOWN")
                        logger.warning(f"Threat detected for {url}: {threat_type}")
                        return False, threat_type
                    
                    return True, None
                    
        except Exception as e:
            logger.error(f"Safe Browsing check failed: {e}")
            return True, None  # Assume seguro em caso de erro
    
    async def check_urls_batch(self, urls: List[str]) -> dict:
        """Verifica múltiplas URLs de uma vez."""
        results = {}
        
        for url in urls:
            is_safe, threat = await self.check_url(url)
            results[url] = {"safe": is_safe, "threat": threat}
        
        return results
```

---

## 🛡️ PARTE 7: CHECKLIST DE SEGURANÇA

### Checklist de Implementação

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SECURITY IMPLEMENTATION CHECKLIST                │
└─────────────────────────────────────────────────────────────────────┘

📋 AUTENTICAÇÃO
├── [ ] Voice biometrics implementado
├── [ ] Session tokens com expiração
├── [ ] Device fingerprinting
└── [ ] Multi-factor opcional

📋 AUTORIZAÇÃO
├── [ ] Command whitelist ativo
├── [ ] Command blacklist atualizado
├── [ ] Rate limiting por usuário
├── [ ] Rate limiting global
└── [ ] Permission levels definidos

📋 DADOS
├── [ ] Encryption at rest (AES-256)
├── [ ] Encryption in transit (TLS 1.3)
├── [ ] Secure key storage (OS keychain)
├── [ ] No sensitive data in logs
└── [ ] Data minimization aplicado

📋 WEB ACCESS
├── [ ] URL validation ativo
├── [ ] Blocklist atualizada
├── [ ] Content sanitization
├── [ ] Timeout configurado
├── [ ] Size limits aplicados
└── [ ] Safe Browsing integrado (opcional)

📋 AUDITORIA
├── [ ] Immutable logs configurados
├── [ ] Hash chain verificável
├── [ ] Alertas automáticos
├── [ ] Retenção de logs definida
└── [ ] Backup de logs

📋 CÓDIGO
├── [ ] Input sanitization em todas entradas
├── [ ] No eval()/exec() usage
├── [ ] Dependencies atualizadas
├── [ ] Secrets em env vars (não hardcoded)
└── [ ] Error handling sem info leak

📋 INFRAESTRUTURA
├── [ ] Process isolation
├── [ ] Resource limits (CPU, RAM)
├── [ ] Network isolation onde aplicável
└── [ ] Graceful degradation
```

### Métricas de Segurança

| Métrica | Target | Medição |
|---------|--------|---------|
| **Comandos bloqueados/dia** | < 5 legítimos | Audit logs |
| **Tentativas de ataque** | 0 sucesso | Audit logs |
| **URLs bloqueadas** | 100% maliciosas | Validator logs |
| **Tempo de autenticação** | < 2s | Prometheus |
| **Taxa de falsos positivos** | < 1% | User feedback |
| **Cobertura de audit** | 100% ações | Log analysis |

---

## ✅ CONCLUSÃO

Esta proposta transforma o JARVIS de um **assistente funcional** em uma **plataforma de IA assistente robusta**, mantendo o compromisso com:

1. **Custo zero** - Todas as ferramentas recomendadas são gratuitas/open-source
2. **Performance** - Otimizações que reduzem latência em 50-80%
3. **Escalabilidade** - Arquitetura que suporta crescimento
4. **Manutenibilidade** - Código modular e bem testado

**Próximos Passos Imediatos:**
1. Aprovar escopo da Fase 1
2. Criar branch `feature/v3-foundation`
3. Implementar ChromaDB + Memory Manager
4. Setup de CI/CD básico

---

*Documento gerado por análise arquitetural automatizada.*  
*Revisão humana recomendada antes da implementação.*
