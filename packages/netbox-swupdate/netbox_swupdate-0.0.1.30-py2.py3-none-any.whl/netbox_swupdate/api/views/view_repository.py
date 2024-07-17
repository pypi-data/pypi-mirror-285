from netbox.api.viewsets import NetBoxModelViewSet

from netbox_swupdate.api.serializers import RepositorySerializer
from netbox_swupdate.models import Repository

__all__ = ("RepositoryViewSet",)


class RepositoryViewSet(NetBoxModelViewSet):
    queryset = Repository.objects.prefetch_related("tags")
    serializer_class = RepositorySerializer

    def get_queryset(self):
        """Grouping request filters."""
        repository: object = None
        return repository
