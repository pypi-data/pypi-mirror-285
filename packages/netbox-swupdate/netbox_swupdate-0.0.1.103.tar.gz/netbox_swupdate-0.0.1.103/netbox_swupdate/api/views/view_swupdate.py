import os
from datetime import datetime, timedelta

from dcim.models import Device
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites import requests
from django.http import FileResponse, HttpResponse, JsonResponse, StreamingHttpResponse
from django.utils import timezone
from rest_framework.views import APIView

from netbox_swupdate.models import Deploy, FirmwareRequest
from netbox_swupdate.permissions import IsDeviceAuthenticated

__all__ = ("RouteDownloadView",)


class RouteDownloadView(APIView):
    """Download firmware."""

    permission_classes = [IsDeviceAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        """
        An anonymous user is assigned to the "request", thus we deceive the "signal" that
        keeps a record of each action and necessarily associates it with a user.
        """
        if not request.user.is_authenticated:
            User = get_user_model()
            request.user = User.objects.get(username="anonymous_user")
        return super(RouteDownloadView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def _allow_update_for_max_time(firmware_request: FirmwareRequest) -> bool:
        """
        If the "STARTED" state time is exceeded without changing the state, the update
        is allowed to be sent again.
        """
        if timezone.is_aware(firmware_request.deploy_time):
            aware_deploy_time = firmware_request.deploy_time
        else:
            aware_deploy_time = timezone.make_aware(
                firmware_request.deploy_time,
                timezone.get_default_timezone(),
            )
        time_difference = timezone.now() - aware_deploy_time
        if time_difference > timedelta(
            minutes=firmware_request.deploy.max_waiting_time
        ):
            return True
        return False

    @staticmethod
    def _file_iterator(file_name, chunk_size=8192):
        """
        Generator that reads the file in chunks of size chunk_size.
        """
        with open(file_name, "rb") as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    @staticmethod
    def _allow_update(firmware_request: FirmwareRequest) -> bool:
        """
        This method has the function of evaluating whether a new update can be
        performed based on different restrictions: time between update requests,
        number of update attempts.
        """
        permitted: bool = True
        if firmware_request.retries > firmware_request.deploy.retries:
            permitted = False
        return permitted

    def _send_to_device(self, firmware_request: FirmwareRequest):
        try:
            software = firmware_request.deploy.software
            repository = software.repository
            if repository.type == "local":
                try:
                    response = StreamingHttpResponse(
                        self._file_iterator(software.file.path),
                        content_type="application/octet-stream",
                    )
                    response[
                        "Content-Disposition"
                    ] = 'attachment; filename="{}"'.format(
                        os.path.basename(software.file.path)
                    )
                    return response
                except Exception as e:
                    return HttpResponse(
                        f"Error: File not found - {e}",
                        status=404,
                        content_type="text/plain; charset=utf-8",
                    )
        except Exception as e:
            return HttpResponse(
                f"500 Error connecting to SWUpdate: {e}",
                status=500,
                content_type="text/plain; charset=utf-8",
            )

    def _register_device_update(self, device: Device, deploy: Deploy):
        firmware_request = FirmwareRequest.objects.create(
            device=device,
            deploy=deploy,
            deploy_time=datetime.now(),
            status=FirmwareRequest.DEPLOY_STATUS_DEVICE[0][0],  # Estado "STARTED"
            retries=0,
        )
        return self._send_to_device(firmware_request=firmware_request)

    def _update_update_status(self, firmware_request: FirmwareRequest):
        """
        The number of update attempts is checked, new attempts are
        counted, and the update is sent.
        """
        if self._allow_update(firmware_request=firmware_request):
            firmware_request.status = FirmwareRequest.DEPLOY_STATUS_DEVICE[0][0]
            firmware_request.deploy_time = timezone.now()
            firmware_request.retries += 1
            firmware_request.save()
            return self._send_to_device(firmware_request=firmware_request)

    def get(self, request):
        device = request.device
        if device:
            deploy_updates = Deploy.objects.get(
                devices__id=device.id, state__in=["INITIATED", "STOPPED"]
            )
            if deploy_updates:
                try:
                    firmware_request = FirmwareRequest.objects.get(
                        deploy=deploy_updates, device__id=device.id
                    )
                except FirmwareRequest.DoesNotExist:
                    firmware_request = None
                if firmware_request:
                    if firmware_request.status == "FINISHED":
                        return JsonResponse(
                            {
                                "data": f"Device updated successfully: {firmware_request.deploy_time}."
                            },
                            status=200,
                        )
                    elif firmware_request.status == "STARTED":
                        if self._allow_update_for_max_time(
                            firmware_request=firmware_request
                        ):
                            firmware_request.status = "FAILED"
                            firmware_request.save()
                            return JsonResponse(
                                {"data": "Update failed due to timeout."}, status=400
                            )
                        return JsonResponse({"data": "Device updating."}, status=200)
                    elif firmware_request.status == "FAILED":
                        return self._update_update_status(
                            firmware_request=firmware_request
                        )
                else:
                    return self._register_device_update(
                        device=device, deploy=deploy_updates
                    )
        return JsonResponse({"error": "No update."}, status=400)


class UpdateMonitoringView(APIView):
    permission_classes = [IsDeviceAuthenticated]

    def put(self, request, *args, **kwargs):
        return JsonResponse(
            {"success": "Update status updated successfully"}, status=200
        )
