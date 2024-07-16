import django_tables2 as tables
from netbox.tables import NetBoxTable

from netbox_swupdate.models import Repository

__all__ = ("RepositoryTable",)


class RepositoryTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta:
        model = Repository
        fields = [
            "pk",
            "id",
            "name",
            "type",
        ]
        attrs = {"class": "table table-hover table-headings"}
        default_columns = fields[2:]
