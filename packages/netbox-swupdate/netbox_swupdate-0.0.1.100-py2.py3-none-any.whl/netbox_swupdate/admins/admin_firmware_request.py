from django.contrib import admin

__all__ = ("FirmwareRequestAdmin",)


class FirmwareRequestAdmin(admin.ModelAdmin):
    fields = (
        "firmware_request_id",
        "deploy_time",
        "device",
        "deploy",
        "status",
        "retries",
    )
