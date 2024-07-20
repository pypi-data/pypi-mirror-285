from django.contrib import admin

__all__ = ("RepositoryAdmin",)


class RepositoryAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "type",
        "local_path",
        "s3_bucket_id",
        "s3_access_key",
        "s3_secret_key",
        "docker_registry_url",
        "docker_access_token",
    )
