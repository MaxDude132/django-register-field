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

    def test_serializer_wrong_value(self):
        serializer = CitySerialier(data={"label": "Paris", "country": "francis"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("country", serializer.errors)

    def test_save(self):
        serializer = CitySerialier(
            data={"label": "Paris", "country": CountryChoices.FRANCE}
        )

        self.assertTrue(serializer.is_valid())
        city = serializer.save()

        self.assertEqual(city.country, CountryChoices.FRANCE)

    def test_wrong_field_type(self):
        class CitySerialier(serializers.ModelSerializer):
            label = RegisterField()
            country = RegisterField()

            class Meta:
                model = City
                fields = ("label", "country")

        serializer = CitySerialier(self.paris)

        with self.assertRaises(ValueError):
            serializer.data

    def test_keys(self):
        class CitySerialier(serializers.ModelSerializer):
            country = RegisterField(keys=["label", "verbose_name", "capital"])

            class Meta:
                model = City
                fields = ("label", "country")

        serializer = CitySerialier(self.paris)
        self.assertEqual(
            serializer.data,
            {
                "label": "Paris",
                "country": {
                    "label": "france",
                    "verbose_name": "France",
                    "capital": "Paris",
                },
            },
        )
