# Django
from django.test import TestCase

# Rest Framework
from rest_framework import serializers

# django_register
from django_register.rest_framework import RegisterField
from tests.models import City, CountryChoices


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
