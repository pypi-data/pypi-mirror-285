from django.urls import include, path
from netbox.api.routers import NetBoxRouter

from netbox_swupdate.api.views import (
    DeployViewSet,
    FirmwareRequestViewSet,
    MonitoringViewSet,
    RepositoryViewSet,
    RouteDownloadView,
    SoftwareViewSet,
)

router = NetBoxRouter()
router.register("repository", RepositoryViewSet)
router.register("deploy", DeployViewSet)
router.register("monitoring", MonitoringViewSet)
router.register("software", SoftwareViewSet)
router.register("firmware-request", FirmwareRequestViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path(
        "api/route-download/",
        RouteDownloadView.as_view(),
        name="route_download",
    ),
]
