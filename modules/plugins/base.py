"""
Plugin/Integration Architecture — Career OS extensible plugin system.
Plugins are self-contained modules dropped into modules/plugins/ or modules/integrations/.
Each plugin implements a known interface and is auto-discovered at startup.
"""
import importlib, importlib.util, os, sys, logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger("plugins")


class Plugin(ABC):
    """Base class for all Career OS plugins."""

    name: str = ""           # Unique plugin identifier
    version: str = "0.1"    # Semantic version
    description: str = ""    # One-line description

    def on_load(self) -> bool:
        """Called when plugin is loaded. Return False to disable plugin."""
        return True

    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        pass

    def on_configure(self, config: Dict[str, Any]) -> None:
        """Called with user config when plugin is initialized."""
        pass


class IntegrationPlugin(Plugin):
    """Plugin that connects to an external service."""

    def health_check(self) -> Dict[str, Any]:
        """Return {'status': 'ok'/'degraded'/'error', 'details': '...'}."""
        return {"status": "ok", "details": "Plugin loaded"}


class ProviderPlugin(Plugin):
    """Plugin that provides job discovery capabilities."""

    @abstractmethod
    def discover(self, **kwargs) -> List[Dict]:
        """Discover jobs. Return list of job dicts with title/company/url/description."""
        return []


class IntelligencePlugin(Plugin):
    """Plugin that adds analytical or intelligence capabilities."""

    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run analysis. Return result dict."""
        return {}


class DocumentPlugin(Plugin):
    """Plugin that generates or transforms career documents."""

    @abstractmethod
    def generate(self, job_id: int, **kwargs) -> str:
        """Generate document. Return path to output file."""
        return ""


class PluginRegistry:
    """Discovers, loads, and manages Career OS plugins."""

    def __init__(self, plugin_dir: str = None):
        root = Path(__file__).resolve().parents[2]
        self.plugin_dir = Path(plugin_dir) if plugin_dir else root / "modules" / "plugins"
        self.integrations_dir = root / "modules" / "integrations"
        self._loaded: Dict[str, Plugin] = {}
        self._failed: Dict[str, str] = {}  # name -> error

    def discover(self) -> List[Dict[str, str]]:
        """Scan plugin directories and return list of available plugins (not yet loaded)."""
        available = []
        for base_dir in [self.plugin_dir, self.integrations_dir]:
            if not base_dir.exists():
                continue
            for py_file in base_dir.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                name = py_file.stem
                if name not in self._loaded:
                    available.append({
                        "name": name,
                        "path": str(py_file),
                        "type": "integration" if "integration" in base_dir.name else "plugin",
                    })
        return available

    def load(self, name: str, config: Dict[str, Any] = None) -> bool:
        """Load a plugin by name. Returns True on success."""
        for base_dir in [self.plugin_dir, self.integrations_dir]:
            path = base_dir / f"{name}.py"
            if not path.exists():
                continue
            try:
                spec = importlib.util.spec_from_file_location(name, path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                # Find Plugin subclass
                plugin = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, Plugin) and attr is not Plugin:
                        plugin = attr()
                        break
                if plugin is None:
                    self._failed[name] = "No Plugin subclass found"
                    return False
                plugin.on_configure(config or {})
                if not plugin.on_load():
                    self._failed[name] = "Plugin on_load() returned False"
                    return False
                self._loaded[name] = plugin
                logger.info(f"Loaded plugin: {name} v{plugin.version}")
                return True
            except Exception as e:
                self._failed[name] = str(e)
                logger.error(f"Failed to load plugin {name}: {e}")
                return False
        self._failed[name] = "Plugin file not found"
        return False

    def unload(self, name: str) -> bool:
        """Unload a plugin."""
        if name in self._loaded:
            self._loaded[name].on_unload()
            del self._loaded[name]
            if name in sys.modules:
                del sys.modules[name]
            logger.info(f"Unloaded plugin: {name}")
            return True
        return False

    def get(self, name: str) -> Optional[Plugin]:
        """Get a loaded plugin by name."""
        return self._loaded.get(name)

    def loaded(self) -> List[Dict[str, Any]]:
        """List all loaded plugins with status."""
        return [
            {
                "name": name,
                "version": p.version,
                "description": p.description,
                "type": type(p).__bases__[0].__name__,
            }
            for name, p in self._loaded.items()
        ]

    def failed(self) -> Dict[str, str]:
        """Return failed plugin attempts with error messages."""
        return self._failed.copy()

    def load_all(self, config: Dict[str, Any] = None) -> None:
        """Auto-discover and load all available plugins."""
        for plugin_info in self.discover():
            self.load(plugin_info["name"], config)


# --- Plugin Interfaces Registry ---
# Career OS knows about these interfaces; plugins implement them:
PLUGIN_INTERFACES = {
    "discovery": ProviderPlugin,      # Job discovery
    "intelligence": IntelligencePlugin,  # Analysis / recommendations
    "document": DocumentPlugin,      # Document generation
    "integration": IntegrationPlugin,  # External service connection
}


# --- Example Plugin Template ---
EXAMPLE_PLUGIN = '''"""
Example Career OS Plugin — copy to modules/plugins/ and rename.
Implements: IntelligencePlugin
"""
from modules.plugins.base import IntelligencePlugin

class MyInsightPlugin(IntelligencePlugin):
    name = "my_insight"
    version = "0.1"
    description = "Generates custom career insights from application data."

    def analyze(self, context):
        # context contains: profile, applications, funnel, gaps, etc.
        return {
            "insight": "Your interview rate improves 40% when you apply within 48 hours of discovery.",
            "confidence": 0.85,
            "evidence": ["5/5 fast applications resulted in interviews"],
        }
'''
