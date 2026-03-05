"""
JARVIS - Docker Tools
=====================
Ferramentas para gerenciamento de Docker containers.
"""

import json
import asyncio
import subprocess
from typing import Optional, List, Dict, Any
from pathlib import Path


class DockerTools:
    """Ferramentas para Docker"""
    
    def __init__(self):
        self._docker_available = self._check_docker()
    
    def _check_docker(self) -> bool:
        """Verifica se Docker está disponível"""
        try:
            result = subprocess.run(
                ["docker", "version", "--format", "json"],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    async def _run_docker(self, *args, timeout: int = 30) -> Dict[str, Any]:
        """Executa comando Docker"""
        try:
            result = await asyncio.to_thread(
                lambda: subprocess.run(
                    ["docker", *args],
                    capture_output=True, text=True, timeout=timeout
                )
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_containers(self, all: bool = False) -> List[Dict]:
        """Lista containers"""
        args = ["ps", "--format", "json"]
        if all:
            args.insert(1, "-a")
        
        result = await self._run_docker(*args)
        if not result["success"]:
            return []
        
        containers = []
        for line in result["stdout"].strip().split("\n"):
            if line:
                try:
                    containers.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return containers
    
    async def list_images(self) -> List[Dict]:
        """Lista imagens"""
        result = await self._run_docker("images", "--format", "json")
        if not result["success"]:
            return []
        
        images = []
        for line in result["stdout"].strip().split("\n"):
            if line:
                try:
                    images.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return images
    
    async def start_container(self, container_id: str) -> Dict:
        """Inicia container"""
        return await self._run_docker("start", container_id)
    
    async def stop_container(self, container_id: str) -> Dict:
        """Para container"""
        return await self._run_docker("stop", container_id)
    
    async def restart_container(self, container_id: str) -> Dict:
        """Reinicia container"""
        return await self._run_docker("restart", container_id)
    
    async def remove_container(self, container_id: str, force: bool = False) -> Dict:
        """Remove container"""
        args = ["rm"]
        if force:
            args.append("-f")
        args.append(container_id)
        return await self._run_docker(*args)
    
    async def get_logs(self, container_id: str, tail: int = 100) -> str:
        """Obtém logs de um container"""
        result = await self._run_docker("logs", "--tail", str(tail), container_id)
        if result["success"]:
            return result["stdout"] or result["stderr"]
        return result.get("error", "Erro ao obter logs")
    
    async def exec_command(self, container_id: str, command: str) -> Dict:
        """Executa comando em container"""
        return await self._run_docker("exec", container_id, "sh", "-c", command)
    
    async def inspect_container(self, container_id: str) -> Dict:
        """Inspeciona container"""
        result = await self._run_docker("inspect", container_id)
        if result["success"]:
            try:
                return json.loads(result["stdout"])[0]
            except (json.JSONDecodeError, IndexError):
                pass
        return {}
    
    async def get_stats(self, container_id: Optional[str] = None) -> List[Dict]:
        """Obtém estatísticas de containers"""
        args = ["stats", "--no-stream", "--format", "json"]
        if container_id:
            args.append(container_id)
        
        result = await self._run_docker(*args, timeout=15)
        if not result["success"]:
            return []
        
        stats = []
        for line in result["stdout"].strip().split("\n"):
            if line:
                try:
                    stats.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return stats
    
    async def pull_image(self, image: str) -> Dict:
        """Baixa uma imagem"""
        return await self._run_docker("pull", image, timeout=300)
    
    async def build_image(self, path: str, tag: str) -> Dict:
        """Constrói imagem a partir de Dockerfile"""
        return await self._run_docker("build", "-t", tag, path, timeout=600)
    
    async def run_container(self, image: str, name: Optional[str] = None,
                           ports: Optional[Dict[str, str]] = None,
                           volumes: Optional[Dict[str, str]] = None,
                           env: Optional[Dict[str, str]] = None,
                           detach: bool = True) -> Dict:
        """Executa um novo container"""
        args = ["run"]
        
        if detach:
            args.append("-d")
        
        if name:
            args.extend(["--name", name])
        
        if ports:
            for host_port, container_port in ports.items():
                args.extend(["-p", f"{host_port}:{container_port}"])
        
        if volumes:
            for host_path, container_path in volumes.items():
                args.extend(["-v", f"{host_path}:{container_path}"])
        
        if env:
            for key, value in env.items():
                args.extend(["-e", f"{key}={value}"])
        
        args.append(image)
        
        return await self._run_docker(*args, timeout=120)
    
    async def docker_compose_up(self, path: str = ".") -> Dict:
        """Executa docker-compose up"""
        try:
            result = await asyncio.to_thread(
                lambda: subprocess.run(
                    ["docker", "compose", "up", "-d"],
                    cwd=path, capture_output=True, text=True, timeout=300
                )
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def docker_compose_down(self, path: str = ".") -> Dict:
        """Executa docker-compose down"""
        try:
            result = await asyncio.to_thread(
                lambda: subprocess.run(
                    ["docker", "compose", "down"],
                    cwd=path, capture_output=True, text=True, timeout=120
                )
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def prune_system(self) -> Dict:
        """Limpa recursos não utilizados"""
        return await self._run_docker("system", "prune", "-f", timeout=120)


# ==================== FUNÇÕES DE FERRAMENTA PARA O AGENTE ====================

def get_docker_tools():
    """Retorna as ferramentas Docker para o CodeAgent"""
    docker = DockerTools()
    
    async def docker_list_containers(show_all: bool = False) -> str:
        """
        Lista containers Docker.
        
        Args:
            show_all: Se True, mostra containers parados também
        
        Returns:
            Lista de containers
        """
        if not docker._docker_available:
            return "❌ Docker não está disponível. Verifique se está instalado e rodando."
        
        containers = await docker.list_containers(all=show_all)
        if not containers:
            return "Nenhum container encontrado"
        
        result = ["🐳 Containers Docker:\n"]
        for c in containers:
            status = "🟢" if c.get("State") == "running" else "🔴"
            result.append(
                f"  {status} {c.get('Names', 'N/A')}\n"
                f"     ID: {c.get('ID', 'N/A')[:12]}\n"
                f"     Imagem: {c.get('Image', 'N/A')}\n"
                f"     Status: {c.get('Status', 'N/A')}\n"
                f"     Portas: {c.get('Ports', 'N/A')}\n"
            )
        return "\n".join(result)
    
    async def docker_list_images() -> str:
        """
        Lista imagens Docker.
        
        Returns:
            Lista de imagens
        """
        if not docker._docker_available:
            return "❌ Docker não está disponível"
        
        images = await docker.list_images()
        if not images:
            return "Nenhuma imagem encontrada"
        
        result = ["📦 Imagens Docker:\n"]
        for img in images:
            result.append(
                f"  • {img.get('Repository', 'N/A')}:{img.get('Tag', 'latest')}\n"
                f"    ID: {img.get('ID', 'N/A')[:12]} | Tamanho: {img.get('Size', 'N/A')}\n"
            )
        return "\n".join(result)
    
    async def docker_start(container: str) -> str:
        """
        Inicia um container Docker.
        
        Args:
            container: Nome ou ID do container
        
        Returns:
            Confirmação
        """
        result = await docker.start_container(container)
        if result["success"]:
            return f"✅ Container '{container}' iniciado"
        return f"❌ Erro: {result.get('stderr', result.get('error', 'Erro desconhecido'))}"
    
    async def docker_stop(container: str) -> str:
        """
        Para um container Docker.
        
        Args:
            container: Nome ou ID do container
        
        Returns:
            Confirmação
        """
        result = await docker.stop_container(container)
        if result["success"]:
            return f"✅ Container '{container}' parado"
        return f"❌ Erro: {result.get('stderr', result.get('error', 'Erro desconhecido'))}"
    
    async def docker_restart(container: str) -> str:
        """
        Reinicia um container Docker.
        
        Args:
            container: Nome ou ID do container
        
        Returns:
            Confirmação
        """
        result = await docker.restart_container(container)
        if result["success"]:
            return f"✅ Container '{container}' reiniciado"
        return f"❌ Erro: {result.get('stderr', result.get('error', 'Erro desconhecido'))}"
    
    async def docker_logs(container: str, lines: int = 50) -> str:
        """
        Obtém logs de um container.
        
        Args:
            container: Nome ou ID do container
            lines: Número de linhas (padrão: 50)
        
        Returns:
            Logs do container
        """
        logs = await docker.get_logs(container, tail=lines)
        return f"📋 Logs de '{container}':\n\n{logs}"
    
    async def docker_stats() -> str:
        """
        Mostra estatísticas de recursos dos containers.
        
        Returns:
            Estatísticas de CPU/memória
        """
        stats = await docker.get_stats()
        if not stats:
            return "Nenhum container rodando ou Docker indisponível"
        
        result = ["📊 Estatísticas Docker:\n"]
        for s in stats:
            result.append(
                f"  {s.get('Name', 'N/A')}\n"
                f"    CPU: {s.get('CPUPerc', 'N/A')} | RAM: {s.get('MemUsage', 'N/A')}\n"
                f"    Net I/O: {s.get('NetIO', 'N/A')} | Block I/O: {s.get('BlockIO', 'N/A')}\n"
            )
        return "\n".join(result)
    
    async def docker_run(image: str, name: str = "", ports: str = "", 
                        volumes: str = "", env_vars: str = "") -> str:
        """
        Executa um novo container.
        
        Args:
            image: Nome da imagem (ex: "nginx:latest", "postgres:15")
            name: Nome do container (opcional)
            ports: Mapeamento de portas (ex: "8080:80,5432:5432")
            volumes: Volumes (ex: "./data:/var/lib/data")
            env_vars: Variáveis de ambiente (ex: "PASSWORD=123,USER=admin")
        
        Returns:
            ID do container criado
        """
        # Parsear portas
        port_map = {}
        if ports:
            for p in ports.split(","):
                if ":" in p:
                    host, container = p.strip().split(":")
                    port_map[host] = container
        
        # Parsear volumes
        vol_map = {}
        if volumes:
            for v in volumes.split(","):
                if ":" in v:
                    parts = v.strip().split(":")
                    vol_map[parts[0]] = parts[1]
        
        # Parsear env
        env_map = {}
        if env_vars:
            for e in env_vars.split(","):
                if "=" in e:
                    key, value = e.strip().split("=", 1)
                    env_map[key] = value
        
        result = await docker.run_container(
            image, name or None, port_map or None, vol_map or None, env_map or None
        )
        
        if result["success"]:
            container_id = result["stdout"].strip()[:12]
            return f"✅ Container criado: {container_id}"
        return f"❌ Erro: {result.get('stderr', result.get('error', 'Erro desconhecido'))}"
    
    async def docker_compose_up(path: str = ".") -> str:
        """
        Executa docker-compose up no diretório especificado.
        
        Args:
            path: Caminho do diretório com docker-compose.yml
        
        Returns:
            Status da execução
        """
        result = await docker.docker_compose_up(path)
        if result["success"]:
            return f"✅ docker-compose up executado em {path}"
        return f"❌ Erro: {result.get('stderr', result.get('error', 'Erro'))}"
    
    async def docker_compose_down(path: str = ".") -> str:
        """
        Executa docker-compose down no diretório especificado.
        
        Args:
            path: Caminho do diretório com docker-compose.yml
        
        Returns:
            Status
        """
        result = await docker.docker_compose_down(path)
        if result["success"]:
            return f"✅ docker-compose down executado em {path}"
        return f"❌ Erro: {result.get('stderr', result.get('error', 'Erro'))}"
    
    async def docker_pull(image: str) -> str:
        """
        Baixa uma imagem Docker.
        
        Args:
            image: Nome da imagem (ex: "python:3.11", "node:20")
        
        Returns:
            Status do download
        """
        result = await docker.pull_image(image)
        if result["success"]:
            return f"✅ Imagem '{image}' baixada com sucesso"
        return f"❌ Erro: {result.get('stderr', result.get('error', 'Erro'))}"
    
    async def docker_cleanup() -> str:
        """
        Limpa recursos Docker não utilizados (containers parados, imagens órfãs).
        
        Returns:
            Espaço liberado
        """
        result = await docker.prune_system()
        if result["success"]:
            return f"✅ Limpeza concluída\n{result.get('stdout', '')}"
        return f"❌ Erro: {result.get('stderr', result.get('error', 'Erro'))}"
    
    return {
        "docker_list_containers": docker_list_containers,
        "docker_list_images": docker_list_images,
        "docker_start": docker_start,
        "docker_stop": docker_stop,
        "docker_restart": docker_restart,
        "docker_logs": docker_logs,
        "docker_stats": docker_stats,
        "docker_run": docker_run,
        "docker_compose_up": docker_compose_up,
        "docker_compose_down": docker_compose_down,
        "docker_pull": docker_pull,
        "docker_cleanup": docker_cleanup,
    }
