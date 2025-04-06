from django.db import models
from django.utils.timezone import now
from users.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)
    NOTIFICATION_TYPES = [
        ('reminder', 'Нагадування'),
        ('warning', 'Попередження'),
        ('block', 'Блокування'),
        ('unblock', 'Розблокування')
    ]

    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='reminder')

    def __str__(self):
        return f"{self.user.username}: {self.message[:30]}..."
