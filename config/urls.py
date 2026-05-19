from django.contrib import admin
from django.urls import path, include
from core.views import SingletonDemoView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/cars/', include('cars.urls')),
    path('api/rentals/', include('rentals.urls')),
    path('api/demo/singleton', SingletonDemoView.as_view(), name='singleton_demo'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)