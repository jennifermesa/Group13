from django.urls import path
from . import views
from .views import create_wishlist

urlpatterns = [
    path("wishlist/create/", create_wishlist),
    path("wishlist/add-book/", views.add_book_to_wishlist, name="add_book_to_wishlist"),
    path('users/create/', views.create_user, name='create_user'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('books/create/', views.add_book, name='add_book'),
    path("books/top-sellers/", views.top_sellers, name="top_sellers"),
    path("books/rating/<str:minRating>/", views.books_by_rating, name="books_by_rating"),
    path("books/discount/", views.discount_books, name="discount_books"),
    path("comments/create/", views.create_comment, name="create_comment"),
    path("books/<int:book_id>/comments/", views.get_book_comments, name="get_book_comments"),
    path("books/<int:book_id>/average-rating/", views.get_average_rating, name="average_rating"),
    path('cart/<int:userId>/items/', views.get_cart_items),
    path('cart/<int:userId>/subtotal/', views.get_cart_subtotal),
    path('cart/remove/', views.remove_from_cart),
    path('cart/<int:userId>/subtotal/', views.get_cart_subtotal),
]
