from dcim.models import Device
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from .deploy import Deploy

__all__ = ["Monitoring"]


class Monitoring(NetBoxModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, help_text="Estado de la actualización"
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        help_text="Dispositivo que se está actualizando",
    )
    deploy = models.ForeignKey(
        Deploy, on_delete=models.CASCADE, help_text="Despliegue asociado al monitoreo"
    )
    update_time = models.DateTimeField(
        auto_now=True, help_text="Fecha y hora de la última actualización"
    )
    log_message = models.TextField(
        blank=True, null=True, help_text="Mensaje de log devuelto por SWUpdate"
    )

    class Meta:
        ordering = ("pk",)

    def get_absolute_url(self):
        return reverse("plugins:netbox_swupdate:monitoring", args=[self.pk])
