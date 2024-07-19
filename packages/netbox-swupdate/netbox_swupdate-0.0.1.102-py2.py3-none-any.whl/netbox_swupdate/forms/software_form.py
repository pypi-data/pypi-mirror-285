from netbox.forms import NetBoxModelForm

from netbox_swupdate.models import Software

__all__ = ("SoftwareForm",)


class SoftwareForm(NetBoxModelForm):
    class Meta:
        model = Software
        fields = ["name", "version", "description", "repository", "file"]
