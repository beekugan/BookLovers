from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .models import Faculty, Speciality, ReaderSpeciality
from .serializers import (
    UserSerializer,
    FacultySerializer,
    SpecialitySerializer,
    ReaderSpecialitySerializer,
)

User = get_user_model()

# ==== Users ====
class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

# ==== Faculties ====
class FacultyListAPIView(generics.ListAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [permissions.AllowAny]

# ==== Specialities ====
class SpecialityListAPIView(generics.ListAPIView):
    serializer_class = SpecialitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        faculty_id = self.request.query_params.get('faculty_id')
        if faculty_id:
            return Speciality.objects.filter(faculty_id=faculty_id)
        return Speciality.objects.all()

# ==== ReaderSpecialities ====
class ReaderSpecialityListAPIView(generics.ListAPIView):
    queryset = ReaderSpeciality.objects.select_related('user', 'faculty', 'speciality')
    serializer_class = ReaderSpecialitySerializer
    permission_classes = [permissions.IsAdminUser]
