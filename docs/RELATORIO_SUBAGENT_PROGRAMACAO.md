# 📋 Relatório Técnico: SubAgent Engenheiro de Software para JARVIS

**Data:** 02 de Março de 2026  
**Versão:** 1.0  
**Autor:** Análise de Arquitetura  

---

## 🎯 Objetivo

Implementar um **SubAgent de Programação** para o JARVIS que funcione como um Engenheiro de Software Sênior, capaz de:

- ✅ Analisar e corrigir código
- ✅ Refatorar e otimizar
- ✅ Criar scripts e sistemas
- ✅ Acessar sistema de arquivos
- ✅ Executar código em sandbox
- ✅ Integrar com GitHub (análise de PRs, issues, etc.)

---

## 📊 Análise de Viabilidade

### ✅ TOTALMENTE VIÁVEL

Baseado na pesquisa realizada, a implementação é **100% viável** utilizando o **Google ADK (Agent Development Kit)** que você já viu no Vertex AI. Este framework é ideal porque:

1. **Já usa Gemini** - Seu projeto atual usa Google Gemini, então a integração é nativa
2. **Multi-Agent Support** - Suporta sistemas multi-agentes nativamente
3. **MCP Tools** - Protocolo padrão para ferramentas (File System, GitHub, etc.)
4. **Code Execution** - Execução segura de código em sandbox
5. **Gratuito** - Framework open-source mantido pelo Google

---

## 🏗️ Arquitetura Proposta

### Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                         JARVIS                                   │
│                    (Agente Principal)                           │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Voice Interface (LiveKit)                     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   Router Agent                             │ │
│  │              (Decide qual SubAgent usar)                  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │   Plugins   │     │  CodeAgent  │     │  Outros...  │       │
│  │  (Atual)    │     │  (NOVO!)    │     │  (Futuro)   │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                              │                                   │
│         ┌─────────────┬──────┴──────┬─────────────┐             │
│         ▼             ▼             ▼             ▼             │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│   │FileSystem│ │  GitHub  │ │Code Exec │ │ Search   │          │
│   │  Tools   │ │  Tools   │ │ Sandbox  │ │  Tools   │          │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes do CodeAgent

| Componente | Função | Tecnologia |
|------------|--------|------------|
| **CodeAgent** | Agente principal de programação | Google ADK LlmAgent |
| **FileSystem Tools** | Ler/escrever/listar arquivos | MCP @modelcontextprotocol/server-filesystem |
| **GitHub Tools** | PRs, issues, análise de código | GitHub MCP Server |
| **Code Executor** | Executar código com segurança | BuiltInCodeExecutor ou GKE Sandbox |
| **Search Tools** | Buscar documentação e soluções | Google Search ou Vertex AI Search |

---

## 🛠️ Opções de Implementação

### Opção 1: Google ADK (RECOMENDADA ⭐)

**Prós:**
- ✅ Framework oficial do Google
- ✅ Integração nativa com Gemini
- ✅ 18.1k stars no GitHub (muito ativo)
- ✅ Multi-agent system built-in
- ✅ MCP tools para File System e GitHub
- ✅ Code execution sandbox
- ✅ Deploy fácil no Google Cloud
- ✅ Gratuito e open-source

**Contras:**
- ⚠️ Curva de aprendizado inicial
- ⚠️ Pode precisar reestruturar parte do código

**Custo estimado:** $0-50/mês (dependendo do uso)

### Opção 2: Vertex AI Agent Builder (Cloud Console)

**Prós:**
- ✅ Interface visual no Console (como nos prints)
- ✅ Gerenciamento via Google Cloud
- ✅ Escalabilidade automática

**Contras:**
- ❌ Menos flexibilidade
- ❌ Custo maior ($100-500/mês)
- ❌ Dependência total do Cloud

**Custo estimado:** $100-500/mês

### Opção 3: Integração Híbrida (ADK + LiveKit Atual)

