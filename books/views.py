from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Book, Author, Genre, Publisher
from .forms import BookForm, AuthorForm, GenreForm, PublisherForm

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
            return redirect('tools')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Додати книгу'})

@login_required
@user_passes_test(is_librarian)
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            book.save()
            form.save_m2m()  # Збереження зв’язків many-to-many
            return redirect('tools')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Редагувати книгу'})

@login_required
@user_passes_test(is_librarian)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.delete()
        return redirect('tools')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

# ==== АВТОРИ ====
@login_required
@user_passes_test(is_librarian)
def author_create(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tools')
    else:
        form = AuthorForm()
    return render(request, 'books/author_form.html', {'form': form, 'title': 'Додати автора'})

@login_required
@user_passes_test(is_librarian)
def author_update(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == "POST":
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            return redirect('tools')
    else:
        form = AuthorForm(instance=author)
    return render(request, 'books/author_form.html', {'form': form, 'title': 'Редагувати автора'})

@login_required
@user_passes_test(is_librarian)
def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == "POST":
        author.delete()
        return redirect('tools')
    return render(request, 'books/author_confirm_delete.html', {'author': author})

# ==== ЖАНРИ ====
@login_required
@user_passes_test(is_librarian)
def genre_create(request):
    if request.method == "POST":
        form = GenreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tools')
    else:
        form = GenreForm()
    return render(request, 'books/genre_form.html', {'form': form, 'title': 'Додати жанр'})

@login_required
@user_passes_test(is_librarian)
def genre_update(request, pk):
    genre = get_object_or_404(Genre, pk=pk)
    if request.method == "POST":
        form = GenreForm(request.POST, instance=genre)
        if form.is_valid():
            form.save()
            return redirect('tools')
    else:
        form = GenreForm(instance=genre)
    return render(request, 'books/genre_form.html', {'form': form, 'title': 'Редагувати жанр'})

@login_required
@user_passes_test(is_librarian)
def genre_delete(request, pk):
    genre = get_object_or_404(Genre, pk=pk)
    if request.method == "POST":
        genre.delete()
        return redirect('tools')
    return render(request, 'books/genre_confirm_delete.html', {'genre': genre})

# ==== ВИДАВНИЦТВА ====
@login_required
@user_passes_test(is_librarian)
def publisher_create(request):
    if request.method == "POST":
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tools')
    else:
        form = PublisherForm()
    return render(request, 'books/publisher_form.html', {'form': form, 'title': 'Додати видавництво'})

@login_required
@user_passes_test(is_librarian)
def publisher_update(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.method == "POST":
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
            return redirect('tools')
    else:
        form = PublisherForm(instance=publisher)
    return render(request, 'books/publisher_form.html', {'form': form, 'title': 'Редагувати видавництво'})

@login_required
@user_passes_test(is_librarian)
def publisher_delete(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.method == "POST":
        publisher.delete()
        return redirect('tools')
    return render(request, 'books/publisher_confirm_delete.html', {'publisher': publisher})
