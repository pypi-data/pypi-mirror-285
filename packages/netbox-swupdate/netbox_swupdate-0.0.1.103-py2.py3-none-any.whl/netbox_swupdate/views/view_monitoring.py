from netbox.views import generic

from netbox_swupdate.filters import MonitoringFilterSet
from netbox_swupdate.forms import MonitoringForm
from netbox_swupdate.models import Monitoring
from netbox_swupdate.tables import MonitoringTable

__all__ = (
    "MonitoringListView",
    "MonitoringView",
    "MonitoringEditView",
    "MonitoringDeleteView",
)


class MonitoringListView(generic.ObjectListView):
    queryset = Monitoring.objects.all()
    filterset = MonitoringFilterSet
    table = MonitoringTable


class MonitoringEditView(generic.ObjectEditView):
    queryset = Monitoring.objects.all()
    form = MonitoringForm


class MonitoringView(generic.ObjectView):
    queryset = Monitoring.objects.all()


class MonitoringDeleteView(generic.ObjectDeleteView):
    queryset = Monitoring.objects.all()
