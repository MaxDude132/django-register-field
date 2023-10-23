# Django
from dataclasses import dataclass
from django.db import models

from django_register import RegisterChoices, RegisterField


@dataclass(hash=True)
class CountryInfo:
    population: int
    capital: str


class CountryChoices(RegisterChoices):
    CANADA = CountryInfo(population=37_742_154, capital="Ottawa")
    FRANCE = CountryInfo(population=65_273_511, capital="Paris")
    GERMANY = CountryInfo(population=83_783_942, capital="Berlin")
    UNITED_STATES = CountryInfo(population=331_900_000, capital="Washington")


class City(models.Model):
    label = models.CharField(max_length=50)
    country = RegisterField(choices=CountryChoices.choices)
