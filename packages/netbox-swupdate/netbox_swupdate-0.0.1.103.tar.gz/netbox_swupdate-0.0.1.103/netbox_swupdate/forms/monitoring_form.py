from netbox.forms import NetBoxModelForm

from netbox_swupdate.models import Monitoring

__all__ = ("MonitoringForm",)


class MonitoringForm(NetBoxModelForm):
    class Meta:
        model = Monitoring
        fields = [
            "status",
            "device",
            "deploy",
            "log_message",
        ]
