import uuid

from dcim.models import Device
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Device)
def set_default_custom_field(sender, instance, **kwargs):
    # Set a default value for the custom field
    field_name = "token_swupdate"
    if field_name not in instance.custom_field_data:
        instance.custom_field_data[field_name] = str(uuid.uuid4())
