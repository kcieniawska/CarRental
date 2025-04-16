from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Strona główna
    path('contact/', views.contact, name='contact'),
    path('car/<int:car_id>/', views.car, name='car_detail'),  # Strona szczegółów samochodu
    path('categories/', views.category_list, name='category_list'),
    path('categories/<str:category>/', views.category_view, name='category_detail'),
    path('car/<int:car_id>/', views.car, name='car'),
    path('<int:car_id>/add_review/', views.add_review, name='add_review'),  # Dodana ścieżka
     path('cars/', views.all_cars_view, name='all_cars')
]



# Dodajemy ścieżki do obsługi plików multimedialnych (np. zdjęć samochodów)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)