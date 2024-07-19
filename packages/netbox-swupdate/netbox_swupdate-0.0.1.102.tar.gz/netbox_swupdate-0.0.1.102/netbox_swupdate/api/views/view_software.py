from netbox.api.viewsets import NetBoxModelViewSet

from netbox_swupdate.api.serializers import SoftwareSerializer
from netbox_swupdate.models import Software

__all__ = ("SoftwareViewSet",)


class SoftwareViewSet(NetBoxModelViewSet):
    queryset = Software.objects.prefetch_related("tags")
    serializer_class = SoftwareSerializer

    def get_queryset(self):
        """Grouping request filters."""
        software: object = None
        return software
