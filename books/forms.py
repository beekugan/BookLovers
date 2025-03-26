from django import forms
from .models import Book, Author, Genre, Publisher


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'publisher', 'author', 'genre', 'quantity']


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name_author', 'surname_author']

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name_genre']

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name_publisher']
