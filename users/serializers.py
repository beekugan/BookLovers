from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Faculty, Speciality, ReaderSpeciality

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'type_user', 'is_blocked']

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name']

class SpecialitySerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = Speciality
        fields = ['id', 'name', 'faculty']

class ReaderSpecialitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    faculty = FacultySerializer()
    speciality = SpecialitySerializer()

    class Meta:
        model = ReaderSpeciality
        fields = ['id', 'user', 'faculty', 'speciality']
