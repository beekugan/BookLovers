from django.db import models
from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta
from users.models import User
from books.models import Book


# Журнал видачі книг
class ServiceHistory(models.Model):
    loan_code = models.CharField(max_length=4, unique=True, editable=False)
    reader = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="borrowed_books", limit_choices_to={'type_user': 'reader'}
    )
    librarian = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="processed_books", limit_choices_to={'type_user': 'librarian'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.loan_code:
            self.loan_code = get_random_string(4).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan {self.loan_code} - {self.reader.username}"


# Окремий запис у журналі (видача книги)

def default_return_date():
    return now().date() + timedelta(days=14)
class LineServiceHistory(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активний'),
        ('returned', 'Повернуто'),
    ]

    service_history = models.ForeignKey(ServiceHistory, on_delete=models.CASCADE, related_name="loan_items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_when_was_taken = models.DateField(auto_now_add=True)
    date_when_should_return = models.DateField(default=default_return_date)
    date_when_returned = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def save(self, *args, **kwargs):
        if self.date_when_returned:
            self.status = 'returned'
            self.book.status = 'available'
            self.book.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.name} ({self.get_status_display()})"
