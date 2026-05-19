from rest_framework import serializers
from .models import Car, Location, CarTag, CarImage


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("широта должна быть между -90 и 90")
        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("долгота должна быть между -180 и 180")
        return value


class CarTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarTag
        fields = ['id', 'name']


class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image', 'is_main', 'order']


class CarListSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    tags = CarTagSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    required_license_display = serializers.CharField(source='get_required_license_display', read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'brand', 'model', 'year', 'plate_number', 'tags', 'capacity',
                  'steering', 'gasoline', 'status', 'price_per_minute', 'location',
                  'main_image', 'required_license', 'required_license_display']

    def get_main_image(self, obj):
        main_img = obj.images.filter(is_main=True).first()
        if main_img:
            return main_img.image.url
        first_img = obj.images.first()
        if first_img:
            return first_img.image.url
        return None


class CarDetailSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    tags = CarTagSerializer(many=True, read_only=True)
    images = CarImageSerializer(many=True, read_only=True)
    required_license_display = serializers.CharField(source='get_required_license_display', read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'brand', 'model', 'year', 'plate_number', 'tags', 'capacity',
                  'steering', 'gasoline', 'description', 'status', 'price_per_minute',
                  'location', 'images', 'required_license', 'required_license_display']

    def validate_plate_number(self, value):
        if len(value) < 6 or len(value) > 9:
            raise serializers.ValidationError("номер должен содержать 6-9 символов")
        return value

    def validate_year(self, value):
        from datetime import datetime
        current_year = datetime.now().year
        if value < 1990 or value > current_year + 1:
            raise serializers.ValidationError(f"год выпуска должен быть между 1990 и {current_year + 1}")
        return value

    def validate_price_per_minute(self, value):
        if value <= 0:
            raise serializers.ValidationError("цена за минуту должна быть больше 0")
        return value


class NearestCarSerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    radius = serializers.FloatField(min_value=0.1, max_value=50, default=5)
    limit = serializers.IntegerField(min_value=1, max_value=50, default=10)