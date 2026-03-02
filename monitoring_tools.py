"""
Módulo de monitoramento avançado do sistema para o JARVIS.
Fornece métricas detalhadas de CPU, memória, disco, rede e processos.

Usa psutil para coleta de métricas do sistema.
"""

import asyncio
import logging
import psutil
import platform
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ============== CLASSES DE DADOS ==============

@dataclass
class SystemMetrics:
    """Métricas do sistema."""
    cpu_percent: float
    cpu_count: int
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    boot_time: str
    uptime: str


@dataclass
class ProcessInfo:
    """Informações de um processo."""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str


# ============== COLETA DE MÉTRICAS ==============

async def get_system_metrics() -> Dict[str, Any]:
    """
    Coleta métricas completas do sistema.
    
    Returns:
        Dict com todas as métricas
    """
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memória
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disco (drive principal)
        disk = psutil.disk_usage('/')
        
        # Boot time e uptime
        boot_timestamp = psutil.boot_time()
        boot_time = datetime.fromtimestamp(boot_timestamp)
        uptime = datetime.now() - boot_time
        
        # Temperatura (se disponível)
        temps = {}
        try:
            temps_data = psutil.sensors_temperatures()
            if temps_data:
                for name, entries in temps_data.items():
                    if entries:
                        temps[name] = entries[0].current
        except:
            pass  # Não disponível no Windows sem drivers específicos
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else None
            },
            "memory": {
                "percent": memory.percent,
                "used_gb": round(memory.used / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2)
            },
            "swap": {
                "percent": swap.percent,
                "used_gb": round(swap.used / (1024**3), 2),
                "total_gb": round(swap.total / (1024**3), 2)
            },
            "disk": {
                "percent": disk.percent,
                "used_gb": round(disk.used / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2)
            },
            "system": {
                "platform": platform.system(),
                "version": platform.version(),
                "machine": platform.machine(),
                "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
                "uptime_hours": round(uptime.total_seconds() / 3600, 1)
            },
            "temperatures": temps if temps else None
        }
        
    except Exception as e:
        logger.error(f"Erro ao coletar métricas: {e}")
        return {"success": False, "error": str(e)}


