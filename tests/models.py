# Standard libraries
from dataclasses import dataclass

# Django
from django.db import models

# django_register
from django_register import RegisterChoices, RegisterField


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


class ContinentChoices(RegisterChoices):
    AMERICA = ContinentInfo(label="America")
    EUROPE = ContinentInfo(label="Europe")


class City(models.Model):
    label = models.CharField(max_length=50)
    country = RegisterField(choices=CountryChoices.choices)
    continent = RegisterField(choices=ContinentChoices.choices, null=True, blank=True)
