from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta

from logbook.models import LineServiceHistory
from notifications.models import Notification
from users.models import User

class Command(BaseCommand):
    help = 'Check for upcoming returns, overdue returns, and block users with long overdue books'

    def handle(self, *args, **options):
        today = now().date()

        loans = LineServiceHistory.objects.filter(status='active')

        for loan in loans:
            user = loan.service_history.reader
            due_date = loan.date_when_should_return
            days_until_due = (due_date - today).days
            days_overdue = (today - due_date).days

            # 🔔 Нагадування за 2 дні до повернення
            if days_until_due == 2:
                self._create_notification(
                    user,
                    f"Нагадування: поверніть книгу '{loan.book.name}' до {due_date}"
                )

            # ❗ Сповіщення про прострочку
            if days_overdue == 1:
                self._create_notification(
                    user,
                    f"Прострочка: книга '{loan.book.name}' мала бути повернена {due_date}"
                )

            # 🚫 Блокування акаунта після 7 днів
            if days_overdue == 7:
                self._create_notification(
                    user,
                    f"Акаунт заблоковано через прострочку книги '{loan.book.name}' на 7 днів"
                )
                user.is_active = False
                user.save()

        self.stdout.write(self.style.SUCCESS('Перевірка завершена'))

    def _create_notification(self, user, message):
        Notification.objects.create(
            user=user,
            message=message
        )
