# Django
from django.forms import ValidationError
from django.test import TestCase

# django_register
from django_register.base import Register, UnknownRegisterItem
from tests.models import CountryChoices, CountryInfo


class RegisterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.register: Register = CountryChoices.register

    def test_can_retrieve_obj(self):
        country_info = CountryInfo(1, capital="Max City")
        with self.assertRaises(ValueError):
            self.register.register(country_info)

        country_info.label = "max_country"
        self.register.register(country_info)

        self.assertEqual(self.register.get_class("max_country"), country_info)
        self.assertEqual(self.register.get_class(country_info), country_info)
        self.assertEqual(self.register.get_key(country_info), "max_country")
        self.assertEqual(self.register.get_key("max_country"), "max_country")

        country_info = CountryInfo(3_000_000_000, capital="Max Capital")
        self.register.register(country_info, db_key="max_big_country")

        self.assertEqual(self.register.get_class("max_big_country"), country_info)
        self.assertEqual(self.register.get_key(country_info), "max_big_country")

    def test_iter(self):
        for klass in self.register:
            self.assertIn(klass, CountryChoices)

    def test_cannot_register_twice(self):
        with self.assertRaises(ValueError):
            self.register.register(CountryChoices.CANADA, db_key="max_big_country")

        with self.assertRaises(ValueError):
            self.register.register(
                CountryInfo(population=2, capital="Some capital"),
                db_key="canada",
            )

    def test_unknown_key(self):
        with self.assertWarns(UserWarning):
            obj = self.register.get_class("unknown")
        self.assertIsInstance(obj, UnknownRegisterItem)

        with self.assertRaises(ValidationError):
            self.register.get_key(CountryInfo(12, capital="Max Capital"))

        class OtherUnknownItem:
            label: str
            description: str = ""

        self.register.unknown_item_class = OtherUnknownItem
        with self.assertWarns(UserWarning):
            obj = self.register.get_class("unknown")
        self.assertIsInstance(obj, OtherUnknownItem)
