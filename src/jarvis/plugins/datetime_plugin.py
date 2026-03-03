"""
JARVIS - Plugin de Data e Hora
==============================
Fornece informações de data, hora, cronômetro e timer.

Autor: Thiago
Versão: 1.0.0
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
import locale

from .base import JarvisPlugin, PluginContext, PluginResponse, PluginPriority

logger = logging.getLogger(__name__)

# Tenta configurar locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except:
        pass  # Usa default


class DateTimePlugin(JarvisPlugin):
    """
    Plugin de data e hora.
    
    Funcionalidades:
    - Hora atual
    - Data atual
    - Dia da semana
    - Contagem regressiva
    """
    
    name = "Data e Hora"
    description = "Informa data, hora, dia da semana"
    version = "1.0.0"
    author = "JARVIS Team"
    
    trigger_phrases = [
        # Hora
        "que horas são",
        "que hora é",
        "hora atual",
        "me diz a hora",
        "qual a hora",
        "horas",
        
        # Data
        "que dia é hoje",
        "qual a data",
        "data de hoje",
        "que data",
        "qual dia",
        
        # Dia da semana
        "que dia da semana",
        "qual dia da semana",
        "hoje é que dia",
        
        # Combinados
        "data e hora",
        "hora e data"
    ]
    
    priority = PluginPriority.HIGH  # Alta prioridade pois é comum
    requires_internet = False
    
    # Dias da semana em português
    DIAS_SEMANA = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo"
    ]
    
    # Meses em português
    MESES = [
        "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]
    
    def _get_greeting(self, hour: int) -> str:
        """Retorna saudação baseada na hora"""
        if 5 <= hour < 12:
            return "Bom dia"
        elif 12 <= hour < 18:
            return "Boa tarde"
        else:
            return "Boa noite"
    
    def _format_time(self, dt: datetime) -> str:
        """Formata hora para fala natural"""
        hour = dt.hour
        minute = dt.minute
        
        if minute == 0:
            return f"{hour} horas em ponto"
        elif minute == 30:
            return f"{hour} e meia"
        elif minute == 15:
            return f"{hour} e quinze"
        elif minute == 45:
            return f"{hour} e quarenta e cinco"
        else:
            return f"{hour} horas e {minute} minutos"
    
    def _format_date(self, dt: datetime) -> str:
        """Formata data para fala natural"""
        day = dt.day
        month = self.MESES[dt.month]
        year = dt.year
        weekday = self.DIAS_SEMANA[dt.weekday()]
        
        return f"{weekday}, {day} de {month} de {year}"
    
    def _classify_command(self, text: str) -> str:
        """Classifica o tipo de comando"""
        text_lower = text.lower()
        
        # Verifica se quer hora
        wants_time = any(word in text_lower for word in ["hora", "horas"])
        
        # Verifica se quer data
        wants_date = any(word in text_lower for word in ["data", "dia"])
        
        # Verifica se quer dia da semana especificamente
        wants_weekday = "semana" in text_lower
        
        if wants_time and wants_date:
            return "both"
        elif wants_weekday:
            return "weekday"
        elif wants_time:
            return "time"
        elif wants_date:
            return "date"
        else:
            return "both"  # Default: mostra tudo
    
    async def execute(self, context: PluginContext) -> PluginResponse:
        """Executa consulta de data/hora"""
        now = datetime.now()
        command = self._classify_command(context.user_message)
        
        greeting = self._get_greeting(now.hour)
        
        if command == "time":
            time_str = self._format_time(now)
            message = f"São {time_str}."
        
        elif command == "date":
            date_str = self._format_date(now)
            message = f"Hoje é {date_str}."
        
        elif command == "weekday":
            weekday = self.DIAS_SEMANA[now.weekday()]
            message = f"Hoje é {weekday}."
        
        else:  # both
            time_str = self._format_time(now)
            date_str = self._format_date(now)
            message = f"{greeting}! Agora são {time_str}. Hoje é {date_str}."
        
        return PluginResponse(
            message=message,
            success=True,
            data={
                "datetime": now.isoformat(),
                "hour": now.hour,
                "minute": now.minute,
                "weekday": now.weekday()
            }
        )
