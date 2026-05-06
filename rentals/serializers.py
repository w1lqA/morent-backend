from rest_framework import serializers
from .models import Rental
from cars.serializers import CarListSerializer
from users.serializers import UserSerializer


class RentalSerializer(serializers.ModelSerializer):
    car_details = CarListSerializer(source='car', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Rental
        fields = ['id', 'user', 'car', 'car_details', 'user_details',
                  'start_time', 'end_time', 'total_price', 'status']
        read_only_fields = ['id', 'start_time', 'total_price']


class StartRentalSerializer(serializers.Serializer):
    car_id = serializers.IntegerField(min_value=1)
    services = serializers.ListField(
        child=serializers.ChoiceField(choices=['insurance', 'child_seat', 'additional_driver', 'gps']),
        required=False,
        default=[]
    )


class EndRentalSerializer(serializers.Serializer):
    rental_id = serializers.IntegerField(min_value=1)
    end_latitude = serializers.FloatField(min_value=-90, max_value=90)
    end_longitude = serializers.FloatField(min_value=-180, max_value=180)