from django.urls import path
from . import views
from .views import create_wishlist

urlpatterns = [
    path("wishlist/create/", create_wishlist),
    path('users/create/', views.create_user, name='create_user'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('books/create/', views.add_book, name='add_book'),
    path('cart/<int:userId>/items/', views.get_cart_items, name='get_cart_items'),
    path('cart/<int:userId>/subtotal/', views.get_cart_subtotal, name='get_cart_subtotal'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
]
