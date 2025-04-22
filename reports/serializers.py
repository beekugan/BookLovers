from rest_framework import serializers
from books.models import Book
from logbook.models import LineServiceHistory

class LoanReportSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    reader = serializers.CharField(source='service_history.reader.username')
    librarian = serializers.CharField(source='service_history.librarian.username')

    class Meta:
        model = LineServiceHistory
        fields = [
            'id', 'book', 'reader', 'librarian', 'status',
            'date_when_was_taken', 'date_when_should_return', 'date_when_returned'
        ]


class BookReportSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    genre = serializers.StringRelatedField()
    publisher = serializers.StringRelatedField()

    class Meta:
        model = Book
        fields = ['id', 'name', 'author', 'genre', 'publisher', 'quantity', 'status']
