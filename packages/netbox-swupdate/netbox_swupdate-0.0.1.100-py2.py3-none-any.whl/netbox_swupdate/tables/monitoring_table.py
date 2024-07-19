import django_tables2 as tables
from netbox.tables import NetBoxTable

from netbox_swupdate.models import Monitoring

__all__ = ("MonitoringTable",)


class MonitoringTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta:
        model = Monitoring
        fields = ["pk", "id", "status", "device", "deploy", "update_time"]
        attrs = {"class": "table table-hover table-headings"}
        default_columns = fields[2:]
