from netbox.views import generic

from netbox_swupdate.filters import RepositoryFilterSet
from netbox_swupdate.forms import RepositoryForm
from netbox_swupdate.models import Repository
from netbox_swupdate.tables import RepositoryTable

__all__ = (
    "RepositoryListView",
    "RepositoryView",
    "RepositoryEditView",
    "RepositoryDeleteView",
)


class RepositoryListView(generic.ObjectListView):
    queryset = Repository.objects.all()
    filterset = RepositoryFilterSet
    table = RepositoryTable


class RepositoryEditView(generic.ObjectEditView):
    queryset = Repository.objects.all()
    form = RepositoryForm


class RepositoryView(generic.ObjectView):
    queryset = Repository.objects.all()


class RepositoryDeleteView(generic.ObjectDeleteView):
    queryset = Repository.objects.all()
