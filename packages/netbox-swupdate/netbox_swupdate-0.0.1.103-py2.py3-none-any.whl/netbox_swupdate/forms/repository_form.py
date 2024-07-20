from netbox.forms import NetBoxModelForm

from netbox_swupdate.models import Repository

__all__ = ("RepositoryForm",)


class RepositoryForm(NetBoxModelForm):
    class Meta:
        model = Repository
        fields = [
            "name",
            "type",
            "local_path",
            "s3_bucket_id",
            "s3_access_key",
            "s3_secret_key",
            "docker_registry_url",
            "docker_access_token",
        ]
        fieldsets = (
            (
                None,
                {
                    "fields": (
                        "name",
                        "type",
                        "local_path",
                        "s3_bucket_id",
                        "s3_access_key",
                        "s3_secret_key",
                        "docker_registry_url",
                        "docker_access_token",
                    )
                },
            ),
        )

    def __init__(self, *args, **kwargs):
        super(RepositoryForm, self).__init__(*args, **kwargs)
        self.fields["local_path"].disabled = True
