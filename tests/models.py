# Standard libraries
from dataclasses import dataclass

# Django
from django.db import models

# django_register
from django_register import Register, RegisterChoices, RegisterField


@dataclass(unsafe_hash=True)
class CountryInfo:
    population: int
    capital: str


class CountryChoices(RegisterChoices):
    CANADA = CountryInfo(population=37_742_154, capital="Ottawa")
    FRANCE = CountryInfo(population=65_273_511, capital="Paris")
    GERMANY = CountryInfo(population=83_783_942, capital="Berlin")
    UNITED_STATES = CountryInfo(population=331_900_000, capital="Washington")


@dataclass(unsafe_hash=True)
class ContinentInfo:
    label: str


@dataclass(unsafe_hash=True)
class FoodInfo:
    verbose_name: str


food_register = Register()
food_register.register(FoodInfo("Pizza"), db_key="pizza")


@dataclass(unsafe_hash=True)
class CarCompanies:
    verbose_name: str


cars_register = Register()


class ContinentChoices(RegisterChoices):
    AMERICA = ContinentInfo(label="America")
    EUROPE = ContinentInfo(label="Europe")


class City(models.Model):
    label = models.CharField(max_length=50)
    country = RegisterField(
        choices=CountryChoices, default=CountryChoices.UNITED_STATES
    )
    continent = RegisterField(choices=ContinentChoices, null=True, blank=True)
    available_food = RegisterField(register=food_register, null=True, blank=True)
    car_companies = RegisterField(
        register=cars_register, null=True, blank=True, max_length=50
    )


class Neighborhood(models.Model):
    label = models.CharField(max_length=50)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
