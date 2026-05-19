from django.contrib import admin
from .models import Car, Location, CarTag, CarTagMap

class CarTagMapInline(admin.TabularInline):
    model = CarTagMap
    extra = 1
    autocomplete_fields = ['tag']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'plate_number', 'status', 'price_per_minute', 'required_license', 'capacity')
    list_filter = ('status', 'brand', 'required_license', 'steering')
    search_fields = ('brand', 'model', 'plate_number')
    inlines = [CarTagMapInline]
    fieldsets = (
        (None, {
            'fields': ('brand', 'model', 'year', 'plate_number', 'status', 'price_per_minute', 'location')
        }),
        ('характеристики', {
            'fields': ('capacity', 'steering', 'gasoline', 'required_license')
        }),
        ('описание', {
            'fields': ('description',)
        }),
    )

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'street', 'house_number')
    search_fields = ('city', 'street')

@admin.register(CarTag)
class CarTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(CarTagMap)
class CarTagMapAdmin(admin.ModelAdmin):
    list_display = ('car', 'tag')
    autocomplete_fields = ['car', 'tag']
    search_fields = ('car__brand', 'car__model', 'tag__name')