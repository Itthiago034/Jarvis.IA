"""
JARVIS - Ferramentas Customizadas
=================================
Ferramentas completas para o CodeAgent - Engenheiro de Software Sênior.
Inclui: terminal, busca, web, análise, git, notebooks, diagramas e refatoração.
"""

# Terminal tools - Execução de comandos
from .terminal import (
    run_command,
    run_command_sync,
    get_command_output,
    CommandResult,
    is_safe_command,
)

# Search tools - Busca em código e arquivos
from .search import (
    grep_search,
    file_search,
    list_directory,
    simple_semantic_search,
    SearchMatch,
    FileMatch,
)

# Web tools - Busca na web e documentação
from .web import (
    fetch_webpage,
    fetch_webpage_sync,
    search_documentation,
    WebPage,
)

# Code Analysis tools - Erros, métricas, usos
from .code_analysis import (
    get_syntax_errors,
    get_python_errors,
    get_all_errors,
    find_symbol_usages,
    analyze_test_failure,
    count_code_metrics,
    CodeError,
    CodeUsage,
)

# Git tools - Controle de versão
from .git_tools import (
    is_git_repository,
    get_changed_files,
    get_file_diff,
    get_commit_history,
    get_current_branch,
    get_branches,
    get_repository_status,
    stage_files,
    unstage_files,
    create_commit,
    get_blame,
    run_git_command,
    ChangedFile,
    FileStatus,
)

# Notebook tools - Jupyter notebooks
from .notebook_tools import (
    read_notebook,
    get_notebook_summary,
    get_cell_content,
    edit_cell,
    add_cell,
    delete_cell,
    run_notebook,
    create_notebook,
    notebook_to_script,
    NotebookCell,
)

# Diagram tools - Geração de diagramas
from .diagram_tools import (
    generate_flowchart,
    add_flowchart_connections,
    generate_sequence_diagram,
    generate_class_diagram,
    generate_er_diagram,
    generate_state_diagram,
    analyze_python_structure,
    generate_class_diagram_from_file,
    generate_architecture_diagram,
    save_diagram,
    DiagramConfig,
)

# Refactoring tools - Refatoração de código
from .refactoring import (
    extract_function,
    rename_symbol,
    organize_imports,
    generate_docstring,
    add_type_hints,
    extract_constant,
    RefactoringResult,
)

__all__ = [
    # Terminal
    "run_command",
    "run_command_sync",
    "get_command_output",
    "CommandResult",
    "is_safe_command",
    # Search
    "grep_search",
    "file_search",
    "list_directory",
    "simple_semantic_search",
    "SearchMatch",
    "FileMatch",
    # Web
    "fetch_webpage",
    "fetch_webpage_sync",
    "search_documentation",
    "WebPage",
    # Code Analysis
    "get_syntax_errors",
    "get_python_errors",
    "get_all_errors",
    "find_symbol_usages",
    "analyze_test_failure",
    "count_code_metrics",
    "CodeError",
    "CodeUsage",
    # Git
    "is_git_repository",
    "get_changed_files",
    "get_file_diff",
    "get_commit_history",
    "get_current_branch",
    "get_branches",
    "get_repository_status",
    "stage_files",
    "unstage_files",
    "create_commit",
    "get_blame",
    "run_git_command",
    "ChangedFile",
    "FileStatus",
    # Notebooks
    "read_notebook",
    "get_notebook_summary",
    "get_cell_content",
    "edit_cell",
    "add_cell",
    "delete_cell",
    "run_notebook",
    "create_notebook",
    "notebook_to_script",
    "NotebookCell",
    # Diagrams
    "generate_flowchart",
    "add_flowchart_connections",
    "generate_sequence_diagram",
    "generate_class_diagram",
    "generate_er_diagram",
    "generate_state_diagram",
    "analyze_python_structure",
    "generate_class_diagram_from_file",
    "generate_architecture_diagram",
    "save_diagram",
    "DiagramConfig",
    # Refactoring
    "extract_function",
    "rename_symbol",
    "organize_imports",
    "generate_docstring",
    "add_type_hints",
    "extract_constant",
    "RefactoringResult",
]
