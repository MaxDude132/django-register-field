from django.test import TestCase
from django_register.rest_framework import RegisterField

from tests.models import City, CountryChoices

from rest_framework import serializers


class CitySerialier(serializers.ModelSerializer):
    country = RegisterField()

    class Meta:
        model = City
        fields = ("label", "country")


class RegisterSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.paris = City.objects.create(label="Paris", country=CountryChoices.FRANCE)

    def test_serialization(self):
        serializer = CitySerialier(self.paris)
        self.assertEqual(serializer.data, {"label": "Paris", "country": "france"})
