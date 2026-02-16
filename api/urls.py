from django.urls import path
from .views import create_wishlist, books_by_genre

urlpatterns = [
    path("wishlist/create/", create_wishlist),
    path("books/genre/<str:genre>/", books_by_genre),
]
