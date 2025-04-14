from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cars import views
from users import views as user_views
from orders import views as orders_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cars/', include('cars.urls')),  # Dodaj ścieżki samochodów
    path('contact/', views.contact, name='contact'),
    path('car/<int:car_id>/', views.car, name='car_detail'),
    path('', views.index, name='index'),
    # Aliasy do logowania i rejestracji
    path('login/', user_views.user_login, name='login'),
    path('register/', user_views.register, name='register'),
    path('users/', include('users.urls')),  # Obsługuje logowanie/wylogowanie
    # Ścieżka koszyka:
    path('cart/', orders_views.cart, name='cart'),  # Zmieniamy cars.views.cart na orders_views.cart
    path('orders/', include('orders.urls')),
]

# Dodajemy ścieżki do obsługi plików multimedialnych
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
