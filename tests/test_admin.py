# Django
from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.views.main import ChangeList

# django_register
from tests.models import (
    City,
    ContinentChoices,
    ContinentInfo,
    Restaurant,
    CountryChoices,
)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "cuisine"]


class AdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.city = City.objects.create(name="Ottawa")

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

    def test_choices_gets_updated(self):
        field = self.admin.opts._forward_fields_map["continent"]
        attr = "choices" if hasattr(field, "choices") else "_choices"

        self.assertEqual(
            getattr(field, attr),
            [
                ("America", "America"),
                ("Europe", "Europe"),
            ],
        )

        register = ContinentChoices.register

        self.assertEqual(
            register.choices, [("America", "America"), ("Europe", "Europe")]
        )

        register.register(ContinentInfo(key="Asia"))

        field = self.admin.opts._forward_fields_map["continent"]

        self.assertEqual(
            register.choices,
            [("America", "America"), ("Europe", "Europe"), ("Asia", "Asia")],
        )
        self.assertEqual(
            getattr(field, attr),
            [
                ("America", "America"),
                ("Europe", "Europe"),
                ("Asia", "Asia"),
            ],
        )

    def test_admin_list_display_with_register_field(self):
        Restaurant.objects.create(name="Le Petit Bistro", country=CountryChoices.FRANCE)

        restaurant_admin = RestaurantAdmin(Restaurant, admin.site)

        request = RequestFactory().get("/admin/tests/restaurant/")
        request.user = User.objects.create_user("testuser", "test@test.com", "testpass")
        request.user.is_staff = True
        request.user.is_superuser = True
        request.user.save()

        changelist = ChangeList(
            request=request,
            model=Restaurant,
            list_display=restaurant_admin.list_display,
            list_display_links=restaurant_admin.list_display_links,
            list_filter=restaurant_admin.list_filter,
            date_hierarchy=restaurant_admin.date_hierarchy,
            search_fields=restaurant_admin.search_fields,
            list_select_related=restaurant_admin.list_select_related,
            list_per_page=restaurant_admin.list_per_page,
            list_max_show_all=restaurant_admin.list_max_show_all,
            list_editable=restaurant_admin.list_editable,
            model_admin=restaurant_admin,
            sortable_by=restaurant_admin.sortable_by,
            search_help_text=restaurant_admin.search_help_text,
        )

        results = list(changelist.result_list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Le Petit Bistro")
        self.assertEqual(results[0].country, CountryChoices.FRANCE)

    def test_admin_list_display_none_value(self):
        Restaurant.objects.create(
            name="Generic Restaurant", country=CountryChoices.CANADA
        )

        restaurant_admin = RestaurantAdmin(Restaurant, admin.site)
        request = RequestFactory().get("/admin/tests/restaurant/")
        request.user = User.objects.create_user(
            "testuser2", "test2@test.com", "testpass"
        )
        request.user.is_staff = True
        request.user.is_superuser = True
        request.user.save()

        from django.contrib.admin.views.main import ChangeList

        changelist = ChangeList(
            request=request,
            model=Restaurant,
            list_display=restaurant_admin.list_display,
            list_display_links=restaurant_admin.list_display_links,
            list_filter=restaurant_admin.list_filter,
            date_hierarchy=restaurant_admin.date_hierarchy,
            search_fields=restaurant_admin.search_fields,
            list_select_related=restaurant_admin.list_select_related,
            list_per_page=restaurant_admin.list_per_page,
            list_max_show_all=restaurant_admin.list_max_show_all,
            list_editable=restaurant_admin.list_editable,
            model_admin=restaurant_admin,
            sortable_by=restaurant_admin.sortable_by,
            search_help_text=restaurant_admin.search_help_text,
        )

        results = list(changelist.result_list)
        self.assertEqual(len(results), 1)
        self.assertIsNone(results[0].cuisine)
