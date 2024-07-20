import django_tables2 as tables
from netbox.tables import NetBoxTable

from netbox_swupdate.models import Deploy

__all__ = ("DeployTable",)


class DeployTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta:
        model = Deploy
        fields = [
            "pk",
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
        ]
        attrs = {"class": "table table-hover table-headings"}
        default_columns = fields[2:]
