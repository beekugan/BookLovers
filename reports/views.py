
import csv
import tempfile
from datetime import date

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.encoding import smart_str


from books.models import Book
from logbook.models import LineServiceHistory
from .forms import LoanReportForm, BookReportForm

# --- Лейбли для CSV заголовків
COLUMN_LABELS = {
    'book': 'Книга',
    'reader': 'Читач',
    'librarian': 'Бібліотекар',
    'status': 'Статус',
    'date_when_was_taken': 'Дата видачі',
    'date_when_should_return': 'Дата повернення',
    'date_when_returned': 'Фактичне повернення',
    'name': 'Назва',
    'author': 'Автор',
    'genre': 'Жанр',
    'publisher': 'Видавництво',
    'quantity': 'Кількість',
}


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
            qs = qs.filter(book__author=loan_form.cleaned_data['author'])

        if loan_form.cleaned_data.get('publisher'):
            qs = qs.filter(book__publisher=loan_form.cleaned_data['publisher'])

        loan_data = qs.order_by('-date_when_was_taken')

    # --- Книги
    elif mode == 'books' and book_form_is_valid:
        qs = Book.objects.all()

        if book_form.cleaned_data.get('book'):
            qs = qs.filter(id=book_form.cleaned_data['book'].id)

        if book_form.cleaned_data.get('author'):
            qs = qs.filter(author=book_form.cleaned_data['author'])

        if book_form.cleaned_data.get('genre'):
            qs = qs.filter(genre=book_form.cleaned_data['genre'])

        if book_form.cleaned_data.get('publisher'):
            qs = qs.filter(publisher=book_form.cleaned_data['publisher'])

        book_data = qs.order_by('name')

    # --- Експорт у CSV ---
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="report_{mode}.csv"'

        # Додаємо BOM для підтримки кирилиці в Excel
        response.write('\ufeff')  # BOM

        writer = csv.writer(response, delimiter=';')
        writer.writerow([COLUMN_LABELS.get(col, col) for col in visible_columns])

        if mode == 'loans':
            for entry in loan_data:
                row = []
                for col in visible_columns:
                    if col == 'book':
                        row.append(smart_str(entry.book.name))
                    elif col == 'reader':
                        row.append(smart_str(entry.service_history.reader.username))
                    elif col == 'librarian':
                        row.append(smart_str(entry.service_history.librarian.username))
                    elif col == 'status':
                        row.append(smart_str(entry.get_status_display()))
                    elif col == 'date_when_was_taken':
                        row.append(entry.date_when_was_taken.strftime('%d.%m.%Y'))
                    elif col == 'date_when_should_return':
                        row.append(entry.date_when_should_return.strftime('%d.%m.%Y'))
                    elif col == 'date_when_returned':
                        row.append(entry.date_when_returned.strftime('%d.%m.%Y') if entry.date_when_returned else '')
                writer.writerow(row)

        elif mode == 'books':
            for book in book_data:
                row = []
                for col in visible_columns:
                    if col == 'name':
                        row.append(smart_str(book.name))
                    elif col == 'author':
                        row.append(smart_str(book.author))
                    elif col == 'genre':
                        row.append(smart_str(book.genre if book.genre else ''))
                    elif col == 'publisher':
                        row.append(smart_str(book.publisher if book.publisher else ''))
                    elif col == 'quantity':
                        row.append(book.quantity)
                    elif col == 'status':
                        row.append(smart_str(book.get_status_display()))
                writer.writerow(row)

        return response

    # --- Звичайне відображення сторінки
    context = {
        'loan_form': loan_form,
        'book_form': book_form,
        'loan_data': loan_data,
        'book_data': book_data,
        'mode': mode,
        'visible_columns': visible_columns,
    }

    return render(request, 'reports/report.html', context)


