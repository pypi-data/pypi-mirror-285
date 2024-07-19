from dcim.models import Device
from django.db.models import Q
from django.utils.translation import gettext as _
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import TreeNodeMultipleChoiceFilter

from netbox_swupdate.models import Deploy, Software

__all__ = ("DeployFilterSet",)


class DeployFilterSet(NetBoxModelFilterSet):
    devices = TreeNodeMultipleChoiceFilter(
        queryset=Device.objects.all(),
        lookup_expr="in",
        field_name="devices__name",
        to_field_name="devices",
        label=_("Device (name)"),
    )

    software = TreeNodeMultipleChoiceFilter(
        queryset=Software.objects.all(),
        lookup_expr="in",
        field_name="software__name",
        to_field_name="software",
        label=_("Software (name)"),
    )

    class Meta:
        model = Deploy
        fields = (
            "id",
            "name",
            "state",
            "type",
            "deploy_time",
            "devices",
            "software",
            "retries",
            "retry_interval",
            "max_waiting_time",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(type__icontains=value)
        return queryset.filter(qs_filter).distinct()
