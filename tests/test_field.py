# Django
from django.test import TestCase

# django_register
from django_register.base import RegisterField
from tests.models import City, CountryChoices


class RegisterFieldTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.paris = City.objects.create(label="Paris", country=CountryChoices.FRANCE)
        cls.berlin = City.objects.create(label="Berlin", country=CountryChoices.GERMANY)

    def test_can_retrieve_obj(self):
        self.assertEqual(self.paris.country, CountryChoices.FRANCE)

    def test_field_errors(self):
        with self.assertRaises(
            ValueError, msg="You must provide choices to the RegisterField."
        ) as exc:
            RegisterField()
            self.assertEqual(
                exc.exception.args[0], "You must provide choices to the RegisterField."
            )

        with self.assertRaises(
            ValueError, msg="Choices must be a RegisterChoices instance."
        ):
            RegisterField(choices=["a", "b", "c"])

        RegisterField(register=CountryChoices.register)

    def test_filter(self):
        self.assertEqual(City.objects.filter(country=CountryChoices.FRANCE).count(), 1)
        self.assertEqual(City.objects.filter(country=CountryChoices.GERMANY).count(), 1)

        self.assertEqual(
            City.objects.filter(country=CountryChoices.FRANCE).first(), self.paris
        )
        self.assertEqual(
            City.objects.filter(country=CountryChoices.FRANCE).first().country,
            self.paris.country,
        )
