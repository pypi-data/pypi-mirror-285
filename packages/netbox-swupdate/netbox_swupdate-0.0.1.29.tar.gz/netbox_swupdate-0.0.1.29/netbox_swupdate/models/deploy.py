from dcim.models import Device
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from .software import Software

__all__ = ["Deploy"]


class Deploy(NetBoxModel):
    DEPLOY_CHOICES = [
        ("test", "Test"),
        ("production", "Production"),
    ]
    DEPLOY_STATES = [
        ("STOPPED", "Stopped"),
        ("INITIATED", "Initiated"),
        ("FINALIZED", "Finalized"),
    ]
    RETRY_CHOICES = [
        (0, "0"),
        (2, "2"),
        (4, "4"),
        (6, "6"),
        (10, "10"),
        (20, "20"),
    ]
    RETRY_INTERVAL_CHOICES = [
        (0, "0 minutes"),
        (1, "1 minutes"),
        (2, "2 minutes"),
        (5, "5 minutes"),
    ]
    MAX_WAITING_TIME_CHOICES = [
        (1, "1 minutes"),
        (5, "5 minutes"),
        (10, "10 minutes"),
        (15, "15 minutes"),
    ]

    name = models.CharField(max_length=255, help_text="Nombre del despliegue")
    state = models.CharField(
        max_length=10,
        choices=DEPLOY_STATES,
        default="STOPPED",
        help_text="Estado actual del despliegue",
    )
    type = models.CharField(
        max_length=50, choices=DEPLOY_CHOICES, help_text="Tipo de despliegue"
    )
    deploy_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha y hora en que se desea realizar el despliegue. Si se "
        "deja en blanco, el despliegue puede realizarse en cualquier "
        "momento.",
    )
    devices = models.ManyToManyField(
        Device, help_text="Dispositivos a los que afectará el despliegue"
    )
    software = models.ForeignKey(
        Software, on_delete=models.CASCADE, help_text="Software asociado al despliegue"
    )
    retries = models.IntegerField(
        choices=RETRY_CHOICES,
        default=0,
        help_text="Número de reintentos permitidos para el despliegue.",
    )
    retry_interval = models.IntegerField(
        choices=RETRY_INTERVAL_CHOICES,
        default=0,
        help_text="Tiempo mínimo entre reintentos, en minutos.",
    )
    max_waiting_time = models.IntegerField(
        choices=MAX_WAITING_TIME_CHOICES,
        default=1,
        help_text="Tiempo mínimo entre reintentos, en minutos.",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("pk",)

    def get_absolute_url(self):
        return reverse("plugins:netbox_swupdate:deploy", args=[self.pk])
