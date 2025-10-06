# Migrating from V1 to V2

There was a fairly major change made in V2 that will break V1 implementations.

`label` has been renamed to `key` and `verbose_name` has been renamed to `label`.
This is to be more inline with the naming conventions in django as a whole,
especially with Choices taking `label` as being the name to be displayed.

You can either make the change in your codebase, or use the newly implemented `REGISTER_FIELD_KEY_NAME` and `REGISTER_FIELD_LABEL_NAME` to change this behaviour.

For exmaple, if you wanted to keep the old behaviour, you could add these lines to your `settings.py`:

``` python
REGISTER_FIELD_KEY_NAME="label"
REGISTER_FIELD_LABEL_NAME="verbose_name"
```
