from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),  # Zmieniono na user_login
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout_view, name='logout'), 
    path('profile/', views.profile, name='profile'),
    path('orders/', views.my_orders, name='my_orders')

]