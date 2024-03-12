# Django
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

# django_register
from django_register.base import RegisterField, UnknownRegisterItem
from tests.models import (
    CountryInfo,
    Neighborhood,
    cars_register,
    CarCompanies,
    City,
    CountryChoices,
)


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

    def test_default_value(self):
        city = City.objects.create(label="Ottawa")
        self.assertEqual(city.country, CountryChoices.UNITED_STATES)
        self.assertEqual(city._meta.get_field("country").default, "united_states")

    def test_set_wrong_default_value(self):
        City._meta.get_field("country").default = CountryInfo(12, capital="Max Capital")

        with self.assertRaises(ValidationError):
            City.objects.create(label="Ottawa")

    def test_fails_if_fetching_before_registering(self):
        with self.assertRaises(ValueError):
            cars_register.register(CarCompanies("Toyota"), db_key="toyota")

        hyundai_car = CarCompanies("Hyundai")

        with self.assertRaises(ValidationError):
            self.paris.car_companies = hyundai_car
            self.paris.save()

        cars_register.register(hyundai_car, db_key="hyundai")

        cars_register._class_to_key.pop(hyundai_car)
        cars_register._key_to_class.pop("hyundai")

    def test_changing_register_dynamically(self):
        with self.assertRaises(ValueError):
            cars_register.register(CarCompanies("Toyota"), db_key="toyota")

        hyundai_car = CarCompanies("Hyundai")
        cars_register.register(hyundai_car, db_key="hyundai")

        self.paris.car_companies = hyundai_car
        self.paris.save()
        self.assertEqual(self.paris.car_companies, hyundai_car)

        cars_register._class_to_key.pop(hyundai_car)
        cars_register._key_to_class.pop("hyundai")

    def test_annotations(self):
        Neighborhood.objects.create(label="Montparnasse", city=self.paris)

        neighborhood = Neighborhood.objects.annotate(
            country=models.F("city__country")
        ).first()

        self.assertNotEqual(
            neighborhood.country,
            "france",
        )
        self.assertEqual(
            neighborhood.country,
            CountryChoices.FRANCE,
        )

    def test_unknown_key(self):
        france = CountryChoices.FRANCE
        CountryChoices.register._key_to_class.pop("france")
        CountryChoices.register._class_to_key.pop(france)

        self.paris.refresh_from_db()
        self.assertIsInstance(self.paris.country, UnknownRegisterItem)

        class UnknownItem:
            label: str
            description: str = ""

        CountryChoices.register.unknown_item_class = UnknownItem
        self.paris.refresh_from_db()
        self.assertIsInstance(self.paris.country, UnknownItem)

        # Clean up
        CountryChoices.register.unknown_item_class = UnknownRegisterItem
        CountryChoices.register.register(france, db_key="france")
