from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from .forms import BookForm, AuthorForm, GenreForm, PublisherForm
from .models import Author, Genre, Publisher
from .models import Book


# Перевірка, чи користувач є бібліотекарем
def is_librarian(user):
    return user.is_authenticated and user.type_user == 'librarian'

# Головна сторінка інструментів бібліотекаря
@login_required
@user_passes_test(is_librarian)
def tools(request):
    return render(request, 'books/tools.html')

# ==== КНИГИ ====
@login_required
@user_passes_test(is_librarian)
def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.save()
            form.save_m2m()  # Збереження зв’язків many-to-many
            return redirect('book_add')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Додати книгу'})

@login_required
@user_passes_test(is_librarian)
def book_update(request, pk=None):
    books = Book.objects.all()
    publishers = Publisher.objects.all()
    authors = Author.objects.all()
    genres = Genre.objects.all()

    if request.method == "POST" and pk:
        book = get_object_or_404(Book, pk=pk)
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('tools')

    elif request.method == "GET" and pk:
        book = get_object_or_404(Book, pk=pk)
        data = {
            'id': book.id,
            'name': book.name,
            'publisher': book.publisher.id if book.publisher else None,
            'author': book.author.id if book.author else None,
            'genre': book.genre.id if book.genre else None  # Один жанр
        }
        return JsonResponse(data)

    return render(request, 'books/book_edit.html', {
        'books': books,
        'publishers': publishers,
        'authors': authors,
        'genres': genres
    })

@login_required
@user_passes_test(is_librarian)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.delete()
        return redirect('book_edit')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

def book_detail(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        return JsonResponse({
            "id": book.id,
            "name": book.name,
            "publisher_id": book.publisher.id if book.publisher else None,
            "author_id": book.author.id if book.author else None,
            "genre_id": book.genre.id if book.genre else None  # Один жанр
        })
    except Book.DoesNotExist:
        return JsonResponse({"error": "Книгу не знайдено"}, status=404)





# ==== АВТОРИ ====
@login_required
@user_passes_test(is_librarian)
def author_create(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('author_add')
    else:
        form = AuthorForm()
    return render(request, 'books/author_form.html', {'form': form, 'title': 'Додати автора'})

@login_required
@user_passes_test(is_librarian)
def author_update(request, pk=None):
    authors = Author.objects.all()

    if request.method == "POST" and pk:
        author = get_object_or_404(Author, pk=pk)
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            return redirect('author_edit')  # Повернення до списку

    elif request.method == "GET" and pk:
        author = get_object_or_404(Author, pk=pk)
        return JsonResponse({'id': author.id, 'name_author': author.name_author, 'surname_author': author.surname_author})

    return render(request, 'books/author_edit.html', {'authors': authors})

@login_required
@user_passes_test(is_librarian)
def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == "POST":
        author.delete()
        return redirect('author_edit')  # Повернення до списку
    return render(request, 'books/author_edit.html', {'author': author})

# ==== ЖАНРИ ====
@login_required
@user_passes_test(is_librarian)
def genre_create(request):
    if request.method == "POST":
        form = GenreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('genre_add')
    else:
        form = GenreForm()
    return render(request, 'books/genre_form.html', {'form': form, 'title': 'Додати жанр'})

@login_required
@user_passes_test(is_librarian)
def genre_update(request, pk=None):
    genres = Genre.objects.all()

    if request.method == "POST" and pk:
        genre = get_object_or_404(Genre, pk=pk)
        form = GenreForm(request.POST, instance=genre)
        if form.is_valid():
            form.save()
            return redirect('genre_edit')  # Повернення до списку

    elif request.method == "GET" and pk:
        genre = get_object_or_404(Genre, pk=pk)
        return JsonResponse({'id': genre.id, 'name_genre': genre.name_genre})  # Виправлено ключ

    return render(request, 'books/genre_edit.html', {'genres': genres})

@login_required
@user_passes_test(is_librarian)
def genre_delete(request, pk):
    genre = get_object_or_404(Genre, pk=pk)
    if request.method == "POST":
        genre.delete()
        return redirect('genre_edit')  # Повернення до списку
    return render(request, 'books/genre_edit.html', {'genre': genre})

# ==== ВИДАВНИЦТВА ====
@login_required
@user_passes_test(is_librarian)
def publisher_create(request):
    if request.method == "POST":
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('publisher_add')
    else:
        form = PublisherForm()
    return render(request, 'books/publisher_form.html', {'form': form, 'title': 'Додати видавництво'})

@login_required
@user_passes_test(is_librarian)
def publisher_update(request, pk=None):
    publishers = Publisher.objects.all()

    if request.method == "POST":
        publisher = get_object_or_404(Publisher, pk=pk)
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
            return redirect('publisher_edit')
    elif request.method == "GET":
        if pk:
            publisher = get_object_or_404(Publisher, pk=pk)
            return JsonResponse({'id': publisher.id, 'name_publisher': publisher.name_publisher})
        else:
            return render(request, 'books/publisher_edit.html', {'publishers': publishers})

@login_required
@user_passes_test(is_librarian)
def publisher_delete(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.method == "POST":
        publisher.delete()
        return redirect('publisher_edit')
    return render(request, 'books/publisher_confirm_delete.html', {'publisher': publisher})
