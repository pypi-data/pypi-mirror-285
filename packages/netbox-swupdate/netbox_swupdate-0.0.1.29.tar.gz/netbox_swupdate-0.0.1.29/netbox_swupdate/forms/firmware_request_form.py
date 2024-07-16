from netbox.forms import NetBoxModelForm

from netbox_swupdate.models import FirmwareRequest

__all__ = ("FirmwareRequestForm",)


class FirmwareRequestForm(NetBoxModelForm):
    class Meta:
        model = FirmwareRequest
        fields = [
            "deploy_time",
            "device",
            "deploy",
            "status",
            "retries",
        ]
