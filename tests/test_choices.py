# Django
from django.test import TestCase

# django_register
from tests.models import CountryChoices


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