**Prós:**
- ✅ Mantém estrutura atual do JARVIS
- ✅ Adiciona CodeAgent como plugin
- ✅ Menor refatoração necessária

**Contras:**
- ⚠️ Pode haver conflitos de dependências
- ⚠️ Complexidade de integração

**Custo estimado:** $0-30/mês

---

## 📦 Dependências Necessárias

```txt
# requirements.txt - Adicionar:
google-adk>=1.26.0          # Agent Development Kit
mcp>=1.0.0                  # Model Context Protocol
```

Para MCP File System (via Node.js):
```bash
npm install -g npx
# O servidor é executado via: npx @modelcontextprotocol/server-filesystem
```

---

## 🔧 Ferramentas Disponíveis

### 1. File System Tools (via MCP)
```python
# Permite:
- list_directory(path)        # Listar arquivos
- read_file(path)             # Ler arquivos
- write_file(path, content)   # Escrever arquivos
- search_files(pattern)       # Buscar arquivos
- get_file_info(path)         # Informações do arquivo
```

### 2. GitHub Tools (via MCP)
```python
# Permite:
- get_repository(owner, repo)     # Info do repositório
- list_commits(owner, repo)       # Histórico de commits
- get_file_contents(...)          # Ler arquivos do repo
- create_issue(...)               # Criar issues
- create_pull_request(...)        # Criar PRs
- search_code(query)              # Buscar código
```

### 3. Code Execution (BuiltInCodeExecutor)
```python
# Permite:
- Executar código Python em sandbox seguro
- Cálculos e processamento de dados
- Validação de sintaxe
- Testes unitários simples
```

### 4. Google Search (Opcional)
```python
# Permite:
- Buscar documentação
- Encontrar soluções para erros
- Pesquisar bibliotecas
```

---

## 📝 Código de Implementação

### Estrutura de Pastas Proposta

```
src/jarvis/
├── agents/
│   ├── __init__.py
│   ├── code_agent.py       # SubAgent de Programação
│   └── router.py           # Roteador de agentes
├── tools/
│   ├── __init__.py
│   ├── filesystem.py       # Wrapper para File System MCP
│   └── github.py           # Wrapper para GitHub MCP
├── plugins/                # Plugins existentes
└── agent.py                # Agent principal (existente)
```

### Implementação Básica do CodeAgent

