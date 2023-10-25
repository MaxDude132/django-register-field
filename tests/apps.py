# Django
from django.apps import AppConfig


class TestsConfig(AppConfig):
    name = "tests"

    def ready(self):
        from .models import cars_register, CarCompanies

        cars_register.register(CarCompanies("Toyota"), db_key="toyota")
