from django.contrib import admin

from .admins import (
    DeployAdmin,
    FirmwareRequestAdmin,
    MonitoringAdmin,
    RepositoryAdmin,
    SoftwareAdmin,
)
from .models import Deploy, FirmwareRequest, Monitoring, Repository, Software

""" Admin view for Settings """

admin.site.register(Deploy, DeployAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(Software, SoftwareAdmin)
admin.site.register(Monitoring, MonitoringAdmin)
admin.site.register(FirmwareRequest, FirmwareRequestAdmin)


from netbox.admin import admin_site

admin_site.site_title = "Sens SWUpdate"
admin_site.site_header = "Sens SWUpdate admin"
admin_site.index_title = "Sens SWUpdate administration"
