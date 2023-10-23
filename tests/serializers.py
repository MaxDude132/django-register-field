# Rest Framework
from rest_framework import serializers

# drf-serializer-prefetch
from django_register.rest_framework import RegisterField
from tests.models import City


class CitySerializer(serializers.ModelSerializer):
    country = RegisterField()

    class Meta:
        model = City
        fields = ("label", "country")
