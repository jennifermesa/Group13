from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# from .models import Wishlist, User, Book, CartItem
# from .models import Comment, Rating
from .models import Wishlist, User, Book, CartItem, Comment, Rating, WishlistItem,Author

@csrf_exempt
def create_wishlist(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = data.get("userId")
    name = data.get("name")

    if not user_id or not name:
        return JsonResponse({"error": "userId and name are required"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if Wishlist.objects.filter(user=user).count() >= 3:
        return JsonResponse({"error": "A user can only have 3 wishlists"}, status=400)

    if Wishlist.objects.filter(user=user, name=name).exists():
        return JsonResponse({"error": "Wishlist name must be unique for this user"}, status=400)

    wishlist = Wishlist.objects.create(user=user, name=name)

    return JsonResponse(
        {"message": "Wishlist created", "wishlistId": wishlist.id},
        status=201
    )

@csrf_exempt
def create_user(request):
    data = json.loads(request.body)
    user = User.objects.create(
        username=data['username'],
        password=data['password'],
        # email=data['email']
    )
    return JsonResponse({'success': True, 'id': user.id})

def get_user_by_username(request, username):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({
        "id": user.id,
        "username": user.username,
    })

def get_user(request, user_id):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({
        "id": user.id,
        "username": user.username,
        # "email": user.email
    })

def update_user(request, user_id):
    if request.method != "PATCH":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    data = json.loads(request.body or "{}")

    username = data.get("username")
    password = data.get("password")
    # email = data.get("email")

    if username:
        user.username = username
    if password:
        user.password = password
    # if email:
    #     user.email = email

    user.save()

    return JsonResponse({"success": True})

def books_by_genre(request, genre):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    books = Book.objects.filter(genre__iexact=genre)

    data = [
        {
            "isbn": b.isbn,
            "title": b.title,
            "genre": b.genre,
            "price": float(b.price) if b.price is not None else None,
        }
        for b in books
    ]

    return JsonResponse(data, safe=False)

@csrf_exempt
def add_to_cart(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body or "{}")

    user_id = data.get("userId")
    book_id = data.get("bookId")
    qty = data.get("quantity")

    if not user_id or not book_id or not qty:
        return JsonResponse({"error": "need userId bookId quantity"}, status=400)

    user = User.objects.get(id=user_id)
    book = Book.objects.get(id=book_id)

    item = CartItem.objects.create(user=user, book=book, quantity=qty)

    return JsonResponse({"success": True, "cartItemId": item.id}, status=201)

@csrf_exempt
def add_book(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    isbn = data.get("isbn")
    title = data.get("title")
    genre = data.get("genre")
    price = data.get("price")
    publisher = data.get("publisher")
    description = data.get("description")
    year_published = data.get("year_published")
    copies_sold = data.get("copies_sold", 0)
    author_id = data.get("authorId")

    if not isbn or not title or not genre or price is None or not publisher:
        return JsonResponse({
            "error": "isbn, title, genre, price, and publisher are required"
        }, status=400)

    author = None
    if author_id is not None:
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return JsonResponse({"error": "Author not found"}, status=404)

    try:
        book = Book.objects.create(
            isbn=isbn,
            title=title,
            genre=genre,
            price=price,
            publisher=publisher,
            description=description,
            year_published=year_published,
            copies_sold=copies_sold,
            author=author
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({
        "success": True,
        "id": book.id,
        "message": "Book created successfully"
    }, status=201)

@csrf_exempt
def top_sellers(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    books = Book.objects.order_by('-copies_sold')[:10]

    data = [
        {
            "isbn": b.isbn,
            "title": b.title,
            "genre": b.genre,
            "price": float(b.price) if b.price is not None else None,
            "publisher": b.publisher,
            "copies_sold": b.copies_sold,
        }
        for b in books
    ]

    return JsonResponse(data, safe=False)

@csrf_exempt
def create_author(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    biography = data.get("biography")
    publisher = data.get("publisher")

    if not first_name or not last_name or not biography or not publisher:
        return JsonResponse({
            "error": "first_name, last_name, biography, and publisher are required"
        }, status=400)

    author = Author.objects.create(
        first_name=first_name,
        last_name=last_name,
        biography=biography,
        publisher=publisher
    )

    return JsonResponse({
        "success": True,
        "authorId": author.id,
        "message": "Author created successfully"
    }, status=201)


def get_book_by_isbn(request, isbn):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    try:
        book = Book.objects.get(isbn=isbn)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)

    return JsonResponse({
        "id": book.id,
        "isbn": book.isbn,
        "title": book.title,
        "genre": book.genre,
        "price": float(book.price) if book.price is not None else None,
        "publisher": book.publisher,
        "description": book.description,
        "year_published": book.year_published,
        "copies_sold": book.copies_sold,
        "author": {
            "id": book.author.id,
            "first_name": book.author.first_name,
            "last_name": book.author.last_name
        } if book.author else None
    })


def get_books_by_author(request, author_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    try:
        author = Author.objects.get(id=author_id)
    except Author.DoesNotExist:
        return JsonResponse({"error": "Author not found"}, status=404)

    books = Book.objects.filter(author=author)

    data = [
        {
            "id": book.id,
            "isbn": book.isbn,
            "title": book.title,
            "genre": book.genre,
            "price": float(book.price) if book.price is not None else None,
            "publisher": book.publisher,
            "year_published": book.year_published,
            "copies_sold": book.copies_sold
        }
        for book in books
    ]

    return JsonResponse(data, safe=False)

@csrf_exempt
def books_by_rating(request, minRating):
    if request.method != "GET":
        return JsonResponse({"error":"GET only"}, status =405)
    
    try:
        min_rating = float(minRating)
    except ValueError:
        return JsonResponse({"error":"Invalid rating value"}, status = 400)
    
    books = Book.objects.filter(rating__gte = min_rating)

    data = [
        {
            "isbn": b.isbn,
            "title": b.title,
            "genre": b.genre,
            "price": float(b.price) if b.price is not None else None,
            "rating": b.rating,
        }
        for b in books
    ]

    return JsonResponse(data, safe=False)

@csrf_exempt
def discount_books(request):
    if request.method != "PATCH":
        return JsonResponse({"error": "PATCH only"}, status = 405)
    
    try:
        data = json.loads(request.body or "{}")

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status= 400)
    
    publisher = data.get("publisher")
    discount_percent = data.get("discountPercent")

    if publisher is None or discount_percent is None:
        return JsonResponse({"error":"publisher and discountPercent required"}, status =400)
    
    try:
        discount_percent = float(discount_percent)
    except ValueError:
        return JsonResponse({"error": "discountPercent must be numeric"}, status=400)
    
    books = Book.objects.filter(publisher=publisher)

    updated =[]

    for book in books:
        if book.price is not None:
            old_price = float(book.price)
            new_price = old_price * (1 - discount_percent / 100)
            book.price = round(new_price, 2)
            book.save()

            updated.append({
                "isbn": book.isbn,
                "title": book.title,
                "old_price": old_price,
                "new_price": float(book.price)
            })

    return JsonResponse({
        "publisher": publisher,
        "discountPercent": discount_percent,
        "updated_books": updated
    })

@csrf_exempt
def create_comment(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = data.get("userId")
    book_id = data.get("bookId")
    comment_text = data.get("comment")

    if not user_id or not book_id or not comment_text:
        return JsonResponse({"error": "userId, bookId, comment required"}, status=400)

    try:
        user = User.objects.get(id=user_id)
        book = Book.objects.get(id=book_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)

    comment = Comment.objects.create(
        user=user,
        book=book,
        comment=comment_text
    )

    return JsonResponse({
        "message": "Comment created",
        "commentId": comment.id
    }, status=201)

def get_book_comments(request, book_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)

    comments = Comment.objects.filter(book=book).order_by("-created_at")

    data = [
        {
            "id": c.id,
            "userId": c.user.id,
            "username": c.user.username,
            "comment": c.comment,
            "created_at": c.created_at
        }
        for c in comments
    ]

    return JsonResponse(data, safe=False)
    
def get_average_rating(request, book_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    ratings = Rating.objects.filter(book_id=book_id)

    if ratings.count() == 0:
        return JsonResponse({
            "bookId": book_id,
            "average_rating": 0,
            "number_of_ratings": 0
        })

    avg = sum(r.rating for r in ratings) / ratings.count()

    return JsonResponse({
        "bookId": book_id,
        "average_rating": round(avg, 2),
        "number_of_ratings": ratings.count()
    })

@csrf_exempt
def add_rating(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = data.get("userId")
    book_id = data.get("bookId")
    rating_value = data.get("rating")

    if user_id is None or book_id is None or rating_value is None:
        return JsonResponse({"error": "userId, bookId, and rating required"}, status=400)

    try:
        rating_value = int(rating_value)
    except (TypeError, ValueError):
        return JsonResponse({"error": "rating must be an integer"}, status=400)

    if rating_value < 1 or rating_value > 5:
        return JsonResponse({"error": "rating must be between 1 and 5"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)

    existing_rating = Rating.objects.filter(user=user, book=book).first()
    if existing_rating:
        return JsonResponse({"error": "User already rated this book"}, status=400)

    new_rating = Rating.objects.create(
        user=user,
        book=book,
        rating=rating_value
    )

    ratings = Rating.objects.filter(book=book)
    avg = sum(r.rating for r in ratings) / ratings.count()
    book.rating = round(avg, 2)
    book.save()

    return JsonResponse({
        "message": "Rating added",
        "ratingId": new_rating.id,
        "bookId": book.id,
        "userId": user.id,
        "rating": new_rating.rating,
        "updated_average_rating": book.rating
    }, status=201)


@csrf_exempt
def add_credit_card(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_id = data.get("userId")
    card_number = data.get("cardNumber")
    expiry_date = data.get("expiryDate")
    cvv = data.get("cvv")

    if not user_id or not card_number or not expiry_date or not cvv:
        return JsonResponse({"error": "All fields are required"}, status=400)

    try:
        User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({"message": "Credit card added successfully"}, status=201)

@csrf_exempt
def add_book_to_wishlist(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    wishlist_id = data.get("wishlistId")
    book_id = data.get("bookId")

    if not wishlist_id or not book_id:
        return JsonResponse({"error": "wishlistId and bookId required"}, status=400)

    try:
        wishlist = Wishlist.objects.get(id=wishlist_id)
    except Wishlist.DoesNotExist:
        return JsonResponse({"error": "Wishlist not found"}, status=404)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)

    wishlist_item = WishlistItem.objects.create(wishlist=wishlist, book=book)

    return JsonResponse({
        "message": "Book added to wishlist",
        "wishlistItemId": wishlist_item.id
    }, status=201)


def get_cart_items(request, userId):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    items = CartItem.objects.filter(user_id=userId)

    data = [
        {
            "book": item.book.title,
            "quantity": item.quantity,
            "price": float(item.book.price) if item.book.price else 0
        }
        for item in items
    ]

    return JsonResponse(data, safe=False)


def get_cart_subtotal(request, userId):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    items = CartItem.objects.filter(user_id=userId)

    subtotal = sum(
        (item.book.price or 0) * item.quantity
        for item in items
    )

    return JsonResponse({"subtotal": float(subtotal)})

def get_wishlist_items(request, wishlistId):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    try:
        wishlist = Wishlist.objects.get(id=wishlistId)
    except Wishlist.DoesNotExist:
        return JsonResponse({"error": "Wishlist not found"}, status=404)

    items = WishlistItem.objects.filter(wishlist=wishlist)

    data = [
        {
            "wishlistItemId": item.id,
            "bookId": item.book.id,
            "isbn": item.book.isbn,
            "title": item.book.title,
            "genre": item.book.genre,
            "price": float(item.book.price) if item.book.price is not None else None,
            "publisher": item.book.publisher
        }
        for item in items
    ]

    return JsonResponse(data, safe=False)


@csrf_exempt
def move_wishlist_item_to_cart(request, wishlistId):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE only"}, status=405)

    try:
        wishlist = Wishlist.objects.get(id=wishlistId)
    except Wishlist.DoesNotExist:
        return JsonResponse({"error": "Wishlist not found"}, status=404)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    book_id = data.get("bookId")
    quantity = data.get("quantity", 1)

    if not book_id:
        return JsonResponse({"error": "bookId is required"}, status=400)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)

    wishlist_item = WishlistItem.objects.filter(wishlist=wishlist, book=book).first()
    if not wishlist_item:
        return JsonResponse({"error": "Book is not in this wishlist"}, status=404)

    cart_item = CartItem.objects.filter(user=wishlist.user, book=book).first()
    if cart_item:
        cart_item.quantity += int(quantity)
        cart_item.save()
    else:
        cart_item = CartItem.objects.create(
            user=wishlist.user,
            book=book,
            quantity=int(quantity)
        )

    wishlist_item.delete()

    return JsonResponse({
        "message": "Book moved from wishlist to cart",
        "cartItemId": cart_item.id,
        "userId": wishlist.user.id,
        "bookId": book.id
    })


@csrf_exempt
def remove_from_cart(request):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE only"}, status=405)

    data = json.loads(request.body or "{}")

    user_id = data.get("userId")
    book_id = data.get("bookId")

    if not user_id or not book_id:
        return JsonResponse({"error": "userId and bookId required"}, status=400)

    CartItem.objects.filter(user_id=user_id, book_id=book_id).delete()

    return JsonResponse({"message": "Item removed"})

