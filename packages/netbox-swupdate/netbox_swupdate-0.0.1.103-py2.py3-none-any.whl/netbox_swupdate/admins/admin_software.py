from django.contrib import admin

__all__ = ("SoftwareAdmin",)


class SoftwareAdmin(admin.ModelAdmin):
    fields = ("name", "version", "description", "repository", "file")
