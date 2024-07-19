from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from netbox_swupdate.models import Repository

__all__ = ("RepositoryFilterSet",)


class RepositoryFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Repository
        fields = ("id", "name")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter).distinct()
