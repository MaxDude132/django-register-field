from django.test import TestCase

from tests.models import City, CountryChoices


class RegisterFieldTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.paris = City.objects.create(label="Paris", country=CountryChoices.FRANCE)

    def test_can_retrieve_obj(self):
        self.assertEqual(self.paris.country, CountryChoices.FRANCE)
