from dcim.tables import DeviceTable
from netbox.views import generic

from netbox_swupdate.filters import DeployFilterSet
from netbox_swupdate.forms import DeployForm
from netbox_swupdate.models import Deploy, FirmwareRequest
from netbox_swupdate.tables import DeployTable, FirmwareRequestTable

__all__ = (
    "DeployListView",
    "DeployView",
    "DeployEditView",
    "DeployDeleteView",
)


class DeployListView(generic.ObjectListView):
    queryset = Deploy.objects.all()
    filterset = DeployFilterSet
    table = DeployTable


class DeployEditView(generic.ObjectEditView):
    queryset = Deploy.objects.all()
    form = DeployForm


class DeployView(generic.ObjectView):
    queryset = Deploy.objects.all()

    def get_extra_context(self, request, instance):
        table_firmwares = FirmwareRequestTable(instance.firmwarerequest_set.all())
        table_firmwares.configure(request)
        table_devices = DeviceTable(instance.devices.all())
        table_devices.configure(request)
        return {"firmwares_table": table_firmwares, "devices_table": table_devices}


class DeployDeleteView(generic.ObjectDeleteView):
    queryset = Deploy.objects.all()
