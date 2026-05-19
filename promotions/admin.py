from django.contrib import admin
from .models import Subscription, UserSubscription, Promotion, Insurance

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_percent')

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription', 'start_date', 'end_date')

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percent', 'start_date', 'end_date')

@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ('rental', 'insurance_type', 'price', 'is_active', 'created_at')
    list_filter = ('insurance_type', 'is_active')
    search_fields = ('rental__id',)