from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cars import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cars/', include('cars.urls')),
    path('contact/', views.contact, name='contact'),
    path('car/<int:car_id>/', views.car, name='car_detail'),
    path('', views.index, name='index'),
    path('users/', include('users.urls')),
]

# Dodajemy ścieżki do obsługi plików multimedialnych
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
