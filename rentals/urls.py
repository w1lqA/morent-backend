from django.urls import path
from .views import (
    StartRentalView, EndRentalView, RentalHistoryView,
    RentalDetailView, PricingDemoView
)

urlpatterns = [
    path('start', StartRentalView.as_view(), name='start_rental'),
    path('end', EndRentalView.as_view(), name='end_rental'),
    path('history', RentalHistoryView.as_view(), name='rental_history'),
    path('<int:rental_id>', RentalDetailView.as_view(), name='rental_detail'),
    path('pricing/demo', PricingDemoView.as_view(), name='pricing_demo'),
]