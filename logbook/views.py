from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.utils.timezone import now, timedelta

from .forms import BookRequestForm
from .forms import IssueBookForm, ReturnBookForm
from .models import LineServiceHistory, BookRequest
from .models import ServiceHistory


# Перевірка, чи є користувач бібліотекарем
def is_librarian(user):
    return user.is_authenticated and user.type_user == 'librarian'


# Видача книги
@login_required
@user_passes_test(is_librarian)
def issue_book(request):
    if request.method == "POST":
        form = IssueBookForm(request.POST)
        if form.is_valid():
            service_history = form.save(librarian=request.user)

            book = form.cleaned_data['book']
            LineServiceHistory.objects.create(
                service_history=service_history,
                book=book,
                date_when_was_taken=now().date(),
                date_when_should_return=now().date() + timedelta(days=14),
            )

            # Оновлення статусу книги
            book.status = 'borrowed'
            book.quantity -= 1
            if book.quantity == 0:
                book.status = 'borrowed'
            book.save()

            return redirect('issue_book')  # Перенаправлення на сторінку видачі
    else:
        form = IssueBookForm()

    return render(request, 'logbook/issue_book.html', {'form': form})


# Повернення книги
@login_required
@user_passes_test(is_librarian)
def return_book(request):
    if request.method == "POST":
        form = ReturnBookForm(request.POST)
        if form.is_valid():
            loan_code = form.cleaned_data['loan_code']
            service_history = get_object_or_404(ServiceHistory, loan_code=loan_code)
            loan_items = service_history.loan_items.filter(status='active')

            for loan in loan_items:
                loan.date_when_returned = now().date()
                loan.status = 'returned'
                loan.book.quantity += 1  # Повертаємо книгу
                if loan.book.status == 'borrowed':
                    loan.book.status = 'available'
                loan.book.save()
                loan.save()

            return redirect('return_book')  # Перенаправлення на сторінку повернення

    else:
        form = ReturnBookForm()

    return render(request, 'logbook/return_book.html', {'form': form})


@login_required
def user_history(request):
    histories = ServiceHistory.objects.filter(reader=request.user).prefetch_related("loan_items")

    return render(request, "logbook/history.html", {"histories": histories})

@login_required
def create_book_request(request):
    if request.method == "POST":
        form = BookRequestForm(request.POST)
        if form.is_valid():
            book_request = form.save(commit=False)
            book_request.reader = request.user
            book_request.save()
            messages.success(request, f"Ваш запит створено. Код вашого запиту: {book_request.request_code}")
            return redirect('user_book_requests')
    else:
        form = BookRequestForm()
    return render(request, 'logbook/create_book_request.html', {'form': form})

def is_librarian(user):
    return user.is_authenticated and user.type_user == 'librarian'

@login_required
@user_passes_test(is_librarian)
def approve_book_request(request, request_code):
    book_request = get_object_or_404(BookRequest, request_code=request_code, is_approved=False)
    book = book_request.book

    if book.quantity > 0:
        book_request.is_approved = True
        book_request.save()

        # Створення запису в ServiceHistory та LineServiceHistory
        service_history = ServiceHistory.objects.create(
            reader=book_request.reader,
            librarian=request.user
        )
        LineServiceHistory.objects.create(
            service_history=service_history,
            book=book,
            date_when_was_taken=now().date(),
            date_when_should_return=now().date() + timedelta(days=14),
        )

        # Оновлення статусу книги
        book.quantity -= 1
        if book.quantity == 0:
            book.status = 'borrowed'
        book.save()

        messages.success(request, f"Запит {request_code} підтверджено. Книга видана читачу.")
    else:
        messages.error(request, "Неможливо видати книгу. Вона недоступна.")

    return redirect('pending_book_requests')


def is_librarian(user):
    return user.is_authenticated and user.type_user == 'librarian'

@login_required
@user_passes_test(is_librarian)
def pending_book_requests(request):
    book_requests = BookRequest.objects.filter(is_approved=False)
    return render(request, 'logbook/pending_book_requests.html', {'book_requests': book_requests})


@login_required
def user_book_requests(request):
    requests = BookRequest.objects.filter(reader=request.user).order_by('-created_at')
    return render(request, 'logbook/user_book_requests.html', {'requests': requests})