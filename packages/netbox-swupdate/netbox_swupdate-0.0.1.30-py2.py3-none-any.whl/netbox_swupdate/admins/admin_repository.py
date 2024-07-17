from django.contrib import admin

__all__ = ("RepositoryAdmin",)


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ("",)
    search_fields = [""]
    list_filter = ("",)
