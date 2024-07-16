from netbox.choices import ButtonColorChoices
from netbox.plugins import PluginMenuButton, PluginMenuItem

from netbox_swupdate.utils import link_adapter

repository_buttons = [
    PluginMenuButton(
        title="Add",
        link=link_adapter("repository_add"),
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
    ),
]
deploy_buttons = [
    PluginMenuButton(
        title="Add",
        link=link_adapter("deploy_add"),
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
    ),
]
software_buttons = [
    PluginMenuButton(
        title="Add",
        link=link_adapter("software_add"),
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
    ),
]
monitoring_buttons = [
    PluginMenuButton(
        title="Add",
        link=link_adapter("monitoring_add"),
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
    ),
]
firmware_request_buttons = [
    PluginMenuButton(
        title="Add",
        link=link_adapter("firmwarerequest_add"),
        icon_class="mdi mdi-plus-thick",
        color=ButtonColorChoices.GREEN,
    ),
]

menu_items = (
    PluginMenuItem(
        link=link_adapter("repository_list"),
        link_text="Repositories",
        buttons=repository_buttons,
    ),
    PluginMenuItem(
        link=link_adapter("deploy_list"),
        link_text="Deployments",
        buttons=deploy_buttons,
    ),
    PluginMenuItem(
        link=link_adapter("software_list"),
        link_text="Softwares",
        buttons=software_buttons,
    ),
    PluginMenuItem(
        link=link_adapter("monitoring_list"),
        link_text="Monitorings",
        buttons=monitoring_buttons,
    ),
    PluginMenuItem(
        link=link_adapter("firmwarerequest_list"),
        link_text="Firmware Requests",
        buttons=firmware_request_buttons,
    ),
)
