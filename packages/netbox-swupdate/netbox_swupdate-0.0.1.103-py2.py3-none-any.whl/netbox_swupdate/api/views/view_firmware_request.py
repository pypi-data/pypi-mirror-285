from netbox.api.viewsets import NetBoxModelViewSet

from netbox_swupdate.api.serializers import FirmwareRequestSerializer
from netbox_swupdate.models import FirmwareRequest

__all__ = ("FirmwareRequestViewSet",)


class FirmwareRequestViewSet(NetBoxModelViewSet):
    queryset = FirmwareRequest.objects.prefetch_related("tags")
    serializer_class = FirmwareRequestSerializer

    def get_queryset(self):
        """Grouping request filters."""
        firmware_request: object = None
        return firmware_request
