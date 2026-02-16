from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Wishlist, User, Book


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


