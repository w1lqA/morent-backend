from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'phone', 'role', 'verification_status', 'license_category')
    list_filter = ('role', 'verification_status', 'license_category')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('личная информация', {'fields': ('first_name', 'last_name', 'phone')}),
        ('документы', {'fields': ('passport_series', 'passport_number', 'passport_issued_by',
                                   'passport_expiry_date', 'driving_license_number',
                                   'driving_license_category', 'driving_license_expiry_date')}),
        ('категория прав', {'fields': ('license_category',)}),
        ('текущее расположение', {'fields': ('current_latitude', 'current_longitude')}),
        ('права и верификация', {'fields': ('role', 'verification_status', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'role', 'license_category')}
        ),
    )
    search_fields = ('email', 'phone')
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)