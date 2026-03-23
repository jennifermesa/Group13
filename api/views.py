from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# from .models import Wishlist, User, Book, CartItem
# from .models import Comment, Rating
from .models import Wishlist, User, Book, CartItem, Comment, Rating, WishlistItem

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

    data = json.loads(request.body or "{}")

    isbn = data.get("isbn")
    title = data.get("title")
    genre = data.get("genre")
    price = data.get("price")

    if not isbn or not title or not genre:
        return JsonResponse({"error": "need isbn title genre"}, status=400)

    book = Book.objects.create(isbn=isbn, title=title, genre=genre, price=price)
    return JsonResponse({"success": True, "id": book.id}, status=201)

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

def add_credit_card(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body or "{}")

    user_id = data.get("userId")
    card_number = data.get("cardNumber")
    expiry_date = data.get("expiryDate")
    cvv = data.get("cvv")

    if not user_id or not card_number or not expiry_date or not cvv:
        return JsonResponse({"error": "All fields are required"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # Here you would normally save the credit card info securely
    # For this example, we'll just return a success message

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

from django.http import JsonResponse
from .models import CartItem

def get_cart_subtotal(request, userId):
    items = CartItem.objects.filter(user_id=userId)

    subtotal = 0

    for item in items:
        if item.book.price:
            subtotal += item.book.price * item.quantity

    return JsonResponse({"subtotal": float(subtotal)})