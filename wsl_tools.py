"""
Módulo de integração WSL para o JARVIS.
Permite executar comandos Linux através do Windows Subsystem for Linux.
"""

import subprocess
import asyncio
import logging
import shlex
from typing import Optional

logger = logging.getLogger(__name__)

# Lista de comandos potencialmente perigosos que requerem confirmação
DANGEROUS_COMMANDS = [
    "rm -rf", "rm -r /", "dd if=", "mkfs", "shutdown", "reboot",
    ":(){:|:&};:", "chmod -R 777 /", "mv / ", "> /dev/sda"
]

# Comandos permitidos sem restrições
SAFE_COMMANDS = [
    "ls", "pwd", "cat", "head", "tail", "grep", "find", "echo",
    "date", "whoami", "uname", "df", "du", "ps", "top", "htop",
    "curl", "wget", "ping", "docker ps", "docker images",
    "git status", "git log", "git branch"
]


def is_dangerous_command(command: str) -> bool:
    """Verifica se o comando contém operações potencialmente perigosas."""
    command_lower = command.lower()
    return any(danger in command_lower for danger in DANGEROUS_COMMANDS)


def sanitize_command(command: str) -> str:
    """Sanitiza o comando removendo caracteres potencialmente perigosos."""
    # Remove tentativas de escape e injeção
    command = command.replace("$(", "").replace("`", "")
    return command.strip()


async def execute_wsl_command(
    command: str,
    timeout: int = 30,
    working_dir: Optional[str] = None,
    allow_dangerous: bool = False
) -> dict:
    """
    Executa um comando no WSL de forma assíncrona.
    
    Args:
        command: Comando bash a ser executado
        timeout: Tempo máximo de execução em segundos
        working_dir: Diretório de trabalho (caminho Linux)
        allow_dangerous: Se True, permite comandos perigosos
    
    Returns:
        Dict com 'success', 'output', 'error', 'return_code'
    """
    
    # Verificação de segurança
    if is_dangerous_command(command) and not allow_dangerous:
        logger.warning(f"Comando perigoso bloqueado: {command}")
        return {
            "success": False,
            "output": "",
            "error": "Comando bloqueado por segurança. Requer confirmação explícita.",
            "return_code": -1,
            "blocked": True
        }
    
    # Sanitiza o comando
    command = sanitize_command(command)
    
    # Prepara o comando completo
    if working_dir:
        full_command = f"cd {shlex.quote(working_dir)} && {command}"
    else:
        full_command = command
    
    try:
        logger.info(f"Executando comando WSL: {command}")
        
        # Executa de forma assíncrona
        process = await asyncio.create_subprocess_exec(
            "wsl", "-e", "bash", "-c", full_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            return {
                "success": False,
                "output": "",
                "error": f"Comando excedeu o tempo limite de {timeout} segundos",
                "return_code": -1,
                "timeout": True
            }
        
        output = stdout.decode("utf-8", errors="replace").strip()
        error = stderr.decode("utf-8", errors="replace").strip()
        
        # Limita o tamanho da saída para não sobrecarregar
        max_output = 2000
        if len(output) > max_output:
            output = output[:max_output] + f"\n... (saída truncada, {len(output)} caracteres total)"
        
        result = {
            "success": process.returncode == 0,
            "output": output,
            "error": error,
            "return_code": process.returncode
        }
        
        logger.info(f"Comando concluído com código {process.returncode}")
        return result
        
    except FileNotFoundError:
        logger.error("WSL não encontrado no sistema")
        return {
            "success": False,
            "output": "",
            "error": "WSL não está instalado ou não foi encontrado no PATH",
            "return_code": -1
        }
    except Exception as e:
        logger.error(f"Erro ao executar comando WSL: {e}")
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "return_code": -1
        }


async def check_wsl_available() -> bool:
    """Verifica se o WSL está disponível no sistema."""
    try:
        process = await asyncio.create_subprocess_exec(
            "wsl", "--status",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        return True
    except:
        return False


async def get_wsl_distros() -> list:
    """Lista as distribuições WSL instaladas."""
    result = await execute_wsl_command("cat /etc/os-release | grep PRETTY_NAME")
    if result["success"]:
        return [result["output"]]
    return []


# Funções de conveniência para comandos comuns
async def wsl_list_files(path: str = ".") -> dict:
    """Lista arquivos em um diretório."""
    return await execute_wsl_command(f"ls -la {shlex.quote(path)}")


async def wsl_read_file(file_path: str, lines: int = 50) -> dict:
    """Lê as primeiras N linhas de um arquivo."""
    return await execute_wsl_command(f"head -n {lines} {shlex.quote(file_path)}")


async def wsl_docker_status() -> dict:
    """Verifica o status dos containers Docker."""
    return await execute_wsl_command("docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")


async def wsl_system_info() -> dict:
    """Obtém informações do sistema Linux."""
    cmd = "echo '=== Sistema ===' && uname -a && echo '\n=== Memória ===' && free -h && echo '\n=== Disco ===' && df -h /"
    return await execute_wsl_command(cmd)


async def wsl_git_status(repo_path: str = ".") -> dict:
    """Obtém o status do repositório Git."""
    return await execute_wsl_command("git status --short", working_dir=repo_path)


# Exemplo de uso
if __name__ == "__main__":
    async def test():
        print("Testando integração WSL...")
        
        # Verifica disponibilidade
        available = await check_wsl_available()
        print(f"WSL disponível: {available}")
        
        if available:
            # Testa um comando simples
            result = await execute_wsl_command("echo 'Olá do WSL!' && uname -a")
            print(f"Resultado: {result}")
            
            # Testa informações do sistema
            info = await wsl_system_info()
            print(f"Sistema: {info['output']}")
    
    asyncio.run(test())
