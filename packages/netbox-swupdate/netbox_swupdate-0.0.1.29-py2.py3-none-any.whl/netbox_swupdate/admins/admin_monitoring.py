from django.contrib import admin

__all__ = ("MonitoringAdmin",)


class MonitoringAdmin(admin.ModelAdmin):
    list_display = ("",)
    search_fields = [""]
    list_filter = ("",)
