from django.contrib import admin

from .admins import DeployAdmin, MonitoringAdmin, RepositoryAdmin, SoftwareAdmin
from .models import Deploy, Monitoring, Repository, Software

""" Admin view for Settings """

admin.site.register(Deploy, DeployAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(Software, SoftwareAdmin)
admin.site.register(Monitoring, MonitoringAdmin)
