# Django
from django.contrib import admin
from django.test import TestCase

# django_register
from tests.models import City, ContinentChoices


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


class AdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.city = City.objects.create(label="Ottawa")

    def setUp(self):
        self.admin = CityAdmin(City, admin.site)

    def test_admin_choices(self):
        # choices was renamed to _choices in Django 5.0
        choices = getattr(
            self.admin.opts._forward_fields_map["available_food"],
            "choices",
        ) or getattr(
            self.admin.opts._forward_fields_map["available_food"], "_choices", None
        )
        self.assertEqual(
            choices,
            [("pizza", "Pizza")],
        )

    def test_admin_select(self):
        field = self.admin.opts._forward_fields_map["continent"]
        cleaned_value = field.clean("America", self.city)
        self.assertEqual(cleaned_value, ContinentChoices.AMERICA)

    def test_admin_flatchoices(self):
        field = self.admin.opts._forward_fields_map["continent"]
        self.assertEqual(
            field.flatchoices,
            [
                (ContinentChoices.AMERICA, "America"),
                (ContinentChoices.EUROPE, "Europe"),
            ],
        )
