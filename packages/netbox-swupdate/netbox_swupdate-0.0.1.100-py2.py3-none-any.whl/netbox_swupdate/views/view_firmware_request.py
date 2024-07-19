from netbox.views import generic

from netbox_swupdate.filters import FirmwareRequestFilterSet
from netbox_swupdate.forms import FirmwareRequestForm
from netbox_swupdate.models import FirmwareRequest
from netbox_swupdate.tables import FirmwareRequestTable

__all__ = (
    "FirmwareRequestListView",
    "FirmwareRequestView",
    "FirmwareRequestEditView",
    "FirmwareRequestDeleteView",
)


class FirmwareRequestListView(generic.ObjectListView):
    queryset = FirmwareRequest.objects.all()
    filterset = FirmwareRequestFilterSet
    table = FirmwareRequestTable


class FirmwareRequestEditView(generic.ObjectEditView):
    queryset = FirmwareRequest.objects.all()
    form = FirmwareRequestForm


class FirmwareRequestView(generic.ObjectView):
    queryset = FirmwareRequest.objects.all()


class FirmwareRequestDeleteView(generic.ObjectDeleteView):
    queryset = FirmwareRequest.objects.all()
