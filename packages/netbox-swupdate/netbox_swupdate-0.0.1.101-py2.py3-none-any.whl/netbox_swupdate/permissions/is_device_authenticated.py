from dcim.models import Device
from rest_framework.permissions import BasePermission

__all__ = ("IsDeviceAuthenticated",)


class IsDeviceAuthenticated(BasePermission):
    """
    Allows access only if the device is authenticated with its custom token 'token_swupdate'.
    """

    def has_permission(self, request, view):
        token = request.headers.get("Authorization", None)
        if not token:
            return False

        try:
            device = Device.objects.filter(
                custom_field_data__token_swupdate=token
            ).first()
            if device:
                request.device = device
                return True
        except Device.DoesNotExist:
            return False

        return False
