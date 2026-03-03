"""
JARVIS - Plugin de Clima
========================
Fornece informações meteorológicas usando OpenWeatherMap API.
Suporta previsão atual e dos próximos dias.

Autor: Thiago
Versão: 1.0.0
"""

import aiohttp
import logging
from datetime import datetime
from typing import Optional

from .base import JarvisPlugin, PluginContext, PluginResponse, PluginPriority

logger = logging.getLogger(__name__)


class WeatherPlugin(JarvisPlugin):
    """
    Plugin de previsão do tempo.
    
    Configuração necessária no plugins.yaml:
        WeatherPlugin:
          enabled: true
          config:
            api_key: "sua_api_key_openweathermap"
            default_city: "São Paulo"
            units: "metric"  # metric (Celsius) ou imperial (Fahrenheit)
    """
    
    name = "Clima"
    description = "Consulta previsão do tempo e condições climáticas"
    version = "1.0.0"
    author = "JARVIS Team"
    
    trigger_phrases = [
        "previsão do tempo",
        "como está o tempo",
        "vai chover",
        "temperatura",
        "clima",
        "weather",
        "está frio",
        "está calor",
        "previsão para amanhã",
        "tempo hoje",
        "condições climáticas"
    ]
    
    priority = PluginPriority.NORMAL
    requires_internet = True
    
    # Mapeamento de condições para português
    WEATHER_CONDITIONS = {
        "clear sky": "céu limpo",
        "few clouds": "poucas nuvens",
        "scattered clouds": "nuvens dispersas",
        "broken clouds": "nuvens fragmentadas",
        "overcast clouds": "nublado",
        "shower rain": "chuva forte",
        "rain": "chuva",
        "light rain": "chuva leve",
        "moderate rain": "chuva moderada",
        "heavy rain": "chuva intensa",
        "thunderstorm": "tempestade",
        "snow": "neve",
        "mist": "névoa",
        "fog": "neblina",
        "haze": "neblina seca",
        "drizzle": "garoa"
    }
    
    # Emojis para condições (usado em logs/debug)
    WEATHER_EMOJIS = {
        "clear": "☀️",
        "clouds": "☁️",
        "rain": "🌧️",
        "drizzle": "🌦️",
        "thunderstorm": "⛈️",
        "snow": "❄️",
        "mist": "🌫️",
        "fog": "🌫️"
    }
    
    def __init__(self):
        super().__init__()
        self._api_key: Optional[str] = None
        self._default_city: str = "São Paulo"
        self._units: str = "metric"
        self._base_url = "https://api.openweathermap.org/data/2.5"
    
    async def initialize(self) -> bool:
        """Inicializa o plugin e valida a API key"""
        self._api_key = self.get_config("api_key")
        self._default_city = self.get_config("default_city", "São Paulo")
        self._units = self.get_config("units", "metric")
        
        if not self._api_key:
            logger.warning("WeatherPlugin: API key não configurada. Usando modo demo.")
            # Permite funcionar em modo demo sem API key
        
        return await super().initialize()
    
    def _translate_condition(self, condition: str) -> str:
        """Traduz condição climática para português"""
        condition_lower = condition.lower()
        return self.WEATHER_CONDITIONS.get(condition_lower, condition)
    
    def _get_emoji(self, main_condition: str) -> str:
        """Retorna emoji para a condição"""
        main_lower = main_condition.lower()
        for key, emoji in self.WEATHER_EMOJIS.items():
            if key in main_lower:
                return emoji
        return "🌡️"
    
    def _format_temperature(self, temp: float) -> str:
        """Formata temperatura com unidade"""
        unit = "°C" if self._units == "metric" else "°F"
        return f"{temp:.0f}{unit}"
    
    def _extract_city(self, text: str) -> str:
        """Extrai nome da cidade do texto do usuário"""
        # Palavras-chave que indicam localização
        location_keywords = ["em ", "de ", "para ", "no ", "na ", "in "]
        
        text_lower = text.lower()
        
        for keyword in location_keywords:
            if keyword in text_lower:
                idx = text_lower.find(keyword) + len(keyword)
                # Pega o resto do texto após a keyword
                remaining = text[idx:].strip()
                # Remove pontuação final
                remaining = remaining.rstrip("?.!")
                if remaining:
                    return remaining.title()
        
        return self._default_city
    
    async def _fetch_weather(self, city: str) -> Optional[dict]:
        """Busca dados do clima na API"""
        if not self._api_key:
            # Modo demo - retorna dados simulados
            return self._get_demo_data(city)
        
        try:
            params = {
                "q": city,
                "appid": self._api_key,
                "units": self._units,
                "lang": "pt_br"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._base_url}/weather",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"Cidade não encontrada: {city}")
                        return None
                    else:
                        logger.error(f"Erro na API: {response.status}")
                        return None
                        
        except aiohttp.ClientError as e:
            logger.error(f"Erro de conexão: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar clima: {e}")
            return None
    
    def _get_demo_data(self, city: str) -> dict:
        """Retorna dados de demonstração quando não há API key"""
        return {
            "name": city,
            "main": {
                "temp": 25,
                "feels_like": 27,
                "humidity": 65,
                "temp_min": 20,
                "temp_max": 30
            },
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "wind": {"speed": 3.5},
            "sys": {"country": "BR"},
            "demo": True
        }
    
    def _format_response(self, data: dict) -> str:
        """Formata os dados do clima para fala natural"""
        city = data["name"]
        country = data.get("sys", {}).get("country", "")
        
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]
        
        weather = data["weather"][0]
        condition = self._translate_condition(weather["description"])
        main = weather["main"]
        
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        # Monta resposta natural
        response_parts = []
        
        # Localização e condição
        location = f"{city}, {country}" if country else city
        response_parts.append(f"Em {location}, o tempo está com {condition}.")
        
        # Temperatura
        temp_str = self._format_temperature(temp)
        response_parts.append(f"A temperatura atual é de {temp_str}")
        
        # Sensação térmica (se diferente)
        if abs(feels_like - temp) >= 2:
            feels_str = self._format_temperature(feels_like)
            response_parts.append(f"com sensação térmica de {feels_str}.")
        else:
            response_parts[-1] += "."
        
        # Mínima e máxima
        min_str = self._format_temperature(temp_min)
        max_str = self._format_temperature(temp_max)
        response_parts.append(f"A mínima é {min_str} e a máxima {max_str}.")
        
        # Umidade
        response_parts.append(f"Umidade do ar em {humidity}%.")
        
        # Vento (se significativo)
        if wind_speed > 5:
            wind_kmh = wind_speed * 3.6 if self._units == "metric" else wind_speed
            response_parts.append(f"Ventos de {wind_kmh:.0f} km/h.")
        
        # Aviso de demo
        if data.get("demo"):
            response_parts.append("Nota: dados de demonstração. Configure a API key para dados reais.")
        
        return " ".join(response_parts)
    
    def _get_weather_advice(self, data: dict) -> Optional[str]:
        """Gera conselho baseado nas condições"""
        temp = data["main"]["temp"]
        main = data["weather"][0]["main"].lower()
        humidity = data["main"]["humidity"]
        
        advice = []
        
        if "rain" in main or "drizzle" in main:
            advice.append("Leve um guarda-chuva!")
        elif "thunderstorm" in main:
            advice.append("Cuidado com a tempestade. Evite sair se possível.")
        
        if temp > 30:
            advice.append("Está bem quente. Mantenha-se hidratado!")
        elif temp < 15:
            advice.append("Vista-se com agasalho, está friozinho.")
        
        if humidity > 80:
            advice.append("Umidade alta, pode ser desconfortável.")
        elif humidity < 30:
            advice.append("Ar muito seco. Beba bastante água.")
        
        return " ".join(advice) if advice else None
    
    async def execute(self, context: PluginContext) -> PluginResponse:
        """Executa a consulta de clima"""
        user_message = context.user_message
        
        # Extrai cidade
        city = self._extract_city(user_message)
        logger.info(f"Consultando clima para: {city}")
        
        # Busca dados
        data = await self._fetch_weather(city)
        
        if not data:
            return PluginResponse.error(
                f"Não consegui encontrar informações do tempo para {city}. "
                "Verifique se o nome da cidade está correto."
            )
        
        # Formata resposta
        response_text = self._format_response(data)
        
        # Adiciona conselho se houver
        advice = self._get_weather_advice(data)
        if advice:
            response_text += f" {advice}"
        
        return PluginResponse(
            message=response_text,
            success=True,
            data={
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "condition": data["weather"][0]["main"]
            }
        )
