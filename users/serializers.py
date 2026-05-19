from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_verified = serializers.BooleanField(read_only=True)
    license_category_display = serializers.CharField(source='get_license_category_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'first_name', 'last_name',
                  'role', 'verification_status', 'is_verified', 'license_category', 'license_category_display']
        read_only_fields = ['id', 'role', 'verification_status', 'is_verified']


class DocumentUploadSerializer(serializers.Serializer):
    passport_series = serializers.CharField(max_length=4, min_length=4, required=False, allow_null=True)
    passport_number = serializers.CharField(max_length=6, min_length=6, required=False, allow_null=True)
    passport_issued_by = serializers.CharField(max_length=255, required=False, allow_null=True)
    passport_expiry_date = serializers.DateField(required=False, allow_null=True)
    driving_license_number = serializers.CharField(min_length=10, max_length=20, required=False, allow_null=True)
    driving_license_category = serializers.CharField(max_length=10, required=False, allow_null=True)
    driving_license_expiry_date = serializers.DateField(required=False, allow_null=True)

    def validate_passport_series(self, value):
        if value and len(str(value)) != 4:
            raise serializers.ValidationError("серия паспорта должна содержать 4 символа")
        return value

    def validate_passport_number(self, value):
        if value and len(str(value)) != 6:
            raise serializers.ValidationError("номер паспорта должен содержать 6 символов")
        return value

    def validate_driving_license_number(self, value):
        if value and (len(str(value)) < 10 or len(str(value)) > 12):
            raise serializers.ValidationError("номер водительского удостоверения должен содержать 10-12 символов")
        return value