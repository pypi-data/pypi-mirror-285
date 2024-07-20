"""Top-level package for NetBox SWUpdate Plugin."""

__author__ = """Óscar Hurtado"""
__email__ = "ohurtadp@sens.solutions"
__version__ = "0.0.1.103"

from extras.plugins import PluginConfig


class SWUpdateConfig(PluginConfig):
    name = "netbox_swupdate"
    verbose_name = "NetBox SWUpdate Plugin"
    description = "NetBox plugin for SWUpdate."
    version = __version__
    author = __author__
    author_email = __email__
    base_url = "netbox_swupdate"
    required_settings = []
    default_settings = {
        "SWUPDATE_TIMEOUT": 30,
        "SWUPDATE_ARGS": {},
    }

    def ready(self):
        from . import signals  # noqa

        super().ready()


config = SWUpdateConfig
