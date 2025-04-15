from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cars import views
from users import views as user_views
from orders import views as orders_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cars/', include('cars.urls')),  # Dodaj ścieżki samochodów z cars/urls.py
    path('', views.index, name='index'),  # Dodaj ścieżkę do strony głównej
    # Aliasy do logowania i rejestracji
    path('login/', user_views.user_login, name='login'),
    path('register/', user_views.register, name='register'),
    path('users/', include('users.urls')),  # Obsługuje logowanie/wylogowanie
    # Ścieżka koszyka:
    path('cart/', orders_views.cart, name='cart'),  # Zmieniamy cars.views.cart na orders_views.cart
    path('orders/', include('orders.urls')),  # Obsługuje wszystkie ścieżki związane z zamówieniami
]

# Dodajemy ścieżki do obsługi plików multimedialnych
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
