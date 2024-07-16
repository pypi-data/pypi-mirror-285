from django.contrib import admin

__all__ = ("SoftwareAdmin",)


class SoftwareAdmin(admin.ModelAdmin):
    list_display = ("",)
    search_fields = [""]
    list_filter = ("",)
