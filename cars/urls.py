from django.urls import path
from .views import (
    NearestCarsView, CarListView, CarDetailView,
    CarCategoriesView, CarIteratorView
)

urlpatterns = [
    path('nearest', NearestCarsView.as_view(), name='nearest_cars'),
    path('list', CarListView.as_view(), name='car_list'),
    path('<int:car_id>', CarDetailView.as_view(), name='car_detail'),
    path('categories', CarCategoriesView.as_view(), name='car_categories'),
    path('iterator-demo', CarIteratorView.as_view(), name='iterator_demo'),
]