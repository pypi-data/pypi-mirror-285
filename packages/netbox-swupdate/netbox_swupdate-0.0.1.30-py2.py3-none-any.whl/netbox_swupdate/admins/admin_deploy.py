from django.contrib import admin

__all__ = ("DeployAdmin",)


class DeployAdmin(admin.ModelAdmin):
    list_display = ("",)
    search_fields = [""]
    list_filter = ("",)
