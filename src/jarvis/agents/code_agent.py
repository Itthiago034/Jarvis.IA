"""
JARVIS - CodeAgent (SubAgent de Programação)
=============================================
Engenheiro de Software Sênior virtual para o JARVIS.

Este módulo implementa um agente de programação usando Google ADK que pode:
- Analisar e corrigir código
- Refatorar e otimizar
- Criar scripts e sistemas
- Acessar sistema de arquivos local
- Executar código em sandbox seguro
- Integrar com GitHub (opcional)

Uso:
    from jarvis.agents.code_agent import CodeAgent
    
    # Criar agente
    agent = CodeAgent(workspace_path="/path/to/project")
    
    # Executar tarefa
    result = await agent.run("analise o arquivo main.py")

Dependências:
    pip install google-adk mcp

Autor: JARVIS Team
Versão: 0.1.0
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# Tenta importar ADK - se não estiver instalado, usa modo fallback
try:
    from google.adk.agents import LlmAgent  # type: ignore
    from google.adk.tools.mcp_tool import McpToolset  # type: ignore
    from google.adk.tools.mcp_tool.mcp_session_manager import (  # type: ignore
        StdioConnectionParams,
        StreamableHTTPServerParams
    )
    from google.adk.code_executors import BuiltInCodeExecutor  # type: ignore
    from google.adk.runners import Runner  # type: ignore
    from google.adk.sessions import InMemorySessionService  # type: ignore
    from mcp import StdioServerParameters  # type: ignore
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    print("⚠️ Google ADK não instalado. Execute: pip install google-adk mcp")

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Tipos de tarefas que o CodeAgent pode executar"""
    ANALYZE = "analyze"           # Analisar código
    REFACTOR = "refactor"         # Refatorar código
    CREATE = "create"             # Criar novo código
    DEBUG = "debug"               # Debugar problemas
    EXPLAIN = "explain"           # Explicar código
    REVIEW = "review"             # Code review
    TEST = "test"                 # Criar/executar testes
    OPTIMIZE = "optimize"         # Otimizar performance


@dataclass
class CodeTaskResult:
    """Resultado de uma tarefa do CodeAgent"""
    success: bool
    message: str
    code_changes: Optional[Dict[str, str]] = None  # {file_path: new_content}
    suggestions: Optional[List[str]] = None
    execution_output: Optional[str] = None
    files_affected: Optional[List[str]] = None


