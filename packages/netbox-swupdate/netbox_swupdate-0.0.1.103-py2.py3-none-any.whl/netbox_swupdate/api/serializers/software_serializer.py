from rest_framework import serializers

from netbox_swupdate.models import Software

__all__ = ("SoftwareSerializer",)


class SoftwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Software
        fields = [
            "name",
            "version",
            "description",
            "creation_date",
            "repository",
        ]
