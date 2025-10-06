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
        fields = ("name", "country")


class RegisterSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.paris = City.objects.create(name="Paris", country=CountryChoices.FRANCE)

    def test_serialization(self):
        serializer = CitySerialier(self.paris)
        self.assertEqual(serializer.data, {"name": "Paris", "country": "france"})

    def test_serializer_wrong_value(self):
        serializer = CitySerialier(data={"name": "Paris", "country": "francis"})
        with self.assertWarns(UserWarning):
            self.assertFalse(serializer.is_valid())
        self.assertIn("country", serializer.errors)

    def test_save(self):
        serializer = CitySerialier(
            data={"name": "Paris", "country": CountryChoices.FRANCE}
        )

        self.assertTrue(serializer.is_valid())
        city = serializer.save()

        self.assertEqual(city.country, CountryChoices.FRANCE)

    def test_wrong_field_type(self):
        class CitySerialier(serializers.ModelSerializer):
            name = RegisterField()
            country = RegisterField()

            class Meta:
                model = City
                fields = ("name", "country")

        serializer = CitySerialier(self.paris)

        with self.assertRaises(ValueError):
            serializer.data

    def test_keys(self):
        class CitySerializer(serializers.ModelSerializer):
            country = RegisterField(keys=["key", "label", "capital"])

            class Meta:
                model = City
                fields = ("name", "country")

        serializer = CitySerializer(self.paris)
        self.assertEqual(
            serializer.data,
            {
                "name": "Paris",
                "country": {
                    "key": "france",
                    "label": "France",
                    "capital": "Paris",
                },
            },
        )
