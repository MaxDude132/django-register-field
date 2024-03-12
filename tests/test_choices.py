# Django
from django.test import TestCase
from django_register import RegisterChoices

# django_register
from tests.models import CountryChoices, CountryInfo


class ChoicesTestCase(TestCase):
    def test_iter(self):
        for klass in CountryChoices:
            self.assertIn(klass, CountryChoices)

    def test_choices(self):
        self.assertEqual(
            CountryChoices.choices,
            [
                ("canada", "Canada"),
                ("france", "France"),
                ("germany", "Germany"),
                ("united_states", "United States"),
            ],
        )

    def test_build_choice(self):
        self.assertEqual(CountryChoices("canada"), CountryChoices.CANADA)
        self.assertEqual(CountryChoices(CountryChoices.CANADA), CountryChoices.CANADA)

    def test_register_choices(self):
        self.assertEqual(
            CountryChoices.register.choices,
            [
                ("canada", "Canada"),
                ("france", "France"),
                ("germany", "Germany"),
                ("united_states", "United States"),
            ],
        )

    def test_register_unknown_option(self):
        class UnknownOption:
            label: str
            description: str = ""

        class CountryChoices(RegisterChoices):
            _UNKNOWN_ = UnknownOption
            CANADA = CountryInfo("canada", "Canada")

        self.assertEqual(
            CountryChoices.register.unknown_item_class,
            UnknownOption,
        )
