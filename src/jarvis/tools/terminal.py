"""
JARVIS - Terminal Tools
=======================
Ferramentas para executar comandos no terminal.
Equivalente às funcionalidades run_in_terminal e get_terminal_output.

Segurança:
- Comandos são executados em subprocessos isolados
- Timeout padrão de 30 segundos
- Output limitado a 64KB para evitar overflow
"""

import asyncio
import subprocess
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Limite de output para evitar overflow
MAX_OUTPUT_SIZE = 64 * 1024  # 64KB


@dataclass
class CommandResult:
    """Resultado da execução de um comando"""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    timed_out: bool = False


async def run_command(
    command: str,
    cwd: Optional[str] = None,
    timeout: int = 30,
    shell: bool = True
) -> CommandResult:
    """
    Executa um comando no terminal.
    
    Args:
        command: Comando a executar
        cwd: Diretório de trabalho (opcional)
        timeout: Timeout em segundos (padrão: 30)
        shell: Se True, executa via shell (padrão: True)
    
    Returns:
        CommandResult com stdout, stderr e return code
    
    Exemplo:
        result = await run_command("python --version")
        print(result.stdout)  # Python 3.14.0
    """
    logger.info(f"Executando comando: {command[:100]}...")
    
    try:
        # Criar processo
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        # Aguardar com timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Comando excedeu timeout de {timeout}s",
                return_code=-1,
                timed_out=True
            )
        
        # Decodificar output
        stdout_str = stdout.decode('utf-8', errors='replace')[:MAX_OUTPUT_SIZE]
        stderr_str = stderr.decode('utf-8', errors='replace')[:MAX_OUTPUT_SIZE]
        
        return CommandResult(
            success=process.returncode == 0,
            stdout=stdout_str,
            stderr=stderr_str,
            return_code=process.returncode
        )
        
    except Exception as e:
        logger.error(f"Erro ao executar comando: {e}")
        return CommandResult(
            success=False,
            stdout="",
            stderr=str(e),
            return_code=-1
        )


async def get_command_output(command: str, cwd: Optional[str] = None) -> str:
    """
    Versão simplificada que retorna apenas o stdout.
    
    Args:
        command: Comando a executar
        cwd: Diretório de trabalho
    
    Returns:
        String com o stdout do comando
    """
    result = await run_command(command, cwd=cwd)
    if result.success:
        return result.stdout.strip()
    else:
        return f"Erro: {result.stderr or result.stdout}"


# Funções síncronas para uso como tools do ADK
def run_command_sync(
    command: str,
    working_directory: Optional[str] = None,
    timeout_seconds: int = 30
) -> Dict[str, Any]:
    """
    Executa um comando no terminal (versão síncrona para ADK).
    
    Args:
        command: O comando a ser executado no terminal
        working_directory: Diretório onde executar o comando
        timeout_seconds: Tempo máximo de execução em segundos
    
    Returns:
        Dicionário com 'success', 'output', 'error', 'return_code'
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=working_directory
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout[:MAX_OUTPUT_SIZE],
            "error": result.stderr[:MAX_OUTPUT_SIZE] if result.stderr else "",
            "return_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Comando excedeu timeout de {timeout_seconds} segundos",
            "return_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "return_code": -1
        }


# Lista de comandos perigosos que devem ser bloqueados
DANGEROUS_COMMANDS = [
    "rm -rf /",
    "del /f /s /q c:\\",
    "format",
    ":(){:|:&};:",  # fork bomb
    "mkfs",
    "dd if=/dev/zero",
]


def is_safe_command(command: str) -> bool:
    """Verifica se um comando é seguro para executar"""
    command_lower = command.lower()
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in command_lower:
            return False
    return True
