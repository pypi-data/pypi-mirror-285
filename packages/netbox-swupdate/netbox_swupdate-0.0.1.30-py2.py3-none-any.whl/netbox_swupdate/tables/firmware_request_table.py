import django_tables2 as tables
from netbox.tables import NetBoxTable

from netbox_swupdate.models import FirmwareRequest

__all__ = ("FirmwareRequestTable",)


class FirmwareRequestTable(NetBoxTable):
    firmware_request_id = tables.Column(linkify=True)

    class Meta:
        model = FirmwareRequest
        fields = [
            "pk",
            "id",
            "firmware_request_id",
            "status",
            "deploy_time",
            "device",
            "deploy",
            "retries",
        ]
        attrs = {"class": "table table-hover table-headings"}
        default_columns = fields[2:]
