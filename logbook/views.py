from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.utils.timezone import now, timedelta

from .forms import IssueBookForm, ReturnBookForm
from .models import LineServiceHistory
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