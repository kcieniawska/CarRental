from django.urls import path
from . import views

app_name = 'orders'  # Przestrzeń nazw

urlpatterns = [
    path('add_to_cart/<int:car_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('remove_from_cart/<int:car_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_rental_days/<int:car_id>/', views.update_rental_days, name='update_rental_days'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('cars/<int:car_id>/add_review/', views.add_review, name='add_review'),
    path('moderate_reviews/', views.moderate_reviews, name='moderate_reviews'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('summary/', views.summary, name='summary'),
    path('complete-order/', views.complete_order, name='complete_order'),  # To jest nasz nowy URL
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('process_payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('complete-order/success/<int:order_id>/', views.complete_order_success, name='complete_order_success'),
    path('review/add/<int:car_id>/', views.add_review, name='add_review'),
    path('moderator/opinie/', views.moderate_reviews_view, name='moderate_reviews'),
    path('moderator/opinia/<int:review_id>/zatwierdz/', views.approve_review, name='approve_review'),
    path('moderator/opinie/usun/<int:review_id>/', views.delete_review, name='delete_review'),
    
]