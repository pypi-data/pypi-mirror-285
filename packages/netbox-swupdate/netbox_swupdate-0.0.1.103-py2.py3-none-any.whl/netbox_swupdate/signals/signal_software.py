from typing import Dict

from django.core.files.base import ContentFile
from django.db.models import Model
from django.db.models.signals import pre_save
from django.dispatch import receiver

from netbox_swupdate.models import Software


@receiver(pre_save, sender=Software, dispatch_uid="pre_software_id")
def manage_software_before_saving(sender: Model, instance: Software, **kwargs: Dict):
    """
    - Adapt the name of the file so that it contains the content of: software name,
    version and date.
    """
    name_file = (
        f"{instance.name}_{instance.version}_{instance.creation_date}.sw".replace(
            " ", ""
        ).lower()
    )
    if instance.file and name_file not in instance.file.name:
        file_content = instance.file.read()
        new_file = ContentFile(file_content)
        instance.file.save(name_file, new_file, save=False)
