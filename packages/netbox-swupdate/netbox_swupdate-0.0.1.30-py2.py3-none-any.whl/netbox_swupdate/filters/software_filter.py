from django.db.models import Q
from django.utils.translation import gettext as _
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import TreeNodeMultipleChoiceFilter

from netbox_swupdate.models import Repository, Software

__all__ = ("SoftwareFilterSet",)


class SoftwareFilterSet(NetBoxModelFilterSet):
    repository = TreeNodeMultipleChoiceFilter(
        queryset=Repository.objects.all(),
        lookup_expr="in",
        field_name="repository__name",
        to_field_name="Repository",
        label=_("Repository (name)"),
    )

    class Meta:
        model = Software
        fields = ("id", "name", "version", "description", "creation_date", "repository")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(version__icontains=value)
        return queryset.filter(qs_filter).distinct()
