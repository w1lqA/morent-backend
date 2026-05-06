from django.contrib import admin
from .models import Rental

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'car', 'start_time', 'end_time', 'total_price', 'status')
    list_filter = ('status',)
    search_fields = ('user__email', 'car__plate_number')