# Instrução principal do CodeAgent
CODE_AGENT_INSTRUCTION = """
# Identidade
Você é um **Engenheiro de Software Sênior** chamado CodeAssistant, 
parte integrante do sistema JARVIS. Você possui expertise em:

## Linguagens & Frameworks
- Python (especialidade), JavaScript/TypeScript, Java, C#, Go, Rust
- React, Vue, Angular, FastAPI, Django, Flask
- Node.js, .NET, Spring Boot

## Áreas de Conhecimento
- Arquitetura de Software e Design Patterns
- Clean Code e SOLID Principles
- DevOps, CI/CD, GitHub Actions
- Debugging, Profiling e Performance
- Segurança de aplicações
- Testes automatizados (unit, integration, e2e)

# Ferramentas Disponíveis
Você tem acesso a **50+ ferramentas** organizadas em 15 categorias:

## 1. 🖥️ Terminal (execute_terminal_command)
Executa comandos no sistema:
- Rodar scripts: `python main.py`, `npm start`
- Instalar pacotes: `pip install`, `npm install`
- Build: `make`, `cargo build`, `go build`

## 2. 🔍 Busca em Código (search_in_code, find_files, list_folder)
- **search_in_code**: Busca texto/regex em arquivos (grep)
- **find_files**: Encontra arquivos por padrão glob
- **list_folder**: Lista conteúdo de diretórios

## 3. 📁 Sistema de Arquivos (MCP FileSystem)
- **read_file**: Lê conteúdo de arquivos
- **write_file**: Escreve/cria arquivos
- **directory_tree**: Visualiza estrutura do projeto

## 4. 🌐 Web/Documentação (fetch_web_page, search_stackoverflow, web_search)
- Buscar documentação oficial online
- Pesquisar soluções no Stack Overflow
- Buscar na web com DuckDuckGo
- Obter info de pacotes (npm, PyPI)

## 5. 🐛 Análise de Código (check_code_errors, find_usages, get_code_metrics)
- **check_code_errors**: Erros de sintaxe e linting (pylint)
- **find_usages**: Encontra todos os usos de um símbolo
- **analyze_test_error**: Analisa falhas de testes
- **get_code_metrics**: Métricas do código (linhas, funções, classes)

## 6. 📊 Git (git_status, git_changed, git_diff, git_log, git_blame_file)
- **git_status**: Status completo do repositório
- **git_changed**: Arquivos modificados
- **git_diff**: Diff de arquivo específico
- **git_log**: Histórico de commits
- **git_blame_file**: Quem modificou cada linha

## 7. 📓 Notebooks (notebook_*)
- **notebook_summary**: Resumo do notebook
- **notebook_read_cell**: Ler célula específica
- **notebook_edit_cell**: Editar célula
- **notebook_add_cell**: Adicionar nova célula
- **notebook_to_python**: Converter para script .py

## 8. 📐 Diagramas (create_*_diagram, save_mermaid_diagram)
- **create_class_diagram_auto**: Diagrama de classes (automático de arquivo)
- **save_mermaid_diagram**: Salvar diagrama em arquivo

## 9. 🐙 GitHub (github_*)
- **github_list_issues**: Listar issues de um repositório
- **github_create_issue**: Criar nova issue
- **github_list_prs**: Listar pull requests
- **github_get_pr_diff**: Diff de um PR
- **github_search_code**: Buscar código no GitHub
- **github_workflow_status**: Status do GitHub Actions

## 10. 🔬 Pesquisa (search_*, web_*)
- **search_stackoverflow**: Buscar no Stack Overflow
- **get_stackoverflow_solution**: Obter solução melhor avaliada
- **web_search**: Buscar na web
- **get_package_info**: Info de pacotes npm/PyPI

## 11. 🖥️ Sistema Windows (system_*)
- **system_status**: CPU, memória, disco
- **list_processes**: Processos rodando
- **kill_process**: Encerrar processo
- **open_app**: Abrir aplicativo
- **get_clipboard / set_clipboard**: Área de transferência

## 12. 👁️ Visão/IA (vision_*)
- **screenshot_analyze**: Capturar e analisar tela
- **analyze_image**: Analisar imagem com Gemini
- **extract_text**: OCR em imagens
- **design_to_code**: Converter design para código

## 13. 🐳 Docker (docker_*)
- **docker_list_containers**: Listar containers
- **docker_start / docker_stop**: Iniciar/parar container
- **docker_logs**: Ver logs
- **docker_compose_up / docker_compose_down**: Docker Compose
- **docker_cleanup**: Limpar imagens não usadas

## 14. 🗄️ Banco de Dados (db_*)
- **sqlite_query / sqlite_schema**: SQLite queries
- **postgres_query**: PostgreSQL queries
- **mongodb_query**: MongoDB queries
- **natural_to_sql**: Converter texto para SQL

## 15. 📁 Scaffolding (project_*)
- **list_project_templates**: Listar templates disponíveis
- **create_project**: Criar projeto (FastAPI, React, Django, etc)
- **add_file_to_project**: Adicionar arquivo a projeto

## 9. 🔧 Refatoração (refactor_*)
- **refactor_extract_function**: Extrair código para função
- **refactor_rename**: Renomear símbolo em todo código
- **refactor_organize_imports**: Organizar imports (PEP8)
- **refactor_generate_docstring**: Gerar docstring (google/numpy/sphinx)
- **refactor_add_types**: Adicionar type hints
- **refactor_extract_constant**: Extrair valor para constante

## 10. 🐍 Code Execution (Sandbox Python)
- Validar sintaxe de código
- Testar funções isoladamente
- Executar cálculos e processamento

## 11. 🐙 GitHub (se habilitado)
- Analisar PRs e issues
- Buscar código em repositórios
- Criar issues e PRs

# Metodologia de Trabalho

## Ao analisar código:
1. Leia o arquivo completo primeiro
2. Identifique problemas de arquitetura, performance, segurança
3. Classifique por severidade (crítico, importante, sugestão)
4. Proponha soluções concretas com código

## Ao refatorar:
1. Entenda o contexto e propósito do código
2. Mantenha compatibilidade com código existente
3. Preserve funcionalidade - não quebre nada
4. Documente mudanças significativas
5. Sugira testes para validar

## Ao criar código novo:
1. Pergunte sobre requisitos se não estiverem claros
2. Use best practices da linguagem/framework
3. Inclua docstrings e comentários
4. Siga padrões do projeto existente
5. Sugira estrutura de arquivos se criar múltiplos

## Ao debugar:
1. Analise mensagens de erro cuidadosamente
2. Trace o fluxo de execução
3. Identifique a causa raiz, não apenas sintomas
4. Execute código de teste se necessário
5. Proponha fix com explicação

# Formato de Resposta

Use markdown formatado:
- Blocos de código com sintaxe highlighting
- Listas para múltiplos itens
- Negrito para conceitos importantes
- Tabelas quando comparando opções

Ao modificar código, sempre mostre:
1. O que será mudado e por quê
2. O código completo modificado
3. Como testar a mudança
4. Impactos potenciais

# Comportamento

- Seja **técnico e preciso**, mas acessível
- **Explique** suas decisões de design
- **Pergunte** se algo não estiver claro
- **Valide** antes de fazer mudanças destrutivas
- **Sugira** melhorias além do solicitado quando relevante
- Use tom profissional mas amigável
"""


