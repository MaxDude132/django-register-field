from django.conf import settings as django_settings
from django.core.signals import setting_changed

DEFAULTS = {
    "KEY_NAME": "key",
    "LABEL_NAME": "label",
}


class Settings:
    def __getattr__(self, item):
        try:
            return getattr(django_settings, "REGISTER_FIELD_" + item)
        except AttributeError:
            if item in DEFAULTS:
                return DEFAULTS[item]
            raise AttributeError("Invalid REGISTER_FIELD setting: '%s'" % item)

    def change_setting(self, setting, value, enter, **kwargs):
        if not setting.startswith("REGISTER_FIELD_"):
            return
        setting = setting[15:]  # strip 'REGISTER_FIELD_'

        # ensure a valid app setting is being overridden
        if setting not in DEFAULTS:
            return

        # if entering, set the value; if exiting, restore or delete
        if enter:
            setattr(self, setting, value)
        else:
            # Only try to delete if the attribute exists as an instance attribute
            if hasattr(self, setting):
                delattr(self, setting)
            # If value is not None, it means we're restoring to a previous override
            if value is not None:
                setattr(self, setting, value)


settings = Settings()
setting_changed.connect(settings.change_setting)
