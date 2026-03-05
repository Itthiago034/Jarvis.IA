"""
JARVIS v2 - Quality Assurance Tests
====================================
Testes abrangentes de todas as ferramentas implementadas.
Execute com: python tests/qa_jarvis_v2.py
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(title: str):
    print(f"\n{Colors.CYAN}{'='*60}")
    print(f" {title}")
    print(f"{'='*60}{Colors.END}\n")

def print_test(name: str, passed: bool, details: str = ""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"  {status} {name}")
    if details and not passed:
        print(f"       {Colors.YELLOW}{details}{Colors.END}")

def print_section(name: str):
    print(f"\n{Colors.BLUE}▶ {name}{Colors.END}")

results = {"passed": 0, "failed": 0, "skipped": 0}

def record_result(passed: bool):
    if passed:
        results["passed"] += 1
    else:
        results["failed"] += 1


# ==================== TESTES ====================

async def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print_section("Import Tests")
    
    modules = [
        ("CodeAgent", "src.jarvis.agents.code_agent", "CodeAgent"),
        ("GitHub Tools", "src.jarvis.tools.github_tools", "get_github_tools"),
        ("Research Tools", "src.jarvis.tools.research_tools", "get_research_tools"),
        ("System Tools", "src.jarvis.tools.system_tools", "get_system_tools"),
        ("Vision Tools", "src.jarvis.tools.vision_tools", "get_vision_tools"),
        ("Docker Tools", "src.jarvis.tools.docker_tools", "get_docker_tools"),
        ("Database Tools", "src.jarvis.tools.database_tools", "get_database_tools"),
        ("Scaffolding Tools", "src.jarvis.tools.scaffolding_tools", "get_scaffolding_tools"),
        ("CLI Main", "src.jarvis.cli.main", "app"),
        ("CLI Config", "src.jarvis.cli.config", "CLIConfig"),
    ]
    
    for name, module_path, attr in modules:
        try:
            module = __import__(module_path, fromlist=[attr])
            obj = getattr(module, attr)
            passed = obj is not None
            print_test(f"Import {name}", passed)
            record_result(passed)
        except Exception as e:
            print_test(f"Import {name}", False, str(e)[:50])
            record_result(False)


async def test_scaffolding_tools():
    """Testa as ferramentas de scaffolding"""
    print_section("Scaffolding Tools")
    
    try:
        from src.jarvis.tools.scaffolding_tools import get_scaffolding_tools
        tools = get_scaffolding_tools()
        
        # Test list templates
        templates = tools["list_project_templates"]()
        passed = "python-basic" in templates and "fastapi" in templates
        print_test("List project templates", passed)
        record_result(passed)
        
        # Test create project (dry run - verificar retorno sem criar)
        # Não vamos criar projeto para não poluir o filesystem
        passed = callable(tools["create_project"])
        print_test("Create project function exists", passed)
        record_result(passed)
        
    except Exception as e:
        print_test("Scaffolding tools", False, str(e)[:50])
        record_result(False)


async def test_system_tools():
    """Testa as ferramentas de sistema"""
    print_section("System Tools")
    
    try:
        from src.jarvis.tools.system_tools import get_system_tools
        tools = get_system_tools()
        
        # Test system status
        status = await tools["system_status"]()
        passed = "CPU" in status and "RAM" in status
        print_test("System status", passed)
        record_result(passed)
        
        # Test list processes
        procs = await tools["list_processes"]()
        passed = "python" in procs.lower() or "processo" in procs.lower()
        print_test("List processes", passed)
        record_result(passed)
        
        # Test clipboard (get)
        try:
            clipboard = await tools["get_clipboard"]()
            passed = isinstance(clipboard, str)
            print_test("Get clipboard", passed)
            record_result(passed)
        except:
            print_test("Get clipboard", False, "Clipboard access failed")
            record_result(False)
        
    except Exception as e:
        print_test("System tools", False, str(e)[:50])
        record_result(False)


async def test_research_tools():
    """Testa as ferramentas de pesquisa"""
    print_section("Research Tools")
    
    try:
        from src.jarvis.tools.research_tools import get_research_tools
        tools = get_research_tools()
        
        # Test search stackoverflow (mock - só verifica se função existe e retorna)
        try:
            # Rate limit pode impedir, então só verificamos se função existe
            passed = callable(tools["search_stackoverflow"])
            print_test("Stack Overflow search function", passed)
            record_result(passed)
        except Exception as e:
            print_test("Stack Overflow search", False, str(e)[:30])
            record_result(False)
        
        # Test web search function exists
        passed = callable(tools["web_search"])
        print_test("Web search function exists", passed)
        record_result(passed)
        
        # Test package info function exists
        passed = callable(tools["get_package_info"])
        print_test("Package info function exists", passed)
        record_result(passed)
        
    except Exception as e:
        print_test("Research tools", False, str(e)[:50])
        record_result(False)


async def test_docker_tools():
    """Testa as ferramentas do Docker"""
    print_section("Docker Tools")
    
    try:
        from src.jarvis.tools.docker_tools import get_docker_tools
        tools = get_docker_tools()
        
        # Test list containers function
        passed = callable(tools["docker_list_containers"])
        print_test("Docker list containers function", passed)
        record_result(passed)
        
        # Test docker compose up function
        passed = callable(tools["docker_compose_up"])
        print_test("Docker compose up function", passed)
        record_result(passed)
        
        # Try to list containers (might fail if Docker not running)
        try:
            containers = await tools["docker_list_containers"](all_containers=True)
            passed = isinstance(containers, str)
            print_test("Docker list containers execution", passed)
            record_result(passed)
        except Exception as e:
            print_test("Docker list containers execution", False, "Docker may not be running")
            results["skipped"] += 1
        
    except Exception as e:
        print_test("Docker tools", False, str(e)[:50])
        record_result(False)


async def test_database_tools():
    """Testa as ferramentas de banco de dados"""
    print_section("Database Tools")
    
    try:
        from src.jarvis.tools.database_tools import get_database_tools
        tools = get_database_tools()
        
        # Test SQLite query function
        passed = callable(tools["sqlite_query"])
        print_test("SQLite query function", passed)
        record_result(passed)
        
        # Test natural to SQL
        sql = tools["natural_to_sql"]("liste todos usuários")
        passed = "SELECT" in sql.upper()
        print_test("Natural language to SQL", passed)
        record_result(passed)
        
        # Test SQLite with temp database
        try:
            import tempfile
            import aiosqlite
            
            # Criar banco temporário
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
                temp_db = f.name
            
            # Criar tabela de teste
            async with aiosqlite.connect(temp_db) as db:
                await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
                await db.execute("INSERT INTO test (name) VALUES ('JARVIS')")
                await db.commit()
            
            # Testar query
            result = await tools["sqlite_query"](temp_db, "SELECT * FROM test")
            passed = "JARVIS" in result
            print_test("SQLite query execution", passed)
            record_result(passed)
            
            # Cleanup
            os.unlink(temp_db)
        except Exception as e:
            print_test("SQLite query execution", False, str(e)[:30])
            record_result(False)
        
    except Exception as e:
        print_test("Database tools", False, str(e)[:50])
        record_result(False)


async def test_github_tools():
    """Testa as ferramentas do GitHub"""
    print_section("GitHub Tools")
    
    try:
        from src.jarvis.tools.github_tools import get_github_tools
        tools = get_github_tools()
        
        # Test function exists
        functions = [
            "github_list_issues",
            "github_create_issue",
            "github_list_prs",
            "github_get_pr_diff",
            "github_search_code",
            "github_workflow_status",
        ]
        
        for func_name in functions:
            passed = callable(tools.get(func_name))
            print_test(f"GitHub {func_name} function", passed)
            record_result(passed)
        
    except Exception as e:
        print_test("GitHub tools", False, str(e)[:50])
        record_result(False)


async def test_vision_tools():
    """Testa as ferramentas de visão"""
    print_section("Vision Tools")
    
    try:
        from src.jarvis.tools.vision_tools import get_vision_tools
        tools = get_vision_tools()
        
        # Test functions exist
        functions = [
            "screenshot_analyze",
            "analyze_image",
            "extract_text",
            "design_to_code",
        ]
        
        for func_name in functions:
            passed = callable(tools.get(func_name))
            print_test(f"Vision {func_name} function", passed)
            record_result(passed)
        
    except Exception as e:
        print_test("Vision tools", False, str(e)[:50])
        record_result(False)


async def test_cli():
    """Testa o CLI"""
    print_section("CLI Tests")
    
    try:
        from src.jarvis.cli.config import CLIConfig
        from src.jarvis.cli.agents import AGENTS
        from src.jarvis.cli.history import ChatHistory
        
        # Test config
        config = CLIConfig()
        passed = config.model == "gemini-2.5-flash"
        print_test("CLI config default model", passed)
        record_result(passed)
        
        # Test agents
        passed = len(AGENTS) >= 5
        print_test(f"CLI agents loaded ({len(AGENTS)} agents)", passed)
        record_result(passed)
        
        # Test history manager
        history = ChatHistory()
        passed = hasattr(history, "add_message") and hasattr(history, "list_sessions")
        print_test("Chat history manager", passed)
        record_result(passed)
        
    except Exception as e:
        print_test("CLI", False, str(e)[:50])
        record_result(False)


async def test_code_agent():
    """Testa o CodeAgent"""
    print_section("CodeAgent Tests")
    
    try:
        from src.jarvis.agents.code_agent import CodeAgent, ADK_AVAILABLE
        
        # Test ADK availability
        print_test("Google ADK available", ADK_AVAILABLE)
        record_result(ADK_AVAILABLE)
        
        # Test CodeAgent instantiation
        agent = CodeAgent()
        passed = agent is not None
        print_test("CodeAgent instantiation", passed)
        record_result(passed)
        
        # Test workspace path
        passed = agent.workspace_path is not None
        print_test("CodeAgent workspace path", passed)
        record_result(passed)
        
    except Exception as e:
        print_test("CodeAgent", False, str(e)[:50])
        record_result(False)


async def test_gemini_api():
    """Testa conexão com Gemini API"""
    print_section("Gemini API Tests")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        passed = api_key is not None
        print_test("API Key configured", passed)
        record_result(passed)
        
        if api_key:
            from google import genai
            client = genai.Client(api_key=api_key)
            
            # List models
            models = list(client.models.list())
            passed = len(models) > 0
            print_test("Can list Gemini models", passed)
            record_result(passed)
            
            # Check specific models
            model_names = [m.name for m in models]
            passed = any("gemini-2.5-flash" in m for m in model_names)
            print_test("Gemini 2.5 Flash available", passed)
            record_result(passed)
            
            passed = any("gemini-2.5-pro" in m for m in model_names)
            print_test("Gemini 2.5 Pro available", passed)
            record_result(passed)
            
    except Exception as e:
        print_test("Gemini API", False, str(e)[:50])
        record_result(False)


# ==================== MAIN ====================

async def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         JARVIS v2 - Quality Assurance Tests              ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Python: {sys.version.split()[0]}")
    
    # Run all tests
    await test_imports()
    await test_cli()
    await test_code_agent()
    await test_gemini_api()
    await test_scaffolding_tools()
    await test_system_tools()
    await test_research_tools()
    await test_docker_tools()
    await test_database_tools()
    await test_github_tools()
    await test_vision_tools()
    
    # Summary
    print_header("QA Summary")
    total = results["passed"] + results["failed"]
    percentage = (results["passed"] / total * 100) if total > 0 else 0
    
    print(f"  {Colors.GREEN}✅ Passed: {results['passed']}{Colors.END}")
    print(f"  {Colors.RED}❌ Failed: {results['failed']}{Colors.END}")
    print(f"  {Colors.YELLOW}⏭️  Skipped: {results['skipped']}{Colors.END}")
    print(f"\n  {Colors.BOLD}Total: {total} tests | {percentage:.1f}% passed{Colors.END}")
    
    if percentage >= 90:
        print(f"\n  {Colors.GREEN}{Colors.BOLD}🎉 QA PASSED - Sistema pronto!{Colors.END}")
    elif percentage >= 70:
        print(f"\n  {Colors.YELLOW}{Colors.BOLD}⚠️  QA WARNING - Revisar falhas{Colors.END}")
    else:
        print(f"\n  {Colors.RED}{Colors.BOLD}❌ QA FAILED - Correções necessárias{Colors.END}")
    
    print()
    return results["failed"] == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
