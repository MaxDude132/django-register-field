# Django
from django.contrib import admin
from django.test import TestCase

# django_register
from tests.models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


class AdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.city = City.objects.create(label="Ottawa")

    def test_admin_choices(self):
        built_admin = CityAdmin(City, admin.site)

        # choices was renamed to _choices in Django 5.0
        choices = getattr(
            built_admin.opts._forward_fields_map["available_food"],
            "choices",
        ) or getattr(
            built_admin.opts._forward_fields_map["available_food"], "_choices", None
        )
        self.assertEqual(
            choices,
            [("pizza", "Pizza")],
        )
