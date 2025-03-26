from django.db import models


# Видавець
class Publisher(models.Model):
    name_publisher = models.CharField(max_length=255)

    def __str__(self):
        return self.name_publisher

# Автор
class Author(models.Model):
    name_author = models.CharField(max_length=255)
    surname_author = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name_author} {self.surname_author}"

# Жанр
class Genre(models.Model):
    name_genre = models.CharField(max_length=255)

    def __str__(self):
        return self.name_genre

# Книга
class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
    ]

    name = models.CharField(max_length=255)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.name} ({self.quantity} шт.)"




