import importlib
from typing import Callable, Protocol

from .options_factory import PyLOTOptionsFactory


class PluginInterface(Protocol):
    """
    Protocol for typing
    """
    @staticmethod
    def initialize( _: Callable[..., PyLOTOptionsFactory]) -> None:
        """Init the plugin"""

def import_module(name:str) ->  PluginInterface:
    """"Load stuff"""

    return importlib.import_module(name) # type: ignore


def load_plogins(plugins : list[str]) -> None:
    """Load plugins"""
    for plugin_name in plugins:
        plugin = import_module(plugin_name)
        plugin.initialize(PyLOTOptionsFactory)