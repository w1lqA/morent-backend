from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'phone', 'role', 'verification_status')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Documents', {'fields': ('passport_series', 'passport_number', 'passport_issued_by',
                                   'passport_expiry_date', 'driving_license_number',
                                   'driving_license_category', 'driving_license_expiry_date')}),
        ('Permissions', {'fields': ('role', 'verification_status', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'role')}
        ),
    )
    search_fields = ('email', 'phone')
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)