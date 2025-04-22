from datetime import date
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from books.models import Book
from logbook.models import LineServiceHistory
from .serializers import LoanReportSerializer, BookReportSerializer

class LoanReportAPIView(generics.ListAPIView):
    serializer_class = LoanReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = LineServiceHistory.objects.select_related(
            'book', 'service_history__reader', 'service_history__librarian'
        ).order_by('-date_when_was_taken')

        status = self.request.query_params.getlist('status')
        if 'overdue' in status:
            today = date.today()
            overdue_qs = qs.filter(status='active', date_when_should_return__lt=today)
            status = [s for s in status if s != 'overdue']
            qs = qs.filter(status__in=status) | overdue_qs
        elif status:
            qs = qs.filter(status__in=status)

        for filter_field in ['book', 'reader', 'librarian', 'genre', 'author', 'publisher']:
            value = self.request.query_params.get(filter_field)
            if value:
                if filter_field in ['reader', 'librarian']:
                    qs = qs.filter(**{f'service_history__{filter_field}': value})
                else:
                    qs = qs.filter(**{f'book__{filter_field}': value})

        return qs


class BookReportAPIView(generics.ListAPIView):
    serializer_class = BookReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Book.objects.all().order_by('name')

        for field in ['book', 'author', 'genre', 'publisher']:
            value = self.request.query_params.get(field)
            if value:
                if field == 'book':
                    qs = qs.filter(id=value)
                else:
                    qs = qs.filter(**{field: value})

        return qs
