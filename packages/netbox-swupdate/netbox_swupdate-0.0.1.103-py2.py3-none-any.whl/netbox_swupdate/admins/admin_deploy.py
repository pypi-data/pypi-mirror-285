from django.contrib import admin

__all__ = ("DeployAdmin",)


class DeployAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "state",
        "type",
        "deploy_time",
        "devices",
        "software",
        "retries",
        "retry_interval",
        "max_waiting_time",
    )
