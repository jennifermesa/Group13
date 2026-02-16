from django.urls import path
from . import views
from .views import create_wishlist

urlpatterns = [
    path("wishlist/create/", create_wishlist), 
    path('users/create/', views.create_user, name='create_user'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('books/create/', views.add_book, name='add_book'),
]
