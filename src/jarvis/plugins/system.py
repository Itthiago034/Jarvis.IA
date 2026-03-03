"""
JARVIS - Plugin de Sistema
==========================
Fornece informações sobre o sistema e controle básico do PC.
Bateria, memória, CPU, disco, etc.

Autor: Thiago
Versão: 1.0.0
"""

import asyncio
import platform
import subprocess
import logging
from datetime import datetime

from .base import JarvisPlugin, PluginContext, PluginResponse, PluginPriority

logger = logging.getLogger(__name__)

# Try importing psutil (may not be installed)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil não instalado. Recursos de sistema limitados.")


class SystemPlugin(JarvisPlugin):
    """
    Plugin de informações do sistema.
    
    Funcionalidades:
    - Status da bateria
    - Uso de CPU/RAM
    - Espaço em disco
    - Informações do sistema
    - Desligar/Reiniciar (com confirmação)
    """
    
    name = "Sistema"
    description = "Informações do sistema: bateria, CPU, RAM, disco"
    version = "1.0.0"
    author = "JARVIS Team"
    
    trigger_phrases = [
        # Bateria
        "bateria",
        "carga da bateria",
        "quanto de bateria",
        "nível de bateria",
        
        # CPU/RAM
        "uso de cpu",
        "processador",
        "memória",
        "ram",
        "uso de memória",
        "desempenho",
        "performance",
        
        # Disco
        "espaço em disco",
        "armazenamento",
        "espaço livre",
        "quanto de espaço",
        
        # Sistema
        "informações do sistema",
        "sobre o computador",
        "qual meu sistema",
        "qual windows",
        
        # Ações
        "desligar computador",
        "reiniciar computador",
        "suspender",
        "hibernar"
    ]
    
    priority = PluginPriority.NORMAL
    requires_internet = False
    
    async def initialize(self) -> bool:
        """Verifica dependências"""
        if not PSUTIL_AVAILABLE:
            logger.warning("SystemPlugin: psutil não disponível. Instale com: pip install psutil")
        return await super().initialize()
    
    def _get_battery_info(self) -> str:
        """Obtém informações da bateria"""
        if not PSUTIL_AVAILABLE:
            return "Não consigo verificar a bateria. Instale o psutil."
        
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return "Este computador não tem bateria ou não consegui detectá-la."
            
            percent = battery.percent
            plugged = battery.power_plugged
            
            status = "carregando" if plugged else "na bateria"
            
            # Tempo restante
            if not plugged and battery.secsleft > 0:
                hours = battery.secsleft // 3600
                minutes = (battery.secsleft % 3600) // 60
                time_str = f"Restam aproximadamente {hours} horas e {minutes} minutos."
            else:
                time_str = ""
            
            # Alerta de bateria baixa
            if percent < 20 and not plugged:
                alert = "Atenção: bateria baixa! Conecte o carregador."
            elif percent == 100 and plugged:
                alert = "Bateria totalmente carregada."
            else:
                alert = ""
            
            return f"A bateria está em {percent}%, {status}. {time_str} {alert}".strip()
            
        except Exception as e:
            logger.error(f"Erro ao obter bateria: {e}")
            return "Não consegui verificar a bateria."
    
    def _get_cpu_info(self) -> str:
        """Obtém informações de CPU"""
        if not PSUTIL_AVAILABLE:
            return "Não consigo verificar o CPU. Instale o psutil."
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Frequência
            freq = psutil.cpu_freq()
            freq_str = f"{freq.current:.0f}MHz" if freq else ""
            
            # Classificação do uso
            if cpu_percent < 30:
                status = "O processador está tranquilo"
            elif cpu_percent < 70:
                status = "O processador está com uso moderado"
            else:
                status = "O processador está trabalhando pesado"
            
            return f"{status}, com {cpu_percent}% de uso. Você tem {cpu_count} núcleos. {freq_str}".strip()
            
        except Exception as e:
            logger.error(f"Erro ao obter CPU: {e}")
            return "Não consegui verificar o processador."
    
    def _get_memory_info(self) -> str:
        """Obtém informações de memória RAM"""
        if not PSUTIL_AVAILABLE:
            return "Não consigo verificar a memória. Instale o psutil."
        
        try:
            mem = psutil.virtual_memory()
            
            total_gb = mem.total / (1024 ** 3)
            used_gb = mem.used / (1024 ** 3)
            available_gb = mem.available / (1024 ** 3)
            percent = mem.percent
            
            # Classificação
            if percent < 50:
                status = "Memória com bastante espaço livre"
            elif percent < 80:
                status = "Uso de memória moderado"
            else:
                status = "Memória quase no limite, considere fechar alguns programas"
            
            return (
                f"{status}. "
                f"Usando {used_gb:.1f}GB de {total_gb:.1f}GB total ({percent}%). "
                f"Disponível: {available_gb:.1f}GB."
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter memória: {e}")
            return "Não consegui verificar a memória."
    
    def _get_disk_info(self) -> str:
        """Obtém informações de disco"""
        if not PSUTIL_AVAILABLE:
            return "Não consigo verificar o disco. Instale o psutil."
        
        try:
            disk = psutil.disk_usage('/')
            
            total_gb = disk.total / (1024 ** 3)
            used_gb = disk.used / (1024 ** 3)
            free_gb = disk.free / (1024 ** 3)
            percent = disk.percent
            
            # Alerta de disco cheio
            if percent > 90:
                alert = "Atenção: disco quase cheio! Considere liberar espaço."
            elif percent > 75:
                alert = "O disco está ficando cheio."
            else:
                alert = ""
            
            return (
                f"Disco principal: {used_gb:.0f}GB usados de {total_gb:.0f}GB ({percent}% ocupado). "
                f"Livre: {free_gb:.0f}GB. {alert}"
            ).strip()
            
        except Exception as e:
            logger.error(f"Erro ao obter disco: {e}")
            return "Não consegui verificar o disco."
    
    def _get_system_info(self) -> str:
        """Obtém informações gerais do sistema"""
        try:
            system = platform.system()
            release = platform.release()
            version = platform.version()
            machine = platform.machine()
            processor = platform.processor()
            
            # Nome do computador
            node = platform.node()
            
            return (
                f"Este computador chama-se {node}. "
                f"Rodando {system} {release} ({machine}). "
                f"Processador: {processor[:30]}..."
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter info do sistema: {e}")
            return "Não consegui obter informações do sistema."
    
    def _classify_command(self, text: str) -> str:
        """Classifica o tipo de comando"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["bateria", "carga"]):
            return "battery"
        
        if any(word in text_lower for word in ["cpu", "processador", "desempenho", "performance"]):
            return "cpu"
        
        if any(word in text_lower for word in ["memória", "memoria", "ram"]):
            return "memory"
        
        if any(word in text_lower for word in ["disco", "armazenamento", "espaço"]):
            return "disk"
        
        if any(word in text_lower for word in ["sistema", "computador", "windows"]):
            return "system"
        
        if any(word in text_lower for word in ["desligar", "shutdown"]):
            return "shutdown"
        
        if any(word in text_lower for word in ["reiniciar", "restart", "reboot"]):
            return "restart"
        
        if any(word in text_lower for word in ["suspender", "hibernar", "sleep"]):
            return "sleep"
        
        return "overview"
    
    def _get_overview(self) -> str:
        """Visão geral do sistema"""
        parts = []
        
        # Bateria (se disponível)
        if PSUTIL_AVAILABLE:
            try:
                battery = psutil.sensors_battery()
                if battery:
                    parts.append(f"Bateria: {battery.percent}%")
            except:
                pass
            
            # CPU
            try:
                cpu = psutil.cpu_percent(interval=0.5)
                parts.append(f"CPU: {cpu}%")
            except:
                pass
            
            # RAM
            try:
                mem = psutil.virtual_memory()
                parts.append(f"RAM: {mem.percent}%")
            except:
                pass
        
        if parts:
            return "Status rápido: " + ", ".join(parts) + "."
        
        return "Não consegui obter o status do sistema."
    
    async def execute(self, context: PluginContext) -> PluginResponse:
        """Executa comando de sistema"""
        command = self._classify_command(context.user_message)
        
        logger.info(f"Comando de sistema: {command}")
        
        if command == "battery":
            message = self._get_battery_info()
        
        elif command == "cpu":
            message = self._get_cpu_info()
        
        elif command == "memory":
            message = self._get_memory_info()
        
        elif command == "disk":
            message = self._get_disk_info()
        
        elif command == "system":
            message = self._get_system_info()
        
        elif command == "shutdown":
            return PluginResponse(
                message="Por segurança, não vou desligar automaticamente. Use o menu Iniciar.",
                success=True,
                data={"blocked": True}
            )
        
        elif command == "restart":
            return PluginResponse(
                message="Por segurança, não vou reiniciar automaticamente. Salve seu trabalho e use o menu Iniciar.",
                success=True,
                data={"blocked": True}
            )
        
        elif command == "sleep":
            return PluginResponse(
                message="Para suspender, use o menu Iniciar ou feche a tampa do notebook.",
                success=True,
                data={"blocked": True}
            )
        
        else:  # overview
            message = self._get_overview()
        
        return PluginResponse(
            message=message,
            success=True
        )
