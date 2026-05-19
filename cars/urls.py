from django.urls import path
from .views import (
    NearestCarsView, CarListView, CarDetailView,
    CarCategoriesView, CarIteratorView, CarsInRadiusView,
    CategoryAdapterView, LicenseCategoryAdapterView, RentalFacadeView
)

urlpatterns = [
    path('nearest', NearestCarsView.as_view(), name='nearest_cars'),
    path('nearest/radius', CarsInRadiusView.as_view(), name='cars_in_radius'),
    path('list', CarListView.as_view(), name='car_list'),
    path('<int:car_id>', CarDetailView.as_view(), name='car_detail'),
    path('categories', CarCategoriesView.as_view(), name='car_categories'),
    path('iterator-demo', CarIteratorView.as_view(), name='iterator_demo'),
    path('category-adapter', CategoryAdapterView.as_view(), name='category_adapter'),
    path('license-adapter', LicenseCategoryAdapterView.as_view(), name='license_adapter'),
    path('rental-facade', RentalFacadeView.as_view(), name='rental_facade'),
]