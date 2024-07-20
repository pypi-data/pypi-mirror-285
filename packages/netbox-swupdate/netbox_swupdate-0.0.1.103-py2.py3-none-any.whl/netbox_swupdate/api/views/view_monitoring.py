from netbox.api.viewsets import NetBoxModelViewSet

from netbox_swupdate.api.serializers import MonitoringSerializer
from netbox_swupdate.models import Monitoring

__all__ = ("MonitoringViewSet",)


class MonitoringViewSet(NetBoxModelViewSet):
    queryset = Monitoring.objects.prefetch_related("tags")
    serializer_class = MonitoringSerializer

    def get_queryset(self):
        """Grouping request filters."""
        monitoring: object = None
        return monitoring