class CodeAgent:
    """
    Agente de programação baseado em Google ADK.
    
    Implementa um Engenheiro de Software Sênior virtual com capacidades
    avançadas de análise, refatoração e criação de código.
    
    Attributes:
        workspace_path: Caminho base do workspace para operações de arquivo
        enable_github: Se True, habilita integração com GitHub
        model: Modelo Gemini a usar (padrão: gemini-2.5-pro)
    """
    
    def __init__(
        self,
        workspace_path: Optional[str] = None,
        enable_github: bool = False,
        model: str = "gemini-2.5-pro"
    ):
        """
        Inicializa o CodeAgent.
        
        Args:
            workspace_path: Caminho do workspace (padrão: diretório atual)
            enable_github: Habilita ferramentas do GitHub
            model: Modelo Gemini a usar
        """
        self.workspace_path = workspace_path or os.getcwd()
        self.enable_github = enable_github
        self.model = model
        self._agent: Optional[LlmAgent] = None
        self._runner: Optional[Runner] = None
        self._session_service: Optional[InMemorySessionService] = None
        self._initialized = False
        
        if not ADK_AVAILABLE:
            logger.warning("Google ADK não disponível. CodeAgent em modo limitado.")
    
    async def initialize(self) -> bool:
        """
        Inicializa o agente e suas ferramentas.
        
        Returns:
            True se inicialização bem sucedida, False caso contrário
        """
        if not ADK_AVAILABLE:
            logger.error("Não é possível inicializar sem Google ADK instalado")
            return False
        
        if self._initialized:
            return True
        
        try:
            # Configurar ferramentas
            tools = await self._setup_tools()
            
            # Criar agente
            # Nota: code_executor (BuiltInCodeExecutor) não pode ser usado junto com
            # custom tools (Function Calling). Remova code_executor para usar as ferramentas.
            self._agent = LlmAgent(
                name="code_engineer",
                model=self.model,
                instruction=CODE_AGENT_INSTRUCTION,
                description="Engenheiro de Software Sênior para programação",
                # code_executor=BuiltInCodeExecutor(),  # Incompatível com custom tools
                tools=tools,
            )
            
            # Configurar session e runner
            self._session_service = InMemorySessionService()
            self._runner = Runner(
                agent=self._agent,
                app_name="jarvis_code_agent",
                session_service=self._session_service,
            )
            
            self._initialized = True
            logger.info("CodeAgent inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar CodeAgent: {e}")
            return False
    
    async def _setup_tools(self) -> List:
        """Configura as ferramentas MCP e customizadas do agente"""
        tools = []
        
        # ===== FERRAMENTAS CUSTOMIZADAS (sem dependência externa) =====
        try:
            from google.adk.tools import FunctionTool  # type: ignore
            from ..tools.terminal import run_command_sync, is_safe_command
            from ..tools.search import grep_search, file_search, list_directory
            from ..tools.web import fetch_webpage_sync, search_documentation
            from ..tools.code_analysis import (
                get_python_errors, get_all_errors, find_symbol_usages,
                analyze_test_failure, count_code_metrics
            )
            from ..tools.git_tools import (
                get_changed_files, get_file_diff, get_commit_history,
                get_current_branch, get_repository_status, get_blame
            )
            from ..tools.notebook_tools import (
                get_notebook_summary, get_cell_content, edit_cell, add_cell,
                delete_cell, create_notebook, notebook_to_script
            )
            from ..tools.diagram_tools import (
                generate_flowchart, generate_sequence_diagram, generate_class_diagram,
                generate_class_diagram_from_file, generate_architecture_diagram, save_diagram
            )
            from ..tools.refactoring import (
                extract_function, rename_symbol, organize_imports,
                generate_docstring, add_type_hints, extract_constant
            )
            
            # ========== TERMINAL TOOLS ==========
            def execute_terminal_command(
                command: str,
                working_directory: str = None,
                timeout_seconds: int = 30
            ) -> dict:
                """
                Executa um comando no terminal do sistema.
                Use para: rodar scripts, instalar pacotes, compilar código, git commands.
                
                Args:
                    command: Comando a executar (ex: "python --version", "npm test")
                    working_directory: Diretório onde executar (opcional)
                    timeout_seconds: Timeout máximo em segundos
                    
                Returns:
                    Dicionário com success, output, error, return_code
                """
                if not is_safe_command(command):
                    return {"success": False, "error": "Comando bloqueado por segurança"}
                return run_command_sync(
                    command,
                    working_directory or self.workspace_path,
                    timeout_seconds
                )
            
            # ========== SEARCH TOOLS ==========
            def search_in_code(
                query: str,
                include_pattern: str = None,
                is_regex: bool = False,
                max_results: int = 50
            ) -> list:
                """
                Busca por texto em arquivos de código (grep).
                Use para: encontrar usos de funções, imports, strings específicas.
                """
                return grep_search(
                    query, self.workspace_path,
                    is_regex=is_regex, include_pattern=include_pattern, max_results=max_results
                )
            
            def find_files(pattern: str, max_results: int = 100) -> list:
                """Busca arquivos por padrão glob (ex: '**/*.py', 'src/**/*.ts')."""
                return file_search(pattern, self.workspace_path, max_results)
            
            def list_folder(path: str = ".", recursive: bool = False) -> list:
                """Lista conteúdo de uma pasta do projeto."""
                from pathlib import Path
                full_path = Path(self.workspace_path) / path
                return list_directory(str(full_path), recursive)
            
            # ========== WEB TOOLS ==========
            def fetch_web_page(url: str, extract_text: bool = True) -> dict:
                """Busca conteúdo de uma página web (documentação, APIs)."""
                return fetch_webpage_sync(url, extract_text_only=extract_text)
            
            def get_documentation_urls(query: str) -> list:
                """Retorna URLs de documentação oficial para um tópico."""
                return search_documentation(query)
            
            # ========== CODE ANALYSIS TOOLS ==========
            def check_code_errors(file_path: str = None, use_pylint: bool = True) -> list:
                """
                Verifica erros de código (sintaxe, linting).
                Se file_path não for fornecido, verifica todos os arquivos Python.
                """
                from pathlib import Path
                if file_path:
                    full_path = str(Path(self.workspace_path) / file_path)
                    return get_python_errors(full_path, use_pylint=use_pylint)
                return get_all_errors(self.workspace_path)
            
            def find_usages(symbol_name: str, file_pattern: str = "**/*.py") -> list:
                """
                Encontra todos os usos de um símbolo (função, classe, variável).
                Retorna: definições, imports e referências.
                """
                return find_symbol_usages(symbol_name, self.workspace_path, file_pattern)
            
            def analyze_test_error(error_output: str, test_file: str = None) -> dict:
                """
                Analisa uma falha de teste e sugere correções.
                Suporta pytest, unittest e jest.
                """
                return analyze_test_failure(error_output, test_file)
            
            def get_code_metrics(file_path: str) -> dict:
                """
                Obtém métricas de código: linhas, funções, classes, complexidade.
                """
                from pathlib import Path
                full_path = str(Path(self.workspace_path) / file_path)
                return count_code_metrics(full_path)
            
            # ========== GIT TOOLS ==========
            def git_status() -> dict:
                """
                Obtém status completo do repositório Git.
                Inclui: branch atual, arquivos modificados, staged, commits pendentes.
                """
                return get_repository_status(self.workspace_path)
            
            def git_changed() -> list:
                """Lista arquivos modificados (staged e unstaged)."""
                return get_changed_files(self.workspace_path)
            
            def git_diff(file_path: str, staged: bool = False) -> dict:
                """
                Obtém o diff de um arquivo específico.
                Mostra adições e remoções.
                """
                return get_file_diff(file_path, staged=staged, repo_path=self.workspace_path)
            
            def git_log(max_commits: int = 10, file_path: str = None) -> list:
                """Obtém histórico de commits."""
                return get_commit_history(self.workspace_path, max_commits, file_path)
            
            def git_blame_file(file_path: str, start_line: int = 1, end_line: int = None) -> list:
                """Obtém informações de blame (quem modificou cada linha)."""
                return get_blame(file_path, start_line, end_line, repo_path=self.workspace_path)
            
            # ========== NOTEBOOK TOOLS ==========
            def notebook_summary(file_path: str) -> dict:
                """
                Obtém resumo de um Jupyter Notebook.
                Lista células, tipos, outputs e métricas.
                """
                from pathlib import Path
                full_path = str(Path(self.workspace_path) / file_path)
                return get_notebook_summary(full_path)
            
            def notebook_read_cell(file_path: str, cell_number: int) -> dict:
                """Lê conteúdo de uma célula específica do notebook."""
                from pathlib import Path
                full_path = str(Path(self.workspace_path) / file_path)
                return get_cell_content(full_path, cell_number)
            
            def notebook_edit_cell(file_path: str, cell_number: int, new_content: str) -> dict:
                """Edita uma célula do notebook."""
                from pathlib import Path
                full_path = str(Path(self.workspace_path) / file_path)
                return edit_cell(full_path, cell_number, new_content)
            
            def notebook_add_cell(file_path: str, content: str, cell_type: str = "code", position: int = None) -> dict:
                """Adiciona nova célula ao notebook."""
                from pathlib import Path
                full_path = str(Path(self.workspace_path) / file_path)
                return add_cell(full_path, content, cell_type, position)
            
            def notebook_to_python(notebook_path: str, script_path: str = None) -> dict:
                """Converte notebook para script Python."""
                from pathlib import Path
                full_nb = str(Path(self.workspace_path) / notebook_path)
                full_script = str(Path(self.workspace_path) / script_path) if script_path else None
                return notebook_to_script(full_nb, full_script)
            
            # ========== DIAGRAM TOOLS ==========
            def create_flowchart(title: str, steps: list, direction: str = "TD") -> str:
                """
                Gera diagrama de fluxo em Mermaid.
                steps: [{"id": "A", "text": "Start", "type": "start"}]
                tipos: start, end, process, decision, io
                """
                return generate_flowchart(title, steps, direction)
            
            def create_sequence_diagram(title: str, participants: list, messages: list) -> str:
                """
                Gera diagrama de sequência em Mermaid.
                messages: [{"from": "A", "to": "B", "text": "Request", "type": "sync"}]
                """
                return generate_sequence_diagram(title, participants, messages)
            
            def create_class_diagram(title: str, classes: list, relationships: list = None) -> str:
                """
                Gera diagrama de classes em Mermaid.
                classes: [{"name": "User", "attributes": ["id"], "methods": ["save()"]}]
                """
                return generate_class_diagram(title, classes, relationships)
            
            def create_class_diagram_auto(file_path: str) -> str:
                """Gera diagrama de classes automaticamente de um arquivo Python."""
                from pathlib import Path
                full_path = str(Path(self.workspace_path) / file_path)
                return generate_class_diagram_from_file(full_path)
            
            def create_architecture_diagram(title: str, components: list, flows: list) -> str:
                """
                Gera diagrama de arquitetura.
                components: [{"id": "api", "name": "API Gateway", "type": "service"}]
                flows: [{"from": "client", "to": "api", "label": "HTTP"}]
                """
                return generate_architecture_diagram(title, components, flows)
            
            def save_mermaid_diagram(mermaid_code: str, file_path: str, format: str = "md") -> dict:
                """Salva diagrama Mermaid em arquivo (md, mmd ou html)."""
                from pathlib import Path
                full_path = str(Path(self.workspace_path) / file_path)
                return save_diagram(mermaid_code, full_path, format)
            
            # ========== REFACTORING TOOLS ==========
            def refactor_extract_function(
                source_code: str, start_line: int, end_line: int,
                function_name: str, parameters: list = None
            ) -> dict:
                """Extrai um trecho de código para uma nova função."""
                return extract_function(source_code, start_line, end_line, function_name, parameters)
            
            def refactor_rename(source_code: str, old_name: str, new_name: str) -> dict:
                """Renomeia um símbolo (variável, função, classe) no código."""
                return rename_symbol(source_code, old_name, new_name)
            
            def refactor_organize_imports(source_code: str) -> dict:
                """Organiza imports no estilo PEP8 (stdlib, terceiros, locais)."""
                return organize_imports(source_code)
            
            def refactor_generate_docstring(source_code: str, function_name: str, style: str = "google") -> dict:
                """
                Gera docstring para uma função.
                Estilos: google, numpy, sphinx
                """
                return generate_docstring(source_code, function_name, style)
            
            def refactor_add_types(source_code: str) -> dict:
                """Adiciona type hints básicos ao código."""
                return add_type_hints(source_code)
            
            def refactor_extract_constant(source_code: str, value: str, constant_name: str) -> dict:
                """Extrai um valor literal para uma constante."""
                return extract_constant(source_code, value, constant_name)
            
            # ========== REGISTRAR TODAS AS FERRAMENTAS ==========
            custom_tools = [
                # Terminal
                FunctionTool(execute_terminal_command),
                # Search
                FunctionTool(search_in_code),
                FunctionTool(find_files),
                FunctionTool(list_folder),
                # Web
                FunctionTool(fetch_web_page),
                FunctionTool(get_documentation_urls),
                # Code Analysis
                FunctionTool(check_code_errors),
                FunctionTool(find_usages),
                FunctionTool(analyze_test_error),
                FunctionTool(get_code_metrics),
                # Git
                FunctionTool(git_status),
                FunctionTool(git_changed),
                FunctionTool(git_diff),
                FunctionTool(git_log),
                FunctionTool(git_blame_file),
                # Notebooks
                FunctionTool(notebook_summary),
                FunctionTool(notebook_read_cell),
                FunctionTool(notebook_edit_cell),
                FunctionTool(notebook_add_cell),
                FunctionTool(notebook_to_python),
                # Diagrams
                FunctionTool(create_class_diagram_auto),
                FunctionTool(save_mermaid_diagram),
                # Refactoring
                FunctionTool(refactor_rename),
                FunctionTool(refactor_organize_imports),
                FunctionTool(refactor_generate_docstring),
                FunctionTool(refactor_add_types),
                FunctionTool(refactor_extract_constant),
            ]
            tools.extend(custom_tools)
            logger.info(f"🔧 Custom tools carregadas: {len(custom_tools)} ferramentas")
            
            # ========== FERRAMENTAS EXPANDIDAS (v2) ==========
            expanded_tools = await self._setup_expanded_tools()
            tools.extend(expanded_tools)
            logger.info(f"🚀 Expanded tools carregadas: {len(expanded_tools)} ferramentas")
            
        except ImportError as e:
            logger.warning(f"Algumas tools customizadas não disponíveis: {e}")
        except Exception as e:
            logger.warning(f"Erro ao configurar custom tools: {e}")
        
        # ===== MCP FILE SYSTEM TOOLS =====
        try:
            filesystem_toolset = McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command='npx',
                        args=[
                            "-y",
                            "@modelcontextprotocol/server-filesystem",
                            self.workspace_path
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
            logger.info(f"FileSystem MCP tools configurado para: {self.workspace_path}")
        except Exception as e:
            logger.warning(f"Não foi possível configurar FileSystem MCP tools: {e}")
            logger.info("Usando apenas custom tools (não requer Node.js)")
        
        # ===== GITHUB MCP TOOLS (opcional) =====
        if self.enable_github:
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                try:
                    github_toolset = McpToolset(
                        connection_params=StreamableHTTPServerParams(
                            url="https://api.githubcopilot.com/mcp/",
                            headers={
                                "Authorization": f"Bearer {github_token}",
                                "X-MCP-Toolsets": "repos,issues,pull_requests,code_security",
                                "X-MCP-Readonly": "true"  # Segurança: só leitura inicialmente
                            },
                        ),
                    )
                    tools.append(github_toolset)
                    logger.info("GitHub MCP tools configurado")
                except Exception as e:
                    logger.warning(f"Não foi possível configurar GitHub MCP tools: {e}")
            else:
                logger.warning("GITHUB_TOKEN não encontrado, GitHub tools desabilitado")
        
        logger.info(f"Total de ferramentas configuradas: {len(tools)}")
        return tools
    
    async def _setup_expanded_tools(self) -> list:
        """Configura ferramentas expandidas v2 (GitHub, Research, System, Vision, Docker, DB, Scaffolding)"""
        from google.adk.tools import FunctionTool  # type: ignore
        tools = []
        
        # ========== GITHUB TOOLS ==========
        try:
            from ..tools.github_tools import get_github_tools
            github_tools = get_github_tools()
            
            def github_list_issues(owner: str, repo: str, state: str = "open", limit: int = 10) -> str:
                """Lista issues de um repositório GitHub."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(github_tools["github_list_issues"](owner, repo, state, limit))
            
            def github_create_issue(owner: str, repo: str, title: str, body: str = "") -> str:
                """Cria uma nova issue no GitHub."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(github_tools["github_create_issue"](owner, repo, title, body))
            
            def github_list_prs(owner: str, repo: str, state: str = "open", limit: int = 10) -> str:
                """Lista pull requests de um repositório."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(github_tools["github_list_prs"](owner, repo, state, limit))
            
            def github_get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
                """Obtém o diff de um pull request."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(github_tools["github_get_pr_diff"](owner, repo, pr_number))
            
            def github_search_code(query: str, owner: str = None, repo: str = None) -> str:
                """Busca código no GitHub."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(github_tools["github_search_code"](query, owner, repo))
            
            def github_workflow_status(owner: str, repo: str) -> str:
                """Status dos workflows do GitHub Actions."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(github_tools["github_workflow_status"](owner, repo))
            
            tools.extend([
                FunctionTool(github_list_issues),
                FunctionTool(github_create_issue),
                FunctionTool(github_list_prs),
                FunctionTool(github_get_pr_diff),
                FunctionTool(github_search_code),
                FunctionTool(github_workflow_status),
            ])
            logger.info("✅ GitHub tools carregadas")
        except ImportError as e:
            logger.warning(f"GitHub tools não disponíveis: {e}")
        
        # ========== RESEARCH TOOLS ==========
        try:
            from ..tools.research_tools import get_research_tools
            research_tools = get_research_tools()
            
            def search_stackoverflow(query: str, limit: int = 5) -> str:
                """Busca no Stack Overflow."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(research_tools["search_stackoverflow"](query, limit))
            
            def get_stackoverflow_solution(question_id: int) -> str:
                """Obtém a melhor resposta de uma pergunta do Stack Overflow."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(research_tools["get_stackoverflow_solution"](question_id))
            
            def web_search(query: str, limit: int = 5) -> str:
                """Busca na web usando DuckDuckGo."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(research_tools["web_search"](query, limit))
            
            def get_package_info(name: str, registry: str = "pypi") -> str:
                """Info de um pacote (pypi ou npm)."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(research_tools["get_package_info"](name, registry))
            
            tools.extend([
                FunctionTool(search_stackoverflow),
                FunctionTool(get_stackoverflow_solution),
                FunctionTool(web_search),
                FunctionTool(get_package_info),
            ])
            logger.info("✅ Research tools carregadas")
        except ImportError as e:
            logger.warning(f"Research tools não disponíveis: {e}")
        
        # ========== SYSTEM TOOLS ==========
        try:
            from ..tools.system_tools import get_system_tools
            system_tools = get_system_tools()
            
            def system_status() -> str:
                """Status do sistema (CPU, memória, disco)."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(system_tools["system_status"]())
            
            def list_processes(filter_name: str = None) -> str:
                """Lista processos do sistema."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(system_tools["list_processes"](filter_name))
            
            def kill_process(pid: int) -> str:
                """Encerra um processo pelo PID."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(system_tools["kill_process"](pid))
            
            def open_app(app_name: str) -> str:
                """Abre um aplicativo."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(system_tools["open_app"](app_name))
            
            def get_clipboard() -> str:
                """Obtém conteúdo da área de transferência."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(system_tools["get_clipboard"]())
            
            def set_clipboard(text: str) -> str:
                """Define conteúdo da área de transferência."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(system_tools["set_clipboard"](text))
            
            tools.extend([
                FunctionTool(system_status),
                FunctionTool(list_processes),
                FunctionTool(kill_process),
                FunctionTool(open_app),
                FunctionTool(get_clipboard),
                FunctionTool(set_clipboard),
            ])
            logger.info("✅ System tools carregadas")
        except ImportError as e:
            logger.warning(f"System tools não disponíveis: {e}")
        
        # ========== VISION TOOLS ==========
        try:
            from ..tools.vision_tools import get_vision_tools
            vision_tools = get_vision_tools()
            
            def screenshot_analyze(prompt: str = "Descreva o que você vê") -> str:
                """Captura a tela e analisa com IA."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(vision_tools["screenshot_analyze"](prompt))
            
            def analyze_image(image_path: str, prompt: str = "Analise esta imagem") -> str:
                """Analisa uma imagem com Gemini."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(vision_tools["analyze_image"](image_path, prompt))
            
            def extract_text_from_image(image_path: str) -> str:
                """Extrai texto de uma imagem (OCR)."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(vision_tools["extract_text"](image_path))
            
            def design_to_code(image_path: str, framework: str = "html") -> str:
                """Converte design/mockup para código."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(vision_tools["design_to_code"](image_path, framework))
            
            tools.extend([
                FunctionTool(screenshot_analyze),
                FunctionTool(analyze_image),
                FunctionTool(extract_text_from_image),
                FunctionTool(design_to_code),
            ])
            logger.info("✅ Vision tools carregadas")
        except ImportError as e:
            logger.warning(f"Vision tools não disponíveis: {e}")
        
        # ========== DOCKER TOOLS ==========
        try:
            from ..tools.docker_tools import get_docker_tools
            docker_tools = get_docker_tools()
            
            def docker_list_containers(all: bool = False) -> str:
                """Lista containers Docker."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(docker_tools["docker_list_containers"](all))
            
            def docker_start(container: str) -> str:
                """Inicia um container."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(docker_tools["docker_start"](container))
            
            def docker_stop(container: str) -> str:
                """Para um container."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(docker_tools["docker_stop"](container))
            
            def docker_logs(container: str, lines: int = 100) -> str:
                """Mostra logs de um container."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(docker_tools["docker_logs"](container, lines))
            
            def docker_compose_up(path: str = ".", detach: bool = True) -> str:
                """Inicia serviços do docker-compose."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(docker_tools["docker_compose_up"](path, detach))
            
            def docker_compose_down(path: str = ".") -> str:
                """Para serviços do docker-compose."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(docker_tools["docker_compose_down"](path))
            
            def docker_cleanup() -> str:
                """Remove imagens e containers não usados."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(docker_tools["docker_cleanup"]())
            
            tools.extend([
                FunctionTool(docker_list_containers),
                FunctionTool(docker_start),
                FunctionTool(docker_stop),
                FunctionTool(docker_logs),
                FunctionTool(docker_compose_up),
                FunctionTool(docker_compose_down),
                FunctionTool(docker_cleanup),
            ])
            logger.info("✅ Docker tools carregadas")
        except ImportError as e:
            logger.warning(f"Docker tools não disponíveis: {e}")
        
        # ========== DATABASE TOOLS ==========
        try:
            from ..tools.database_tools import get_database_tools
            db_tools = get_database_tools()
            
            def sqlite_query(db_path: str, query: str) -> str:
                """Executa query SQLite."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(db_tools["sqlite_query"](db_path, query))
            
            def sqlite_schema(db_path: str) -> str:
                """Obtém schema de um banco SQLite."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(db_tools["sqlite_schema"](db_path))
            
            def postgres_query(connection_string: str, query: str) -> str:
                """Executa query PostgreSQL."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(db_tools["postgres_query"](connection_string, query))
            
            def mongodb_query(connection_string: str, database: str, collection: str, query: str = "{}") -> str:
                """Executa query MongoDB."""
                import asyncio
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(db_tools["mongodb_query"](connection_string, database, collection, query))
            
            def natural_to_sql(description: str, table_schema: str = "") -> str:
                """Converte descrição em linguagem natural para SQL."""
                return db_tools["natural_to_sql"](description, table_schema)
            
            tools.extend([
                FunctionTool(sqlite_query),
                FunctionTool(sqlite_schema),
                FunctionTool(postgres_query),
                FunctionTool(mongodb_query),
                FunctionTool(natural_to_sql),
            ])
            logger.info("✅ Database tools carregadas")
        except ImportError as e:
            logger.warning(f"Database tools não disponíveis: {e}")
        
        # ========== SCAFFOLDING TOOLS ==========
        try:
            from ..tools.scaffolding_tools import get_scaffolding_tools
            scaffolding = get_scaffolding_tools()
            
            def list_project_templates() -> str:
                """Lista templates de projeto disponíveis."""
                return scaffolding["list_project_templates"]()
            
            def create_project(template: str, name: str, output_dir: str = ".", description: str = "") -> str:
                """Cria novo projeto a partir de template."""
                return scaffolding["create_project"](template, name, output_dir, description)
            
            def add_file_to_project(project_dir: str, filepath: str, content: str) -> str:
                """Adiciona arquivo a um projeto existente."""
                return scaffolding["add_file_to_project"](project_dir, filepath, content)
            
            tools.extend([
                FunctionTool(list_project_templates),
                FunctionTool(create_project),
                FunctionTool(add_file_to_project),
            ])
            logger.info("✅ Scaffolding tools carregadas")
        except ImportError as e:
            logger.warning(f"Scaffolding tools não disponíveis: {e}")
        
        return tools
    
    async def run(
        self,
        request: str,
        session_id: Optional[str] = None,
        user_id: str = "jarvis_user"
    ) -> CodeTaskResult:
        """
        Executa uma solicitação de programação.
        
        Args:
            request: Solicitação do usuário em linguagem natural
            session_id: ID da sessão (cria nova se não fornecido)
            user_id: ID do usuário
            
        Returns:
            CodeTaskResult com o resultado da execução
        """
        if not self._initialized:
            success = await self.initialize()
            if not success:
                return CodeTaskResult(
                    success=False,
                    message="CodeAgent não pôde ser inicializado. Verifique se google-adk está instalado."
                )
        
        try:
            from google.genai import types
            
            # Criar sessão se necessário
            if not session_id:
                session_id = f"session_{asyncio.get_event_loop().time()}"
            
            session = await self._session_service.create_session(
                app_name="jarvis_code_agent",
                user_id=user_id,
                session_id=session_id
            )
            
            # Criar mensagem
            content = types.Content(
                role="user",
                parts=[types.Part(text=request)]
            )
            
            # Executar
            final_response = ""
            code_output = ""
            
            async for event in self._runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=content
            ):
                # Processar eventos
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            final_response += part.text
                        if hasattr(part, 'code_execution_result') and part.code_execution_result:
                            code_output = part.code_execution_result.output
                
                # Capturar resposta final
                if event.is_final_response():
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                final_response = part.text
            
            return CodeTaskResult(
                success=True,
                message=final_response,
                execution_output=code_output if code_output else None
            )
            
        except Exception as e:
            logger.error(f"Erro ao executar solicitação: {e}")
            return CodeTaskResult(
                success=False,
                message=f"Erro durante execução: {str(e)}"
            )
    
    async def analyze_file(self, file_path: str) -> CodeTaskResult:
        """
        Analisa um arquivo específico.
        
        Args:
            file_path: Caminho do arquivo a analisar
            
        Returns:
            CodeTaskResult com análise detalhada
        """
        request = f"""
        Por favor, analise o arquivo em '{file_path}':
        
        1. Leia o conteúdo do arquivo
        2. Identifique problemas de código (bugs, code smells, segurança)
        3. Sugira melhorias de performance se aplicável
        4. Verifique aderência a boas práticas
        5. Liste suas recomendações por prioridade
        """
        return await self.run(request)
    
    async def refactor_code(
        self,
        file_path: str,
        instructions: str
    ) -> CodeTaskResult:
        """
        Refatora código baseado em instruções.
        
        Args:
            file_path: Arquivo a refatorar
            instructions: Instruções de refatoração
            
        Returns:
            CodeTaskResult com código refatorado
        """
        request = f"""
        Refatore o arquivo '{file_path}' seguindo estas instruções:
        
        {instructions}
        
        Por favor:
        1. Leia o arquivo atual
        2. Aplique as mudanças solicitadas
        3. Mantenha compatibilidade
        4. Mostre o código refatorado completo
        5. Explique cada mudança significativa
        """
        return await self.run(request)
    
    async def create_code(
        self,
        description: str,
        output_path: Optional[str] = None
    ) -> CodeTaskResult:
        """
        Cria código novo baseado em descrição.
        
        Args:
            description: Descrição do que criar
            output_path: Caminho onde salvar (opcional)
            
        Returns:
            CodeTaskResult com código criado
        """
        save_instruction = ""
        if output_path:
            save_instruction = f"\nSalve o código no arquivo: {output_path}"
        
        request = f"""
        Crie código para: {description}
        {save_instruction}
        
        Requisitos:
        1. Use boas práticas da linguagem
        2. Inclua documentação/docstrings
        3. Trate erros apropriadamente
        4. Código limpo e legível
        """
        return await self.run(request)
    
    async def debug_error(
        self,
        error_message: str,
        context: Optional[str] = None
    ) -> CodeTaskResult:
        """
        Ajuda a debugar um erro.
        
        Args:
            error_message: Mensagem de erro
            context: Contexto adicional (arquivo, linha, etc)
            
        Returns:
            CodeTaskResult com diagnóstico e solução
        """
        context_info = f"\nContexto: {context}" if context else ""
        
        request = f"""
        Ajude a debugar este erro:
        
        ```
        {error_message}
        ```
        {context_info}
        
        Por favor:
        1. Analise a causa raiz do erro
        2. Se houver arquivo mencionado, leia-o
        3. Identifique a linha problemática
        4. Proponha a correção com código
        5. Explique por que o erro ocorreu
        """
        return await self.run(request)
    
    async def shutdown(self):
        """Encerra o agente e libera recursos"""
        if hasattr(self, '_filesystem_toolset'):
            try:
                await self._filesystem_toolset.close()
            except:
                pass
        self._initialized = False
        logger.info("CodeAgent encerrado")


