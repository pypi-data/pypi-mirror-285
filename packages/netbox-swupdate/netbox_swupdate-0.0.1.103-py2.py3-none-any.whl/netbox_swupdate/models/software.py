from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from .repository import Repository

__all__ = ["Software"]


class Software(NetBoxModel):
    name = models.CharField(max_length=255, help_text="Nombre del software")
    version = models.CharField(max_length=50, help_text="Versión del software")
    description = models.TextField(help_text="Descripción del software")
    creation_date = models.DateTimeField(
        auto_now_add=True, help_text="Fecha de creación del software"
    )
    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        help_text="Repositorio que contiene el software",
    )
    file = models.FileField(
        upload_to="swupdate_firmware_files/",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("pk",)

    def get_absolute_url(self):
        return reverse("plugins:netbox_swupdate:software", args=[self.pk])