```python
# src/jarvis/agents/code_agent.py
"""
JARVIS - CodeAgent (SubAgent de Programação)
=============================================
Engenheiro de Software Sênior virtual com capacidades de:
- Análise e correção de código
- Refatoração e otimização
- Criação de scripts e sistemas
- Acesso ao sistema de arquivos
- Execução de código em sandbox
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StreamableHTTPServerParams
)
from google.adk.code_executors import BuiltInCodeExecutor
from mcp import StdioServerParameters

# Configurações
WORKSPACE_PATH = os.path.dirname(os.path.abspath(__file__))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Instrução do CodeAgent
CODE_AGENT_INSTRUCTION = """
# Persona
Você é um Engenheiro de Software Sênior chamado CodeAssistant, 
assistente do JARVIS. Você tem expertise em:

- Python, JavaScript, TypeScript, Java, C#, Go
- Arquitetura de Software e Design Patterns
- DevOps, CI/CD, GitHub Actions
- Debugging e análise de performance
- Boas práticas de código limpo

# Capacidades
Você tem acesso a ferramentas poderosas:
1. **File System**: Ler, escrever, listar arquivos no workspace
2. **Code Execution**: Executar código Python em sandbox seguro
3. **GitHub**: Analisar repositórios, PRs, issues (se configurado)

# Estilo de Trabalho
- Seja direto e técnico
- Explique suas decisões de arquitetura
- Sempre valide mudanças antes de aplicar
- Sugira testes quando apropriado
- Use comentários explicativos no código

# Fluxo de Trabalho
1. Entenda o problema completamente
2. Analise o código existente (se aplicável)
3. Proponha solução com justificativa
4. Implemente com código limpo e documentado
5. Sugira melhorias adicionais se relevante

# Formato de Resposta
- Use markdown para código
- Explique mudanças linha a linha quando complexo
- Liste arquivos modificados ao final
"""

def create_code_agent(
    workspace_path: str = WORKSPACE_PATH,
    enable_github: bool = False
) -> LlmAgent:
    """
    Cria o CodeAgent com todas as ferramentas configuradas.
    
    Args:
        workspace_path: Caminho do workspace para operações de arquivo
        enable_github: Se True, habilita ferramentas do GitHub
    
    Returns:
        LlmAgent configurado como Engenheiro de Software
    """
    
    tools = []
    
    # 1. File System Tools (MCP)
    filesystem_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    workspace_path
                ],
            ),
            timeout=30,
        ),
        tool_filter=[
            'read_file',
            'read_multiple_files',
            'write_file',
            'list_directory',
            'directory_tree',
            'search_files',
            'get_file_info',
        ]
    )
    tools.append(filesystem_toolset)
    
    # 2. GitHub Tools (opcional)
    if enable_github and GITHUB_TOKEN:
        github_toolset = McpToolset(
            connection_params=StreamableHTTPServerParams(
                url="https://api.githubcopilot.com/mcp/",
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "X-MCP-Toolsets": "repos,issues,pull_requests,code_security",
                    "X-MCP-Readonly": "false"
                },
            ),
        )
        tools.append(github_toolset)
    
    # 3. Criar o Agent
    code_agent = LlmAgent(
        name="code_engineer",
        model="gemini-2.5-flash",  # ou gemini-2.5-pro para tarefas complexas
        instruction=CODE_AGENT_INSTRUCTION,
        description="Engenheiro de Software Sênior para análise, correção e criação de código",
        code_executor=BuiltInCodeExecutor(),  # Execução de código em sandbox
        tools=tools,
    )
    
    return code_agent


# Funções de conveniência para integração com JARVIS
async def analyze_code(file_path: str) -> str:
    """Analisa um arquivo de código e retorna sugestões."""
    agent = create_code_agent()
    # Lógica de execução...
    pass

async def refactor_code(file_path: str, instructions: str) -> str:
    """Refatora código baseado em instruções."""
    agent = create_code_agent()
    # Lógica de execução...
    pass

async def create_script(description: str) -> str:
    """Cria um novo script baseado em descrição."""
    agent = create_code_agent()
    # Lógica de execução...
    pass
```

### Integração com JARVIS (Plugin)

```python
# src/jarvis/plugins/code_assistant.py
"""
Plugin de integração do CodeAgent com JARVIS
"""

from ..plugins.base import JarvisPlugin, PluginContext, PluginResponse, PluginPriority

class CodeAssistantPlugin(JarvisPlugin):
    """
    Plugin que conecta o JARVIS ao CodeAgent.
    Permite que o usuário peça análises de código por voz.
    """
    
    name = "Code Assistant"
    description = "Engenheiro de Software Sênior para programação"
    version = "1.0.0"
    author = "JARVIS Team"
    
    trigger_phrases = [
        "analise o código",
        "corrija o erro",
        "refatore",
        "crie um script",
        "programa",
        "código",
        "função",
        "classe",
        "bug",
        "erro no código",
        "engenheiro",
        "desenvolvedor",
    ]
    
    priority = PluginPriority.HIGH
    requires_internet = True
    
    async def initialize(self) -> bool:
        """Inicializa conexão com CodeAgent"""
        try:
            from ..agents.code_agent import create_code_agent
            self._agent = create_code_agent()
            self._status = PluginStatus.ENABLED
            return True
        except Exception as e:
            self._error_message = str(e)
            self._status = PluginStatus.ERROR
            return False
    
    async def execute(self, context: PluginContext) -> PluginResponse:
        """Executa solicitação de programação"""
        user_request = context.user_message
        
        # Delega para o CodeAgent
        # ... implementação da execução
        
        return PluginResponse(
            message="Análise concluída. Encontrei 3 melhorias sugeridas...",
            success=True,
            should_speak=True,
            data={"changes": [...]}
        )
```

