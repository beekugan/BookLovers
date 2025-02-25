from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Genre, BookGenre, Book
import json

@csrf_exempt  # Вимикаємо CSRF для тестування (небезпечно для продакшну)
def add_genre(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            genre_name = data.get("name_genre")

            if not genre_name:
                return JsonResponse({"error": "Поле 'name_genre' обов'язкове"}, status=400)

            genre, created = Genre.objects.get_or_create(name_genre=genre_name)

            if created:
                return JsonResponse({"message": "Жанр додано", "id": genre.id, "name_genre": genre.name_genre}, status=201)
            else:
                return JsonResponse({"message": "Жанр вже існує", "id": genre.id, "name_genre": genre.name_genre}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Некоректний JSON"}, status=400)

    return JsonResponse({"error": "Доступний тільки POST-запит"}, status=405)
