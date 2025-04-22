from rest_framework import generics, permissions
from .models import ServiceHistory, LineServiceHistory, BookRequest
from .serializers import ServiceHistorySerializer, LineServiceHistorySerializer, BookRequestSerializer

class ServiceHistoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = ServiceHistory.objects.all()
    serializer_class = ServiceHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ServiceHistoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceHistory.objects.all()
    serializer_class = ServiceHistorySerializer
    permission_classes = [permissions.IsAuthenticated]


class LineServiceHistoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = LineServiceHistory.objects.all()
    serializer_class = LineServiceHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

class LineServiceHistoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LineServiceHistory.objects.all()
    serializer_class = LineServiceHistorySerializer
    permission_classes = [permissions.IsAuthenticated]


class BookRequestListCreateAPIView(generics.ListCreateAPIView):
    queryset = BookRequest.objects.all()
    serializer_class = BookRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

class BookRequestDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BookRequest.objects.all()
    serializer_class = BookRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
