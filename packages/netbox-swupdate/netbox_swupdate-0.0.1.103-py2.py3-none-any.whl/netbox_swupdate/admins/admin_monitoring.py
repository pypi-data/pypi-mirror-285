from django.contrib import admin

__all__ = ("MonitoringAdmin",)


class MonitoringAdmin(admin.ModelAdmin):
    fields = ("status", "device", "deploy", "log_message")
