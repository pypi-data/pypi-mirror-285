from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

__all__ = ["Repository"]


class Repository(NetBoxModel):
    REPO_CHOICES = [
        ("local", "Local Disk"),
        ("s3", "S3"),
        ("docker", "Docker Registry UI"),
    ]
    name = models.CharField(max_length=255, help_text="Nombre del repositorio")
    type = models.CharField(
        max_length=50, choices=REPO_CHOICES, help_text="Tipo de repositorio"
    )
    local_path = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="swupdate_firmware_files/",
        help_text="Ruta al repositorio en el disco local",
    )
    s3_bucket_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="ID del bucket S3 para el repositorio",
    )
    s3_access_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Clave de acceso para el bucket S3",
    )
    s3_secret_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Clave secreta para el bucket S3",
    )
    docker_registry_url = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="URL del registro Docker para el repositorio",
    )
    docker_access_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Token de acceso para el registro Docker",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("pk",)

    def get_absolute_url(self):
        return reverse("plugins:netbox_swupdate:repository", args=[self.pk])
