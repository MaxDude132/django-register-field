import warnings

# Django
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


class UnknownRegisterItem:
    label: str


@deconstructible
class Register:
    def __init__(self, unknown_item_class=None):
        self._key_to_class = {}
        self._class_to_key = {}
        self.unknown_item_class = unknown_item_class or UnknownRegisterItem

    def register(self, klass, db_key=None):
        if db_key is None:
            try:
                db_key = klass.label
            except AttributeError:
                raise ValueError(
                    _(
                        "The class {klass} does not have a label. Define "
                        "one or pass a db_key to be used as database value."
                    ).format(klass=klass)
                )

        if db_key in self._key_to_class:
            raise ValueError(_("Key {key} already registered.").format(key=db_key))

        if klass in self._class_to_key:
            raise ValueError(_("Class {klass} already registered.").format(klass=klass))

        self._key_to_class[db_key] = klass
        self._class_to_key[klass] = db_key

        return klass

    def from_key(self, value, ignore_warning=False):
        try:
            return self._key_to_class[value]
        except (KeyError, TypeError):
            if not ignore_warning:
                warnings.warn(
                    _(
                        "Value {value} not a registered key. The unknown_item_class will be used to return the value"
                    ).format(value=value)
                )
            obj = self.unknown_item_class()
            obj.label = value
            return obj

    def from_class(self, value):
        try:
            return self._class_to_key[value]
        except KeyError:
            raise ValidationError(
                _("Value {value} not a registered class.").format(value=value)
            )

    def get_key(self, value):
        obj = self.from_key(value, ignore_warning=True)

        if value is not None and isinstance(obj, self.unknown_item_class):
            return self.from_class(value)

        return value

    def get_class(self, value):
        try:
            self.from_class(value)
        except ValidationError:
            return self.from_key(value)

        return value

    @property
    def max_length(self):
        if self._key_to_class:
            return max(len(key) for key in self._key_to_class)

    @property
    def choices(self):
        return [
            (k, self._get_verbose_name(v, k)) for k, v in self._key_to_class.items()
        ]

    @property
    def flatchoices(self):
        return [
            (v, self._get_verbose_name(v, k)) for k, v in self._key_to_class.items()
        ]

    def _get_verbose_name(self, klass, key):
        return getattr(klass, "verbose_name", key.replace("_", " ").title())

    def __iter__(self):
        return iter(self._key_to_class.values())


class RegisterList(list):
    register = None


class RegisterChoicesMeta(type):
    def __new__(mcs, name, bases, attrs):  # noqa: N804
        cls = super().__new__(mcs, name, bases, attrs)

        unknown_key = "_UNKNOWN_"
        cls.register = Register(unknown_item_class=attrs.get(unknown_key))

        for label, member in cls._all_mapping.items():
            cls.register.register(member, db_key=label)

        return cls

    def _label_name(cls, name, obj):
        default_label = name.lower()
        return getattr(obj, "label", default_label)

    @property
    def _all_mapping(cls):
        return {
            cls._label_name(key, value): value
            for key, value in cls.__dict__.items()
            if not key.startswith("_") and key.isupper()
        }

    @property
    def choices(cls):
        choices = RegisterList()

        for label, obj in cls._all_mapping.items():
            default_verbose_name = label.replace("_", " ").title()
            verbose_name = getattr(obj, "verbose_name", default_verbose_name)

            choices.append((label, verbose_name))

        choices.register = cls.register
        return choices

    def __iter__(cls):
        return iter(cls.register)


class RegisterChoices(metaclass=RegisterChoicesMeta):
    def __new__(cls, klass):
        return cls.register.get_class(klass)


class RegisterField(models.CharField):
    description = _("Store a string, return the associated class")

    def __init__(self, *args, **kwargs):
        if "register" not in kwargs and "choices" not in kwargs:
            raise ValueError(_("You must provide choices to the RegisterField."))

        if "register" not in kwargs and not hasattr(kwargs["choices"], "register"):
            raise ValueError(_("Choices must be a RegisterChoices instance."))

        # When building the migrations, the register cannot be in the choices.
        # It will be passed individually, so we take it from there.
        self.register: Register = (
            kwargs.pop("register")
            if "register" in kwargs
            else kwargs["choices"].register
        )

        if "choices" not in kwargs:
            kwargs["choices"] = self.register.choices

        if "max_length" not in kwargs and (max_length := self.register.max_length):
            kwargs["max_length"] = max_length

        if "default" in kwargs:
            try:
                kwargs["default"] = self.register.get_key(kwargs["default"])
            except ValidationError:
                pass

        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if not value:
            return value

        return self.register.get_class(value)

    def get_default(self):
        default = super().get_default()

        if default:
            return self.register.get_class(default)

        return default

    def to_python(self, value):
        if not value:
            return value

        return self.register.get_class(value)

    def get_prep_value(self, value):
        if not value:
            return value

        return self.register.get_key(value)

    def value_from_object(self, obj):
        value = super().value_from_object(obj)
        return self.get_prep_value(value)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop("choices", None)
        kwargs["register"] = self.register
        return name, path, args, kwargs

    def clean(self, value, model_instance):
        """
        We need to override clean because it runs the validations on the
        Python object instead of on the database string.
        """
        value = self.get_prep_value(value)
        self.validate(value, model_instance)
        self.run_validators(value)
        return self.to_python(value)

    def _get_flatchoices(self):
        return self.register.flatchoices

    flatchoices = property(_get_flatchoices)

    def _register_choices(self):
        return self.register.choices

    def _register_choices_set(self, value):
        return

    choices = property(_register_choices, _register_choices_set)
    _choices = property(_register_choices, _register_choices_set)
