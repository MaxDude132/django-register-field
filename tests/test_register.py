from django.test import TestCase
from django_register.base import Register

from tests.models import CountryChoices, CountryInfo


class RegisterFieldTestCase(TestCase):
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
        self.register.register(country_info, db_key="max_powerful_country")

        self.assertEqual(self.register.get_class("max_powerful_country"), country_info)
        self.assertEqual(self.register.get_key(country_info), "max_powerful_country")