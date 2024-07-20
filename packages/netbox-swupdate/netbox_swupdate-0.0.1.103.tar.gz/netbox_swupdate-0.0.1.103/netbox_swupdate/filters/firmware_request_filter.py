from dcim.models import Device
from django.db.models import Q
from django.utils.translation import gettext as _
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import TreeNodeMultipleChoiceFilter

from netbox_swupdate.models import Deploy, FirmwareRequest

__all__ = ("FirmwareRequestFilterSet",)


class FirmwareRequestFilterSet(NetBoxModelFilterSet):
    device = TreeNodeMultipleChoiceFilter(
        queryset=Device.objects.all(),
        lookup_expr="in",
        field_name="device__name",
        to_field_name="device",
        label=_("Device (name)"),
    )

    deploy = TreeNodeMultipleChoiceFilter(
        queryset=Deploy.objects.all(),
        lookup_expr="in",
        field_name="deploy__name",
        to_field_name="deploy",
        label=_("Deploy (name)"),
    )

    class Meta:
        model = FirmwareRequest
        fields = (
            "id",
            "firmware_request_id",
            "deploy_time",
            "device",
            "deploy",
            "status",
            "retries",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(type__icontains=value)
        return queryset.filter(qs_filter).distinct()
