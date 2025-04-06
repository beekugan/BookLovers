from django.core.management.base import BaseCommand
from django.utils.timezone import now

from logbook.models import LineServiceHistory
from notifications.utils import notify_user


class Command(BaseCommand):
    help = "Перевіряє строки повернення книг і надсилає сповіщення або блокує акаунти"

    def handle(self, *args, **kwargs):
        today = now().date()

        loans = LineServiceHistory.objects.filter(status='active')
        self.stdout.write(f"🔍 Знайдено {loans.count()} активних видач")

        for loan in loans:
            user = loan.service_history.reader
            days_until_return = (loan.date_when_should_return - today).days
            days_overdue = (today - loan.date_when_should_return).days

            self.stdout.write(f"📚 Книга: {loan.book.name}")
            self.stdout.write(f"👤 Користувач: {user.email}")
            self.stdout.write(f"📅 До повернення: {days_until_return} днів | Протерміновано на: {days_overdue} днів")

            if days_until_return == 2:
                notify_user(
                    user,
                    f"Через 2 дні потрібно повернути книгу «{loan.book.name}» (до {loan.date_when_should_return}).",
                    type='reminder'
                )
                self.stdout.write("🔔 Надіслано нагадування")

            elif days_overdue == 1:
                notify_user(
                    user,
                    f"Ви прострочили повернення книги «{loan.book.name}». Поверніть якомога швидше.",
                    type='warning'
                )
                self.stdout.write("⚠️ Надіслано попередження")

            elif 2 <= days_overdue < 7:
                notify_user(
                    user,
                    f"Ви прострочили повернення книги «{loan.book.name}» на {days_overdue} днів. Поверніть її якнайшвидше.",
                    type='warning'
                )
                self.stdout.write(f"⚠️ Надіслано повторне попередження (на {days_overdue} днів)")

            elif days_overdue >= 7 and not user.is_blocked:
                notify_user(
                    user,
                    f"Ваш акаунт заблоковано через прострочення книги «{loan.book.name}» на понад 7 днів.",
                    type='block'
                )
                user.is_blocked = True
                user.save()
                self.stdout.write("⛔ Користувача заблоковано")
