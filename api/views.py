from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Wishlist, User, Book, CartItem


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