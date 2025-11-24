import warnings

from django.test import TestCase

from django_register.base import Register, RegisterField, UnknownRegisterItem
from tests.models import City, CountryChoices


class MigrationTestCase(TestCase):
    def test_register_deconstruct(self):
        register = CountryChoices.register
        _path, args, kwargs = register.deconstruct()
        new_register = Register(*args, **kwargs)

        self.assertEqual(
            len(new_register._migration_keys),
            len(register._key_to_class),
            f"Expected {len(register._key_to_class)} migration keys, "
            f"but got {len(new_register._migration_keys)}",
        )
        self.assertEqual(
            new_register._migration_keys, set(register._key_to_class.keys())
        )

    def test_register_field_deconstruct(self):
        field = City._meta.get_field("country")
        _name, _path, _args, kwargs = field.deconstruct()

        self.assertIn("register", kwargs)

        register = kwargs["register"]
        _reg_path, _reg_args, reg_kwargs = register.deconstruct()

        self.assertIn("_migration_keys", reg_kwargs)
        self.assertGreater(
            len(reg_kwargs["_migration_keys"]),
            0,
            "Register deconstruct should include migration keys",
        )

    def test_migration_with_existing_data(self):
        original_register = CountryChoices.register
        _reg_path, reg_args, reg_kwargs = original_register.deconstruct()
        migration_register = Register(*reg_args, **reg_kwargs)
        new_field = RegisterField(register=migration_register, max_length=13)
        db_value = "france"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            python_value = new_field.to_python(db_value)

            self.assertEqual(
                len(w),
                0,
                f"Expected no warnings but got: {[str(warning.message) for warning in w]}",
            )

        self.assertIsInstance(python_value, UnknownRegisterItem)
        self.assertEqual(python_value.key, "france")

    def test_migration_handles_all_registered_keys(self):
        original_register = CountryChoices.register
        _reg_path, reg_args, reg_kwargs = original_register.deconstruct()
        migration_register = Register(*reg_args, **reg_kwargs)

        original_keys = set(original_register._key_to_class.keys())
        migration_keys = migration_register._migration_keys

        self.assertEqual(original_keys, migration_keys)

    def test_data_migration_example(self):
        City.objects.create(name="Toronto", country=CountryChoices.CANADA)
        City.objects.create(name="Vancouver", country=CountryChoices.CANADA)
        City.objects.create(name="Montreal", country=CountryChoices.CANADA)

        def migrate_canadian_cities_to_usa(apps, schema_editor):
            for city in City.objects.filter(country="canada"):
                city.country = "united_states"
                city.save()

        migrate_canadian_cities_to_usa(None, None)

        canadian_cities = City.objects.filter(country=CountryChoices.CANADA)
        us_cities = City.objects.filter(country=CountryChoices.UNITED_STATES)

        self.assertEqual(canadian_cities.count(), 0)
        self.assertEqual(us_cities.count(), 3)

        for city in City.objects.all():
            self.assertEqual(city.country, CountryChoices.UNITED_STATES)

    def test_migration_with_removed_choices(self):
        from dataclasses import dataclass
        from django.db import connection

        @dataclass(unsafe_hash=True)
        class OldCountryInfo:
            population: int
            capital: str

        old_register = Register()
        old_register.register(
            OldCountryInfo(population=37_742_154, capital="Ottawa"), db_key="canada"
        )
        old_register.register(
            OldCountryInfo(population=65_273_511, capital="Paris"), db_key="france"
        )
        old_register.register(
            OldCountryInfo(population=100_000_000, capital="London"), db_key="uk"
        )
        old_register.register(
            OldCountryInfo(population=50_000_000, capital="Rome"), db_key="italy"
        )

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tests_city (name, country) VALUES (?, ?)",
                ["London", "uk"],
            )
            cursor.execute(
                "INSERT INTO tests_city (name, country) VALUES (?, ?)",
                ["Rome", "italy"],
            )
            cursor.execute(
                "INSERT INTO tests_city (name, country) VALUES (?, ?)",
                ["Paris", "france"],
            )

        _path, args, kwargs = old_register.deconstruct()
        old_migration_register = Register(*args, **kwargs)

        self.assertIn("uk", old_migration_register._migration_keys)
        self.assertIn("italy", old_migration_register._migration_keys)

        def migrate_removed_countries(apps, schema_editor):
            mapping = {"uk": "germany", "italy": "france"}

            with schema_editor.connection.cursor() as cursor:
                for old_key, new_key in mapping.items():
                    cursor.execute(
                        "UPDATE tests_city SET country = %s WHERE country = %s",
                        [new_key, old_key],
                    )

        from django.db import connection
        from django.db.backends.base.schema import BaseDatabaseSchemaEditor

        migrate_removed_countries(None, BaseDatabaseSchemaEditor(connection))

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM tests_city WHERE country IN (%s, %s)",
                ["uk", "italy"],
            )
            old_count = cursor.fetchone()[0]

        self.assertEqual(old_count, 0)
        self.assertEqual(City.objects.filter(country=CountryChoices.GERMANY).count(), 1)
        self.assertEqual(City.objects.filter(country=CountryChoices.FRANCE).count(), 2)

        london = City.objects.get(name="London")
        rome = City.objects.get(name="Rome")
        paris = City.objects.get(name="Paris")

        self.assertEqual(london.country, CountryChoices.GERMANY)
        self.assertEqual(rome.country, CountryChoices.FRANCE)
        self.assertEqual(paris.country, CountryChoices.FRANCE)

    def test_migration_with_renamed_choices(self):
        from dataclasses import dataclass
        from django.db import connection

        @dataclass(unsafe_hash=True)
        class StateInfo:
            abbreviation: str

        old_register = Register()
        old_register.register(StateInfo(abbreviation="CA"), db_key="california")
        old_register.register(StateInfo(abbreviation="TX"), db_key="texas")
        old_register.register(StateInfo(abbreviation="NY"), db_key="new_york")

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tests_city (name, country) VALUES (?, ?)",
                ["Los Angeles", "california"],
            )
            cursor.execute(
                "INSERT INTO tests_city (name, country) VALUES (?, ?)",
                ["Houston", "texas"],
            )
            cursor.execute(
                "INSERT INTO tests_city (name, country) VALUES (?, ?)",
                ["New York City", "new_york"],
            )

        new_register = Register()
        new_register.register(StateInfo(abbreviation="CA"), db_key="ca_state")
        new_register.register(StateInfo(abbreviation="TX"), db_key="tx_state")
        new_register.register(StateInfo(abbreviation="NY"), db_key="ny_state")

        def migrate_renamed_choices(apps, schema_editor):
            mapping = {
                "california": "ca_state",
                "texas": "tx_state",
                "new_york": "ny_state",
            }

            with schema_editor.connection.cursor() as cursor:
                for old_key, new_key in mapping.items():
                    cursor.execute(
                        "UPDATE tests_city SET country = %s WHERE country = %s",
                        [new_key, old_key],
                    )

        from django.db import connection
        from django.db.backends.base.schema import BaseDatabaseSchemaEditor

        migrate_renamed_choices(None, BaseDatabaseSchemaEditor(connection))

        old_keys = ["california", "texas", "new_york"]
        new_keys = ["ca_state", "tx_state", "ny_state"]

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM tests_city WHERE country IN (%s, %s, %s)",
                old_keys,
            )
            old_count = cursor.fetchone()[0]
            cursor.execute(
                "SELECT COUNT(*) FROM tests_city WHERE country IN (%s, %s, %s)",
                new_keys,
            )
            new_count = cursor.fetchone()[0]

        self.assertEqual(old_count, 0)
        self.assertEqual(new_count, 3)

        la = City.objects.get(name="Los Angeles")
        self.assertIsInstance(la.country, UnknownRegisterItem)
        self.assertEqual(la.country.key, "ca_state")
