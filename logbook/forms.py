from django import forms
from books.models import Book
from users.models import User
from .models import ServiceHistory, LineServiceHistory, BookRequest


# Форма для видачі книги
class IssueBookForm(forms.ModelForm):
    reader = forms.ModelChoiceField(
        queryset=User.objects.filter(type_user='reader', is_blocked=False),
        label="Читач"
    )
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(status='available'),
        label="Книга"
    )

    class Meta:
        model = ServiceHistory
        fields = ['reader']

    def save(self, librarian, commit=True):
        service_history = super().save(commit=False)
        service_history.librarian = librarian

        if commit:
            service_history.save()

        return service_history


# Форма для повернення книги
class ReturnBookForm(forms.Form):
    loan_code = forms.CharField(max_length=4, label="Номер видачі")

    def clean_loan_code(self):
        loan_code = self.cleaned_data['loan_code']
        if not ServiceHistory.objects.filter(loan_code=loan_code).exists():
            raise forms.ValidationError("Неправильний номер видачі.")
        return loan_code


class BookRequestForm(forms.ModelForm):
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(status='available'),
        label="Оберіть книгу"
    )

    class Meta:
        model = BookRequest
        fields = ['book']

