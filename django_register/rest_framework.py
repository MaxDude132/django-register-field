# Standard libraries
from typing import TYPE_CHECKING, Any, Iterable

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
    def __init__(self, *args, **kwargs) -> None:
        self.register: Register = kwargs.pop("register", None)
        self.keys: Iterable[str] = kwargs.pop("keys", None)
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

    def run_validation(self, data: Any = ...) -> Any:
        obj = self.register.get_class(data)
        if isinstance(obj, self.register.unknown_item_class):
            raise serializers.ValidationError(
                _("Value {value} not a registered key.").format(value=data)
            )
        return super().run_validation(data)

    def to_representation(self, value: str) -> str | dict[str, Any]:  # type: ignore[override]
        if self.keys is None:
            return self.register.get_key(value)

        out: dict[str, Any] = {}
        errors: list[str] = []

        for key in self.keys:
            try:
                out[key] = getattr(value, key)
            except AttributeError:
                # If label or verbose_name are not on the object, the default was used.
                # We can get the default from the register.
                if key == "label":
                    out[key] = self.register.get_key(value)
                elif key == "verbose_name":
                    out[key] = self.register.get_key(value).replace("_", " ").title()
                else:
                    errors.append(key)

        if errors:
            raise ValueError(
                _("Cannot get the following keys from {value}: {errors}").format(
                    value=value.__class__.__name__, errors=", ".join(errors)
                )
            )

        return out