async def get_top_processes(
    sort_by: str = "memory",
    limit: int = 10
) -> Dict[str, Any]:
    """
    Lista os processos que mais consomem recursos.
    
    Args:
        sort_by: "memory", "cpu" ou "name"
        limit: Número máximo de processos
    
    Returns:
        Dict com lista de processos
    """
    try:
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status']):
            try:
                info = proc.info
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "cpu_percent": info['cpu_percent'] or 0,
                    "memory_percent": round(info['memory_percent'] or 0, 2),
                    "memory_mb": round(info['memory_info'].rss / (1024**2), 1) if info['memory_info'] else 0,
                    "status": info['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Ordenar
        if sort_by == "memory":
            processes.sort(key=lambda x: x["memory_percent"], reverse=True)
        elif sort_by == "cpu":
            processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
        elif sort_by == "name":
            processes.sort(key=lambda x: x["name"].lower())
        
        return {
            "success": True,
            "processes": processes[:limit],
            "total_count": len(processes),
            "sort_by": sort_by
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar processos: {e}")
        return {"success": False, "error": str(e)}


async def get_network_info() -> Dict[str, Any]:
    """
    Coleta informações de rede.
    
    Returns:
        Dict com estatísticas de rede
    """
    try:
        # Estatísticas gerais
        net_io = psutil.net_io_counters()
        
        # Interfaces
        interfaces = []
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for name, addr_list in addrs.items():
            interface_stats = stats.get(name)
            
            interface_info = {
                "name": name,
                "is_up": interface_stats.isup if interface_stats else False,
                "speed_mbps": interface_stats.speed if interface_stats else 0,
                "addresses": []
            }
            
            for addr in addr_list:
                if addr.family.name == 'AF_INET':  # IPv4
                    interface_info["addresses"].append({
                        "type": "IPv4",
                        "address": addr.address
                    })
                elif addr.family.name == 'AF_INET6':  # IPv6
                    interface_info["addresses"].append({
                        "type": "IPv6",
                        "address": addr.address
                    })
            
            if interface_info["addresses"]:  # Só incluir interfaces com IP
                interfaces.append(interface_info)
        
        # Conexões ativas
        connections = []
        try:
            for conn in psutil.net_connections(kind='inet')[:20]:  # Limitar a 20
                if conn.status == 'ESTABLISHED':
                    connections.append({
                        "local": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "",
                        "remote": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "",
                        "status": conn.status
                    })
        except psutil.AccessDenied:
            pass  # Requer privilégios elevados
        
        return {
            "success": True,
            "io_stats": {
                "bytes_sent_gb": round(net_io.bytes_sent / (1024**3), 2),
                "bytes_recv_gb": round(net_io.bytes_recv / (1024**3), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            },
            "interfaces": interfaces,
            "connections_sample": connections
        }
        
    except Exception as e:
        logger.error(f"Erro ao coletar info de rede: {e}")
        return {"success": False, "error": str(e)}


async def get_disk_info() -> Dict[str, Any]:
    """
    Coleta informações detalhadas de todos os discos.
    
    Returns:
        Dict com informações de cada partição
    """
    try:
        partitions = []
        
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent
                })
            except (PermissionError, OSError):
                continue
        
        return {
            "success": True,
            "partitions": partitions
        }
        
    except Exception as e:
        logger.error(f"Erro ao coletar info de disco: {e}")
        return {"success": False, "error": str(e)}


# ============== ALERTAS ==============

async def check_system_health() -> Dict[str, Any]:
    """
    Verifica a saúde do sistema e gera alertas.
    
    Returns:
        Dict com status e alertas
    """
    metrics = await get_system_metrics()
    
    if not metrics.get("success"):
        return metrics
    
    alerts = []
    status = "healthy"
    
    # Verificar CPU
    cpu_pct = metrics["cpu"]["percent"]
    if cpu_pct > 90:
        alerts.append({"level": "critical", "message": f"CPU muito alta: {cpu_pct}%"})
        status = "critical"
    elif cpu_pct > 70:
        alerts.append({"level": "warning", "message": f"CPU elevada: {cpu_pct}%"})
        if status != "critical":
            status = "warning"
    
    # Verificar memória
    mem_pct = metrics["memory"]["percent"]
    if mem_pct > 90:
        alerts.append({"level": "critical", "message": f"Memória muito alta: {mem_pct}%"})
        status = "critical"
    elif mem_pct > 80:
        alerts.append({"level": "warning", "message": f"Memória elevada: {mem_pct}%"})
        if status != "critical":
            status = "warning"
    
    # Verificar disco
    disk_pct = metrics["disk"]["percent"]
    if disk_pct > 95:
        alerts.append({"level": "critical", "message": f"Disco quase cheio: {disk_pct}%"})
        status = "critical"
    elif disk_pct > 85:
        alerts.append({"level": "warning", "message": f"Disco elevado: {disk_pct}%"})
        if status != "critical":
            status = "warning"
    
    return {
        "success": True,
        "status": status,
        "alerts": alerts,
        "summary": {
            "cpu": f"{cpu_pct}%",
            "memory": f"{mem_pct}%",
            "disk": f"{disk_pct}%"
        }
    }


async def find_resource_hogs() -> Dict[str, Any]:
    """
    Identifica processos consumindo muitos recursos.
    
    Returns:
        Dict com processos problemáticos
    """
    # Coletar duas amostras para CPU preciso
    psutil.cpu_percent(interval=0.5, percpu=False)
    
    hogs = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            cpu = info['cpu_percent'] or 0
            mem = info['memory_percent'] or 0
            
            if cpu > 20 or mem > 10:  # Thresholds
                hogs.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "cpu_percent": cpu,
                    "memory_percent": round(mem, 2),
                    "issue": []
                })
                
                if cpu > 50:
                    hogs[-1]["issue"].append("CPU muito alta")
                elif cpu > 20:
                    hogs[-1]["issue"].append("CPU elevada")
                
                if mem > 20:
                    hogs[-1]["issue"].append("Memória muito alta")
                elif mem > 10:
                    hogs[-1]["issue"].append("Memória elevada")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Ordenar por consumo total (CPU + memória)
    hogs.sort(key=lambda x: x["cpu_percent"] + x["memory_percent"], reverse=True)
    
    return {
        "success": True,
        "resource_hogs": hogs[:10]
    }


