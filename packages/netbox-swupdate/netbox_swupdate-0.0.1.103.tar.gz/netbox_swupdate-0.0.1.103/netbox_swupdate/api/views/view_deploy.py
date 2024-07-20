from netbox.api.viewsets import NetBoxModelViewSet

from netbox_swupdate.api.serializers import DeploySerializer
from netbox_swupdate.models import Deploy

__all__ = ("DeployViewSet",)


class DeployViewSet(NetBoxModelViewSet):
    queryset = Deploy.objects.prefetch_related("tags")
    serializer_class = DeploySerializer

    def get_queryset(self):
        """Grouping request filters."""
        deploy: object = None
        return deploy
