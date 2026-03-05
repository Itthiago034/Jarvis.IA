"""
JARVIS CLI - Output Formatting
==============================
Formatação rica para output no terminal.
"""

import re
from typing import Optional

# Tentar importar rich, se não disponível usar fallback
try:
    from rich.console import Console  # type: ignore[reportMissingImports]
    from rich.markdown import Markdown  # type: ignore[reportMissingImports]
    from rich.syntax import Syntax  # type: ignore[reportMissingImports]
    from rich.panel import Panel  # type: ignore[reportMissingImports]
    from rich.table import Table  # type: ignore[reportMissingImports]
    from rich.progress import Progress, SpinnerColumn, TextColumn  # type: ignore[reportMissingImports]
    from rich.live import Live  # type: ignore[reportMissingImports]
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Console global
console = Console() if RICH_AVAILABLE else None


def print_markdown(text: str):
    """Imprime texto formatado como Markdown"""
    if RICH_AVAILABLE:
        console.print(Markdown(text))
    else:
        print(text)


def print_code(code: str, language: str = "python", title: Optional[str] = None):
    """Imprime código com syntax highlighting"""
    if RICH_AVAILABLE:
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        if title:
            console.print(Panel(syntax, title=title))
        else:
            console.print(syntax)
    else:
        print(f"```{language}")
        print(code)
        print("```")


def print_panel(content: str, title: str, style: str = "blue"):
    """Imprime conteúdo em um painel"""
    if RICH_AVAILABLE:
        console.print(Panel(content, title=title, style=style))
    else:
        print(f"\n=== {title} ===")
        print(content)
        print("=" * (len(title) + 8))


def print_error(message: str):
    """Imprime mensagem de erro"""
    if RICH_AVAILABLE:
        console.print(f"[bold red]❌ Erro:[/bold red] {message}")
    else:
        print(f"❌ Erro: {message}")


def print_success(message: str):
    """Imprime mensagem de sucesso"""
    if RICH_AVAILABLE:
        console.print(f"[bold green]✅[/bold green] {message}")
    else:
        print(f"✅ {message}")


def print_warning(message: str):
    """Imprime aviso"""
    if RICH_AVAILABLE:
        console.print(f"[bold yellow]⚠️[/bold yellow] {message}")
    else:
        print(f"⚠️ {message}")


def print_info(message: str):
    """Imprime informação"""
    if RICH_AVAILABLE:
        console.print(f"[bold blue]ℹ️[/bold blue] {message}")
    else:
        print(f"ℹ️ {message}")


def print_agent_header(agent_name: str, emoji: str):
    """Imprime cabeçalho do agente"""
    if RICH_AVAILABLE:
        console.print(f"\n[bold cyan]{emoji} {agent_name}[/bold cyan]")
        console.print("[dim]─" * 50 + "[/dim]")
    else:
        print(f"\n{emoji} {agent_name}")
        print("─" * 50)


def print_user_input(prompt: str = ">>> "):
    """Imprime prompt de entrada do usuário"""
    if RICH_AVAILABLE:
        return console.input(f"[bold green]{prompt}[/bold green]")
    else:
        return input(prompt)


def print_table(title: str, headers: list, rows: list):
    """Imprime uma tabela"""
    if RICH_AVAILABLE:
        table = Table(title=title)
        for header in headers:
            table.add_column(header)
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        console.print(table)
    else:
        print(f"\n{title}")
        print("-" * len(title))
        print(" | ".join(headers))
        print("-" * (sum(len(h) for h in headers) + len(headers) * 3))
        for row in rows:
            print(" | ".join(str(cell) for cell in row))


def create_spinner(message: str = "Pensando..."):
    """Cria um spinner de loading"""
    if RICH_AVAILABLE:
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        )
    return None


def format_response(response: str) -> str:
    """
    Formata a resposta do agente, detectando blocos de código.
    """
    if not RICH_AVAILABLE:
        return response
    
    # Detectar blocos de código e formatá-los
    code_pattern = r"```(\w+)?\n(.*?)```"
    
    def replace_code(match):
        language = match.group(1) or "text"
        code = match.group(2)
        return f"\n[code:{language}]\n{code}[/code]\n"
    
    formatted = re.sub(code_pattern, replace_code, response, flags=re.DOTALL)
    return formatted


def print_welcome():
    """Imprime mensagem de boas-vindas estilo Gemini CLI"""
    # Banner ASCII colorido
    banner = """
[bold blue]     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗[/bold blue]
[bold cyan]     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝[/bold cyan]
[bold green]     ██║███████║██████╔╝██║   ██║██║███████╗[/bold green]
[bold yellow]██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║[/bold yellow]
[bold magenta]╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║[/bold magenta]
[bold red] ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝[/bold red]
"""
    
    tips = """[dim]Tips for getting started:
1. Ask questions, edit files, or run commands.
2. Use @agents to specialize: @coder, @reviewer, @debugger, @tester
3. Be specific for best results.
4. /help for more information.[/dim]
"""
    
    if RICH_AVAILABLE:
        console.print(banner)
        console.print(tips)
        console.print()
    else:
        # Versão sem cores
        plain_banner = """
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝

Tips for getting started:
1. Ask questions, edit files, or run commands.
2. Use @agents to specialize: @coder, @reviewer, @debugger, @tester
3. Be specific for best results.
4. /help for more information.
"""
        print(plain_banner)


def print_context_info(context):
    """Imprime informações do contexto detectado"""
    if RICH_AVAILABLE:
        info_parts = []
        if context.language:
            info_parts.append(f"[yellow]{context.language.upper()}[/yellow]")
        if context.framework:
            info_parts.append(f"[cyan]{context.framework}[/cyan]")
        if context.git_branch:
            info_parts.append(f"[green]📍 {context.git_branch}[/green]")
        
        if info_parts:
            console.print(f"📂 {context.root_path.name} | " + " | ".join(info_parts))
    else:
        parts = []
        if context.language:
            parts.append(context.language.upper())
        if context.framework:
            parts.append(context.framework)
        if context.git_branch:
            parts.append(f"📍 {context.git_branch}")
        
        if parts:
            print(f"📂 {context.root_path.name} | " + " | ".join(parts))


def clear_screen():
    """Limpa a tela"""
    if RICH_AVAILABLE:
        console.clear()
    else:
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