# ============== FORMATAÇÃO ==============

def format_system_metrics(metrics: Dict[str, Any]) -> str:
    """Formata métricas do sistema para exibição."""
    if not metrics.get("success"):
        return f"❌ Erro: {metrics.get('error', 'Desconhecido')}"
    
    cpu = metrics["cpu"]
    mem = metrics["memory"]
    disk = metrics["disk"]
    sys = metrics["system"]
    
    # Determinar ícones de status
    def status_icon(pct):
        if pct > 90:
            return "🔴"
        elif pct > 70:
            return "🟡"
        return "🟢"
    
    return f"""
📊 **Monitor do Sistema**
━━━━━━━━━━━━━━━━━━━━━━━

{status_icon(cpu['percent'])} **CPU:** {cpu['percent']}% ({cpu['count']} cores)
{status_icon(mem['percent'])} **Memória:** {mem['percent']}% ({mem['used_gb']}/{mem['total_gb']} GB)
{status_icon(disk['percent'])} **Disco:** {disk['percent']}% ({disk['free_gb']} GB livres)

💻 **Sistema:** {sys['platform']} ({sys['machine']})
⏱️ **Uptime:** {sys['uptime_hours']} horas
"""


def format_top_processes(result: Dict[str, Any]) -> str:
    """Formata lista de processos."""
    if not result.get("success"):
        return f"❌ Erro: {result.get('error', 'Desconhecido')}"
    
    output = [f"📋 Top Processos (por {result['sort_by']}):\n"]
    
    for i, proc in enumerate(result["processes"], 1):
        output.append(
            f"{i:2}. {proc['name'][:20]:<20} "
            f"CPU: {proc['cpu_percent']:5.1f}% "
            f"MEM: {proc['memory_mb']:6.0f}MB"
        )
    
    return "\n".join(output)


def format_health_check(result: Dict[str, Any]) -> str:
    """Formata verificação de saúde."""
    if not result.get("success"):
        return f"❌ Erro: {result.get('error', 'Desconhecido')}"
    
    status_icons = {
        "healthy": "✅",
        "warning": "⚠️",
        "critical": "🚨"
    }
    
    status = result["status"]
    icon = status_icons.get(status, "❓")
    
    output = [f"{icon} **Status do Sistema: {status.upper()}**\n"]
    
    summary = result["summary"]
    output.append(f"CPU: {summary['cpu']} | RAM: {summary['memory']} | Disco: {summary['disk']}")
    
    if result["alerts"]:
        output.append("\n**Alertas:**")
        for alert in result["alerts"]:
            level_icon = "🔴" if alert["level"] == "critical" else "🟡"
            output.append(f"  {level_icon} {alert['message']}")
    
    return "\n".join(output)


# ============== TESTE ==============

if __name__ == "__main__":
    async def test():
        print("=== MÉTRICAS DO SISTEMA ===\n")
        metrics = await get_system_metrics()
        print(format_system_metrics(metrics))
        
        print("\n=== TOP PROCESSOS ===\n")
        procs = await get_top_processes(sort_by="memory", limit=5)
        print(format_top_processes(procs))
        
        print("\n=== VERIFICAÇÃO DE SAÚDE ===\n")
        health = await check_system_health()
        print(format_health_check(health))
        
        print("\n=== RESOURCE HOGS ===\n")
        hogs = await find_resource_hogs()
        if hogs["resource_hogs"]:
            for h in hogs["resource_hogs"][:5]:
                print(f"  {h['name']}: CPU {h['cpu_percent']}%, MEM {h['memory_percent']}%")
        else:
            print("  Nenhum processo consumindo recursos excessivos.")
    
    asyncio.run(test())
