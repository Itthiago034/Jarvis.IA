# 🚀 PROPOSTA DE APRIMORAMENTO - JARVIS v3.0

> **Análise Arquitetural e Roadmap de Evolução**  
> Autor: Arquitetura de Software & Engenharia de IA  
> Data: Março 2026  
> Versão Atual: 0.2.0 → Versão Alvo: 3.0.0

---

## 📋 Sumário Executivo

O JARVIS atingiu uma maturidade considerável com:
- **Agente de voz funcional** (LiveKit + Google Realtime)
- **Sistema de plugins extensível** (15+ plugins/tools)
- **Memória persistente** (mem0)
- **CodeAgent poderoso** (50+ ferramentas)

Este documento propõe evoluções em **três pilares**:
1. 🏗️ **Arquitetura** - Modernização e escalabilidade
2. ⚡ **Performance** - Otimização de componentes críticos
3. ✨ **Features** - Novas funcionalidades de alto impacto

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
