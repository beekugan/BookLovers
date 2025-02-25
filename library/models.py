from django.db import models
from users.models import User
from books.models import Book

# Журнал видачі книг
class ServiceHistory(models.Model):
    reader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowed_books", limit_choices_to={'type_user': 'reader'})
    librarian = models.ForeignKey(User, on_delete=models.CASCADE, related_name="processed_books", limit_choices_to={'type_user': 'librarian'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Service #{self.id} - {self.reader.username}"


# Окремий запис у журналі (видача книги)
class LineServiceHistory(models.Model):
    service_history = models.ForeignKey(ServiceHistory, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_when_was_taken = models.DateField()
    date_when_should_return = models.DateField()
    date_when_returned = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.name} (Taken: {self.date_when_was_taken})"
