import uuid

__all__ = ("generate_uuid",)


def generate_uuid():
    return str(uuid.uuid4())
