# Standard libraries
from dataclasses import dataclass

# Django
from django.test import TestCase, override_settings
from django.db import models

# django_register
from django_register import (
    Register,
    RegisterChoices,
    RegisterField,
)
from django_register.base import UnknownRegisterItem
from django_register.rest_framework import RegisterField as DRFRegisterField
from django_register.settings import settings


class SettingsTestCase(TestCase):
    def test_default_settings(self):
        self.assertEqual(settings.KEY_NAME, "key")
        self.assertEqual(settings.LABEL_NAME, "label")

    @override_settings(
        REGISTER_FIELD_KEY_NAME="name", REGISTER_FIELD_LABEL_NAME="pretty_name"
    )
    def test_custom_key_and_label_names_in_register(self):
        @dataclass(unsafe_hash=True)
        class CustomItem:
            name: str
            pretty_name: str

        custom_register = Register()

        item = CustomItem(name="test_key", pretty_name="Test Label")
        custom_register.register(item)

        self.assertEqual(custom_register.from_class(item), "test_key")
        self.assertEqual(custom_register.from_key("test_key"), item)

    @override_settings(
        REGISTER_FIELD_KEY_NAME="name", REGISTER_FIELD_LABEL_NAME="pretty_name"
    )
    def test_custom_key_and_label_names_with_unknown_item(self):
        self.assertEqual(settings.KEY_NAME, "name")

        unknown_item = UnknownRegisterItem()

        self.assertTrue(hasattr(unknown_item, "name"))
        self.assertIsNone(getattr(unknown_item, "name"))

    @override_settings(
        REGISTER_FIELD_KEY_NAME="name", REGISTER_FIELD_LABEL_NAME="pretty_name"
    )
    def test_custom_key_and_label_names_in_register_choices(self):
        @dataclass(unsafe_hash=True)
        class CustomCountry:
            name: str
            pretty_name: str
            population: int

        class CustomCountryChoices(RegisterChoices):
            FRANCE = CustomCountry(
                name="fr", pretty_name="France", population=65_000_000
            )
            GERMANY = CustomCountry(
                name="de", pretty_name="Germany", population=83_000_000
            )

        choices = CustomCountryChoices.choices
        choice_dict = dict(choices)

        self.assertEqual(choice_dict["fr"], "France")
        self.assertEqual(choice_dict["de"], "Germany")

        self.assertEqual(
            CustomCountryChoices.register.from_class(CustomCountryChoices.FRANCE), "fr"
        )
        self.assertEqual(
            CustomCountryChoices.register.from_key("fr"), CustomCountryChoices.FRANCE
        )

    @override_settings(
        REGISTER_FIELD_KEY_NAME="name", REGISTER_FIELD_LABEL_NAME="pretty_name"
    )
    def test_custom_key_and_label_names_register_choices_without_attributes(self):
        @dataclass(unsafe_hash=True)
        class SimpleCountry:
            population: int

        class SimpleCountryChoices(RegisterChoices):
            FRANCE = SimpleCountry(population=65_000_000)
            GERMANY = SimpleCountry(population=83_000_000)

        choices = SimpleCountryChoices.choices
        choice_dict = dict(choices)

        self.assertEqual(choice_dict["france"], "France")
        self.assertEqual(choice_dict["germany"], "Germany")

    @override_settings(
        REGISTER_FIELD_KEY_NAME="name", REGISTER_FIELD_LABEL_NAME="pretty_name"
    )
    def test_custom_key_and_label_names_in_register_field(self):
        @dataclass(unsafe_hash=True)
        class CustomItem:
            name: str
            pretty_name: str

        class CustomChoices(RegisterChoices):
            ITEM1 = CustomItem(name="item1", pretty_name="Item One")
            ITEM2 = CustomItem(name="item2", pretty_name="Item Two")

        class TestModel(models.Model):
            choice_field = RegisterField(choices=CustomChoices)

            class Meta:
                app_label = "tests"

        choices = TestModel._meta.get_field("choice_field").choices
        choice_dict = dict(choices)

        self.assertEqual(choice_dict["item1"], "Item One")
        self.assertEqual(choice_dict["item2"], "Item Two")

    @override_settings(
        REGISTER_FIELD_KEY_NAME="name", REGISTER_FIELD_LABEL_NAME="pretty_name"
    )
    def test_custom_key_and_label_names_in_drf_serializer_field(self):
        @dataclass(unsafe_hash=True)
        class CustomItem:
            name: str
            pretty_name: str
            extra_field: str

        custom_register = Register()
        item = CustomItem(
            name="test_key", pretty_name="Test Label", extra_field="Extra"
        )
        custom_register.register(item)

        field = DRFRegisterField(
            register=custom_register, keys=["name", "pretty_name", "extra_field"]
        )

        representation = field.to_representation(item)
        expected = {
            "name": "test_key",
            "pretty_name": "Test Label",
            "extra_field": "Extra",
        }
        self.assertEqual(representation, expected)

    @override_settings(
        REGISTER_FIELD_KEY_NAME="name", REGISTER_FIELD_LABEL_NAME="pretty_name"
    )
    def test_custom_key_and_label_names_drf_field_defaults(self):
        @dataclass(unsafe_hash=True)
        class ItemWithoutCustomAttrs:
            population: int

        custom_register = Register()
        item = ItemWithoutCustomAttrs(population=1000)
        custom_register.register(item, db_key="test_item")

        field = DRFRegisterField(register=custom_register, keys=["name", "pretty_name"])

        representation = field.to_representation(item)
        expected = {
            "name": "test_item",
            "pretty_name": "Test Item",
        }
        self.assertEqual(representation, expected)

    @override_settings(
        REGISTER_FIELD_KEY_NAME="name", REGISTER_FIELD_LABEL_NAME="pretty_name"
    )
    def test_register_error_messages_use_custom_key_name(self):
        @dataclass(unsafe_hash=True)
        class ItemWithoutKey:
            population: int

        register = Register()

        with self.assertRaises(ValueError) as context:
            register.register(ItemWithoutKey(population=1000))

        error_message = str(context.exception)
        self.assertIn("name", error_message)

    @override_settings(
        REGISTER_FIELD_KEY_NAME="name", REGISTER_FIELD_LABEL_NAME="pretty_name"
    )
    def test_settings_change_at_runtime(self):
        from django_register.settings import settings as register_settings

        self.assertEqual(register_settings.KEY_NAME, "name")
        self.assertEqual(register_settings.LABEL_NAME, "pretty_name")

        @override_settings(REGISTER_FIELD_KEY_NAME="identifier")
        def inner_test():
            self.assertEqual(register_settings.KEY_NAME, "identifier")
            self.assertEqual(
                register_settings.LABEL_NAME, "pretty_name"
            )  # Should remain unchanged

        inner_test()

        self.assertEqual(register_settings.KEY_NAME, "name")
        self.assertEqual(register_settings.LABEL_NAME, "pretty_name")

    def test_invalid_setting_raises_attribute_error(self):
        from django_register.settings import settings as register_settings

        with self.assertRaises(AttributeError) as context:
            _ = register_settings.INVALID_SETTING

        self.assertIn("Invalid REGISTER_FIELD setting", str(context.exception))

    @override_settings(
        REGISTER_FIELD_KEY_NAME="name", REGISTER_FIELD_LABEL_NAME="pretty_name"
    )
    def test_label_name_behavior_unified(self):
        @dataclass(unsafe_hash=True)
        class Item:
            name: str
            pretty_name: str

        class ItemChoices(RegisterChoices):
            TEST = Item(name="test", pretty_name="Pretty Name")

        choices_from_register_choices = ItemChoices.choices
        self.assertEqual(dict(choices_from_register_choices), {"test": "Pretty Name"})

        choices_from_register = ItemChoices.register.choices
        self.assertEqual(dict(choices_from_register), {"test": "Pretty Name"})

        class TestModel(models.Model):
            item = RegisterField(choices=ItemChoices)

            class Meta:
                app_label = "tests"

        field_choices = TestModel._meta.get_field("item").choices
        self.assertEqual(dict(field_choices), {"test": "Pretty Name"})

    @override_settings(
        REGISTER_FIELD_KEY_NAME="name", REGISTER_FIELD_LABEL_NAME="pretty_name"
    )
    def test_mixed_settings_comprehensive(self):
        @dataclass(unsafe_hash=True)
        class Product:
            name: str
            pretty_name: str
            price: float

        class ProductChoices(RegisterChoices):
            LAPTOP = Product(name="lpt", pretty_name="Laptop Computer", price=999.99)
            PHONE = Product(name="phn", pretty_name="Smart Phone", price=699.99)

        class Order(models.Model):
            product = RegisterField(choices=ProductChoices)

            class Meta:
                app_label = "tests"

        choices = ProductChoices.choices
        self.assertEqual(
            dict(choices), {"lpt": "Laptop Computer", "phn": "Smart Phone"}
        )

        register = ProductChoices.register
        self.assertEqual(register.from_class(ProductChoices.LAPTOP), "lpt")
        self.assertEqual(register.from_key("lpt"), ProductChoices.LAPTOP)

        field_choices = Order._meta.get_field("product").choices
        self.assertEqual(
            dict(field_choices), {"lpt": "Laptop Computer", "phn": "Smart Phone"}
        )

        field = DRFRegisterField(
            register=ProductChoices.register, keys=["name", "pretty_name", "price"]
        )

        representation = field.to_representation(ProductChoices.LAPTOP)
        expected = {"name": "lpt", "pretty_name": "Laptop Computer", "price": 999.99}
        self.assertEqual(representation, expected)
