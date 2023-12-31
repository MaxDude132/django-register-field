# Standard libraries
from typing import TYPE_CHECKING

# Django
from django.utils.translation import gettext_lazy as _

# Rest Framework
from rest_framework import serializers

# django_register
from django_register.base import Register

if TYPE_CHECKING:
    # Rest Framework
    from rest_framework.serializers import BaseSerializer


class RegisterField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        self.register: Register = kwargs.pop("register", None)
        super().__init__(*args, **kwargs)

    def _get_register_from_parent(self, parent: "BaseSerializer"):
        assert hasattr(parent, "Meta") and hasattr(  # noqa: S101
            parent.Meta, "model"
        ), (
            "Cannot infer the register from the serializer field. "
            "Please provide a register or a Meta class with a model attribute."
        )

        field = parent.Meta.model._meta.get_field(self.field_name)

        try:
            register = field.register
        except AttributeError:
            raise ValueError(
                _(
                    "Cannot infer the register from the serializer field. "
                    "It is not a RegisterField."
                )
            )

        return register

    def bind(self, field_name: str, parent: "BaseSerializer") -> None:
        super().bind(field_name, parent)

        if self.register is None:
            self.register = self._get_register_from_parent(parent)

    def to_internal_value(self, data: str) -> str:
        return self.register.get_class(data)

    def to_representation(self, value: str) -> str:
        return self.register.get_key(value)
