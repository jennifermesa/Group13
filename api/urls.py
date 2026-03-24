from django.urls import path
from . import views
from .views import create_wishlist

urlpatterns = [
    path("wishlist/create/", create_wishlist),
    path("wishlist/add-book/", views.add_book_to_wishlist, name="add_book_to_wishlist"),
    path("wishlist/<int:wishlistId>/items/", views.get_wishlist_items, name="get_wishlist_items"),
    path("wishlist/<int:wishlistId>/move-to-cart/", views.move_wishlist_item_to_cart, name="move_wishlist_item_to_cart"),
    path('users/create/', views.create_user, name='create_user'),
    path('users/credit-card/', views.add_credit_card, name='add_credit_card'),
    path('users/<str:username>/', views.get_user_by_username, name='get_user_by_username'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('books/create/', views.add_book, name='add_book'),
    path("books/top-sellers/", views.top_sellers, name="top_sellers"),
    path("books/rating/<str:minRating>/", views.books_by_rating, name="books_by_rating"),
    path("books/discount/", views.discount_books, name="discount_books"),
    path("books/genre/<str:genre>/", views.books_by_genre, name="books_by_genre"),
    path("comments/create/", views.create_comment, name="create_comment"),
    path("books/<int:book_id>/comments/", views.get_book_comments, name="get_book_comments"),
    path("books/<int:book_id>/average-rating/", views.get_average_rating, name="average_rating"),
    path("ratings/add/", views.add_rating, name="add_rating"),
    path('cart/<int:userId>/items/', views.get_cart_items),
    path('cart/<int:userId>/subtotal/', views.get_cart_subtotal),
    path('cart/remove/', views.remove_from_cart),
    path('books/isbn/<str:isbn>/', get_book_by_isbn),
    path('authors/create/', create_author),
    path('authors/<int:authorId>/books/', get_books_by_author),
]

