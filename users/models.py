from django.db import models
from django.contrib.auth.models import AbstractUser

# Користувач (розширюємо стандартного User)
class User(AbstractUser):
    TYPE_CHOICES = [
        ('reader', 'Reader'),
        ('librarian', 'Librarian'),
    ]
    type_user = models.CharField(max_length=10, choices=TYPE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_type_user_display()})"


# Факультет
class Faculty(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name




# Спеціальність
class Speciality(models.Model):
    name = models.CharField(max_length=255, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="specialities")

    def __str__(self):
        return f"{self.name} ({self.faculty})"


    def __str__(self):
        return f"{self.name} ({self.faculty.name})"


# Зв’язок читача зі спеціальністю та факультетом
class ReaderSpeciality(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'type_user': 'reader'})
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.speciality} ({self.faculty})"
