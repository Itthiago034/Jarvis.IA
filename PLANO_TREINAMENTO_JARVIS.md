# Plano de Execução: "Treinar" o JARVIS

> **Baseado no:** ATLAS_GUIA_COMPLETO.md  
> **Data:** Março de 2026  
> **Objetivo:** Personalizar e aprimorar o JARVIS com conhecimento específico

---

## 1. Contexto: JARVIS vs Atlas

| Aspecto | Atlas | JARVIS |
|---------|-------|--------|
| **Modelo** | Local (DeepSeek-Coder GGUF) | API (Google Gemini) |
| **Execução** | 100% Offline | Requer internet |
| **Customização** | Fine-tuning com LoRA | Prompt Engineering + Memória |
| **Memória** | JSON local | mem0 (cloud) |
| **Interface** | CLI Terminal | Voz (LiveKit) |

### Limitação Importante

O JARVIS usa a **Google Gemini API**, que é um modelo fechado. Isso significa que:
- ❌ **Não é possível fazer fine-tuning tradicional** (treinar os pesos do modelo)
- ✅ **É possível personalizar via:**
  - Prompt Engineering avançado
  - Sistema de memória persistente (já temos com mem0)
  - RAG (Retrieval-Augmented Generation)
  - Context injection

---

## 2. Estratégias de "Treinamento" Disponíveis

### 2.1 Opção A: Prompt Engineering Avançado (Rápido)
**Complexidade:** 🟢 Baixa | **Tempo:** 1-2 dias

O que já temos em `prompts.py` pode ser expandido com:

```python
AGENT_INSTRUCTION = """
# Persona
Você é JARVIS...

# Base de Conhecimento Específico
## Sobre o usuário Thiago:
- Desenvolvedor focado em Python e C#
- Projetos atuais: JARVIS, Atlas
- Preferências de código: tipagem forte, async/await
- Estilo: pragmático, gosta de soluções diretas

## Conhecimento técnico prioritário:
- LiveKit Agents SDK
- Google Gemini API
- mem0 para memória
- PowerShell e WSL
- React + TypeScript (frontend)

## Contexto de projetos:
- JARVIS: Assistente de voz pessoal
- Atlas: IA local para análise de código
"""
```

**Prós:** Implementação imediata, sem infraestrutura adicional  
**Contras:** Limitado pelo contexto (~32K tokens), não escala bem

---

### 2.2 Opção B: RAG (Retrieval-Augmented Generation) 
**Complexidade:** 🟡 Média | **Tempo:** 1-2 semanas

Adicionar base de conhecimento vetorial, igual o Atlas faz:

```
┌─────────────────────────────────────────────────────────────────┐
│                 JARVIS COM RAG - ARQUITETURA                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  VOCÊ: "Como configuro o LiveKit Agent?"                         │
│                                                                   │
│              │                                                    │
│              ▼                                                    │
│  ┌───────────────────────────────────────────────────┐           │
│  │ ETAPA 1: BUSCA VETORIAL                           │           │
│  │ ─────────────────────                             │           │
│  │ ChromaDB busca nos documentos indexados:          │           │
│  │ - Documentação LiveKit                            │           │
│  │ - READMEs dos seus projetos                       │           │
│  │ - Código-fonte relevante                          │           │
│  │                                                   │           │
│  │ Retorna: Top 3-5 chunks mais relevantes           │           │
│  └───────────────────────────────────────────────────┘           │
│              │                                                    │
│              ▼                                                    │
│  ┌───────────────────────────────────────────────────┐           │
│  │ ETAPA 2: PROMPT AUMENTADO                         │           │
│  │ ─────────────────────────                         │           │
│  │ SYSTEM: Você é JARVIS...                          │           │
│  │ CONTEXTO:                                          │           │
│  │ [Doc 1]: "Para iniciar um agente LiveKit..."      │           │
│  │ [Doc 2]: "O método start() aceita..."             │           │
│  │ USER: Como configuro o LiveKit Agent?             │           │
│  └───────────────────────────────────────────────────┘           │
│              │                                                    │
│              ▼                                                    │
│  ┌───────────────────────────────────────────────────┐           │
│  │ ETAPA 3: RESPOSTA COM CONHECIMENTO                │           │
│  │ ─────────────────────────────────                 │           │
│  │ JARVIS responde com informações precisas          │           │
│  │ baseadas nos seus documentos reais                │           │
│  └───────────────────────────────────────────────────┘           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

#### Implementação sugerida:

```python
# jarvis_rag.py
import chromadb
from sentence_transformers import SentenceTransformer

