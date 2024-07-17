"""Top-level package for NetBox SWUpdate Plugin."""

__author__ = """Óscar Hurtado"""
__email__ = "ohurtadp@sens.solutions"
__version__ = "0.0.1.27"


import uuid

from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from netbox.plugins import PluginConfig


class SWUpdateConfig(PluginConfig):
    name = "netbox_swupdate"
    verbose_name = "NetBox SWUpdate Plugin"
    description = "NetBox plugin for SWUpdate."
    version = __version__
    author = __author__
    author_email = __email__
    base_url = "netbox_swupdate"
    required_settings = []
    default_settings = {
        "SWUPDATE_TIMEOUT": 30,
        "SWUPDATE_ARGS": {},
    }

    def ready(self):
        from core.models import ObjectType
        from dcim.models import Device
        from django.contrib.contenttypes.models import ContentType
        from extras.choices import CustomFieldTypeChoices
        from extras.models import CustomField

        from . import signals

        @receiver(post_migrate)
        def create_custom_field(sender, **kwargs):
            field_name = "token_swupdate"
            content_type = ContentType.objects.get(app_label="dcim", model="device")
            field, created = CustomField.objects.get_or_create(
                name=field_name,
                type=CustomFieldTypeChoices.TYPE_TEXT,
                defaults={
                    "label": "Token SWUpdate",
                },
            )
            if created:
                field.object_types.set(
                    ObjectType.objects.filter(
                        app_label="dcim",
                        model__in=[
                            "device",
                        ],
                    )
                )
                field.save()

            for device in Device.objects.all():
                if (
                    field_name not in device.custom_field_data
                    or device.custom_field_data[field_name] is None
                ):
                    device.custom_field_data[field_name] = str(uuid.uuid4())
                    device.save()

            User = get_user_model()
            username = "anonymous_user"
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password=None)

        super().ready()


config = SWUpdateConfig
