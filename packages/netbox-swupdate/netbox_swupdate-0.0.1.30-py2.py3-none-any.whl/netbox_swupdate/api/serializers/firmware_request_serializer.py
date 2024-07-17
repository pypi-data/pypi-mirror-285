from rest_framework import serializers

from netbox_swupdate.models import FirmwareRequest

__all__ = ("FirmwareRequestSerializer",)


class FirmwareRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirmwareRequest
        fields = [
            "firmware_request_id",
            "device",
            "deploy",
            "status",
            "deploy_time",
            "retries",
        ]