class JarvisKnowledgeBase:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./knowledge_db")
        self.collection = self.client.get_or_create_collection("jarvis_docs")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_document(self, content: str, metadata: dict):
        """Adiciona documento à base de conhecimento."""
        embedding = self.embedder.encode(content).tolist()
        self.collection.add(
            documents=[content],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[metadata.get("id", str(hash(content)))]
        )
    
    def search(self, query: str, n_results: int = 3) -> list[str]:
        """Busca documentos relevantes."""
        query_embedding = self.embedder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results["documents"][0] if results["documents"] else []
```

**O que indexar:**
- Documentação dos seus projetos (READMEs, guias)
- Código-fonte importante (agent.py, wsl_tools.py)
- Preferências e padrões pessoais
- FAQs e soluções que você já usou

**Prós:** Conhecimento escalável, respostas precisas baseadas em dados reais  
**Contras:** Requer setup de ChromaDB, precisa indexar documentos

---

### 2.3 Opção C: Memória Expandida (mem0 Avançado)
**Complexidade:** 🟢 Baixa | **Tempo:** 3-5 dias

O JARVIS já usa mem0. Podemos expandir para armazenar mais contexto:

```python
# Atualmente: mem0 armazena conversas
# Expandir para: armazenar conhecimento estruturado

async def add_knowledge_to_memory(mem0: AsyncMemoryClient, knowledge: dict):
    """
    Adiciona conhecimento estruturado à memória do JARVIS.
    
    Exemplo:
    {
        "tipo": "preferencia_codigo",
        "conteudo": "Thiago prefere usar async/await ao invés de callbacks",
        "prioridade": "alta"
    }
    """
    await mem0.add([{
        "role": "system",
        "content": f"[CONHECIMENTO]: {knowledge['tipo']} - {knowledge['conteudo']}"
    }], user_id="Thiago")
```

**Prós:** Já temos a infraestrutura, fácil de implementar  
**Contras:** mem0 tem limites, não é ideal para grandes volumes

---

### 2.4 Opção D: Modelo Local (Como o Atlas)
**Complexidade:** 🔴 Alta | **Tempo:** 2-4 semanas

Trocar o Gemini por um modelo local com fine-tuning:

```
┌─────────────────────────────────────────────────────────────────┐
│                JARVIS COM MODELO LOCAL                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  OPÇÃO 1: Híbrido                                                │
│  ────────────────                                                │
│  - Gemini para voz (manter qualidade)                            │
│  - Modelo local para tarefas específicas (código, análise)       │
│                                                                   │
│  OPÇÃO 2: 100% Local                                             │
│  ───────────────────                                              │
│  - Substituir Gemini por modelo local                            │
│  - Fine-tuning com LoRA no seu estilo                            │
│  - Perda de qualidade de voz                                     │
│                                                                   │
│  MODELO RECOMENDADO:                                              │
│  - Qwen2.5-7B-Instruct (melhor custo/benefício)                  │
│  - Llama-3.2-3B (mais leve)                                      │
│  - DeepSeek-V2-Lite (bom para código)                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Prós:** Controle total, fine-tuning real, 100% privado  
**Contras:** Precisa de GPU, perde qualidade de voz do Gemini

---

## 3. Plano de Execução Recomendado

### Fase 1: Quick Wins (Esta semana)
**Objetivo:** Melhorar JARVIS sem mudanças estruturais

| # | Tarefa | Tempo | Impacto |
|---|--------|-------|---------|
| 1 | Expandir AGENT_INSTRUCTION com conhecimento específico | 2h | Alto |
| 2 | Criar arquivo de "fatos" sobre você para o prompt | 1h | Médio |
| 3 | Adicionar mais exemplos de comportamento desejado | 1h | Médio |

