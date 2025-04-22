from rest_framework import serializers
from .models import ServiceHistory, LineServiceHistory, BookRequest
from books.models import Book
from users.models import User


class ServiceHistorySerializer(serializers.ModelSerializer):
    reader = serializers.StringRelatedField()
    librarian = serializers.StringRelatedField()
    loan_items = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ServiceHistory
        fields = '__all__'


class LineServiceHistorySerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    service_history = serializers.StringRelatedField()

    class Meta:
        model = LineServiceHistory
        fields = '__all__'


class BookRequestSerializer(serializers.ModelSerializer):
    reader = serializers.StringRelatedField()
    book = serializers.StringRelatedField()

    class Meta:
        model = BookRequest
        fields = '__all__'
