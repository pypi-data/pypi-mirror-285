from rest_framework import serializers

from netbox_swupdate.models import Repository

__all__ = ("RepositorySerializer",)


class RepositorySerializer(serializers.ModelSerializer):
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