**Arquivo a criar:** `knowledge.py`
```python
# knowledge.py - Base de conhecimento inline

THIAGO_FACTS = """
## Informações sobre o usuário
- Nome: Thiago
- Profissão: Desenvolvedor de software
- Linguagens principais: Python, C#, TypeScript
- IDE preferida: VS Code
- Ambiente: Windows 11 + WSL2

## Projetos atuais
- JARVIS: Assistente pessoal com voz (LiveKit + Gemini)
- Atlas: IA local para análise de código (llama-cpp + PydanticAI)

## Preferências de código
- Tipagem forte (type hints em Python)
- Async/await quando possível
- Código limpo e bem documentado
- Testes unitários com pytest

## Comportamentos conhecidos
- Trabalha principalmente à noite
- Gosta de automação
- Prefere soluções pragmáticas
"""

TECHNICAL_KNOWLEDGE = """
## Stack JARVIS
- Backend: Python 3.11+
- Agent: LiveKit Agents SDK
- LLM: Google Gemini Realtime API
- Memória: mem0 AsyncMemoryClient
- Execução: Windows PowerShell + WSL

## Stack Atlas  
- Backend: Python 3.11+
- LLM: DeepSeek-Coder-1.3B (GGUF)
- Engine: llama-cpp-python
- Orquestração: PydanticAI
"""
```

### Fase 2: RAG Implementation (2 semanas)
**Objetivo:** Base de conhecimento vetorial

| # | Tarefa | Tempo |
|---|--------|-------|
| 1 | Instalar ChromaDB e sentence-transformers | 30min |
| 2 | Criar `jarvis_rag.py` com classe KnowledgeBase | 2h |
| 3 | Indexar documentação dos projetos | 2h |
| 4 | Indexar código-fonte relevante | 2h |
| 5 | Integrar busca RAG no agent.py | 3h |
| 6 | Criar tool `pesquisar_conhecimento` | 1h |
| 7 | Testar e ajustar relevância | 4h |

**Dependências:**
```
chromadb>=0.4.0
sentence-transformers>=2.2.0
```

### Fase 3: Especialização (Opcional, 1 mês)
**Objetivo:** Modelo especializado para tarefas específicas

| # | Tarefa | Tempo |
|---|--------|-------|
| 1 | Criar dataset de instruções personalizadas | 1 semana |
| 2 | Configurar ambiente de fine-tuning (Unsloth) | 2 dias |
| 3 | Treinar adaptadores LoRA | 2-3 dias |
| 4 | Integrar modelo híbrido (Gemini voz + Local código) | 1 semana |

---

## 4. Dataset para Fine-Tuning (Se escolher Opção D)

Estrutura JSONL para treinar o JARVIS no seu estilo:

```jsonl
{"instruction": "Cumprimente o usuário", "input": "", "output": "E aí, Chefe. O que precisamos resolver hoje?"}
{"instruction": "O usuário pediu para listar arquivos", "input": "lista os arquivos da minha pasta documentos", "output": "Entendido, senhor. Vou executar `Get-ChildItem ~/Documents`. [executa comando] Encontrei 15 arquivos e 3 pastas. Quer que eu detalhe algum?"}
{"instruction": "Analise este código Python e identifique problemas", "input": "def soma(a,b):\n  return a+b", "output": "Código funcional, mas faltam type hints. Versão melhorada:\n```python\ndef soma(a: int, b: int) -> int:\n    return a + b\n```"}
{"instruction": "O usuário perguntou algo que você não sabe", "input": "qual a previsao do tempo para amanha", "output": "Não tenho acesso a informações em tempo real sobre clima, Chefe. Sugiro verificar um app de previsão ou eu posso abrir o site do tempo para você."}
```

**Quantidade recomendada:** 500-1000 exemplos para resultados visíveis

---

## 5. Próximos Passos Imediatos

### Esta semana:
1. ✅ Criar `knowledge.py` com fatos sobre você
2. ⬜ Integrar knowledge.py no prompts.py
3. ⬜ Testar melhorias no comportamento

### Próxima semana:
4. ⬜ Setup ChromaDB
5. ⬜ Implementar `jarvis_rag.py`
6. ⬜ Indexar documentação

---

## 6. Comparativo de Esforço vs Resultado

| Estratégia | Esforço | Resultado | Recomendação |
|------------|---------|-----------|--------------|
| Prompt Engineering | 🟢 Baixo | Médio | ✅ Fazer primeiro |
| RAG com ChromaDB | 🟡 Médio | Alto | ✅ Fazer em seguida |
| Memória Expandida | 🟢 Baixo | Baixo-Médio | ⚠️ Complementar |
| Modelo Local + LoRA | 🔴 Alto | Muito Alto | ⏳ Fase 3 |

---

> **Conclusão:** Comece pela Fase 1 (prompt engineering) que dá resultados imediatos. 
> A Fase 2 (RAG) é o maior ganho de longo prazo sem precisar de GPU.
> A Fase 3 (modelo local) só faz sentido se você quiser controle total ou privacidade.

