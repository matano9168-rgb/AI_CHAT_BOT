"""
Weather plugin for the AI Chatbot.
Provides current weather information for any location.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from .base import BasePlugin, PluginResponse


class WeatherPlugin(BasePlugin):
    """Plugin for getting weather information."""
    
    def __init__(self):
        super().__init__(
            name="weather",
            description="Get current weather information for any location",
            version="1.0.0"
        )
        self.required_api_keys = ["weather_api_key"]
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_capabilities(self) -> list[str]:
        return [
            "current_weather",
            "weather_forecast",
            "temperature_conversion",
            "weather_alerts"
        ]
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters."""
        required_params = ["location"]
        return all(param in kwargs for param in required_params)
    
    async def execute(self, **kwargs) -> PluginResponse:
        """Execute the weather plugin."""
        try:
            location = kwargs.get("location")
            units = kwargs.get("units", "metric")  # metric, imperial, kelvin
            
            # Get current weather
            weather_data = await self._get_current_weather(location, units)
            
            if not weather_data:
                return PluginResponse(
                    success=False,
                    error=f"Could not retrieve weather data for {location}"
                )
            
            # Format the response
            formatted_response = self._format_weather_response(weather_data, units)
            
            return PluginResponse(
                success=True,
                data=formatted_response,
                metadata={
                    "location": location,
                    "units": units,
                    "timestamp": weather_data.get("dt"),
                    "source": "OpenWeatherMap"
                }
            )
            
        except Exception as e:
            return PluginResponse(
                success=False,
                error=f"Weather plugin error: {str(e)}"
            )
    
    async def _get_current_weather(self, location: str, units: str) -> Optional[Dict[str, Any]]:
        """Get current weather data from OpenWeatherMap API."""
        try:
            api_key = self.api_keys.get("weather_api_key")
            if not api_key:
                return None
            
            # Determine unit parameter for API
            unit_param = "metric" if units == "metric" else "imperial" if units == "imperial" else ""
            
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": unit_param
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        print(f"Weather API error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def _format_weather_response(self, weather_data: Dict[str, Any], units: str) -> Dict[str, Any]:
        """Format weather data into a user-friendly response."""
        try:
            main = weather_data.get("main", {})
            weather = weather_data.get("weather", [{}])[0]
            wind = weather_data.get("wind", {})
            sys = weather_data.get("sys", {})
            
            # Temperature unit symbols
            temp_symbol = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
            speed_symbol = "m/s" if units == "metric" else "mph"
            
            formatted = {
                "location": weather_data.get("name", "Unknown"),
                "country": sys.get("country", "Unknown"),
                "weather_description": weather.get("description", "Unknown"),
                "weather_icon": weather.get("icon", ""),
                "temperature": {
                    "current": f"{main.get('temp', 'N/A')}{temp_symbol}",
                    "feels_like": f"{main.get('feels_like', 'N/A')}{temp_symbol}",
                    "min": f"{main.get('temp_min', 'N/A')}{temp_symbol}",
                    "max": f"{main.get('temp_max', 'N/A')}{temp_symbol}"
                },
                "humidity": f"{main.get('humidity', 'N/A')}%",
                "pressure": f"{main.get('pressure', 'N/A')} hPa",
                "wind": {
                    "speed": f"{wind.get('speed', 'N/A')} {speed_symbol}",
                    "direction": wind.get('deg', 'N/A')
                },
                "visibility": f"{weather_data.get('visibility', 'N/A')} m",
                "clouds": f"{weather_data.get('clouds', {}).get('all', 'N/A')}%",
                "sunrise": sys.get("sunrise"),
                "sunset": sys.get("sunset"),
                "timestamp": weather_data.get("dt")
            }
            
            return formatted
            
        except Exception as e:
            print(f"Error formatting weather response: {e}")
            return {"error": "Failed to format weather data"}
    
    def get_usage_examples(self) -> list[str]:
        return [
            "Get weather for London: weather(location='London')",
            "Get weather in Fahrenheit: weather(location='New York', units='imperial')",
            "Get weather for Tokyo: weather(location='Tokyo')"
        ]
    
    async def health_check(self) -> bool:
        """Check if the weather plugin is healthy."""
        try:
            # Check if we have the required API key
            if not self.api_keys.get("weather_api_key"):
                return False
            
            # Try a simple API call to verify connectivity
            test_data = await self._get_current_weather("London", "metric")
            return test_data is not None
            
        except Exception:
            return False
