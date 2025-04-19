from django.urls import path
from . import views
app_name = 'users'  # Przestrzeń nazw
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),  # Zmieniono na user_login
    path('logout/', views.logout_view, name='logout'), 
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('orders/<int:order_id>/', views.user_orders, name='user_orders'),
    path('orders/<int:order_id>/add_review/', views.add_review, name='add_review'),

]