from django.shortcuts import render
from .forms import LoanReportForm, BookReportForm
from logbook.models import LineServiceHistory
from books.models import Book
from datetime import date

def report_view(request):
    mode = request.GET.get('mode', 'loans')
    form_submitted = bool(request.GET)

    # --- Створюємо форми
    loan_form = LoanReportForm(request.GET if form_submitted else None)
    book_form = BookReportForm(request.GET if form_submitted else None)

    loan_form_is_valid = loan_form.is_valid()
    book_form_is_valid = book_form.is_valid()

    # --- Задаємо дефолтні значення для visible_columns, якщо форма невалідна
    if mode == 'loans':
        if loan_form_is_valid:
            visible_columns = loan_form.cleaned_data.get('visible_columns')
        else:
            visible_columns = [c[0] for c in LoanReportForm.base_fields['visible_columns'].choices]
            loan_form = LoanReportForm(initial={
                'status': [s[0] for s in LoanReportForm.base_fields['status'].choices],
                'visible_columns': visible_columns,
            })
    elif mode == 'books':
        if book_form_is_valid:
            visible_columns = book_form.cleaned_data.get('visible_columns')
        else:
            visible_columns = [c[0] for c in BookReportForm.base_fields['visible_columns'].choices]
            book_form = BookReportForm(initial={
                'visible_columns': visible_columns,
            })

    loan_data = []
    book_data = []

    # --- Видачі
    if mode == 'loans' and loan_form_is_valid:
        qs = LineServiceHistory.objects.select_related(
            'book', 'service_history__reader', 'service_history__librarian'
        )

        statuses = loan_form.cleaned_data.get('status') or [s[0] for s in LoanReportForm.base_fields['status'].choices]

        if 'overdue' in statuses:
            today = date.today()
            overdue_qs = qs.filter(status='active', date_when_should_return__lt=today)
            statuses = [s for s in statuses if s != 'overdue']
            qs = qs.filter(status__in=statuses) | overdue_qs
        else:
            qs = qs.filter(status__in=statuses)

        if loan_form.cleaned_data.get('book'):
            qs = qs.filter(book=loan_form.cleaned_data['book'])

        if loan_form.cleaned_data.get('reader'):
            qs = qs.filter(service_history__reader=loan_form.cleaned_data['reader'])

        if loan_form.cleaned_data.get('librarian'):
            qs = qs.filter(service_history__librarian=loan_form.cleaned_data['librarian'])

        if loan_form.cleaned_data.get('genre'):
            qs = qs.filter(book__genre=loan_form.cleaned_data['genre'])

        if loan_form.cleaned_data.get('author'):
            qs = qs.filter(book__authors=loan_form.cleaned_data['author'])

        if loan_form.cleaned_data.get('publisher'):
            qs = qs.filter(book__publisher=loan_form.cleaned_data['publisher'])

        loan_data = qs.order_by('-date_when_was_taken')

    # --- Книги
    elif mode == 'books' and book_form_is_valid:
        qs = Book.objects.all()

        if book_form.cleaned_data.get('book'):
            qs = qs.filter(id=book_form.cleaned_data['book'].id)

        if book_form.cleaned_data.get('author'):
            qs = qs.filter(authors=book_form.cleaned_data['author'])

        if book_form.cleaned_data.get('genre'):
            qs = qs.filter(genre=book_form.cleaned_data['genre'])

        if book_form.cleaned_data.get('publisher'):
            qs = qs.filter(publisher=book_form.cleaned_data['publisher'])

        book_data = qs.order_by('name')

    context = {
        'loan_form': loan_form,
        'book_form': book_form,
        'loan_data': loan_data,
        'book_data': book_data,
        'mode': mode,
        'visible_columns': visible_columns,
    }
    return render(request, 'reports/report.html', context)
