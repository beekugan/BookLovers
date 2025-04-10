from django import forms
from books.models import Genre, Author, Publisher, Book
from users.models import User

STATUS_CHOICES = [
    ('active', 'Активні'),
    ('returned', 'Повернені'),
    ('overdue', 'Прострочені'),
]

COLUMN_CHOICES_LOAN = [
    ('book', 'Книга'),
    ('reader', 'Читач'),
    ('librarian', 'Бібліотекар'),
    ('status', 'Статус'),
    ('date_when_was_taken', 'Дата видачі'),
    ('date_when_should_return', 'Дата повернення'),
    ('date_when_returned', 'Дата фактичного повернення'),
]

COLUMN_CHOICES_BOOK = [
    ('name', 'Назва'),
    ('author', 'Автор'),
    ('genre', 'Жанр'),
    ('publisher', 'Видавництво'),
    ('quantity', 'Кількість'),
    ('status', 'Статус'),
]


class LoanReportForm(forms.Form):
    status = forms.MultipleChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Статуси видач"
    )

    visible_columns = forms.MultipleChoiceField(
        choices=COLUMN_CHOICES_LOAN,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        initial=[c[0] for c in COLUMN_CHOICES_LOAN],
        label="Колонки таблиці"
    )

    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        required=False,
        label="Книга"
    )
    reader = forms.ModelChoiceField(
        queryset=User.objects.filter(type_user='reader'),
        required=False,
        label="Читач"
    )
    librarian = forms.ModelChoiceField(
        queryset=User.objects.filter(type_user='librarian'),
        required=False,
        label="Бібліотекар"
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        label="Жанр"
    )
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        required=False,
        label="Автор"
    )
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        label="Видавництво"
    )


class BookReportForm(forms.Form):
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        required=False,
        label="Книга"
    )
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        required=False,
        label="Автор"
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        label="Жанр"
    )
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        label="Видавництво"
    )

    visible_columns = forms.MultipleChoiceField(
        choices=COLUMN_CHOICES_BOOK,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        initial=[c[0] for c in COLUMN_CHOICES_BOOK],
        label="Колонки таблиці"
    )
