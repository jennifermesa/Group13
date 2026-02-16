from django.urls import path
from .views import create_wishlist

urlpatterns = [
    path("wishlist/create/", create_wishlist), path('users/create/', views.create_user, name='create_user')
]
