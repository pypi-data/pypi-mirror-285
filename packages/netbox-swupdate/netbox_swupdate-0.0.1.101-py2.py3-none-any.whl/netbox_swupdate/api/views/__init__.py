from .view_deploy import DeployViewSet
from .view_firmware_request import FirmwareRequestViewSet
from .view_monitoring import MonitoringViewSet
from .view_repository import RepositoryViewSet
from .view_software import SoftwareViewSet
from .view_swupdate import RouteDownloadView

__all__ = (
    "RepositoryViewSet",
    "DeployViewSet",
    "MonitoringViewSet",
    "SoftwareViewSet",
    "FirmwareRequestViewSet",
    "RouteDownloadView",
)
