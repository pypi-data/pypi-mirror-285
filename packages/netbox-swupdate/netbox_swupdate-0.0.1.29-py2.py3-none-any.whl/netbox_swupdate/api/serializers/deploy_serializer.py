from rest_framework import serializers

from netbox_swupdate.models import Deploy

__all__ = ("DeploySerializer",)


class DeploySerializer(serializers.ModelSerializer):
    class Meta:
        model = Deploy
        fields = [
            "DEPLOY_CHOICES",
            "name",
            "type",
            "deploy_time",
            "devices",
            "software",
            "retries",
            "retry_interval",
        ]
