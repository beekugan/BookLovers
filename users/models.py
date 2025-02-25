from django.db import models
from django.contrib.auth.models import AbstractUser

# Користувач (розширюємо стандартного User)
class User(AbstractUser):
    TYPE_CHOICES = [
        ('reader', 'Reader'),
        ('librarian', 'Librarian'),
    ]
    type_user = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.get_type_user_display()})"


# Факультет
class Faculty(models.Model):
    name_faculty = models.CharField(max_length=255)
    name_dean = models.CharField(max_length=255)
    tel_dean = models.CharField(max_length=20)

    def __str__(self):
        return self.name_faculty


# Спеціальність
class Speciality(models.Model):
    name_speciality = models.CharField(max_length=255)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_speciality


# Зв’язок читача зі спеціальністю
class ReaderSpeciality(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'type_user': 'reader'})
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.speciality.name_speciality}"