---

## 🚀 Plano de Implementação

### Fase 1: Setup Básico (1-2 dias)
- [ ] Instalar `google-adk` e `mcp`
- [ ] Configurar Node.js para MCP servers
- [ ] Criar estrutura de pastas `agents/` e `tools/`
- [ ] Implementar CodeAgent básico

### Fase 2: Ferramentas Core (2-3 dias)
- [ ] Integrar File System MCP
- [ ] Testar leitura/escrita de arquivos
- [ ] Implementar Code Execution sandbox
- [ ] Criar wrapper functions

### Fase 3: Integração JARVIS (1-2 dias)
- [ ] Criar plugin CodeAssistantPlugin
- [ ] Integrar com sistema de plugins existente
- [ ] Testar fluxo de voz → análise → resposta

### Fase 4: GitHub Integration (Opcional, 1-2 dias)
- [ ] Configurar GitHub PAT
- [ ] Integrar GitHub MCP Server
- [ ] Testar PR review e issue creation

### Fase 5: Refinamento (Contínuo)
- [ ] Ajustar prompts baseado em feedback
- [ ] Otimizar performance
- [ ] Adicionar mais ferramentas conforme necessário

---

## 💰 Análise de Custos

### Opção Recomendada (ADK + Gemini)

| Item | Custo Mensal |
|------|--------------|
| Gemini API (uso moderado) | $0-20 |
| Google Cloud (opcional) | $0-30 |
| Node.js (MCP servers) | Gratuito |
| **Total** | **$0-50** |

### Vertex AI Agent Engine (Alternativa)

| Item | Custo Mensal |
|------|--------------|
| Agent Engine | $50-200 |
| Compute | $20-100 |
| Storage | $5-20 |
| **Total** | **$75-320** |

---

## 🔒 Considerações de Segurança

1. **File System Access**
   - Limitar a paths específicos (workspace apenas)
   - Usar `tool_filter` para restringir operações
   - Evitar acesso a arquivos sensíveis (.env, credentials)

2. **Code Execution**
   - Usar sandbox (BuiltInCodeExecutor)
   - Limite de tempo de execução
   - Sem acesso a rede no sandbox

3. **GitHub**
   - Usar tokens com escopo mínimo necessário
   - Preferir `X-MCP-Readonly: true` inicialmente
   - Audit log de todas as operações

---

## 📚 Recursos e Documentação

### Links Oficiais
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Python GitHub](https://github.com/google/adk-python)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)

### Tutoriais Recomendados
- [Get Started with ADK Python](https://google.github.io/adk-docs/get-started/python/)
- [Multi-Agent Systems](https://google.github.io/adk-docs/agents/multi-agents/)
- [MCP Tools Integration](https://google.github.io/adk-docs/tools-custom/mcp-tools/)
- [Code Execution](https://google.github.io/adk-docs/integrations/code-execution/)

---

## ✅ Conclusão e Recomendação

### Recomendação: **Google ADK + MCP Tools**

Esta é a melhor opção porque:

1. **Alinhamento Tecnológico**: Você já usa Gemini, o ADK é feito para Gemini
2. **Custo-Benefício**: Praticamente gratuito para uso inicial
3. **Flexibilidade**: Controle total sobre o código e comportamento
4. **Comunidade Ativa**: 18.1k stars, 245 contribuidores, updates semanais
5. **Escalabilidade**: Pode deployar no Vertex AI quando precisar
6. **Ferramentas Prontas**: MCP servers para File System e GitHub já existem

### Próximos Passos

1. **Aprovar** esta proposta de arquitetura
2. **Instalar** dependências básicas (`google-adk`, `mcp`)
3. **Implementar** CodeAgent em fases
4. **Testar** incrementalmente

---

**Aguardo sua aprovação para iniciar a implementação!** 🚀
