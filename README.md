[![codecov](https://codecov.io/gh/MaxDude132/django-register-field/graph/badge.svg?token=32HWMCV4JQ)](https://codecov.io/gh/MaxDude132/django-register-field)

# django-register-field

A field that returns a python object.

## Installation

```bash
pip install django-register-field
```

## Migration from V1 to V2

There have been breaking changes made between V1 and V2. Please read the [migration docs](migration_v1_to_v2.md).

## Usage

The `RegisterField` allows storing specific objects in the database and retrieving them directly from the model. They will be stored as strings, with a `Register` that is used to keep track of which string maps to what object. It cannot be used to store objects dynamically, but can be very useful for separating some logic into their related classes, reducing the number of if/else required in the model methods.

There are 2 ways to implement the fields: through the `RegisterChoices`, or by manually implementing the register. The former makes it easy to implement and use, while the latter offers more flexibility.

### RegisterChoices

The implementation of the `RegisterChoices` is very similar to django's default `Choices`, but even simpler. It looks like this:

```python
from dataclasses import dataclass
from django_register import RegisterChoices


@dataclass(unsafe_hash=True)
class MyOptions:
    some_field: str
    some_description: str


class SomeRegisterChoices(RegisterChoices):
    OPTION_1 = MyOptions(some_field='field_name', some_description='field_description')
    OPTION_2 = MyOptions(some_field='field_name_2', some_description='field_description_2')

```

`SomeRegisterChoices` is now usable in a `RegisterField` on a model:

```python
from django_register import RegisterField


class SomeModel(models.Model):
    my_field = RegisterField(choices=SomeRegisterChoices)

```

Note that the objects passed to `RegisterChoices` must be hashable. This is because the register keeps track of the relationship between the label and the object in both directions, so the object needs to be usable as a key in a dictionary.

By default, the label used in the database will be the same as the variable name of the choices, in lower case. This can be changed by having a `key` attribute on the object. If one is set, that is what will be used database side. Similarly, the verbose field used in the `.choices` to be displayed in Django admin will be the variable name with all underscores replaced by a space, and `.title` applied to it. This can be changed by setting the `label` attribute on the object.

In the background, `RegisterChoices` takes care of setting and handling the Register for you. You can also create it and set it manually, if using the Choices is not an option.

### Setting the Register directly

The method with the Choices is very good when what you want to keep is information. However, if there is logic that changes as well, you can quickly end up with circular dependencies, 
where the `RegisterField` needs the `RegisterChoices`, which in turn needs you objects. If your code calling the model then is in those same objects, you get the circularity. In that situation,
it might be better to keep a structure where the `RegisterField` has no knowledge of the objects it holds. This can be done by creating the `Register` manually and then adding the objects
to it. This register can then be passed directly to the `RegisterField`.

To set the register manually, you first need to instantiate a Register:

```python
from django_register import Register


register = Register()

```

With that done, you can register objects:

```python
register.register(some_object, db_key='some_label')
```

`db_key` is optional. If not set, the `key` must be set on the object, otherwise a `ValueError` is raised. You can then pass the register to the `RegisterField` directly:

```python
from django_register import RegisterField


class SomeModel(models.Model):
    my_field = RegisterField(register=register)
```

You can also have it be part of the `Model` class:

```python
from django_register import RegisterField


class SomeModel(models.Model):
    register = Register()
    register.register(some_object, db_key='some_label')

    my_field = RegisterField(register=register)
```

You can even use it as a decorator:

```python
@register.register
class SomeClass:
    key = "some_class"

@register.register(db_key="some_other_class")
class SomeOtherClass:
    pass
```

Note that if using that technique, you are responsible for keeping track of your object. The `RegisterChoices` make it easier to keep your objects for comparison and use them outside of the model, but both methods will give the same results database side.

If you need to set the register values dynamically, you can do so after the fact by using the register directly. However in that case, you need to provide a `max_length` if your database does not support having a `CharField` without a `max_length`. That is because in the background, a `CharField` is used to store the key in the database.

You can set the values dynamically like this:

```python
class SomeApp(AppConfig):
    def ready(self):
        register.register(some_object, db_key='some_label')
```

It does not have to be in the `ready` method, values can be added to the register anywhere, however you should be very careful about where you allow adding values and when. If the value is not available somewhere in the code, it will return the `unknown_item_class` instead of the expected object.

## Considerations when removing objects

Removing items from the register requires some consideration. The string in the database is still there unless you create a migration, and it is possible it will cause issues due to the class linked to it not existing anymore. Before version `1.0.8`, this would fail dramatically, giving a ValidationError and stopping anyone from interacting with the database items it was linked to, not even to delete (in most cases). In that case, the only solution would be to add the item back, delete or edit the affected database rows, then remove the item again.

From `v1.0.8` onward, it will no longer fail dramatically, but rather return a default object. This default object will only contain the label. If you want to define other defaults for fields that are accessed, you can pass an `unknown_item_class` parameter to the `RegisterField`, to the register itself, or set an `_UNKNOWN_` attribute in the `RegisterChoices`. All these methods will give the same result: defining the default object to be used when the item can no longer be found. Note that the label will not be passed, but rather set after the creation of the object, so make sure that the `__init__` takes no arguments. It is also recommended to use a different class from the one used to set the options, if only to allow checking if the object is an instance of said class later.

### Examples

#### `RegisterChoices`

```python
class SomeRegisterChoices(RegisterChoices):
    OPTION_1 = MyOptions(some_field='field_name', some_description='field_description')
    OPTION_2 = MyOptions(some_field='field_name_2', some_description='field_description_2')
    _UNKNOWN_ = UnknownOption
```

#### `RegisterField`

```python
class SomeModel(models.Model):
    my_field = RegisterField(register=register, unknown_item_class=UnknownOption)
```

#### To the register itself

```python
register = Register(unknown_item_class=UnknownOption)
```

## Using with django-rest-framework

If using with rest_framework, there is a Serializer Field already built in to be used by the Serializer. You simply need to set the field as such:

```python
from django_register.rest_framework import RegisterField


class SomeModelSerializer(serializers.ModelSerializer):
    some_register_field = RegisterField()

    class Meta:
        model = SomeModel
        fields = ('some_register_field',)
```

Behind the scenes, the serializer field goes and gets the register from the model field to get the work done.

---

Since `v1.0.7`, it is now possible to pass `keys` to the serializer RegisterField to tell it to return an object with those keys. This is useful if you want to expose certain values on the object to the API.

It would look something like this:

```python
from django_register.rest_framework import RegisterField


class SomeModelSerializer(serializers.ModelSerializer):
    some_register_field = RegisterField(keys=['key', 'some_value', 'some_other_value'])

    class Meta:
        model = SomeModel
        fields = ('some_register_field',)
```

The example above would return the following JSON:

```json
{
    "some_register_field": {
        "key": "obj_label",
        "some_value": "value",
        "some_other_value": "other_value"
    }
}
```

Note that if the `key` or `label` is not set on the object directly, the default value that is set automatically will be returned, so they can always be used this way.

## Supported Versions

This library is tested against the following versions:
- Python 3.10, 3.11, 3.12 and 3.13
- Django 4.2 and 5.2
- Django REST Framework 3.14, 3.15 and 3.16

While it probably works with some other versions, it is not garanteed.

## Thanks

Huge thanks to Tim Schilling from Better Simple for his [article](https://www.better-simple.com/django/2023/10/03/registerfields-in-django/) that was the catalyst behind the idea for this library.