# Funções de conveniência para uso direto
async def quick_analyze(file_path: str) -> str:
    """Analisa rapidamente um arquivo e retorna resultado"""
    agent = CodeAgent()
    result = await agent.analyze_file(file_path)
    await agent.shutdown()
    return result.message


async def quick_create(description: str) -> str:
    """Cria código rapidamente baseado em descrição"""
    agent = CodeAgent()
    result = await agent.create_code(description)
    await agent.shutdown()
    return result.message


# Exemplo de uso
if __name__ == "__main__":
    async def main():
        print("🤖 CodeAgent - Teste de Inicialização")
        print("=" * 50)
        
        if not ADK_AVAILABLE:
            print("\n❌ Google ADK não está instalado!")
            print("Execute: pip install google-adk mcp")
            return
        
        agent = CodeAgent(
            workspace_path=os.path.dirname(os.path.abspath(__file__)),
            enable_github=False,
            model="gemini-2.5-flash"
        )
        
        print("\n📦 Inicializando agente...")
        success = await agent.initialize()
        
        if success:
            print("✅ CodeAgent inicializado com sucesso!")
            
            # Teste básico
            print("\n🧪 Executando teste básico...")
            result = await agent.run("Qual é a soma de 2 + 2? Use code execution para calcular.")
            print(f"\nResultado: {result.message}")
        else:
            print("❌ Falha ao inicializar CodeAgent")
        
        await agent.shutdown()
        print("\n👋 Teste concluído!")
    
    asyncio.run(main())
