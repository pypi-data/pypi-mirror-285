PLUGIN_APPLICATION_NAME = "netbox_swupdate"


__all__ = ("link_adapter",)


def link_adapter(name):
    return f"plugins:{PLUGIN_APPLICATION_NAME}:{name}"
