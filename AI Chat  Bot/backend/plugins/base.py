"""
Base plugin class for the AI Chatbot plugin system.
Defines the interface that all plugins must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class PluginResponse(BaseModel):
    """Standard response format for all plugins."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BasePlugin(ABC):
    """Abstract base class for all chatbot plugins."""
    
    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        self.name = name
        self.description = description
        self.version = version
        self.enabled = True
        self.required_api_keys: List[str] = []
        self.api_keys: Dict[str, str] = {}
    
    @abstractmethod
    async def execute(self, **kwargs) -> PluginResponse:
        """Execute the plugin's main functionality."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities this plugin provides."""
        pass
    
    def is_available(self) -> bool:
        """Check if the plugin is available (has required API keys, etc.)."""
        if not self.enabled:
            return False
        
        for key in self.required_api_keys:
            if key not in self.api_keys or not self.api_keys[key]:
                return False
        
        return True
    
    def set_api_key(self, key_name: str, value: str):
        """Set an API key for the plugin."""
        if key_name in self.required_api_keys:
            self.api_keys[key_name] = value
    
    def get_help_text(self) -> str:
        """Return help text explaining how to use this plugin."""
        return f"Plugin: {self.name} v{self.version}\n{self.description}"
    
    def get_usage_examples(self) -> List[str]:
        """Return example usage patterns for this plugin."""
        return []
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters before execution."""
        return True
    
    async def health_check(self) -> bool:
        """Check if the plugin is healthy and working."""
        try:
            # Basic health check - plugins can override this
            return self.is_available()
        except Exception:
            return False


class PluginManager:
    """Manages all available plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
    
    def register_plugin(self, plugin: BasePlugin):
        """Register a new plugin."""
        self.plugins[plugin.name] = plugin
        print(f"✅ Registered plugin: {plugin.name}")
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin by name."""
        return self.plugins.get(name)
    
    def get_available_plugins(self) -> List[BasePlugin]:
        """Get all available plugins."""
        return [plugin for plugin in self.plugins.values() if plugin.is_available()]
    
    def get_plugin_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all available plugins."""
        capabilities = {}
        for plugin in self.plugins.values():
            if plugin.is_available():
                capabilities[plugin.name] = plugin.get_capabilities()
        return capabilities
    
    async def execute_plugin(self, plugin_name: str, **kwargs) -> PluginResponse:
        """Execute a specific plugin."""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return PluginResponse(
                success=False,
                error=f"Plugin '{plugin_name}' not found"
            )
        
        if not plugin.is_available():
            return PluginResponse(
                success=False,
                error=f"Plugin '{plugin_name}' is not available"
            )
        
        if not plugin.validate_input(**kwargs):
            return PluginResponse(
                success=False,
                error=f"Invalid input for plugin '{plugin_name}'"
            )
        
        try:
            return await plugin.execute(**kwargs)
        except Exception as e:
            return PluginResponse(
                success=False,
                error=f"Error executing plugin '{plugin_name}': {str(e)}"
            )
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all plugins."""
        health_status = {}
        for plugin_name, plugin in self.plugins.items():
            health_status[plugin_name] = await plugin.health_check()
        return health_status


# Global plugin manager instance
plugin_manager = PluginManager()
