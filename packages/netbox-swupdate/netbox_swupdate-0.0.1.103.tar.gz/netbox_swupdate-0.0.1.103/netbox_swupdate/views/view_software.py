from netbox.views import generic

from netbox_swupdate.filters import SoftwareFilterSet
from netbox_swupdate.forms import SoftwareForm
from netbox_swupdate.models import Software
from netbox_swupdate.tables import SoftwareTable

__all__ = (
    "SoftwareListView",
    "SoftwareView",
    "SoftwareEditView",
    "SoftwareDeleteView",
)


class SoftwareListView(generic.ObjectListView):
    queryset = Software.objects.all()
    filterset = SoftwareFilterSet
    table = SoftwareTable


class SoftwareEditView(generic.ObjectEditView):
    queryset = Software.objects.all()
    form = SoftwareForm


class SoftwareView(generic.ObjectView):
    queryset = Software.objects.all()


class SoftwareDeleteView(generic.ObjectDeleteView):
    queryset = Software.objects.all()
