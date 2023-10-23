[![codecov](https://codecov.io/gh/MaxDude132/django-register-field/graph/badge.svg?token=32HWMCV4JQ)](https://codecov.io/gh/MaxDude132/django-register-field)

# django-register-field

A field that returns a python object.

## Installation

To install, call `pip install django-register-field`.

## Usage

The RegisterField allows storing specific objects in the database and retriving them directly from the model. The will be stored as strings, with a Register that is used to keep track of which string maps to what object. It cannot be used to store objects dynamically, but can be very useful to separate some logic into their related classes, reducing the number of if/else required in the model methods.

There are 2 ways to implement the fields: through the RegisterChoices, or by manually implementing the register. The former makes it easy to implement and use, the latter offers more flexibility.

### RegisterChoices

The implementation of the RegisterChoices is very similar to django's default Choices, but even simpler. It looks like this:

``` python
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

`SomeRegisterChoices` is now usable in a RegisterField on a model:

``` python
from django_register import RegisterField


class SomeModel(models.Model):
    my_field = RegisterField(choices=SomeRegisterChoices.choices)

```

Note that the objects passed to RegisterChoices must be hashable. This is because the register keeps track of the relationship between the label and the object in both directions, so the object needs to be usable as a key in a dictionary.

By default, the label used in the database will be the same as the variable name on the choices, in lower case. This can be changed by having a `label` attribute on the object. If one is set, that is what will be used database side. Similarly, the verbose field used in the `.choices` to be displayed in django admin will be the variable name with all underscores replaced by a space, and `.title` applied to it. This can be changed by setting the `verbose_name` attribute on the object.

In the background, the RegisterChoices takes care of setting and handling the Register for you. You can also create it and set it manually, if using the Choices is not an option.

### Setting the Register directly

To set the register manually, you first need to instantiate a Register:

``` python
from django_register import Register


register = Register()

```

With that done, you can register objects with it in your app config's `ready` method (found in `apps.py`).:

``` python
class SomeApp(AppConfig):
    def ready(self):
        register.register(some_object, db_key='some_label')
```

`db_key` is not required. If not set, the `label` must be set on the object, otherwise a `ValueError` is raised. You can then pass the register to the `RegisterField` directly:

``` python
from django_register import RegisterField


class SomeModel(models.Model):
    my_field = RegisterField(register=register)
```

Note that if using that technique, you are responsible for keeping track of your object. The `RegisterChoices` make it easier to keep your objects for comparison and use them outside of the model, but both methods will give the same results database side.
