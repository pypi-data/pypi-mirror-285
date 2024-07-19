from netbox.forms import NetBoxModelForm

from netbox_swupdate.models import Deploy

__all__ = ("DeployForm",)


class DeployForm(NetBoxModelForm):
    class Meta:
        model = Deploy
        fields = [
            "name",
            "type",
            "deploy_time",
            "devices",
            "software",
            "retries",
            "retry_interval",
            "max_waiting_time",
        ]
