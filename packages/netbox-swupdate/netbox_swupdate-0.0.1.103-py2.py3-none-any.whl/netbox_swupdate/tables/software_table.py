import django_tables2 as tables
from netbox.tables import NetBoxTable

from netbox_swupdate.models import Software

__all__ = ("SoftwareTable",)


class SoftwareTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta:
        model = Software
        fields = [
            "pk",
            "id",
            "name",
            "version",
            "description",
            "creation_date",
            "repository",
        ]
        attrs = {"class": "table table-hover table-headings"}
        default_columns = fields[2:]
