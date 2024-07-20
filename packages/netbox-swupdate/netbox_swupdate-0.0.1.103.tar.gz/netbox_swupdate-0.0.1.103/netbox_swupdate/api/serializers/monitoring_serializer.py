from rest_framework import serializers

from netbox_swupdate.models import Monitoring

__all__ = ("MonitoringSerializer",)


class MonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitoring
        fields = [
            "STATUS_CHOICES",
            "status",
            "device",
            "deploy",
            "update_time",
            "log_message",
        ]
