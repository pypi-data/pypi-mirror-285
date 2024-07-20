from django.contrib import admin

__all__ = ("FirmwareRequestAdmin",)


class FirmwareRequestAdmin(admin.ModelAdmin):
    fields = (
        "deploy_time",
        "device",
        "deploy",
        "status",
        "retries",
    )
